# HU-202-ADP-AVV: Adaptador AV Villas — Bloqueo TC

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-202-ADP-AVV                                              |
| ID Servicio    | SFA-010                                                     |
| Épica          | Épica 2 — Mantenimiento Tarjeta Crédito (P2)                |
| Componente     | Adaptador AVV — Bloqueo TC                                  |
| Microservicio  | `ofic-actualizaciones-adp-bavv`                             |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P2)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | Pendiente                                                    |
| HU Padre       | HU-202-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-21                                                  |
| Última revisión | 2026-09-15 — contrato completo documentado desde YAML/SoapUI AVV (`PFBA_CanalOtros295.yaml`); todos los campos de request y response mapeados; constantes `tipoProducto=TC`, `indBloqueo=S` confirmadas; `causal` no tiene campo equivalente en el contrato AVV; `fechaFinal` pendiente confirmar si aplica para bloqueo definitivo TC |

---

## Historia de Usuario

**Como** microservicio `ofic-actualizaciones-adp-bavv`,
**quiero** recibir del orquestador (`ofic-actualizaciones-orq`) la solicitud de bloqueo de tarjeta de crédito de AV Villas,
**para** invocar el servicio REST `PFBA_CanalOtros295 / WRBA_CanalOtros_BloqTempMedios / FMBA_BloqTempMedios` de AVV con `tipoProducto=TC, indBloqueo=S` y retornar el resultado normalizado.

---

## Contexto de Negocio

AVV expone el bloqueo de medios (TD y TC) a través del servicio REST `PFBA_CanalOtros295 / WRBA_CanalOtros_BloqTempMedios`. El campo `tipoProducto` diferencia el tipo de producto (`TC` para tarjeta de crédito) y el campo `indBloqueo=S` indica bloqueo. El campo `fechaFinal` se usa en bloqueos temporales; para bloqueo TC definitivo se debe confirmar con AVV si se envía vacío o nulo.

El contrato del servicio proviene del archivo `PFBA_CanalOtros295.yaml` (Swagger 2.0) y del proyecto SoapUI entregados por AVV.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/avv/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los campos requeridos por el servicio bancario correspondiente (ver sección Gestión de Headers).
- **CA-02:** El adaptador invoca `POST /PFBA_CanalOtros295/WRBA_CanalOtros_BloqTempMedios` en AVV con el body construido según las Reglas de Integración.
- **CA-03:** Los campos `tipoProducto=TC` e `indBloqueo=S` se envían como constantes en el request.
- **CA-04:** Si AVV retorna `200` con `codRespuesta` exitoso → el ADP retorna la respuesta normalizada al ORQ.
- **CA-05:** Mapea códigos de error del banco al código HTTP estándar.
- **CA-06:** Circuit Breaker activo en el consumo del servicio AVV.
- **CA-07:** Registra en Elastic ante error de conectividad o servicio.
- **CA-08:** Los números de tarjeta circulan completos en el flujo funcional (entre ORQ, ADP y servicio bancario). El enmascaramiento se aplica únicamente en logs (Elastic): últimos 4 dígitos visibles (ejemplo: `****5678`). En el campo `nroMedioManejo` se envía el número completo.
- **CA-09:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-10:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

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

## Servicio de AVV a Invocar

| Campo               | Valor                                                                       |
|---------------------|-----------------------------------------------------------------------------|
| Tipo                | REST                                                                        |
| API                 | `PFBA_CanalOtros295`                                                        |
| Recurso             | `WRBA_CanalOtros_BloqTempMedios`                                            |
| Operación           | `FMBA_BloqTempMedios`                                                       |
| Método              | POST                                                                        |
| Content-Type        | `application/json`                                                          |
| Middleware          | Datapower Interno → ESB AVV                                                 |

### Endpoints

| Ambiente | URL |
|----------|-----|
| DEV      | `https://10.10.10.88:9444/PFBA_CanalOtros295/WRBA_CanalOtros_BloqTempMedios` |
| QA       | `https://10.10.9.200:543/PFBA_CanalOtros295/WRBA_CanalOtros_BloqTempMedios` |
| PRD      | `https://10.10.21.10:543/PFBA_CanalOtros295/WRBA_CanalOtros_BloqTempMedios` |

> **Nota:** El endpoint DEV alternativo `10.10.10.201:543` fue documentado anteriormente — usar `10.10.10.88:9444` según proyecto SoapUI entregado por AVV.

---

## Contrato del Servicio

### Request body (`oe_BloquTempMedios`)

```json
{
  "TipoCanal": "OF",
  "identificacionDispositivo": "10.10.111.31",
  "fechaTransaccion": "2026-09-15T10:30:00.000",
  "nroSecuencia": 152030,
  "tipoDocumento": "CC",
  "nroDocumento": 80080106,
  "indBloqueo": "S",
  "tipoProducto": "TC",
  "nroMedioManejo": 6013678000024336,
  "fechaFinal": null
}
```

