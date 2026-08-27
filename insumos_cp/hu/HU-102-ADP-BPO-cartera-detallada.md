# HU-102-ADP-BPO: Adaptador Banco Popular — Consulta Detallada de Cartera

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-102-ADP-BPO                                              |
| Épica          | Épica 1 — Consultas P1                                      |
| Componente     | Adaptador BPO — Cartera Detallada                           |
| Microservicio  | `ms-consultas-oficinas` (mismo que HU-101 y HU-102-ORQ)    |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P1)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | Pendiente                                                   |
| HU Padre       | HU-102-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-20                                                  |

---

## Audiencias

| Rol / Audiencia       | Cómo interactúa                                                                                          |
|-----------------------|----------------------------------------------------------------------------------------------------------|
| Desarrollador Backend | Implementa el adaptador: invoca `consultarCreditoLV` de BPO y mapea la respuesta normalizada             |
| QA / Tester           | Valida la llamada REST a BPO, los certificados TLS, la whitelist IP y el mapeo de campos                 |
| Integrador BPO        | Provee WSDLs, certificados TLS, whitelist IP y soporte técnico al endpoint `CPLIDConsultaProductoLibreDestino` |

---

## Historia de Usuario

**Como** adaptador del canal Oficinas para Banco Popular,  
**quiero** recibir del orquestador la solicitud de consulta detallada de cartera,  
**para** invocar el servicio `consultarCreditoLV` de BPO, transformar la respuesta al modelo normalizado y retornarla al orquestador.

---

## Contexto de Negocio

BPO expone la consulta detallada de cartera (libre destino) a través del servicio `CPLIDConsultaProductoLibreDestino` (`consultarCreditoLV`) con método POST. El servicio se accede a través del Datapower interno de BPO con autenticación por AAA Policy y whitelist de IPs.

> **Nota:** El endpoint de producción para este servicio no está documentado en los archivos actuales. Debe solicitarse al equipo de BPO.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe `tipoDocumento`, `numeroDocumento` y `numeroObligacion` del orquestador.
- **CA-02:** El adaptador invoca `POST /WSLineaVerde/consultarCreditoLV` con los datos de la obligación.
- **CA-03:** El adaptador transforma la respuesta de BPO al modelo normalizado de cartera del canal Oficinas.
- **CA-04:** Si BPO retorna error de obligación no encontrada, el adaptador mapea al código estándar `404`.
- **CA-05:** Si BPO retorna error de conectividad o certificado, el adaptador mapea al código estándar y registra en Elastic.
- **CA-06:** El adaptador gestiona los certificados TLS según el ambiente (QA vs PRD).
- **CA-07:** El adaptador no realiza lógica de negocio — solo invoca, transforma y retorna.

---

## Inputs

### Recibidos del Orquestador

```json
{
  "tipoDocumento": "CC",
  "numeroDocumento": "12345678",
  "numeroObligacion": "987654321"
}
```

| Campo              | Tipo   | Descripción                              | Obligatorio |
|--------------------|--------|------------------------------------------|-------------|
| `tipoDocumento`    | String | Tipo de documento del cliente            | SI          |
| `numeroDocumento`  | String | Número de documento del cliente          | SI          |
| `numeroObligacion` | String | Número de la obligación a consultar      | SI          |

---

## Servicio de BPO Invocado

| Tipo | Código  | Servicio / Operación                          | Endpoint QA                                          | Endpoint PROD      |
|------|---------|-----------------------------------------------|------------------------------------------------------|--------------------|
| REST | CPLID   | `CPLIDConsultaProductoLibreDestino` / `consultarCreditoLV` | `https://10.213.133.10:55460/WSLineaVerde/consultarCreditoLV` | No documentado     |

**Método:** `POST`  
**Certificado QA:** `datapower.servint.pruebas`  
**Certificado PRD:** `prd.dp.int.ssl.sofia.bpop`  
**TLS QA:** 1.0 / 1.1 / 1.2  
**TLS PRD:** 1.2 / 1.3

---

## Outputs

### Modelo normalizado de cartera

| Campo                | Tipo    | Descripción                                          |
|----------------------|---------|------------------------------------------------------|
| `numeroObligacion`   | String  | Número de la obligación                              |
| `tipoCartera`              | String  | Tipo de cartera — mapeado desde `LineaCredito`                   |
| `estado`                   | String  | Estado — mapeado desde `sestadocredito`                          |
| `oficina`                  | String  | Código de oficina — mapeado desde `CodOfiObligacion`             |
| `fechaDesembolso`          | Date    | Mapeado desde `FechaDesembolsoCredito`                           |
| `fechaVencimiento`         | Date    | Mapeado desde `FechaVencimientoCredito`                          |
| `plazoMeses`               | Integer | Mapeado desde `PlazoCredito`                                     |
| `valorCuota`               | Decimal | Mapeado desde `ValorProximaCuota`                                |
| `saldoCapital`             | Decimal | Mapeado desde `SaldoCapital`                                     |
| `saldoInteresesCorrientes` | Decimal | Mapeado desde `SaldoIntereses`                                   |
| `saldoInteresesMora`       | Decimal | Mapeado desde `TasaMoraEA` / intereses de cuotas vencidas        |
| `saldoMora`                | Decimal | Mapeado desde `ValorTotalCuotasVencidas`                         |
| `diasMora`                 | Integer | Mapeado desde `AlturaMora`                                       |
| `tasaEA`                   | Decimal | Mapeado desde `TasaInteresCorrienteEA`                           |
| `proximaFechaPago`         | Date    | Mapeado desde `FechaProximoPago`                                 |
| `valorProximoPago`         | Decimal | Mapeado desde `ValorProximaCuota`                                |

> **Nota:** Los campos BPO usan PascalCase. La tabla de mapeo anterior es orientativa — confirmar con el equipo BPO el significado exacto de cada campo antes de codificar el mapeo definitivo.

### Mapeo de errores BPO → estructura estándar

| Error BPO                          | Código HTTP | StatusDesc                              |
|------------------------------------|-------------|----------------------------------------|
| Obligación no encontrada           | `404`        | "Obligación no encontrada en BPO"      |
| Error de certificado TLS           | `502`        | "Error de certificado TLS con BPO"     |
| IP no autorizada (whitelist)       | `502`        | "IP no autorizada en Datapower BPO"    |
| Timeout                            | `504`        | "Timeout del servicio BPO"             |
| Error interno BPO                  | `502`        | "Error en el servicio del banco"       |

---

## Reglas de Negocio

1. **RN-01:** Las credenciales, certificados y endpoints de BPO se configuran por variable de ambiente — nunca hardcodeados.
2. **RN-02:** El certificado TLS usado debe corresponder al ambiente activo (QA o PRD).
3. **RN-03:** La IP desde la que se hacen las llamadas debe estar en la whitelist de BPO — coordinar con infraestructura.
4. **RN-04:** El adaptador no filtra ni modifica datos de negocio — solo mapea al modelo normalizado.

---

## Caminos Alternativos y Excepciones

| ID      | Condición                                               | Comportamiento esperado                           |
|---------|---------------------------------------------------------|---------------------------------------------------|
| ALT-01  | Obligación no encontrada en BPO                        | Retorna `404` al orquestador                      |
| EXC-01  | Timeout en llamada REST a BPO                          | Retorna `504` al orquestador                      |
| EXC-02  | Error de certificado TLS                               | Retorna `502` y alerta en Elastic                 |
| EXC-03  | IP del pod AKS no está en la whitelist de BPO          | Retorna `502` con mensaje de IP no autorizada     |

---

## Tecnología a Usar

| Componente   | Tecnología   | Versión | Nota                                                   |
|--------------|--------------|---------|--------------------------------------------------------|
| Lenguaje     | Java         | 21      |                                                        |
| Framework    | Spring Boot  | 3.2.6   |                                                        |
| Cliente REST | WebClient    | —       | Para `consultarCreditoLV` (POST)                       |
| TLS          | Keystore JKS | —       | Certificados por ambiente gestionados por Infra        |
| Logs         | Elastic      | —       |                                                        |

---

## Dependencias

| HU / Componente | Relación | Descripción                              |
|-----------------|----------|------------------------------------------|
| HU-102-ORQ      | Padre    | Orquestador que invoca este adaptador    |

### Servicios externos (BPO)

| Servicio                              | Código | Tipo | Endpoint QA                                          | Endpoint PRD       |
|---------------------------------------|--------|------|------------------------------------------------------|--------------------|
| `CPLIDConsultaProductoLibreDestino`   | CPLID  | REST | `https://10.213.133.10:55460/WSLineaVerde/consultarCreditoLV` | No documentado |

---

## Seguridad

- **Autenticación BPO:** AAA Policy del Datapower — gestionada por certificado TLS de cliente.
- **Whitelist IP:** Los pods AKS deben tener IP fija de salida o NAT. Coordinar con infraestructura.
- **Certificados:** Cargados en el Keystore del servicio según ambiente.

---

## Preguntas Abiertas

| # | Pregunta                                                                                  | Impacto                                   |
|---|-------------------------------------------------------------------------------------------|-------------------------------------------|
| 1 | ¿Cuál es el endpoint de producción para `consultarCreditoLV`?                            | Bloquea despliegue a PRD                  |
| 2 | ¿`consultarCreditoLV` retorna el nivel de detalle completo (cuotas, tasa, mora)?         | Define si se completa el modelo normalizado |
| 3 | ¿Los pods AKS tienen IP fija de salida o se debe configurar NAT para la whitelist?       | Bloquea conectividad en todos los ambientes |
| 4 | ¿El servicio `CPLID` cubre todos los tipos de cartera o solo libre destino?               | Define si se necesitan servicios adicionales |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador BPO — Consulta Detallada de Cartera
  Como adaptador de Banco Popular
  Quiero invocar consultarCreditoLV para obtener el detalle de la obligación
  Para retornar la información normalizada al orquestador

  Background:
    Given el adaptador BPO está configurado con credenciales y certificados válidos
    And la IP del servicio está en la whitelist de BPO
    And hay conectividad con el Datapower de BPO

  Scenario: Consulta exitosa de cartera
    Given el adaptador recibe tipoDocumento "CC", numeroDocumento "12345678" y numeroObligacion "987654321"
    When invoca POST consultarCreditoLV en BPO
    Then obtiene el detalle de la obligación
    And retorna la respuesta normalizada al orquestador con StatusCode 200

  Scenario: Obligación no encontrada
    Given el adaptador recibe un numeroObligacion que no existe en BPO
    When invoca consultarCreditoLV
    Then BPO retorna error de no encontrado
    And el adaptador retorna 404 al orquestador

  Scenario: IP del servicio no está en whitelist de BPO
    Given la IP del pod AKS no está registrada en el Datapower de BPO
    When el adaptador intenta invocar el servicio
    Then recibe un error de conexión rechazada
    And retorna 502 al orquestador con mensaje "IP no autorizada en Datapower BPO"

  Scenario: Timeout del servicio
    Given el servicio de BPO no responde en el tiempo configurado
    When el adaptador espera la respuesta
    Then retorna 504 al orquestador
    And registra el evento en Elastic
```

---

## Notas Técnicas

- El endpoint de `consultarCreditoLV` usa IP pública en QA (`10.213.133.10`). Verificar resolución de hostname DNS en los pods AKS para el ambiente de PRD una vez documentado.
- El mismo Keystore JKS configurado en HU-101-ADP-BPO puede reutilizarse para este adaptador.
- Coordinar con BPO si el servicio `CPLID` cubre carteras hipotecarias y de vehículo, o si se necesita un servicio diferente para cada tipo.

---

## Definition of Ready

- [ ] Endpoint de producción de `consultarCreditoLV` confirmado con BPO
- [ ] Estructura de request y response de `consultarCreditoLV` documentada
- [ ] IPs de salida de los pods AKS registradas en la whitelist de BPO
- [ ] Certificados TLS por ambiente disponibles en PT
- [ ] Conectividad de red desde pods AKS hacia Datapower BPO confirmada
- [ ] Modelo de respuesta normalizado definido y acordado
- [ ] HU-102-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación de story points asignada
- [ ] Aprobada por líder técnico y product owner

---

## Definition of Done

- [ ] Cliente REST hacia `consultarCreditoLV` implementado (POST)
- [ ] Certificados TLS por ambiente cargados en Keystore
- [ ] IPs de los pods AKS registradas en whitelist de BPO
- [ ] Mapeo de respuesta BPO → modelo normalizado implementado
- [ ] Manejo de errores y timeouts implementado
- [ ] Pruebas unitarias (cobertura ≥ 80%)
- [ ] Prueba de integración contra BPO en PT
- [ ] Aprobado por QA
