# HU-203-ADP-BDB: Adaptador Banco de Bogotá — Actualización de Datos del Cliente

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-203-ADP-BDB                                              |
| ID Servicio    | SFA-027                                                     |
| Épica          | Épica 3 — Actualización de Datos (P2)                       |
| Componente     | Adaptador BdB — Actualización de Datos                      |
| Microservicio  | `ofic-actualizaciones-adp-bbog`                             |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P2)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | Pendiente                                                   |
| HU Padre       | HU-203-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-21                                                  |
| Última revisión | 2026-09-15 — gap resuelto: servicio documentado (SFA-027); endpoint REST `customer-management-v3 PUT /V3/enterprise/customer/basic-info` + SOAP BUS `CustomerInformationManagement/modCustSecureInfo`; reglas de integración, mapeo de campos, headers, outputs, Gherkin y DoD completos |

---

## Historia de Usuario

**Como** microservicio `ofic-actualizaciones-adp-bbog`,
**quiero** recibir del orquestador (`ofic-actualizaciones-orq`) la solicitud de actualización de datos del cliente de Banco de Bogotá,
**para** invocar el servicio REST `customer-management-v3` de BdB y retornar el resultado normalizado.

---

## Contexto de Negocio

BdB expone la actualización de datos del cliente a través de dos canales: SOAP BUS (`CustomerInformationManagement / modCustSecureInfo`) y REST AWS (`customer-management-v3 PUT /V3/enterprise/customer/basic-info`). Para el canal Oficinas se usa el canal **REST AWS** siguiendo el patrón establecido en los demás adaptadores BdB. El servicio actualiza datos de persona natural en el CRM del banco (nombre, teléfonos, correos, direcciones, información financiera, empleo).

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/bog/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente (ver sección Gestión de Headers).
- **CA-02:** El adaptador invoca `PUT /V3/enterprise/customer/basic-info` del servicio `customer-management-v3` de BdB con los headers y body construidos según las Reglas de Integración.
- **CA-03:** Si BdB retorna `200` → operación exitosa; el ADP retorna la respuesta normalizada al ORQ.
- **CA-04:** Si BdB retorna `400` o `404` → el ADP mapea a `400` al ORQ con el detalle del error.
- **CA-05:** Si BdB retorna `401` → el ADP mapea a `502` (credenciales de integración inválidas).
- **CA-06:** Si BdB no responde en el tiempo configurado → el ADP mapea a `504`.
- **CA-07:** Circuit Breaker activo en el consumo del servicio BdB.
- **CA-08:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-09:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

---

## Inputs

### Recibidos del Orquestador

El ADP recibe del orquestador: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`.

```json
{
  "operacion": "ACTUALIZACION_DATOS",
  "obj_operacion": {
    "banco": "BDB",
    "tipoDocumento": "CC",
    "numeroDocumento": "12345678",
    "datosActualizar": {
      "celular": "3101234567",
      "correoElectronico": "cliente@email.com"
    }
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
| Servicio            | `customer-management-v3`                                      |
| Método              | PUT                                                           |
| Path                | `/V3/enterprise/customer/basic-info`                          |
| Middleware          | AWS ECS                                                       |
| Timeout             | 29 segundos (API Gateway AWS)                                 |

### Endpoints

| Ambiente | URL base |
|----------|----------|
| QA       | `https://api-clients.labdigitalbdbtvsqa.com/customer-management-v3-mngr` |
| STG      | `https://api-clients.labdigitalbdbtvsstg.com/customer-management-v3-mngr` |
| PROD     | `https://api-clients.labdigitalbdbtvs.com/customer-management-v3-mngr` |

URL completa de ejemplo (QA): `https://api-clients.labdigitalbdbtvsqa.com/customer-management-v3-mngr/V3/enterprise/customer/basic-info`

### Headers del request a BdB

| Header | Tipo | Descripción | Obligatorio |
|--------|------|-------------|-------------|
| `X-CustIdentType` | String | Tipo de documento (CC, CE, LC, NI, OT, PA, RC, NJ, NE, TI) | SI |
| `X-CustIdentNum` | String | Número de documento (1–25 chars alfanumérico) | SI |
| `X-RqUID` | String | UUID v4 (36 chars), único por petición | SI |
| `X-Channel` | String | Canal de origen (valor fijo: `Oficinas`) | SI |
| `X-CompanyId` | String | Código de empresa (valor fijo: `001`) | SI |
| `X-IPAddr` | String | IP de origen del asesor | SI |
| `X-NetworkOwner` | String | Nombre de la aplicación consumidora (valor fijo: `ofic-actualizaciones-adp-bbog`) | SI |
| `X-TerminalId` | String | ID de terminal AKS | SI |

### Body del request a BdB

```json
{
  "modCustSecureInfoRq": {
    "CustInfo": {
      "TypeId": "CC",
      "ParticipantId": "12345678",
      "PersonName": {
        "FirstName": "Juan",
        "LastName": "Pérez"
      },
      "ContactInfo": {
        "PhoneNum": [
          {
            "PhoneType": "12",
            "Phone": "3101234567"
          }
        ],
        "EmailAddr": "cliente@email.com",
        "PostAddr": []
      },
      "FinantialInfo": {},
      "EmploymentHistory": {},
      "IncomeTaxInd": "N"
    },
    "Flag": []
  }
}
```

> Los campos de `CustInfo` son opcionales salvo `TypeId` y `ParticipantId`. El ORQ envía en `obj_operacion` solo los campos a actualizar — el ADP construye el body enviando únicamente los campos presentes.

### Referencia de PhoneType (campo `PhoneNum`)

| Valor | Descripción |
|-------|-------------|
| `11`  | Teléfono oficina |
| `12`  | Celular |
| `15`  | Teléfono residencia |

---

## Outputs

> El ADP retorna la respuesta del banco directamente — no hay transformación a un modelo normalizado propio.

### Response BdB exitoso (HTTP 200)

```json
{
  "modCustSecureInfoRs": {
    "StatusCode": "200",
    "StatusDesc": "Successfully updated"
  }
}
```

### Modelo normalizado de salida al ORQ

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `exito` | Boolean | `true` si BdB retornó 200 |
| `mensaje` | String | Descripción del resultado |

### Mapeo de errores BdB → estándar

| Código BdB | Código HTTP al ORQ | StatusDesc |
|------------|-------------------|------------|
| `200`      | `200`             | Actualización exitosa |
| `400`      | `400`             | "Datos inválidos en la solicitud" |
| `404`      | `400`             | "Cliente no encontrado en BdB" |
| `401`      | `502`             | "Error de autenticación con BdB" |
| `403`      | `502`             | "API key inválida o IP no registrada en BdB" |
| Timeout    | `504`             | "Timeout del servicio BdB" |

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `ACTUALIZACION_DATOS` | `BBOG` | `customer-management-v3` / `PUT /V3/enterprise/customer/basic-info` — REST AWS |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo | Valor fijo | Descripción |
|-------|------------|-------------|
| `X-Channel` | `Oficinas` | Canal de origen fijo para este adaptador |
| `X-CompanyId` | `001` | Código de empresa BdB |
| `X-NetworkOwner` | `ofic-actualizaciones-adp-bbog` | Nombre del consumidor |

### Mapeo de campos

| Campo obj_operacion | Header / Campo BdB | Notas |
|---------------------|---------------------|-------|
| `tipoDocumento` | `X-CustIdentType` (header) | Tipo de documento del cliente |
| `numeroDocumento` | `X-CustIdentNum` (header) | Número de documento del cliente |
| `datosActualizar.celular` | `CustInfo.ContactInfo.PhoneNum[PhoneType=12].Phone` | PhoneType 12 = celular |
| `datosActualizar.correoElectronico` | `CustInfo.ContactInfo.EmailAddr` | |
| `datosActualizar.telefonoResidencia` | `CustInfo.ContactInfo.PhoneNum[PhoneType=15].Phone` | PhoneType 15 = residencia |
| `datosActualizar.telefonoOficina` | `CustInfo.ContactInfo.PhoneNum[PhoneType=11].Phone` | PhoneType 11 = oficina |
| (generado por ADP) | `X-RqUID` | UUID v4 único por petición |
| (del contexto AKS) | `X-IPAddr` | IP de origen |
| (del contexto AKS) | `X-TerminalId` | ID de terminal |

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** El ADP construye el body enviando únicamente los campos presentes en `datosActualizar` — no incluye campos vacíos.
- **RO-03:** `X-RqUID` es generado por el ADP (UUID v4) en cada petición — no propagado del ORQ.
- **RO-04:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`). Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU.
- **RO-05:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.
- **RO-06:** Las credenciales (`x-api-key` si aplica) se configuran como variables de ambiente.

---

## Caminos Alternativos y Excepciones

| ID | Condición | Comportamiento |
|---|---|---|
| ALT-00 | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. |
| ALT-01 | BdB retorna 400/404 | ADP retorna `400` al ORQ con detalle del error bancario |
| ALT-02 | BdB retorna 401/403 | ADP retorna `502` al ORQ — credenciales de integración inválidas |
| ALT-03 | Timeout conectividad BdB | ADP retorna `504` al ORQ y registra en Elastic |

---

## Tecnología a Usar

| Componente      | Tecnología          | Versión  | Nota |
|-----------------|---------------------|----------|------|
| Lenguaje        | Java                | 21       | |
| Framework       | Spring Boot         | 3.5.13   | |
| Cliente REST    | Retrofit            | 2.x      | Para `customer-management-v3` |
| Circuit Breaker | Resilience4j        | —        | Activo en todos los consumos externos |
| Logs            | Elastic             | —        | |
| Mensajería      | AWS SQS FIFO        | —        | Cola de auditoría — `avc-everest-pt-logs.fifo` |

---

## Dependencias

| HU         | Relación |
|------------|----------|
| HU-203-ORQ | Padre — `ofic-actualizaciones-orq` |

---

## Preguntas Abiertas

| # | Pregunta | Impacto |
|---|----------|---------|
| 1 | ¿El canal Oficinas requiere `x-api-key` específica o usa la misma que otros ADPs BdB? | Define configuración de credenciales |
| 2 | ¿Qué campos de `datosActualizar` son habilitados para el canal Oficinas (solo contacto o también financiero/laboral)? | Define el alcance del mapeo |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador BdB — Actualización de Datos del Cliente
  Background:
    Given el adaptador BdB está configurado con credenciales válidas
    And hay conectividad con el API Gateway AWS de BdB

  Scenario: Actualización exitosa de celular y correo
    Given el adaptador recibe tipoDocumento "CC", numeroDocumento "12345678"
    And datosActualizar contiene celular "3101234567" y correoElectronico "cliente@email.com"
    When invoca PUT /V3/enterprise/customer/basic-info en BdB
    Then BdB retorna HTTP 200
    And el adaptador retorna la respuesta exitosa al orquestador

  Scenario: Datos inválidos
    Given el adaptador recibe un tipoDocumento con valor inválido
    When invoca el servicio REST
    Then BdB retorna HTTP 400
    And el adaptador retorna 400 al orquestador con el detalle del error

  Scenario: Timeout
    Given el servicio BdB no responde en el tiempo configurado
    When el adaptador espera la respuesta
    Then retorna 504 al orquestador
    And registra el evento en Elastic

  Scenario: Operacion no soportada
    Given el adaptador recibe una operacion distinta de ACTUALIZACION_DATOS
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

El ADP NO reenvía los headers del ORQ directamente al banco. Para la combinación `ACTUALIZACION_DATOS + BBOG`, el ADP construye los headers requeridos por `customer-management-v3`.

### Nivel 3 — Headers enviados al banco

#### ACTUALIZACION_DATOS → customer-management-v3 PUT /V3/enterprise/customer/basic-info (REST)

| Header | Origen | Valor |
|--------|--------|-------|
| `X-CustIdentType` | `obj_operacion.tipoDocumento` | Tipo de documento del cliente |
| `X-CustIdentNum` | `obj_operacion.numeroDocumento` | Número de documento del cliente |
| `X-RqUID` | Generado por ADP | UUID v4 único por petición |
| `X-Channel` | Constante | `Oficinas` |
| `X-CompanyId` | Constante | `001` |
| `X-IPAddr` | Contexto AKS | IP del pod |
| `X-NetworkOwner` | Constante | `ofic-actualizaciones-adp-bbog` |
| `X-TerminalId` | Contexto AKS | ID de terminal |

---

## Definition of Ready

- [x] Servicio documentado: `customer-management-v3 PUT /V3/enterprise/customer/basic-info`
- [x] Endpoints QA/STG/PROD confirmados
- [x] Headers y body del request documentados
- [x] Mapeo de campos completo
- [ ] API key para canal Oficinas confirmada con BdB
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Cliente Retrofit para `customer-management-v3` implementado
- [ ] Headers construidos correctamente desde `obj_operacion` y contexto AKS
- [ ] Body construido con solo los campos presentes en `datosActualizar`
- [ ] Mapeo de errores BdB → HTTP estándar implementado
- [ ] Circuit Breaker activo
- [ ] Pruebas unitarias (cobertura ≥ 90%)
- [ ] Prueba de integración contra BdB en QA
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada
