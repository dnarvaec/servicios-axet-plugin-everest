# HU-202-ADP-OCC: Adaptador Banco de Occidente — Bloqueo TC

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-202-ADP-OCC                                              |
| ID Servicio    | SFA-010                                                     |
| Épica          | Épica 2 — Mantenimiento Tarjeta Crédito (P2)                |
| Componente     | Adaptador OCC — Bloqueo TC                                  |
| Microservicio  | `ofic-actualizaciones-adp-bocc`                             |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P2)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | Pendiente                                                   |
| HU Padre       | HU-202-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-21                                                  |
| Última revisión | 2026-09-15 — gap resuelto: servicio documentado; endpoint REST `POST /products/credit-cards/block` con autenticación OAuth 2.0 Bearer (mismo patrón que UpdateCustomerData OCC); permite bloqueo definitivo de TC con bloqueo preventivo previo; reglas de integración, mapeo de campos, flujo de token, headers, outputs y Gherkin completos |

---

## Historia de Usuario

**Como** microservicio `ofic-actualizaciones-adp-bocc`,
**quiero** recibir del orquestador (`ofic-actualizaciones-orq`) la solicitud de bloqueo de tarjeta de crédito de Banco de Occidente,
**para** obtener un token OAuth 2.0, invocar el servicio REST `products/credit-cards/block` de OCC y retornar el resultado normalizado.

---

## Contexto de Negocio

OCC expone el bloqueo de TC a través del servicio REST `POST /products/credit-cards/block`, publicado en Datapower DMZ en el puerto 4860. El servicio permite **bloquear de manera definitiva una tarjeta de crédito que tiene un bloqueo preventivo**. Al igual que el servicio `UpdateCustomerData`, requiere autenticación OAuth 2.0 con `grant_type=client_credentials`. El endpoint de token es el mismo que el usado en la HU de actualización de datos OCC.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/occ/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`.
- **CA-02:** Antes de invocar el servicio de negocio, el ADP obtiene un token OAuth 2.0 mediante `POST /token` con `grant_type=client_credentials`, `client_id` y `client_secret` (variables de ambiente). El token tiene vigencia de 7200 segundos y puede cachearse en memoria hasta su expiración.
- **CA-03:** El ADP invoca `POST /products/credit-cards/block` con el header `Authorization: Bearer <token>` y el body construido según las Reglas de Integración.
- **CA-04:** Si OCC retorna `200` con `RtaCod: "00"` → operación exitosa; el ADP retorna la respuesta normalizada al ORQ.
- **CA-05:** Si OCC retorna `206` → error de negocio; el ADP mapea a `422` al ORQ.
- **CA-06:** Si OCC retorna `401` → token expirado o inválido; el ADP renueva el token y reintenta una vez. Si falla de nuevo → retorna `502` al ORQ.
- **CA-07:** Si OCC retorna `408` (timeout del servicio bancario) → el ADP mapea a `504` al ORQ.
- **CA-08:** Si OCC retorna `500` → el ADP mapea a `502` al ORQ.
- **CA-09:** Los números de tarjeta circulan completos en el flujo funcional (entre ORQ, ADP y servicio bancario). El enmascaramiento se aplica únicamente en logs (Elastic): últimos 4 dígitos visibles (ejemplo: `****5678`).
- **CA-10:** Circuit Breaker activo en el consumo del servicio OCC.
- **CA-11:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-12:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

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

#### Body del request de token

| Campo | Descripción |
|-------|-------------|
| `grant_type` | `client_credentials` (fijo) |
| `client_id` | Variable de ambiente |
| `client_secret` | Variable de ambiente — distinto por ambiente |

#### Response de token

| Campo | Descripción |
|-------|-------------|
| `token_type` | `Bearer` |
| `access_token` | Token de acceso |
| `expires_in` | `7200` segundos |

El token puede cachearse hasta 30 segundos antes de su expiración (`expires_in - 30`).

---

### Paso 2 — Servicio de bloqueo TC

| Campo               | Valor                                                    |
|---------------------|----------------------------------------------------------|
| Tipo                | REST                                                     |
| Método              | POST                                                     |
| Path                | `/products/credit-cards/block`                           |
| Middleware          | Datapower DMZ OCC                                        |

#### Endpoints servicio

| Ambiente | URL |
|----------|-----|
| DES      | `https://boc201.des.app.bancodeoccidente.net:4860/products/credit-cards/block` |
| CAL (QA) | `https://boc201.tesdmz.app.bancodeoccidente.net:4860/products/credit-cards/block` |
| PROD     | `https://boc201.prddmz.app.bancodeoccidente.net:4860/products/credit-cards/block` |

