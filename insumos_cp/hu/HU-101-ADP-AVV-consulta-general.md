# HU-101-ADP-AVV: Adaptador AV Villas — Consulta General de Cliente y Productos

## Metadatos

| Campo          | Valor                                                  |
|----------------|--------------------------------------------------------|
| ID             | HU-101-ADP-AVV                                         |
| Épica          | Épica 1 — Consultas P1                                 |
| Componente     | Adaptador AVV — Consulta General                       |
| Sprint         | Por definir                                            |
| Prioridad      | Alta (P1)                                              |
| Estimación     | Por estimar                                            |
| Estado         | Pendiente                                              |
| HU Padre       | HU-101 (Orquestador)                                   |
| Autor          | Por definir                                            |
| Fecha          | 2026-08-19                                             |

---

## Audiencias

| Rol / Audiencia       | Cómo interactúa                                                                                        |
|-----------------------|--------------------------------------------------------------------------------------------------------|
| Desarrollador Backend | Implementa el adaptador: realiza 2 llamadas a AVV (productos y cliente), consolida y mapea la respuesta |
| QA / Tester           | Valida las dos llamadas a AVV, la consolidación y el mapeo de campos                                   |
| Integrador AVV        | Provee acceso y soporte técnico a los endpoints de AVV (SOAP/REST vía Datapower)                       |

---

## Historia de Usuario

**Como** adaptador del canal Oficinas para AV Villas,  
**quiero** recibir una solicitud de consulta general del orquestador,  
**para** invocar los servicios de AVV de consulta de productos y de datos del cliente, consolidar ambas respuestas y retornar el resultado normalizado.

---

## Contexto de Negocio

AVV expone los servicios de consulta de productos y consulta de datos del cliente en dos servicios separados. El adaptador debe orquestar **dos llamadas distintas**: una a `PJBA_Multiaplicacion_consultarProductosCliente` (o `WSBA_Multiaplicacion_consultarSaldosIFX`) para productos, y otra a `PJBA_Crm_consultarDatosCliente` para los datos del cliente. Ambas pasan por el Datapower interno de AVV.

> **Nota:** Todos los endpoints de AVV tienen IPs privadas — el acceso requiere conectividad de red con el ambiente de AVV (VPN o interconexión de red entre ambientes).

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe el payload de `obj_operacion` proveniente del orquestador.
- **CA-02:** El adaptador invoca el servicio de consulta de productos de AVV para obtener el resumen de cuentas, CDT, carteras y TC.
- **CA-03:** El adaptador invoca el servicio de datos del cliente de AVV (`PJBA_Crm_consultarDatosCliente`) para obtener nombre, documento y segmento.
- **CA-04:** El adaptador consolida la respuesta de ambos servicios en un único objeto normalizado.
- **CA-05:** El adaptador transforma la respuesta consolidada al modelo de datos del canal Oficinas.
- **CA-06:** Si cualquiera de los dos servicios de AVV retorna error, el adaptador mapea el error a la estructura estándar y lo propaga al orquestador.
- **CA-07:** El adaptador no realiza lógica de negocio adicional — solo invoca, consolida y transforma.

---

## Inputs

### Recibidos del Orquestador

El adaptador recibe el contenido de `obj_operacion`. Estructura mínima esperada:

```json
{
  "tipoDocumento": "CC",
  "numeroDocumento": "12345678"
}
```

| Campo              | Tipo   | Descripción                        | Obligatorio | Ejemplo    |
|--------------------|--------|------------------------------------|-------------|------------|
| `tipoDocumento`    | String | Tipo de documento del cliente      | SI          | `CC`, `CE`, `NIT` |
| `numeroDocumento`  | String | Número de documento del cliente    | SI          | `12345678` |

> **Nota:** La estructura exacta de `obj_operacion` está **pendiente de definición** con el equipo.

---

## Servicios de AVV Invocados

### Llamada 1 — Consulta de Productos

| Tipo | Servicio / Operación | Endpoint DEV | Endpoint QA | Endpoint PROD |
|------|----------------------|--------------|-------------|---------------|
| SOAP | `WSBA_Multiaplicacion_consultarSaldosIFX` / `getBalanceGroupedByProduct` | `https://10.10.10.201:443/PFBA_Multiaplicacion31/sca/WSBA_Multiaplicacion_consultarSaldosIFX` | `https://10.10.9.200:443/PFBA_Multiaplicacion31/sca/WSBA_Multiaplicacion_consultarSaldosIFX` | `https://10.10.21.10:443/PFBA_Multiaplicacion31/sca/WSBA_Multiaplicacion_consultarSaldosIFX` |
| REST | `PJBA_Multiaplicacion_consultarProductosCliente` / `consultar` | No documentado | No documentado | No documentado |

> **Decisión pendiente:** ¿Se usa el canal SOAP o REST para productos? Los endpoints REST de AVV no están documentados en los archivos actuales.

### Llamada 2 — Consulta de Datos del Cliente

| Tipo | Servicio / Operación | Alcance | Endpoint |
|------|----------------------|---------|----------|
| REST | `PJBA_Crm_consultarDatosCliente` / `consultarDatosCliente` | Todos los canales, Producción | No documentado (Datapower Interno) |

---

## Outputs

### Datos a consolidar para la respuesta normalizada

**De la Llamada 1 (productos):**

| Producto    | Campos a mapear                                                    |
|-------------|---------------------------------------------------------------------|
| Cuentas     | Tipo de cuenta, número, saldo, sobregiro (corriente)               |
| CDT         | Número de producto                                                  |
| Carteras    | Tipo de cartera, número de obligación, saldo a pagar               |
| TC          | Número enmascarado, estado, franquicia, cupo disponible            |

**De la Llamada 2 (cliente):**
- Nombre completo
- Tipo y número de documento
- Segmento

### Mapeo de errores AVV → estructura estándar

| Error AVV                        | Código HTTP a retornar | StatusDesc                             |
|----------------------------------|------------------------|----------------------------------------|
| Cliente no encontrado            | `206`                  | "Cliente no encontrado en AVV"         |
| Sin productos                    | `206`                  | "El cliente no tiene productos en AVV" |
| Error de conectividad (IP privada) | `502`                | "Error de conectividad con AVV"        |
| Timeout                          | `504`                  | "Timeout del servicio AVV"             |
| Error interno del servicio AVV   | `502`                  | "Error en el servicio del banco"       |

---

## Reglas de Negocio

1. **RN-01:** Las credenciales y endpoints de AVV se configuran por variable de ambiente — nunca hardcodeadas.
2. **RN-02:** Si ambas llamadas fallan, el adaptador retorna error total al orquestador.
3. **RN-03:** El adaptador consolida las dos respuestas antes de retornar al orquestador — nunca retorna dos respuestas separadas.
4. **RN-04:** Los números de tarjeta de crédito se retornan **enmascarados** en la respuesta normalizada.
5. **RN-05:** Ante una respuesta parcial (cuando un bloque llega con error pero el otro es exitoso), el adaptador retorna la información disponible con el indicador de bloque faltante — no retorna error total.

---

## Caminos Alternativos y Excepciones

| ID      | Condición                                                    | Comportamiento esperado                                     |
|---------|--------------------------------------------------------------|-------------------------------------------------------------|
| ALT-01  | Llamada 1 (productos) exitosa pero Llamada 2 (cliente) falla | Retorna respuesta parcial con `bloquesFaltantes` indicando el bloque de cliente — **no retorna error total** |
| ALT-02  | Cliente sin productos en AVV                                 | Retorna código de negocio de AVV                            |
| ALT-03  | Respuesta parcial — un bloque falla pero el otro tiene datos | Retorna lo obtenido con un campo `bloquesFaltantes` indicando qué no pudo consultarse — **no retorna error total** |
| EXC-01  | Timeout en cualquiera de las dos llamadas                    | Retorna `504` al orquestador                                |
| EXC-02  | Error de certificado / TLS con Datapower AVV                 | Retorna `502` y registra en Elastic                         |

---

## Tecnología a Usar

| Componente    | Tecnología         | Versión | Nota                                        |
|---------------|--------------------|---------|---------------------------------------------|
| Lenguaje      | Java               | 21      |                                             |
| Framework     | Spring Boot        | 3.2.6   |                                             |
| Cliente REST  | WebClient          | —       | Para `PJBA_Crm_consultarDatosCliente`       |
| Cliente SOAP  | JAX-WS / CXF       | —       | Para `WSBA_Multiaplicacion_consultarSaldosIFX` |
| Logs          | Elastic            | —       |                                             |

---

## Dependencias

### HUs relacionadas

| HU      | Relación | Descripción                          |
|---------|----------|--------------------------------------|
| HU-101  | Padre    | Orquestador que invoca este adaptador |

### Servicios externos (AVV)

| Servicio                                   | Tipo | URL QA                                | URL PRD                               |
|--------------------------------------------|------|---------------------------------------|---------------------------------------|
| `WSBA_Multiaplicacion_consultarSaldosIFX`  | SOAP | `https://10.10.9.200:443/.../WSBA...` | `https://10.10.21.10:443/.../WSBA...` |
| `PJBA_Multiaplicacion_consultarProductos`  | REST | Por documentar                        | Por documentar                        |
| `PJBA_Crm_consultarDatosCliente`           | REST | Por documentar                        | Por documentar                        |

---

## Preguntas Abiertas

| # | Pregunta                                                                                | Impacto                               |
|---|-----------------------------------------------------------------------------------------|---------------------------------------|
| 1 | ¿Se usa SOAP o REST para la consulta de productos en AVV?                               | Define cliente HTTP a implementar     |
| 2 | ¿Cuáles son los endpoints REST de AVV en QA y PRD?                                     | Bloquea implementación y pruebas      |
| 3 | ¿Hay conectividad de red entre los ambientes del canal Oficinas y los Datapowers de AVV? | Bloquea pruebas en PT                |
| 4 | ¿`getBalanceGroupedByProduct` devuelve las TC o solo productos pasivos/activos?         | Afecta si se necesita llamada extra para TC |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador AVV — Consulta General Cliente y Productos
  Como adaptador de AV Villas
  Quiero invocar los servicios de AVV para obtener cliente y productos
  Para retornar la información consolidada al orquestador

  Background:
    Given el adaptador AVV está configurado con credenciales válidas
    And hay conectividad con los servicios de AVV

  Scenario: Consulta exitosa — ambas llamadas exitosas
    Given el adaptador recibe tipoDocumento "CC" y numeroDocumento "12345678"
    When invoca el servicio de productos de AVV (Llamada 1)
    And invoca el servicio de datos del cliente de AVV (Llamada 2)
    Then consolida los datos del cliente y los productos
    And retorna la respuesta al orquestador con StatusCode 200

  Scenario: Fallo en la llamada de productos (Llamada 1)
    Given el servicio de productos de AVV no está disponible
    When el adaptador intenta invocar la Llamada 1
    Then retorna error al orquestador sin intentar la Llamada 2

  Scenario: Fallo en la llamada de cliente (Llamada 2)
    Given la Llamada 1 es exitosa
    And el servicio de datos del cliente de AVV retorna error
    When el adaptador intenta invocar la Llamada 2
    Then retorna error al orquestador

  Scenario: Timeout en servicio AVV
    Given cualquiera de los servicios de AVV no responde a tiempo
    When el adaptador espera la respuesta
    Then retorna 504 al orquestador
    And registra el evento en Elastic
```

---

## Notas Técnicas

- Todos los endpoints de AVV tienen IPs privadas — se requiere gestionar la conectividad de red como prerequisito de infraestructura.
- AVV usa Datapower como gateway; los certificados y la whitelist IP deben coordinarse con el equipo de integración de AVV.
- Si el SOAP `getBalanceGroupedByProduct` no incluye TC, podría necesitarse una tercera llamada para obtenerlas — confirmar con AVV.

---

## Definition of Ready

> La HU puede entrar a sprint solo cuando **todos** los ítems están cumplidos.

- [ ] Canal de comunicación definido (SOAP vs REST) para consulta de productos de AVV
- [ ] Endpoints de los servicios de AVV documentados y confirmados (productos y cliente)
- [ ] Conectividad de red desde pods AKS hacia Datapower AVV confirmada en PT
- [ ] Credenciales de AVV disponibles en el ambiente PT
- [ ] Confirmado si `getBalanceGroupedByProduct` incluye TC o requiere llamada adicional
- [ ] Estructura de `obj_operacion` definida y acordada
- [ ] Modelo de respuesta normalizada definido y acordado con el orquestador
- [ ] HU-101 (Orquestador) en estado "En desarrollo" o "Completada"
- [ ] Estimación de story points asignada por el equipo
- [ ] Aprobada por líder técnico y product owner

---

## Definition of Done

- [ ] Estrategia de integración (SOAP o REST) definida y aprobada
- [ ] Conectividad de red con AVV confirmada en PT
- [ ] Implementación de las dos llamadas a AVV
- [ ] Consolidación de respuestas
- [ ] Mapeo al modelo normalizado
- [ ] Pruebas unitarias (cobertura ≥ 80%)
- [ ] Prueba de integración contra AVV en PT
- [ ] Aprobado por QA
