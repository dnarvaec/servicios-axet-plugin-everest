# HU-102-ADP-AVV: Adaptador AV Villas — Consulta Detallada de Cartera

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-102-ADP-AVV                                              |
| Épica          | Épica 1 — Consultas P1                                      |
| Componente     | Adaptador AVV — Cartera Detallada                           |
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

| Rol / Audiencia       | Cómo interactúa                                                                                         |
|-----------------------|---------------------------------------------------------------------------------------------------------|
| Desarrollador Backend | Implementa el adaptador: invoca el servicio de AVV para cartera detallada y mapea la respuesta          |
| QA / Tester           | Valida la llamada a AVV, el manejo del protocolo (SOAP o REST) y el mapeo de campos                     |
| Integrador AVV        | Provee confirmación del servicio (`getBalanceByProduct` o `PJBA_CreditoHiptCons_consultarCarteras`) y su endpoint |

---

## Historia de Usuario

**Como** adaptador del canal Oficinas para AV Villas,  
**quiero** recibir del orquestador la solicitud de consulta detallada de cartera,  
**para** invocar el servicio correspondiente de AVV, transformar la respuesta al modelo normalizado y retornarla al orquestador.

---

## Contexto de Negocio

AVV cuenta con dos opciones potenciales para la consulta detallada de cartera:

1. **SOAP:** `WSBA_Multiaplicacion_consultarSaldosIFX` / `getBalanceByProduct` — el mismo servicio de la consulta general, con un código de producto diferente (crédito). Pasa por Datapower → Bus → CTG → z/OS (ICBS).
2. **REST:** `PJBA_CreditoHiptCons_consultarCarteras` — disponible para productos activos e hipotecarios, acceso a producción confirmado.

> **Decisión pendiente:** ¿Se usa el canal SOAP (`getBalanceByProduct`) o el REST (`consultarCarteras`)? Esta decisión define el cliente a implementar. La pregunta clave es si `getBalanceByProduct` retorna el nivel de detalle requerido (cuotas, fechas, mora) o solo el saldo.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe `tipoDocumento`, `numeroDocumento` y `numeroObligacion` del orquestador.
- **CA-02:** El adaptador invoca el servicio de cartera detallada de AVV (SOAP o REST según decisión) para la obligación indicada.
- **CA-03:** El adaptador transforma la respuesta de AVV al modelo normalizado de cartera del canal Oficinas.
- **CA-04:** Si AVV retorna error de obligación no encontrada, el adaptador mapea al código estándar `404`.
- **CA-05:** Si AVV retorna error técnico, el adaptador mapea al código estándar correspondiente y registra en Elastic.
- **CA-06:** El adaptador no realiza lógica de negocio — solo invoca, transforma y retorna.

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

## Servicios de AVV a Invocar

### Opción A — SOAP (Bus interno)

| Tipo | Servicio / Operación | Endpoint QA | Endpoint PROD |
|------|----------------------|-------------|---------------|
| SOAP | `WSBA_Multiaplicacion_consultarSaldosIFX` / `getBalanceByProduct` | No documentado — confirmar con AVV | `https://10.10.21.10:443/PFBA_Multiaplicacion31/sca/WSBA_Multiaplicacion_consultarSaldosIFX` |

> **Nota:** El endpoint `https://10.10.9.200:443/...` corresponde al servicio general SOAP de consulta de productos (HU-101), no a un endpoint de QA confirmado para detalle de cartera. El endpoint QA para esta operación debe confirmarse con AVV.
>
> **Pendiente confirmar:** si `getBalanceByProduct` retorna el nivel de detalle requerido (cuotas, fechas, tasa, mora) para cartera.

### Opción B — REST (Datapower Interno)

| Tipo | Servicio / Operación | Endpoint |
|------|----------------------|----------|
| REST | `PJBA_CreditoHiptCons_consultarCarteras` / `consultarCarteras` | Activo / Hipotecario, Producción — endpoint exacto por confirmar con AVV |

> **Decisión pendiente:** definir con el equipo de AVV cuál opción usar para este canal.

---

## Outputs

### Modelo normalizado de cartera

| Campo                | Tipo    | Descripción                                          |
|----------------------|---------|------------------------------------------------------|
| `numeroObligacion`   | String  | Número de la obligación                              |
| `tipoCartera`              | String  | Tipo de cartera                                      |
| `estado`                   | String  | Estado (AL_DIA, EN_MORA, CANCELADA)                  |
| `oficina`                  | String  | Código de oficina de la obligación                   |
| `fechaDesembolso`          | Date    | Fecha de desembolso                                  |
| `fechaVencimiento`         | Date    | Fecha de vencimiento del crédito                     |
| `plazoMeses`               | Integer | Plazo total en meses                                 |
| `cuotasPagadas`            | Integer | Cuotas pagadas                                       |
| `cuotasPendientes`         | Integer | Cuotas pendientes                                    |
| `valorCuota`               | Decimal | Valor de la cuota                                    |
| `saldoCapital`             | Decimal | Saldo de capital vigente                             |
| `saldoInteresesCorrientes` | Decimal | Saldo de intereses corrientes                        |
| `saldoInteresesMora`       | Decimal | Saldo de intereses de mora                           |
| `saldoMora`                | Decimal | Saldo total en mora                                  |
| `diasMora`                 | Integer | Días de mora                                         |
| `tasaEA`                   | Decimal | Tasa efectiva anual                                  |
| `proximaFechaPago`         | Date    | Fecha del próximo pago                               |
| `valorProximoPago`         | Decimal | Valor del próximo pago                               |

> El modelo exacto está **pendiente de confirmar** con la respuesta real del servicio AVV elegido.

### Mapeo de errores AVV → estructura estándar

| Error AVV                          | Código HTTP | StatusDesc                              |
|------------------------------------|-------------|----------------------------------------|
| Obligación no encontrada           | `404`        | "Obligación no encontrada en AVV"      |
| Error de conectividad (IP privada) | `502`        | "Error de conectividad con AVV"        |
| Timeout                            | `504`        | "Timeout del servicio AVV"             |
| Error interno AVV                  | `502`        | "Error en el servicio del banco"       |

---

## Reglas de Negocio

1. **RN-01:** Las credenciales y endpoints de AVV se configuran por variable de ambiente — nunca hardcodeados.
2. **RN-02:** El adaptador no filtra ni modifica los datos de negocio retornados por AVV — solo los mapea al modelo normalizado.
3. **RN-03:** El adaptador no realiza llamadas adicionales para completar datos faltantes.

---

## Caminos Alternativos y Excepciones

| ID      | Condición                                     | Comportamiento esperado                              |
|---------|-----------------------------------------------|------------------------------------------------------|
| ALT-01  | Obligación no encontrada en AVV               | Retorna `404` al orquestador                         |
| EXC-01  | Timeout en llamada a AVV                      | Retorna `504` al orquestador                         |
| EXC-02  | Error de certificado / TLS con Datapower AVV  | Retorna `502` y registra en Elastic                  |

---

## Tecnología a Usar

| Componente    | Tecnología       | Versión | Nota                                                        |
|---------------|------------------|---------|-------------------------------------------------------------|
| Lenguaje      | Java             | 21      |                                                             |
| Framework     | Spring Boot      | 3.2.6   |                                                             |
| Cliente REST  | WebClient        | —       | Para opción REST (`PJBA_CreditoHiptCons_consultarCarteras`) |
| Cliente SOAP  | JAX-WS / CXF     | —       | Para opción SOAP (`getBalanceByProduct`)                    |
| Logs          | Elastic          | —       |                                                             |

---

## Dependencias

| HU / Componente | Relación | Descripción                              |
|-----------------|----------|------------------------------------------|
| HU-102-ORQ      | Padre    | Orquestador que invoca este adaptador    |

---

## Preguntas Abiertas

| # | Pregunta                                                                                             | Impacto                                       |
|---|------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| 1 | ¿Se usa SOAP (`getBalanceByProduct`) o REST (`consultarCarteras`) para cartera detallada en AVV?     | Define cliente a implementar y nivel de detalle |
| 2 | ¿`getBalanceByProduct` retorna cuotas, fechas de pago, mora y tasa? ¿O solo saldo?                  | Define si es suficiente o se necesita otro servicio |
| 3 | ¿Cuál es el endpoint exacto de `PJBA_CreditoHiptCons_consultarCarteras` en QA y PRD?                | Bloquea implementación si se elige opción REST |
| 4 | ¿Hay conectividad de red entre los ambientes del canal Oficinas y los Datapowers de AVV?             | Bloquea pruebas en PT                         |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador AVV — Consulta Detallada de Cartera
  Como adaptador de AV Villas
  Quiero invocar el servicio de cartera detallada de AVV
  Para retornar la información normalizada al orquestador

  Background:
    Given el adaptador AVV está configurado con credenciales válidas
    And hay conectividad con los servicios de AVV

  Scenario: Consulta exitosa de cartera
    Given el adaptador recibe tipoDocumento "CC", numeroDocumento "12345678" y numeroObligacion "987654321"
    When invoca el servicio de cartera detallada de AVV
    Then obtiene el detalle de la obligación
    And retorna la respuesta normalizada al orquestador con StatusCode 200

  Scenario: Obligación no encontrada
    Given el adaptador recibe un numeroObligacion que no existe en AVV
    When invoca el servicio
    Then AVV retorna error de no encontrado
    And el adaptador retorna 404 al orquestador

  Scenario: Timeout del servicio
    Given el servicio de AVV no responde en el tiempo configurado
    When el adaptador espera la respuesta
    Then retorna 504 al orquestador
    And registra el evento en Elastic
```

---

## Notas Técnicas

- Todos los endpoints de AVV tienen IPs privadas — la conectividad de red es un prerequisito de infraestructura.
- Si se elige la opción SOAP, el mismo cliente `JAX-WS/CXF` ya configurado en HU-101-ADP-AVV puede reutilizarse.
- Si se elige la opción REST, el endpoint `PJBA_CreditoHiptCons_consultarCarteras` cubre créditos activos e hipotecarios; verificar si cubre libre destino también.

---

## Definition of Ready

- [ ] Decisión tomada sobre canal (SOAP `getBalanceByProduct` vs REST `consultarCarteras`)
- [ ] Endpoint del servicio elegido confirmado en QA y PRD
- [ ] Credenciales disponibles en PT
- [ ] Conectividad de red desde pods AKS hacia Datapower AVV confirmada
- [ ] Modelo de respuesta normalizado definido y acordado
- [ ] HU-102-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación de story points asignada
- [ ] Aprobada por líder técnico y product owner

---

## Definition of Done

- [ ] Decisión SOAP vs REST documentada y aprobada
- [ ] Cliente HTTP/SOAP implementado para el servicio elegido
- [ ] Mapeo de respuesta AVV → modelo normalizado implementado
- [ ] Manejo de errores y timeouts implementado
- [ ] Pruebas unitarias (cobertura ≥ 80%)
- [ ] Prueba de integración contra AVV en PT
- [ ] Aprobado por QA