#### Headers del request a OCC

| Header | Tipo | Descripción | Obligatorio |
|--------|------|-------------|-------------|
| `Authorization` | String | `Bearer <access_token>` obtenido en paso 1 | SI |
| `Content-Type` | String | `application/json` | SI |

#### Body del request a OCC

```json
{
  "AplCod": 218,
  "TrmnalId": "OFICINAS-AKS-01",
  "PtciondId": "20260915103000001",
  "Usrio": "asesor@banco.com",
  "PtcionFecha": "2026-09-15",
  "BancoCod": 823,
  "TrjtaNro": "5406250250436417",
  "BloqueoCod": "BL01",
  "FuncCod": "",
  "MonedaCodigo": "COP",
  "BloqueoMtvoCod": "",
  "AplDest": "230",
  "ClienteNombre": "Juan Pérez",
  "AmprdoNombre": ""
}
```

| Campo | Tipo | Descripción | Obligatorio |
|-------|------|-------------|-------------|
| `AplCod` | Integer | Código de aplicación (variable de ambiente) | SI |
| `TrmnalId` | String | ID del terminal AKS | SI |
| `PtciondId` | String | ID único de la petición | SI |
| `Usrio` | String | Usuario ejecutor (del JWT) | SI |
| `PtcionFecha` | String (date) | Fecha de la petición | SI |
| `BancoCod` | Integer | Código del banco OCC (variable de ambiente) | SI |
| `TrjtaNro` | String | Número completo de la tarjeta de crédito | SI |
| `BloqueoCod` | String | Código de bloqueo / causal (del canal Oficinas) | SI |
| `FuncCod` | String | Código de función First Data | No |
| `MonedaCodigo` | String | Código de moneda (valor fijo: `COP`) | SI |
| `BloqueoMtvoCod` | String | Código motivo bloqueo | No |
| `AplDest` | String | Código de oficina | SI |
| `ClienteNombre` | String | Nombre del cliente | SI |
| `AmprdoNombre` | String | Nombre del amparado (vacío si no aplica) | No |

---

## Outputs

### Response OCC exitoso (HTTP 200)

```json
{
  "PtcionId": "20260915103000001",
  "RtaCod": "00",
  "RtaMnsje": "Transaccion Exitosa"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `PtcionId` | String | ID de petición correlacionado con el request |
| `RtaCod` | String | `"00"` = exitoso |
| `RtaMnsje` | String | Descripción del resultado |

### Modelo normalizado de salida al ORQ

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `numeroTarjeta` | String | Número enmascarado |
| `estadoActual` | String | `BLOQUEADA` |
| `causal` | String | Causal del bloqueo (BL01/BL02/BL03) |
| `fechaBloqueo` | String | Timestamp de la operación |
| `consecutivoOCC` | String | `PtcionId` retornado por OCC |

### Mapeo de errores OCC → estándar

| Código OCC | Código HTTP al ORQ | StatusDesc |
|------------|-------------------|------------|
| `200` / `RtaCod=00` | `200` | Bloqueo exitoso |
| `206`      | `422`             | "Error de negocio OCC — tarjeta no puede ser bloqueada" |
| `401`      | `502`             | "Token OAuth expirado o inválido" (después de reintento) |
| `408`      | `504`             | "Timeout del servicio OCC" |
| `500`      | `502`             | "Error interno en OCC" |

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `BLOQUEO_TC` | `BOCC` | `POST /products/credit-cards/block` — REST OAuth 2.0, Datapower DMZ OCC |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo | Valor fijo | Descripción |
|-------|------------|-------------|
| `MonedaCodigo` | `COP` | Moneda fija para operaciones en Colombia |
| `AplCod` | Variable de ambiente | Código de aplicación asignado por OCC |
| `BancoCod` | Variable de ambiente | Código de banco OCC |
| `grant_type` | `client_credentials` | Tipo de grant OAuth 2.0 |

### Mapeo de campos

| Campo obj_operacion | Campo OCC | Notas |
|---------------------|-----------|-------|
| `numeroTarjeta` | `TrjtaNro` | Número completo de la TC — no enmascarado en el payload funcional |
| `causal` | `BloqueoCod` | Causal del canal Oficinas → código OCC (ver tabla de causales) |
| (del JWT) | `Usrio` | Usuario del asesor |
| (generado por ADP) | `PtciondId` | ID único de petición |
| (generado por ADP) | `PtcionFecha` | Fecha actual |
| (del contexto AKS) | `TrmnalId` | ID de terminal |
| (de la sesión) | `AplDest` | Código de oficina |

### Tabla de causales

| Causal Canal Oficinas | Descripción | `BloqueoCod` OCC |
|-----------------------|-------------|------------------|
| `BL01` | Robo | `BL01` (confirmar código OCC con banco) |
| `BL02` | Pérdida | `BL02` (confirmar código OCC con banco) |
| `BL03` | Fraude | `BL03` (confirmar código OCC con banco) |

> Pendiente: Confirmar con OCC los valores exactos de `BloqueoCod` y `FuncCod` para cada causal, y el valor de `BloqueoMtvoCod` si aplica.

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** El ADP obtiene el token OAuth 2.0 antes de cada llamada al servicio de negocio. El token puede cachearse con TTL de `expires_in - 30` segundos.
- **RO-03:** Si el servicio de negocio retorna `401`, el ADP invalida el token cacheado, lo renueva y reintenta la operación una vez.
- **RO-04:** Los números de tarjeta circulan completos en el flujo funcional (entre ORQ, ADP y servicio bancario). El enmascaramiento se aplica **únicamente en logs** (Elastic): últimos 4 dígitos visibles (ejemplo: `****5678`). Nunca ofuscar el número real en el payload funcional.
- **RO-05:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`). Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU.
- **RO-06:** Las credenciales OAuth (`client_id`, `client_secret`) se configuran como variables de ambiente — nunca hardcodeadas.
- **RO-07:** La URL base del token y del servicio son variables de ambiente independientes. Nunca se hardcodean en el código.
- **RO-08:** `PtciondId` debe ser único por petición.

---

## Caminos Alternativos y Excepciones

| ID | Condición | Comportamiento |
|---|---|---|
| ALT-00 | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. |
| ALT-01 | Error al obtener token OAuth 2.0 | ADP retorna `502` al ORQ — no puede autenticarse con OCC |
| ALT-02 | OCC retorna 401 en servicio de negocio | ADP renueva token y reintenta una vez; si falla → `502` |
| ALT-03 | OCC retorna 206 (error negocio) | ADP retorna `422` al ORQ |
| ALT-04 | OCC retorna 408 (timeout bancario) | ADP retorna `504` al ORQ |
| ALT-05 | Timeout de conectividad ADP → OCC | Circuit Breaker abre → ADP retorna `504` |

---

## Tecnología a Usar

| Componente      | Tecnología   | Versión | Nota |
|-----------------|--------------|---------|------|
| Lenguaje        | Java         | 21      | |
| Framework       | Spring Boot  | 3.5.13  | |
| Cliente REST    | Retrofit     | 2.x     | Para endpoint de token y servicio de bloqueo TC |
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
| 1 | ¿Cuáles son los valores exactos de `BloqueoCod` y `FuncCod` para cada causal (Robo/Pérdida/Fraude)? | Define el mapeo de causales |
| 2 | ¿El `client_id` y `client_secret` para el servicio de bloqueo TC son los mismos que para `UpdateCustomerData` o distintos? | Define la configuración de credenciales OAuth |
| 3 | ¿El `BancoCod` es el mismo para todas las operaciones OCC (`823`) o varía? | Define el valor de la constante |
| 4 | ¿Hay conectividad confirmada desde pods AKS hacia Datapower DMZ OCC (puerto 4860)? | Bloquea pruebas en PT |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador OCC — Bloqueo TC
  Background:
    Given el adaptador OCC está configurado con credenciales OAuth 2.0 válidas
    And hay conectividad con Datapower DMZ de OCC (puerto 4860)

  Scenario: Bloqueo exitoso
    Given el adaptador recibe tipoDocumento "CC", numeroDocumento "12345678", numeroTarjeta completo y causal "BL01"
    When el ADP obtiene el token OAuth y luego invoca POST /products/credit-cards/block
    Then OCC retorna HTTP 200 con RtaCod "00"
    And el adaptador retorna respuesta normalizada con estadoActual "BLOQUEADA"

  Scenario: Error de negocio — tarjeta no bloqueable
    Given el adaptador recibe un numeroTarjeta sin bloqueo preventivo previo
    When invoca el servicio REST
    Then OCC retorna HTTP 206
    And el adaptador retorna 422 al orquestador

  Scenario: Token expirado — renovación exitosa
    Given el token cacheado está expirado
    When el ADP intenta invocar el servicio y recibe 401
    Then el ADP renueva el token OAuth y reintenta la operación
    And si el segundo intento es exitoso retorna 200 al ORQ

  Scenario: Timeout
    Given el servicio OCC no responde en el tiempo configurado
    When el adaptador espera la respuesta
    Then retorna 504 al orquestador
    And registra el evento en Elastic

  Scenario: Numero de tarjeta enmascarado en logs
    Given el adaptador procesa una solicitud con numeroTarjeta "5406250250431234"
    Then en los logs de Elastic el numero aparece como "****1234"
    And en el payload funcional enviado a OCC el numero circula completo

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
| `X-Destination-Bank` | Confirma que el banco destino es `BOCC` |

### Nivel 2 — Selección y transformación en el ADP

El ADP NO reenvía los headers del ORQ directamente al banco. Para la combinación `BLOQUEO_TC + BOCC`, el ADP:
1. Obtiene el token OAuth 2.0 mediante el endpoint de token OCC.
2. Construye el header `Authorization: Bearer <token>` para el servicio de negocio.

### Nivel 3 — Headers enviados al banco

#### BLOQUEO_TC → POST /products/credit-cards/block (REST OAuth 2.0)

| Header | Origen | Valor |
|--------|--------|-------|
| `Authorization` | Obtenido del endpoint de token OCC | `Bearer <access_token>` |
| `Content-Type` | Fijo | `application/json` |

Los demás datos de contexto (`AplCod`, `TrmnalId`, `Usrio`, etc.) se envían en el body del request, no como headers HTTP.

---

## Definition of Ready

- [x] Servicio documentado: `POST /products/credit-cards/block` con OAuth 2.0
- [x] Endpoints DES/CAL/PROD confirmados (puerto 4860)
- [x] Flujo de token OAuth 2.0 documentado
- [x] Headers y body del request documentados
- [ ] Valores exactos de `BloqueoCod` y `FuncCod` para cada causal confirmados con OCC
- [ ] Credenciales OAuth para bloqueo TC confirmadas (¿mismas que UpdateCustomerData?)
- [ ] Conectividad desde AKS hacia Datapower DMZ OCC puerto 4860 confirmada
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Cliente Retrofit para `POST /products/credit-cards/block` implementado
- [ ] Flujo OAuth 2.0 implementado con caché de token (`expires_in - 30s`)
- [ ] Retry en caso de 401 (renovación de token + reintento una vez)
- [ ] Mapeo de causales Oficinas → `BloqueoCod` OCC implementado
- [ ] Número de tarjeta enmascarado en logs, completo en payload funcional
- [ ] Mapeo de errores OCC → HTTP estándar implementado
- [ ] Circuit Breaker activo
- [ ] Pruebas unitarias (cobertura ≥ 90%)
- [ ] Prueba de integración contra OCC en DES o CAL
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada
