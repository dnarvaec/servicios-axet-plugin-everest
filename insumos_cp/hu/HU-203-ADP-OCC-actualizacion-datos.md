# HU-203-ADP-OCC: Adaptador Banco de Occidente — Actualización de Datos del Cliente

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-203-ADP-OCC                                              |
| ID Servicio    | SFA-027                                                     |
| Épica          | Épica 3 — Actualización de Datos (P2)                       |
| Componente     | Adaptador OCC — Actualización de Datos                      |
| Microservicio  | `ofic-actualizaciones-adp-bocc`                             |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P2)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | Pendiente                                                   |
| HU Padre       | HU-203-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-21                                                  |
| Última revisión | 2026-09-15 — gap resuelto: servicio documentado; endpoint REST `PUT /UpdateCustomerData/v1/customers/persons/data/updatePersonsData` con autenticación OAuth 2.0 Bearer; reglas de integración, mapeo de campos, flujo de token, headers, outputs y Gherkin completos |

---

## Historia de Usuario

**Como** microservicio `ofic-actualizaciones-adp-bocc`,
**quiero** recibir del orquestador (`ofic-actualizaciones-orq`) la solicitud de actualización de datos del cliente de Banco de Occidente,
**para** obtener un token OAuth 2.0, invocar el servicio REST `UpdateCustomerData` de OCC y retornar el resultado normalizado.

---

## Contexto de Negocio

OCC expone la actualización de datos del cliente a través del servicio REST `UpdateCustomerData PUT /UpdateCustomerData/v1/customers/persons/data/updatePersonsData`, publicado en Datapower DMZ. A diferencia de los demás servicios OCC (que son SOAP internos sin autenticación adicional), este servicio requiere autenticación **OAuth 2.0** con `grant_type=client_credentials` previo a cada llamada. El ADP debe obtener el token antes de invocar el servicio de negocio.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/occ/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`.
- **CA-02:** Antes de invocar el servicio de negocio, el ADP obtiene un token OAuth 2.0 mediante `POST /token` con `grant_type=client_credentials`, `client_id` y `client_secret` (variables de ambiente). El token tiene vigencia de 7200 segundos y puede cachearse en memoria hasta su expiración.
- **CA-03:** El ADP invoca `PUT /UpdateCustomerData/v1/customers/persons/data/updatePersonsData` con el header `Authorization: Bearer <token>`, los headers de contexto y el body construido según las Reglas de Integración.
- **CA-04:** Si OCC retorna `200` → operación exitosa; el ADP retorna la respuesta normalizada al ORQ.
- **CA-05:** Si OCC retorna `400` → el ADP mapea a `400` al ORQ.
- **CA-06:** Si OCC retorna `401` → el token expiró o es inválido; el ADP renueva el token y reintenta una vez. Si falla de nuevo → retorna `502` al ORQ.
- **CA-07:** Si OCC no responde en el tiempo configurado → el ADP mapea a `504` al ORQ y registra en Elastic.
- **CA-08:** Circuit Breaker activo en el consumo del servicio OCC.
- **CA-09:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-10:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

---

## Inputs

### Recibidos del Orquestador

El ADP recibe del orquestador: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`.

```json
{
  "operacion": "ACTUALIZACION_DATOS",
  "obj_operacion": {
    "banco": "OCC",
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

## Servicio de OCC a Invocar

### Paso 1 — Obtención del token OAuth 2.0

| Campo | Valor |
|-------|-------|
| Método | POST |
| Content-Type | `application/x-www-form-urlencoded` |

#### Endpoints token

| Ambiente | URL |
|----------|-----|
| DES      | `https://boc201.des.app.bancodeoccidente.net:4852/token` |
| CAL (QA) | `https://boc201.tesdmz.app.bancodeoccidente.net:4852/token` |
| PROD     | `https://boc201.prddmz.app.bancodeoccidente.net:4852/token` |

> Nota: la documentación original de OCC omite el puerto en CAL (`https://boc201.tesdmz.app.bancodeoccidente.net:/token`). Se asume puerto 4852 igual a DES — confirmar con OCC.

#### Body del request de token

| Campo | Descripción |
|-------|-------------|
| `grant_type` | `client_credentials` (fijo) |
| `client_id` | Variable de ambiente — ejemplo QA: `adl.oauth.bocc.com` |
| `client_secret` | Variable de ambiente — distinto por ambiente |

#### Response de token

| Campo | Descripción |
|-------|-------------|
| `token_type` | `Bearer` |
| `access_token` | Token de acceso |
| `expires_in` | `7200` segundos |

El ADP construye el header: `Authorization: Bearer <access_token>`

El token puede cachearse hasta 30 segundos antes de su expiración (`expires_in - 30`) para evitar llamadas innecesarias al endpoint de token.

---

### Paso 2 — Servicio de negocio

| Campo               | Valor                                                                              |
|---------------------|------------------------------------------------------------------------------------|
| Tipo                | REST                                                                               |
| Servicio            | `UpdateCustomerData`                                                               |
| Método              | PUT                                                                                |
| Path                | `/UpdateCustomerData/v1/customers/persons/data/updatePersonsData`                  |
| Middleware          | Datapower DMZ OCC                                                                  |

#### Endpoints servicio

| Ambiente | URL |
|----------|-----|
| DES      | `https://boc201.des.app.bancodeoccidente.net:4848/UpdateCustomerData/v1/customers/persons/data/updatePersonsData` |
| CAL (QA) | `https://boc201.tesdmz.app.bancodeoccidente.net:4848/UpdateCustomerData/v1/customers/persons/data/updatePersonsData` |
| PROD     | `https://boc201.prddmz.app.bancodeoccidente.net:4848/UpdateCustomerData/v1/customers/persons/data/updatePersonsData` |

#### Headers del request a OCC

| Header | Tipo | Descripción | Obligatorio |
|--------|------|-------------|-------------|
| `Authorization` | String | `Bearer <access_token>` obtenido en paso 1 | SI |
| `Aplcod` | String | Código de aplicación (variable de ambiente, ej: `408`) | SI |
| `Usrio` | String | Usuario ejecutor | SI |
| `Sesionid` | String | ID de sesión | SI |
| `Ptcionid` | String | ID único de petición | SI |
| `Trmnalid` | String | ID de terminal | SI |
| `Ptcionfecha` | String (datetime) | Fecha y hora de la petición (`yyyy-MM-ddTHH:mm:ss`) | SI |

#### Body del request a OCC

```json
{
  "Data": {
    "IdentificacionTipo": "CC",
    "Identificacion": "12345678",
    "InfoCntactoDatos": {
      "Item": [
        {
          "CntactoTipo": "2",
          "DatoTipo": "15",
          "CntctoMdio": "3101234567",
          "IndPrefMtCntcto": "Y"
        }
      ]
    }
  }
}
```

| Campo | Tipo | Descripción | Obligatorio |
|-------|------|-------------|-------------|
| `Data.IdentificacionTipo` | String | Tipo de documento (ej: `CC`) | SI |
| `Data.Identificacion` | String | Número de documento | SI |
| `Data.InfoCntactoDatos.Item` | Array | Lista de datos de contacto a actualizar | SI (min 1) |
| `Item[].CntactoTipo` | String | Tipo de contacto | SI |
| `Item[].DatoTipo` | String | Tipo de dato del contacto | SI |
| `Item[].CntctoMdio` | String | Valor del dato (número de teléfono, correo, etc.) | SI |
| `Item[].IndPrefMtCntcto` | String | Indicador de medio preferido (`Y`/`N`) | SI |

---

## Outputs

> El ADP retorna la respuesta del banco directamente.

### Response OCC exitoso (HTTP 200)

OCC retorna HTTP 200 sin body o con body vacío en caso de éxito.

### Modelo normalizado de salida al ORQ

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `exito` | Boolean | `true` si OCC retornó 200 |
| `mensaje` | String | Descripción del resultado |

### Mapeo de errores OCC → estándar

| Código OCC | Código HTTP al ORQ | StatusDesc |
|------------|-------------------|------------|
| `200`      | `200`             | Actualización exitosa |
| `400`      | `400`             | "Datos inválidos en la solicitud" |
| `401`      | `502`             | "Token OAuth expirado o inválido" (después de reintento) |
| `500`      | `502`             | "Error interno en OCC" |
| Timeout    | `504`             | "Timeout del servicio OCC" |

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `ACTUALIZACION_DATOS` | `BOCC` | `UpdateCustomerData / PUT /UpdateCustomerData/v1/customers/persons/data/updatePersonsData` — REST OAuth 2.0 |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo | Valor fijo | Descripción |
|-------|------------|-------------|
| `grant_type` | `client_credentials` | Tipo de grant OAuth 2.0 |
| `Aplcod` | Variable de ambiente | Código de aplicación asignado por OCC |

### Mapeo de campos

| Campo obj_operacion | Campo OCC | Notas |
|---------------------|-----------|-------|
| `tipoDocumento` | `Data.IdentificacionTipo` | Tipo de documento del cliente |
| `numeroDocumento` | `Data.Identificacion` | Número de documento del cliente |
| `datosActualizar.celular` | `Item[CntactoTipo=2, DatoTipo=15].CntctoMdio` | Confirmar valores de CntactoTipo/DatoTipo con OCC |
| `datosActualizar.correoElectronico` | `Item[CntactoTipo=1, DatoTipo=...].CntctoMdio` | Confirmar valores con OCC |
| (generado por ADP) | `Ptcionid` | ID único de petición |
| (generado por ADP) | `Ptcionfecha` | Timestamp actual |
| (del contexto) | `Trmnalid` | ID de terminal |
| (del JWT) | `Usrio` | Usuario del asesor |

> Pendiente: Confirmar con OCC los valores exactos de `CntactoTipo` y `DatoTipo` para celular y correo electrónico.

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** El ADP obtiene el token OAuth 2.0 antes de cada llamada al servicio de negocio. El token puede cachearse con TTL de `expires_in - 30` segundos para evitar llamadas innecesarias.
- **RO-03:** Si el servicio de negocio retorna `401`, el ADP invalida el token cacheado, lo renueva y reintenta la operación una vez.
- **RO-04:** El ADP construye `Ptcionid` como identificador único por petición.
- **RO-05:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`). Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU.
- **RO-06:** Las credenciales OAuth (`client_id`, `client_secret`) se configuran como variables de ambiente — nunca hardcodeadas.
- **RO-07:** La URL base del token y del servicio son variables de ambiente independientes. Nunca se hardcodean en el código.

---

## Caminos Alternativos y Excepciones

| ID | Condición | Comportamiento |
|---|---|---|
| ALT-00 | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. |
| ALT-01 | Error al obtener token OAuth 2.0 | ADP retorna `502` al ORQ — no puede autenticarse con OCC |
| ALT-02 | OCC retorna 401 en servicio de negocio | ADP renueva token y reintenta una vez; si falla → `502` |
| ALT-03 | OCC retorna 400 | ADP retorna `400` al ORQ con detalle del error |
| ALT-04 | Timeout conectividad ADP → OCC | Circuit Breaker abre → ADP retorna `504` |

---

## Tecnología a Usar

| Componente      | Tecnología   | Versión | Nota |
|-----------------|--------------|---------|------|
| Lenguaje        | Java         | 21      | |
| Framework       | Spring Boot  | 3.5.13  | |
| Cliente REST    | Retrofit     | 2.x     | Para `UpdateCustomerData` y endpoint de token |
| Circuit Breaker | Resilience4j | —       | Activo en todos los consumos externos |
| Logs            | Elastic      | —       | |
| Mensajería      | AWS SQS FIFO | —       | Cola de auditoría — `avc-everest-pt-logs.fifo` |

---

## Dependencias

| HU         | Relación |
|------------|----------|
| HU-203-ORQ | Padre — `ofic-actualizaciones-orq` |

---

## Preguntas Abiertas

| # | Pregunta | Impacto |
|---|----------|---------|
| 1 | ¿Cuáles son los valores exactos de `CntactoTipo` y `DatoTipo` para celular y correo en OCC? | Define el mapeo de campos |
| 2 | ¿El puerto del endpoint de token en CAL es 4852 (como DES) u otro? | Define la URL de pruebas |
| 3 | ¿El `client_secret` de QA puede ser usado en pruebas PT o se requiere uno específico? | Define las credenciales de integración |
| 4 | ¿Qué campos del cliente son actualizables desde el canal Oficinas en OCC (solo contacto o también otros)? | Define el alcance del adaptador |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador OCC — Actualización de Datos del Cliente
  Background:
    Given el adaptador OCC está configurado con credenciales OAuth 2.0 válidas
    And hay conectividad con Datapower DMZ de OCC

  Scenario: Actualización exitosa de celular
    Given el adaptador recibe tipoDocumento "CC", numeroDocumento "12345678"
    And datosActualizar contiene celular "3101234567"
    When el ADP obtiene el token OAuth y luego invoca PUT /UpdateCustomerData/.../updatePersonsData
    Then OCC retorna HTTP 200
    And el adaptador retorna la respuesta exitosa al orquestador

  Scenario: Token expirado — renovación exitosa
    Given el token cacheado está expirado
    When el ADP intenta invocar el servicio y recibe 401
    Then el ADP renueva el token OAuth y reintenta la operación
    And si el segundo intento es exitoso retorna 200 al ORQ

  Scenario: Token expirado — segundo intento fallido
    Given el token cacheado está expirado
    When el ADP renueva el token pero el servicio sigue retornando 401
    Then el adaptador retorna 502 al orquestador
    And registra el evento en Elastic

  Scenario: Timeout
    Given el servicio OCC no responde en el tiempo configurado
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
| `X-Destination-Bank` | Confirma que el banco destino es `BOCC` |

### Nivel 2 — Selección y transformación en el ADP

El ADP NO reenvía los headers del ORQ directamente al banco. Para la combinación `ACTUALIZACION_DATOS + BOCC`, el ADP:
1. Obtiene el token OAuth 2.0 mediante el endpoint de token OCC.
2. Construye los headers del servicio de negocio con ese token y datos de contexto.

### Nivel 3 — Headers enviados al banco

#### ACTUALIZACION_DATOS → UpdateCustomerData PUT /updatePersonsData (REST OAuth 2.0)

| Header | Origen | Valor |
|--------|--------|-------|
| `Authorization` | Obtenido del endpoint de token OCC | `Bearer <access_token>` |
| `Aplcod` | Variable de ambiente | Código de aplicación asignado por OCC |
| `Usrio` | JWT del asesor | Usuario ejecutor |
| `Sesionid` | Contexto de sesión | ID de sesión |
| `Ptcionid` | Generado por ADP | ID único de petición |
| `Trmnalid` | Contexto AKS | ID de terminal |
| `Ptcionfecha` | Generado por ADP | Timestamp actual (ISO 8601) |

---

## Definition of Ready

- [x] Servicio documentado: `UpdateCustomerData PUT /updatePersonsData` con OAuth 2.0
- [x] Endpoints DES/CAL/PROD confirmados
- [x] Flujo de token OAuth 2.0 documentado
- [x] Headers y body del request documentados
- [ ] Valores de `CntactoTipo`/`DatoTipo` para celular y correo confirmados con OCC
- [ ] Puerto del endpoint de token en CAL confirmado
- [ ] Credenciales OAuth de pruebas PT definidas
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Cliente Retrofit para `UpdateCustomerData` implementado
- [ ] Flujo OAuth 2.0 implementado con caché de token (`expires_in - 30s`)
- [ ] Retry en caso de 401 (renovación de token + reintento una vez)
- [ ] Headers de contexto construidos correctamente
- [ ] Body construido con campos de contacto de `datosActualizar`
- [ ] Mapeo de errores OCC → HTTP estándar implementado
- [ ] Circuit Breaker activo
- [ ] Pruebas unitarias (cobertura ≥ 90%)
- [ ] Prueba de integración contra OCC en DES o CAL
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada
