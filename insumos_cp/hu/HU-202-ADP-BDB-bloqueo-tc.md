# HU-202-ADP-BDB: Adaptador Banco de Bogotá — Bloqueo TC

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-202-ADP-BDB                                              |
| ID Servicio    | SFA-010                                                     |
| Épica          | Épica 2 — Mantenimiento Tarjeta Crédito (P2)                |
| Componente     | Adaptador BdB — Bloqueo TC                                  |
| Microservicio  | `ofic-actualizaciones-adp-bbog`                             |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P2)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | Pendiente                                                   |
| HU Padre       | HU-202-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-21                                                  |
| Última revisión | 2026-09-15 — gap resuelto: servicio documentado (SFA-010); endpoint REST `credit-card-management POST /V1/Product/credit-card/block` (`CreditCardBlockPreventiveManagement`); reglas de integración, mapeo de campos, headers, outputs y Gherkin completos |

---

## Historia de Usuario

**Como** microservicio `ofic-actualizaciones-adp-bbog`,
**quiero** recibir del orquestador (`ofic-actualizaciones-orq`) la solicitud de bloqueo de tarjeta de crédito de Banco de Bogotá,
**para** invocar el servicio REST `credit-card-management` de BdB y retornar el resultado normalizado.

---

## Contexto de Negocio

BdB expone el bloqueo de TC a través del servicio REST `credit-card-management POST /V1/Product/credit-card/block`, cuyo backend es `CreditCardBlockPreventiveManagement / modCCBlockPreventiveBank`. El servicio aplica un bloqueo preventivo sobre la tarjeta de crédito (`LockId: "P"`). Este es el mecanismo disponible en BdB para el canal Oficinas.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/bog/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente (ver sección Gestión de Headers).
- **CA-02:** El adaptador invoca `POST /V1/Product/credit-card/block` del servicio `credit-card-management` de BdB con los headers y body construidos según las Reglas de Integración.
- **CA-03:** Si BdB retorna `200` con `Status.StatusCode=200` → operación exitosa; el ADP retorna la respuesta normalizada al ORQ.
- **CA-04:** Si BdB retorna `400` → el ADP mapea a `400` al ORQ.
- **CA-05:** Si BdB retorna `408` (timeout) → el ADP mapea a `504` al ORQ.
- **CA-06:** Si BdB retorna `409` (conflicto de negocio) → el ADP mapea a `422` al ORQ.
- **CA-07:** Si BdB retorna `500` → el ADP mapea a `502` al ORQ.
- **CA-08:** Circuit Breaker activo en el consumo del servicio BdB.
- **CA-09:** Los números de tarjeta circulan completos en el flujo funcional (entre ORQ, ADP y servicio bancario). El enmascaramiento se aplica únicamente en logs (Elastic): últimos 4 dígitos visibles (ejemplo: `****5678`).
- **CA-10:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-11:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

---

## Inputs

### Recibidos del Orquestador

El ADP recibe del orquestador: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`.

```json
{
  "operacion": "BLOQUEO_TC",
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

| Campo               | Valor                                                         |
|---------------------|---------------------------------------------------------------|
| Tipo                | REST                                                          |
| Servicio            | `credit-card-management`                                      |
| Método              | POST                                                          |
| Path                | `/V1/Product/credit-card/block`                               |
| Backend             | `CreditCardBlockPreventiveManagement / modCCBlockPreventiveBank` |
| Middleware          | AWS                                                           |

### Endpoints

| Ambiente | URL base |
|----------|----------|
| QA       | `https://alb-0.labdigitalbdbqatc.com:9212/credit-card-management` |
| STG      | `https://alb-0.labdigitalbdbsttc.com:9212/credit-card-management` |
| PROD     | `https://alb-0.labdigitalbdbtc.com:9212/credit-card-management` |

URL completa de ejemplo (QA): `https://alb-0.labdigitalbdbqatc.com:9212/credit-card-management/V1/Product/credit-card/block`

> Nota del proveedor: el puerto de la URL de ejemplo en la documentación BdB usa 9213 para QA — se tomará el valor confirmado en pruebas.

### Headers del request a BdB

| Header | Tipo | Descripción | Obligatorio |
|--------|------|-------------|-------------|
| `X-RqUID` | String | UUID v4 único por petición | SI |
| `X-Channel` | String | Canal de origen (valor fijo: `Oficinas`) | SI |
| `X-IPAddr` | String | IP de origen del asesor | SI |
| `X-Name` | String | Nombre del asesor | SI |
| `X-CustIdentNum` | String | Número de documento del cliente | SI |
| `X-CustIdentType` | String | Tipo de documento del cliente | SI |
| `X-NetworkOwner` | String | Nombre aplicación consumidora (valor fijo: `ofic-actualizaciones-adp-bbog`) | SI |
| `x-api-key` | String | API key para autenticación (variable de ambiente) | SI |

### Body del request a BdB

```json
{
  "CardId": "4111111111111234",
  "StatusDesc": "BLOQUEO POR OFICINA",
  "LockId": "P",
  "BlockReason": 33
}
```

| Campo | Tipo | Descripción | Obligatorio |
|-------|------|-------------|-------------|
| `CardId` | String | Número completo de la tarjeta de crédito | SI |
| `StatusDesc` | String | Descripción del bloqueo (valor fijo: `BLOQUEO POR OFICINA`) | SI |
| `LockId` | String | Tipo de bloqueo (valor fijo: `P` = Preventivo) | SI |
| `BlockReason` | Integer | Código de razón del bloqueo (valor fijo: `33`) | SI |

---

## Outputs

> El ADP retorna la respuesta del banco directamente — no hay transformación a un modelo normalizado propio.

### Response BdB exitoso (HTTP 200)

```json
{
  "Status": {
    "StatusCode": 200,
    "StatusDesc": "SUCCESSFUL TRANSACTION"
  },
  "ResponseInfo": {
    "OperationType": "Block",
    "EndDt": "2026-09-15T10:30:00"
  }
}
```

### Modelo normalizado de salida al ORQ

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `numeroTarjeta` | String | Número enmascarado |
| `estadoActual` | String | `BLOQUEADA` |
| `causal` | String | Causal del bloqueo (BL01/BL02/BL03) |
| `fechaBloqueo` | String | `EndDt` retornado por BdB |

### Mapeo de errores BdB → estándar

| Código BdB | Código HTTP al ORQ | StatusDesc |
|------------|-------------------|------------|
| `200`      | `200`             | Bloqueo exitoso |
| `400`      | `400`             | "Datos inválidos — solicitud rechazada por BdB" |
| `408`      | `504`             | "Timeout del servicio BdB" |
| `409`      | `422`             | "Conflicto de negocio — estado de tarjeta no permite bloqueo" |
| `500`      | `502`             | "Error interno en BdB" |

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `BLOQUEO_TC` | `BBOG` | `credit-card-management` / `POST /V1/Product/credit-card/block` — REST AWS |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo | Valor fijo | Descripción |
|-------|------------|-------------|
| `LockId` | `P` | Tipo de bloqueo preventivo — único disponible en BdB para este canal |
| `BlockReason` | `33` | Código de razón de bloqueo |
| `StatusDesc` | `BLOQUEO POR OFICINA` | Descripción fija del bloqueo |
| `X-Channel` | `Oficinas` | Canal de origen |
| `X-NetworkOwner` | `ofic-actualizaciones-adp-bbog` | Nombre del consumidor |

### Mapeo de campos

| Campo obj_operacion | Header / Campo BdB | Notas |
|---------------------|---------------------|-------|
| `numeroTarjeta` | `CardId` | Número completo de la TC — no enmascarado en el payload funcional |
| `tipoDocumento` | `X-CustIdentType` (header) | |
| `numeroDocumento` | `X-CustIdentNum` (header) | |
| (generado por ADP) | `X-RqUID` | UUID v4 único por petición |
| (del contexto AKS) | `X-IPAddr` | IP de origen |
| (del JWT) | `X-Name` | Nombre del asesor |

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** Los números de tarjeta circulan completos en el flujo funcional (entre ORQ, ADP y servicio bancario). El enmascaramiento se aplica **únicamente en logs** (Elastic): últimos 4 dígitos visibles (ejemplo: `****5678`). Nunca ofuscar el número real en el payload funcional.
- **RO-03:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`). Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU.
- **RO-04:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.
- **RO-05:** La `x-api-key` se configura como variable de ambiente — nunca hardcodeada.
- **RO-06:** `X-RqUID` es generado por el ADP (UUID v4) en cada petición.

---

## Caminos Alternativos y Excepciones

| ID | Condición | Comportamiento |
|---|---|---|
| ALT-00 | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. |
| ALT-01 | BdB retorna 400 | ADP retorna `400` al ORQ con detalle del error |
| ALT-02 | BdB retorna 408 (timeout BdB interno) | ADP retorna `504` al ORQ y registra en Elastic |
| ALT-03 | BdB retorna 409 (conflicto negocio) | ADP retorna `422` al ORQ |
| ALT-04 | BdB retorna 500 | ADP retorna `502` al ORQ y registra en Elastic |
| ALT-05 | Timeout de conectividad ADP → BdB | Circuit Breaker abre → ADP retorna `504` |

---

## Tecnología a Usar

| Componente      | Tecnología   | Versión | Nota |
|-----------------|--------------|---------|------|
| Lenguaje        | Java         | 21      | |
| Framework       | Spring Boot  | 3.5.13  | |
| Cliente REST    | Retrofit     | 2.x     | Para `credit-card-management` |
| Circuit Breaker | Resilience4j | —       | Activo en todos los consumos externos |
| Logs            | Elastic      | —       | |
| Mensajería      | AWS SQS FIFO | —       | Cola de auditoría — `avc-everest-pt-logs.fifo` |

---

## Dependencias

| HU         | Relación |
|------------|----------|
| HU-202-ORQ | Padre — `ofic-actualizaciones-orq` |

---

## Preguntas Abiertas

| # | Pregunta | Impacto |
|---|----------|---------|
| 1 | ¿La `x-api-key` para `credit-card-management` es la misma que para `customer_debit_card_management` (bloqueo TD)? | Define configuración de credenciales |
| 2 | ¿Confirmar el puerto correcto en QA (9212 vs 9213 mencionado en el ejemplo de la documentación)? | Define la URL de pruebas |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador BdB — Bloqueo TC
  Background:
    Given el adaptador BdB está configurado con credenciales válidas
    And hay conectividad con el API Gateway AWS de BdB

  Scenario: Bloqueo exitoso
    Given el adaptador recibe tipoDocumento "CC", numeroDocumento "12345678" y numeroTarjeta completo
    When invoca POST /V1/Product/credit-card/block en BdB con LockId "P"
    Then BdB retorna HTTP 200 con StatusCode 200
    And el adaptador retorna respuesta normalizada con estadoActual "BLOQUEADA"

  Scenario: Tarjeta con estado incompatible
    Given el adaptador recibe un numeroTarjeta con estado que no permite bloqueo
    When invoca el servicio REST
    Then BdB retorna HTTP 409
    And el adaptador retorna 422 al orquestador

  Scenario: Timeout
    Given el servicio BdB no responde en el tiempo configurado
    When el adaptador espera la respuesta
    Then retorna 504 al orquestador
    And registra el evento en Elastic

  Scenario: Numero de tarjeta enmascarado en logs
    Given el adaptador procesa una solicitud con numeroTarjeta "4111111111111234"
    Then en los logs de Elastic el numero aparece como "****1234"
    And en el payload funcional enviado a BdB el numero circula completo

  Scenario: Operacion no soportada
    Given el adaptador recibe una operacion distinta de BLOQUEO_TC
    Then el adaptador lanza IllegalArgumentException y retorna 400 al ORQ
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

El ADP NO reenvía los headers del ORQ directamente al banco. Para la combinación `BLOQUEO_TC + BBOG`, el ADP construye los headers requeridos por `credit-card-management`.

### Nivel 3 — Headers enviados al banco

#### BLOQUEO_TC → credit-card-management POST /V1/Product/credit-card/block (REST)

| Header | Origen | Valor |
|--------|--------|-------|
| `X-RqUID` | Generado por ADP | UUID v4 único por petición |
| `X-Channel` | Constante | `Oficinas` |
| `X-IPAddr` | Contexto AKS | IP del pod |
| `X-Name` | JWT del asesor | Nombre del asesor |
| `X-CustIdentNum` | `obj_operacion.numeroDocumento` | Número de documento |
| `X-CustIdentType` | `obj_operacion.tipoDocumento` | Tipo de documento |
| `X-NetworkOwner` | Constante | `ofic-actualizaciones-adp-bbog` |
| `x-api-key` | Variable de ambiente | API key de integración BdB |

---

## Definition of Ready

- [x] Servicio documentado: `credit-card-management POST /V1/Product/credit-card/block`
- [x] Endpoints QA/STG/PROD confirmados
- [x] Headers y body del request documentados
- [x] Constantes de mapeo definidas (LockId=P, BlockReason=33)
- [ ] API key para `credit-card-management` confirmada con BdB
- [ ] Puerto correcto en QA confirmado (9212 vs 9213)
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Cliente Retrofit para `credit-card-management` implementado
- [ ] Headers construidos correctamente (X-RqUID generado, X-Name desde JWT)
- [ ] Body con constantes fijas (LockId=P, BlockReason=33) implementado
- [ ] Número de tarjeta enmascarado en logs, completo en payload funcional
- [ ] Mapeo de errores BdB → HTTP estándar implementado
- [ ] Circuit Breaker activo
- [ ] Pruebas unitarias (cobertura ≥ 90%)
- [ ] Prueba de integración contra BdB en QA
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada
