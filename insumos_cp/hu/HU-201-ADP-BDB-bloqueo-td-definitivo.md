# HU-201-ADP-BDB: Adaptador Banco de Bogotá — Bloqueo TD Definitivo

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-201-ADP-BDB                                              |
| ID Servicio    | SFA-009                                                     |
| Épica          | Épica 2 — Mantenimiento Tarjeta Débito (P2)                 |
| Componente     | Adaptador BdB — Bloqueo TD Definitivo                       |
| Microservicio  | `ofic-actualizaciones-adp-bbog`                             |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P2)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | **Desarrollada**                                            |
| HU Padre       | HU-201-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-21                                                  |
| Última revisión | 2026-09-03 — campo operacion agregado; identificación de servicio por operacion+banco documentada; masking solo en logs; gestión de headers documentada; cola SQS FIFO de auditoría documentada; OperacionEnum definido localmente en cada microservicio con valores canónicos de HU-101-ORQ; operación no soportada: excepción + 400 documentada |

---

## Historia de Usuario

**Como** microservicio `ofic-actualizaciones-adp-bbog`,  
**quiero** recibir del orquestador (`ofic-actualizaciones-orq`) la solicitud de bloqueo definitivo de tarjeta débito de Banco de Bogotá,  
**para** invocar el API REST `customer_debit_card_management` de BdB y retornar el resultado normalizado.

---

## Contexto de Negocio

BdB expone dos servicios para gestión de estado de TD: SOAP (`AccountDebitCardStatusModify` vía AWS VPC Endpoint — no accesible externamente) y REST (`customer_debit_card_management` vía API Gateway AWS ECS — accesible externamente con `x-api-key`). **Se usará la API REST**, que es la que está expuesta y autenticada para canales digitales.

Para bloqueo definitivo, el campo clave es `debitCardStatus: "C"` (Bloqueo Definitivo). El campo `debitCardStatus: "R"` también aplica para Robo/extravío según la documentación, pero se unifica al status `"C"` para bloqueo definitivo desde el canal Oficinas.

> **Nota:** El SOAP `AccountDebitCardStatusModify` existe pero está en AWS VPC Endpoint, accesible solo dentro de la VPC de BdB. Queda documentado como opción de contingencia, pero la integración principal es REST.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/bog/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente, los cuales varían según banco y operación (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** El adaptador recibe el contenido de `obj_operacion` proveniente del ORQ e invoca `PUT /V1/product/debitcard/status-lock` de BdB.
- **CA-03:** Invoca `PUT /V1/product/debitcard/status-lock` con `debitCardStatus: "C"` hacia la API REST de BdB.
- **CA-04:** Incluye todos los headers requeridos por BdB (ver tabla de headers).
- **CA-05:** Mapea la causal del canal Oficinas (`BL01`, `BL02`, `BL03`) al `debitCardStatus` de BdB según las Reglas de Integración.
- **CA-06:** Si BdB retorna código de error por tarjeta ya bloqueada, mapea a `409`.
- **CA-07:** Si BdB retorna 408 (timeout), mapea a `504`.
- **CA-08:** Si BdB retorna error de negocio, mapea a `422`.
- **CA-09:** Transforma la respuesta al modelo normalizado de la HU ORQ.
- **CA-10:** Circuit Breaker activo en el consumo del servicio BdB.
- **CA-11:** Registra en Elastic ante error de conectividad o código de error del banco.
- **CA-12:** Credenciales (`x-api-key`) en variables de ambiente — nunca hardcodeadas.
- **CA-13:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-14:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

---

## Inputs

### Recibidos del Orquestador

El ADP recibe del orquestador: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`.

```json
{
  "operacion": "BLOQUEO_TD_DEFINITIVO",
  "obj_operacion": {
    "tipoDocumento": "CC",
    "numeroDocumento": "12345678",
    "numeroTarjeta": "************1234",
    "causal": "BL01"
  }
}
```

| Campo | Tipo | Descripción | Obligatorio |
|---|---|---|---|
| `operacion` | `OperacionEnum` | Identificador de la operación. Junto con `X-Destination-Bank` determina el servicio bancario a invocar. Recibido como `OperacionEnum` desde el ORQ — no re-parsear el String. Ver definición completa en **HU-101-ORQ** | SI |
| `X-Origin-Bank` | String (header) | Banco de origen | SI |
| `X-Destination-Bank` | String (header) | Banco destino | SI |
| `obj_operacion` | Object | Campos funcionales | SI |

> **Nota:** Los campos de `obj_operacion` son referenciales. El ADP recibe `obj_operacion` como tipo genérico (`Object`) — no valida sus campos internos ni lo implementa como clase Java campo a campo. La validación es responsabilidad del servicio bancario.

---

## Servicio de BdB a Invocar

### REST (Principal)

| Campo       | Valor |
|-------------|-------|
| Tipo        | REST  |
| API         | `customer_debit_card_management` |
| Método      | `PUT` |
| Path        | `/V1/product/debitcard/status-lock` |

| Ambiente | URL base | Endpoint completo |
|----------|----------|-------------------|
| QA       | `https://alb-0.labdigitalbdbtvsqa.com:10929` | `.../customer_debit_card_management/V1/product/debitcard/status-lock` |
| PRD      | `https://alb-0.labdigitalbdbtvs.com:10929`   | `.../customer_debit_card_management/V1/product/debitcard/status-lock` |

#### Headers requeridos por BdB

| Header             | Descripción                                          | Obligatorio |
|--------------------|------------------------------------------------------|-------------|
| `x-api-key`        | API key de autenticación (en variable de ambiente)   | SI          |
| `X-RqUID`          | UUID único de la petición                            | SI          |
| `X-Channel`        | Canal que realiza la transacción                     | SI          |
| `X-IPAddr`         | IP del dispositivo de origen                         | SI          |
| `X-Name`           | Nombre del canal / sistema consumidor                | SI          |
| `X-CustIdentNum`   | Número de documento del cliente                      | SI          |
| `X-CustIdentType`  | Tipo de documento del cliente                        | SI          |
| `X-NetworkOwner`   | Propietario de la red / canal                        | SI          |
| `X-TerminalId`     | ID del terminal de atención                          | SI          |

#### Request body REST BdB

```json
{
  "debitCardStatus": "C",
  "cardNumber": "4915110202429901"
}
```

| Campo            | Valor para bloqueo definitivo | Descripción                            |
|------------------|-------------------------------|----------------------------------------|
| `debitCardStatus`| `"C"` (Bloqueo Definitivo)    | Estado destino de la tarjeta           |
| `cardNumber`     | Número completo (interno)     | Número de tarjeta — requiere número real, no enmascarado |

> **Pendiente:** Confirmar con BdB si el endpoint recibe el número enmascarado como token o el número completo de tarjeta. Este punto condiciona la forma en que el orquestador y el adaptador manejan `numeroTarjeta`.

### SOAP (Contingencia — no expuesto externamente)

| Campo    | Valor |
|----------|-------|
| Tipo     | SOAP  |
| Servicio | `AccountDebitCardStatusModify` |
| Operación| `modDebitCardStatus` |
| URL      | `http://vpce-096b03cc10b6c6fc8-4hb9vqom.vpce-svc-0ccf78a08235e209d.us-east-1.vpce.amazonaws.com:3590/accounts/AccountDebitCardStatusModify` |
| StatusCode para bloqueo definitivo | `C` (con `LockId: C`) |

> El SOAP solo es accesible dentro de la VPC de BdB. No disponible para pods AKS externos. Se documenta como referencia para contingencia.

---

## Outputs

### Modelo normalizado

> **Nota:** El ADP retorna la respuesta del banco directamente — no hay transformación a un modelo normalizado propio. Los campos listados son referenciales según el contrato del banco.

| Campo             | Tipo   | Descripción                           |
|-------------------|--------|---------------------------------------|
| `numeroTarjeta`   | String | Número enmascarado                    |
| `estadoAnterior`  | String | Estado de la tarjeta antes del bloqueo|
| `estadoActual`    | String | `BLOQUEADA`                           |
| `causal`          | String | Causal del bloqueo (BL01/BL02/BL03)   |
| `fechaBloqueo`    | String | Timestamp de la operación             |

### Mapeo de errores BdB → estándar

| Error BdB                      | Código HTTP | StatusDesc                            |
|--------------------------------|-------------|---------------------------------------|
| Tarjeta no encontrada          | `404`        | "Tarjeta no encontrada en BdB"        |
| Tarjeta ya bloqueada           | `409`        | "Tarjeta ya bloqueada"                |
| Timeout (408)                  | `504`        | "Timeout del servicio BdB"            |
| Business Error (409 BdB)       | `422`        | "Error de negocio BdB"                |
| Error de conectividad          | `502`        | "Error de conectividad con BdB"       |

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `BLOQUEO_TD_DEFINITIVO` | `BBOG` | `customer_debit_card_management PUT /V1/product/debitcard/status-lock` (`debitCardStatus=C`) — REST expuesto |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo            | Valor fijo            | Descripción                                                             |
|------------------|-----------------------|-------------------------------------------------------------------------|
| `debitCardStatus`| `"C"`                 | Estado para bloqueo definitivo (constante para todas las causales)      |
| `X-Channel`      | PENDIENTE POR DEFINIR | Valor fijo del canal Oficinas — confirmar con BdB                       |
| `X-Name`         | PENDIENTE POR DEFINIR | Nombre del sistema consumidor — confirmar con BdB                       |
| `X-NetworkOwner` | PENDIENTE POR DEFINIR | Propietario de la red — confirmar con BdB                               |

### Mapeo de campos

| Campo obj_operacion       | Campo BdB              | Notas                                                                        |
|---------------------------|------------------------|------------------------------------------------------------------------------|
| `numeroDocumento`         | `X-CustIdentNum`       | Número de documento del cliente (header)                                     |
| `tipoDocumento`           | `X-CustIdentType`      | Tipo de documento del cliente (header)                                       |
| `numeroTarjeta`           | `cardNumber`           | PENDIENTE CONFIRMAR: ¿número enmascarado o completo?                         |
| `causal` BL01/BL02/BL03   | `debitCardStatus: "C"` | Todas las causales mapean a `"C"` — PENDIENTE CONFIRMAR si BL01 (Robo) usa `"R"` |

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** `X-RqUID` debe ser un UUID único generado por el adaptador en cada llamada.
- **RO-03:** Credenciales (`x-api-key`) en variables de ambiente — nunca hardcodeadas.
- **RO-04:** El número de tarjeta retornado en la respuesta debe estar enmascarado.
- **RO-05:** Los números de tarjeta circulan completos en el flujo funcional (entre ORQ, ADP y servicio bancario). El enmascaramiento se aplica **únicamente en logs** (Elastic): últimos 4 dígitos visibles (ejemplo: `****5678`). Nunca ofuscar el número real en el payload funcional.
- **RO-06:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`). Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU.
- **RO-07:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.

---

## Caminos Alternativos

| ID      | Condición                              | Comportamiento                           |
|---------|----------------------------------------|------------------------------------------|
| ALT-00  | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. Verificación defensiva: el ORQ no debería enrutar operaciones no soportadas a este ADP. |
| ALT-01  | Tarjeta no encontrada                  | Retorna `404` al orquestador             |
| ALT-02  | Tarjeta ya bloqueada                   | Retorna `409` al orquestador             |
| EXC-01  | Timeout (408 de BdB)                   | Retorna `504` al orquestador             |
| EXC-02  | Error de negocio BdB                   | Retorna `422` y registra en Elastic      |
| EXC-03  | Error TLS / conectividad               | Retorna `502` y registra en Elastic      |

---

## Tecnología a Usar

| Componente     | Tecnología   | Versión | Nota                     |
|----------------|--------------|---------|--------------------------|
| Lenguaje       | Java         | 21      |                          |
| Framework      | Spring Boot  | 3.5.13   |                          |
| Cliente REST   | Retrofit 2.11.0 + OkHttp 4.12.0    |  2.11.0 / 4.12.0       | Para REST BdB (PUT)      |
| Cliente SOAP   | Spring-WS 3.x + JAXB 4.0.2 | 3.x / 4.0.2       | Contingencia SOAP        |
| Circuit Breaker| Resilience4j | —       | Activo en todos los consumos externos |
| Logs           | Elastic      | —       |                          |
| Mensajería     | AWS SQS FIFO | —       | Cola de auditoría y observabilidad — `avc-everest-pt-logs.fifo` |


---

## Dependencias

| HU         | Relación |
|------------|----------|
| HU-201-ORQ | Padre — `ofic-actualizaciones-orq` |

---

## Preguntas Abiertas

| # | Pregunta                                                                                      | Impacto                                            |
|---|-----------------------------------------------------------------------------------------------|----------------------------------------------------|
| 1 | ¿El endpoint REST recibe el número enmascarado como token de búsqueda o el número completo?  | Define el manejo de `numeroTarjeta` en el adaptador|
| 2 | ¿La `x-api-key` del canal Oficinas ya está provisionada por BdB?                             | Bloquea integración hasta obtenerla                |
| 3 | ¿Hay conectividad confirmada desde pods AKS hacia `alb-0.labdigitalbdbtvs.com:10929`?         | Bloquea pruebas en PT                              |
| 4 | ¿El campo `debitCardStatus: "C"` aplica para todas las causales (BL01/BL02/BL03) o se usa `"R"` para Robo? | Define el mapeo causal → status     |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador BdB — Bloqueo TD Definitivo
  Background:
    Given el adaptador BdB está configurado con API key válida
    And hay conectividad con el API Gateway de BdB

  Scenario: Bloqueo exitoso
    Given el adaptador recibe tipoDocumento "CC", numeroDocumento "12345678" y causal "BL01"
    When invoca PUT /V1/product/debitcard/status-lock con debitCardStatus "C"
    Then BdB retorna confirmación del bloqueo
    And el adaptador retorna la respuesta normalizada con estadoActual "BLOQUEADA"

  Scenario: Tarjeta no encontrada
    Given el adaptador recibe un numeroTarjeta que no existe en BdB
    When invoca el servicio REST
    Then BdB retorna error de tarjeta no encontrada
    And el adaptador retorna 404 al orquestador

  Scenario: Tarjeta ya bloqueada
    Given la tarjeta ya tiene un bloqueo activo en BdB
    When invoca el servicio REST
    Then BdB retorna error de tarjeta bloqueada
    And el adaptador retorna 409 al orquestador

  Scenario: Timeout
    Given el servicio BdB no responde en el tiempo configurado
    When el adaptador espera la respuesta
    Then retorna 504 al orquestador
    And registra el evento en Elastic
```

---

## Gestión de Headers

### Nivel 1 — Headers recibidos del ORQ

El ADP recibe del ORQ los siguientes headers de contexto, propagados sin modificación:

| Header | Descripción |
|--------|-------------|
| `Authorization` | Bearer JWT del asesor |
| `X-Trace-Id` | ID de traza para correlación de logs |
| `X-Origin-Bank` | Banco de origen de la operación |
| `X-Destination-Bank` | Confirma que el banco destino es `BBOG` |

### Nivel 2 — Selección y transformación en el ADP

El ADP NO reenvía los headers del ORQ directamente al banco. Para la combinación `BLOQUEO_TD_DEFINITIVO + BBOG`, el ADP determina qué headers requiere el servicio bancario específico y construye únicamente esos.

### Nivel 3 — Headers enviados al banco

#### BLOQUEO_TD_DEFINITIVO → customer_debit_card_management PUT /V1/product/debitcard/status-lock (REST)

Los headers requeridos por este servicio bancario se obtienen de la documentación técnica del banco (contrato del servicio). El ADP reenvía al banco únicamente los headers definidos en ese contrato — los de valor fijo se configuran como variables de ambiente y los de contexto se propagan desde el request entrante. El ADP no valida su presencia: si el llamador omite un header requerido, el banco retorna el error correspondiente.

---

## Definition of Ready


- [ ] `x-api-key` para canal Oficinas provisionada por BdB
- [ ] Confirmación del campo que identifica la tarjeta (enmascarado vs número completo)
- [ ] Mapeo de causales (BL01/BL02/BL03) → `debitCardStatus` confirmado con BdB
- [ ] Conectividad de red desde AKS hacia ALB de BdB confirmada
- [ ] HU-201-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Cliente REST `PUT /V1/product/debitcard/status-lock` implementado
- [ ] Headers requeridos por BdB incluidos en cada llamada
- [ ] Mapeo de respuesta BdB → modelo normalizado implementado
- [ ] Manejo de errores y timeouts implementado
- [ ] Credenciales en variables de ambiente — validado en pruebas
- [ ] Número de tarjeta enmascarado en respuesta
- [ ] Pruebas unitarias (cobertura ≥ 90%)
- [ ] Prueba de integración contra BdB en PT
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada — request y response encolados en cada invocación