| Campo | Tipo | Descripción | Obligatorio |
|-------|------|-------------|-------------|
| `TipoCanal` | String | Canal de origen. Para Oficinas confirmar valor con AVV (ejemplo SoapUI usa `"MB"` para Mobile) | SI |
| `identificacionDispositivo` | String | IP del dispositivo / asesor | SI |
| `fechaTransaccion` | String | Timestamp de la transacción en formato ISO 8601 con milisegundos (`yyyy-MM-dd'T'HH:mm:ss.SSS`) | SI |
| `nroSecuencia` | Integer | Número secuencial de la transacción (generado por ADP) | SI |
| `tipoDocumento` | String | Tipo de documento del cliente (ejemplo: `CC`, `CE`, `TI`) | SI |
| `nroDocumento` | Integer | Número de documento del cliente (valor numérico entero) | SI |
| `indBloqueo` | String | Indicador de bloqueo: `S` = bloquear, `N` = desbloquear | SI |
| `tipoProducto` | String | Tipo de producto: `TC` para tarjeta de crédito, `D` para débito | SI |
| `nroMedioManejo` | Integer (Long) | Número completo de la tarjeta (16 dígitos) como valor numérico entero. Usar `Long` en Java | SI |
| `fechaFinal` | String | Fecha final del bloqueo en formato ISO 8601. Para bloqueo TC definitivo confirmar con AVV si se envía `null` o no aplica | SI (a confirmar) |

### Response body (`os_BloquTempMedios`)

```json
{
  "canal": "OF",
  "identificacionDispositivo": "10.10.111.31",
  "fechaTransaccion": "2026-09-15T10:30:00.000",
  "nroSecuencia": 152030,
  "nroAutorizacion": 9876543,
  "codRespuesta": 0,
  "mensajeRespuesta": "Transaccion exitosa"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `canal` | String | Canal de la respuesta |
| `identificacionDispositivo` | String | IP del dispositivo |
| `fechaTransaccion` | String | Timestamp de la transacción |
| `nroSecuencia` | Integer | Número de secuencia de la transacción |
| `nroAutorizacion` | Integer | Número de autorización de la operación |
| `codRespuesta` | Integer | Código de respuesta del banco (`0` = exitoso; valores distintos de 0 = error) |
| `mensajeRespuesta` | String | Mensaje descriptivo del resultado |

---

## Outputs

### Modelo normalizado de salida al ORQ

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `numeroTarjeta` | String | Número enmascarado (últimos 4 dígitos visibles) |
| `estadoActual` | String | `BLOQUEADA` |
| `nroAutorizacion` | String | `nroAutorizacion` retornado por AVV |
| `mensajeRespuesta` | String | `mensajeRespuesta` retornado por AVV |

### Mapeo de errores AVV → estándar

| Condición AVV | Código HTTP al ORQ | Descripción |
|---|---|---|
| `codRespuesta = 0` | `200` | Bloqueo exitoso |
| `codRespuesta != 0` (error negocio) | `422` | Error de negocio AVV |
| HTTP 500 | `502` | Error interno en AVV |
| Timeout conectividad | `504` | Timeout del servicio AVV |

> **Nota:** Confirmar con AVV el catálogo de `codRespuesta` para definir el mapeo exacto de errores de negocio.

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `BLOQUEO_TC` | `BAVV` | `PFBA_CanalOtros295 / WRBA_CanalOtros_BloqTempMedios / FMBA_BloqTempMedios` — REST POST — Datapower → ESB |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo AVV | Valor fijo | Descripción |
|-----------|-----------|-------------|
| `tipoProducto` | `TC` | Tipo de producto: Tarjeta Crédito |
| `indBloqueo` | `S` | Indicador de bloqueo activo |
| `TipoCanal` | Variable de ambiente (confirmar valor con AVV para canal Oficinas) | Canal de origen |

### Mapeo de campos

| Campo obj_operacion / contexto | Campo AVV | Tipo AVV | Notas |
|---|---|---|---|
| `obj_operacion.tipoDocumento` | `tipoDocumento` | String | Tipo de documento del cliente |
| `obj_operacion.numeroDocumento` | `nroDocumento` | Integer | Número de documento como entero |
| `obj_operacion.numeroTarjeta` | `nroMedioManejo` | Integer (Long) | Número completo de tarjeta como Long — no enmascarado en el payload funcional |
| `obj_operacion.causal` | — | — | No tiene campo equivalente en el contrato AVV — no se envía al banco |
| Generado por ADP | `nroSecuencia` | Integer | Número secuencial único por petición |
| Fecha/hora actual con ms | `fechaTransaccion` | String | ISO 8601 con milisegundos (`yyyy-MM-dd'T'HH:mm:ss.SSS`) |
| IP del pod AKS | `identificacionDispositivo` | String | IP de origen del asesor/pod |
| PENDIENTE confirmar con AVV | `fechaFinal` | String | Para bloqueo TC definitivo: confirmar si se envía null, vacío o no aplica |

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** El campo `causal` de `obj_operacion` no tiene equivalente en el contrato AVV — no se envía al banco.
- **RO-03:** El campo `nroMedioManejo` se envía como valor numérico entero (Long en Java) — no como String. Usar `Long.parseLong(numeroTarjeta.replaceAll("[^0-9]", ""))` para convertir desde el número enmascarado recibido del ORQ (el ORQ enviará el número completo, el enmascaramiento es solo de logs).
- **RO-04:** El Circuit Breaker se activa ante fallos o timeouts del servicio AVV.
- **RO-05:** Los números de tarjeta circulan completos en el flujo funcional (entre ORQ, ADP y servicio bancario). El enmascaramiento se aplica **únicamente en logs** (Elastic): últimos 4 dígitos visibles (ejemplo: `****5678`). Nunca ofuscar el número real en el payload funcional.
- **RO-06:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`). Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU.
- **RO-07:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.

---

## Caminos Alternativos y Excepciones

| ID | Condición | Comportamiento |
|---|---|---|
| ALT-00 | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. |
| ALT-01 | AVV retorna `codRespuesta != 0` (error de negocio) | ADP retorna `422` al ORQ con `mensajeRespuesta` del banco |
| ALT-02 | AVV retorna HTTP 500 | ADP retorna `502` al ORQ y registra en Elastic |
| ALT-03 | Timeout de conectividad ADP → AVV | Circuit Breaker abre → ADP retorna `504` |

---

## Tecnología a Usar

| Componente      | Tecnología   | Versión | Nota                                  |
|-----------------|--------------|---------|---------------------------------------|
| Lenguaje        | Java         | 17      | Arquetipo base ACE                    |
| Framework       | Spring Boot  | 3.x     |                                       |
| Cliente REST    | Retrofit 2.11.0 + OkHttp 4.12.0 | 2.11.0 / 4.12.0 | Para servicio AVV |
| Circuit Breaker | Resilience4j | —       | Activo en todos los consumos externos |
| Logs            | Elastic      | —       |                                       |
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
| 1 | ¿Cuál es el valor de `TipoCanal` para el canal Oficinas en AVV? (SoapUI usa `"MB"` para Mobile) | Define constante de mapeo |
| 2 | ¿Se envía `fechaFinal` para bloqueo TC definitivo? ¿`null`, vacío, o fecha lejana? | Define el campo en el request |
| 3 | ¿Cuál es el catálogo de `codRespuesta` (errores de negocio AVV)? | Define el mapeo de errores `422` |
| 4 | ¿Hay conectividad confirmada desde pods AKS hacia el ESB de AVV? | Bloquea pruebas en PT |

---

## Gestión de Headers

### Nivel 1 — Headers recibidos del ORQ

El ADP recibe del ORQ los siguientes headers de contexto, propagados sin modificación:

| Header | Descripción |
|--------|-------------|
| `Authorization` | Bearer JWT del asesor |
| `X-Trace-Id` | ID de traza para correlación de logs |
| `X-Origin-Bank` | Banco de origen de la operación |
| `X-Destination-Bank` | Confirma que el banco destino es `BAVV` |

### Nivel 2 — Selección y transformación en el ADP

El ADP NO reenvía los headers del ORQ directamente al banco. El servicio AVV es REST y la información de contexto se envía en el body JSON (campos `TipoCanal`, `identificacionDispositivo`, `nroSecuencia`).

### Nivel 3 — Headers HTTP enviados al banco

#### BLOQUEO_TC → PFBA_CanalOtros295 / FMBA_BloqTempMedios (REST POST)

| Header HTTP | Valor |
|-------------|-------|
| `Content-Type` | `application/json` |
| `Accept` | `application/json` |

> La información de contexto del canal y dispositivo se envía dentro del body JSON, no como headers HTTP adicionales.

---

## Definition of Ready

- [x] AVV confirmó el servicio: `PFBA_CanalOtros295 / WRBA_CanalOtros_BloqTempMedios / FMBA_BloqTempMedios`
- [x] Contrato completo del servicio documentado (YAML + SoapUI de AVV)
- [x] Todos los campos de request y response documentados
- [x] Constantes `tipoProducto=TC` e `indBloqueo=S` confirmadas
- [x] Mapeo de campos `tipoDocumento`, `nroDocumento`, `nroMedioManejo` documentados
- [ ] Valor de `TipoCanal` para canal Oficinas confirmado con AVV
- [ ] Comportamiento de `fechaFinal` para bloqueo definitivo TC confirmado con AVV
- [ ] Credenciales disponibles en PT
- [ ] Conectividad de red desde AKS hacia ESB AVV confirmada
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Cliente Retrofit para `PFBA_CanalOtros295` implementado
- [ ] Body construido con constantes `tipoProducto=TC`, `indBloqueo=S` y campos mapeados desde `obj_operacion`
- [ ] `nroMedioManejo` enviado como Long (valor numérico entero)
- [ ] `nroDocumento` enviado como Integer
- [ ] `fechaTransaccion` en formato ISO 8601 con milisegundos
- [ ] `nroSecuencia` generado por ADP (secuencial único)
- [ ] Número de tarjeta enmascarado en logs (últimos 4 dígitos), completo en payload funcional
- [ ] Mapeo de errores `codRespuesta` → HTTP estándar implementado
- [ ] Circuit Breaker activo
- [ ] Pruebas unitarias (cobertura >= 90%)
- [ ] Prueba de integración contra AVV en QA
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada
