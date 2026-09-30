# HU-302-ADP-AVV: Adaptador AV Villas — Desbloqueo TD por PIN Errado

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-302-ADP-AVV                                              |
| ID Servicio    | SFA-009 (P3 — DB01)                                         |
| Épica          | Épica 4 — Mantenimiento Tarjeta Débito P3                   |
| Componente     | Adaptador AVV — Desbloqueo TD PIN Errado                    |
| Microservicio  | `ofic-actualizaciones-adp-bavv`                             |
| Sprint         | Por definir                                                 |
| Prioridad      | Media (P3)                                                  |
| Estimación     | Por estimar                                                 |
| Estado         | **Pendiente implementación**                                |
| HU Padre       | HU-302-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-21                                                  |
| Última revisión | 2026-09-03 — campo operacion agregado; identificación de servicio por operacion+banco documentada; masking solo en logs; gestión de headers documentada; cola SQS FIFO de auditoría documentada; OperacionEnum definido localmente en cada microservicio con valores canónicos de HU-101-ORQ; operación no soportada: excepción + 400 documentada |

---

## Historia de Usuario

**Como** adaptador AVV del microservicio `ofic-actualizaciones-adp-bavv`,  
**quiero** invocar el servicio `PFBA_CanalOtros295 / WRBA_CanalOtros_BloqTempMedios` de AV Villas con `indBloqueo: "N"`  
**para** desbloquear una tarjeta débito bloqueada por PIN errado, en respuesta a la solicitud recibida del orquestador `ofic-actualizaciones-orq`.

---

## Contexto de Negocio

AVV gestiona el desbloqueo temporal de tarjeta débito con el servicio `PFBA_CanalOtros295 / WRBA_CanalOtros_BloqTempMedios / FMBA_BloqTempMedios`. El mismo servicio gestiona bloqueo (`indBloqueo: "S"`) y desbloqueo (`indBloqueo: "N"`). Para el caso de desbloqueo por PIN errado, se envía `indBloqueo: "N"` con el número de tarjeta y el tipo de producto `"D"`.

**Middleware:** Datapower Interno → ESB AVV → ICBS (z/OS)  
**Protocolo:** REST POST  
**Contrato:** YAML documentado en `Transacciones/PFBA_CanalOtros295/PFBA_CanalOtros295.yaml`

> **Nota:** No existe un servicio dedicado para desbloqueo por PIN errado en AVV. La documentación de Everest indica que el bloqueo temporal y el desbloqueo se realizan con el mismo servicio `BloqTempMedios`. La distinción de "desbloqueo por PIN errado" se gestiona en la lógica de negocio: el frontend verifica que la tarjeta esté en bloqueo temporal por PIN antes de invocar este servicio.

---

## Inputs — Recibidos del Orquestador

El ADP recibe del orquestador: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. El ADP **no valida** los campos de `obj_operacion`.

| Campo | Tipo | Descripción | Obligatorio |
|---|---|---|---|
| `operacion` | `OperacionEnum` | Identificador de la operación. Junto con `X-Destination-Bank` determina el servicio bancario a invocar. Recibido como `OperacionEnum` desde el ORQ — no re-parsear el String. Ver definición completa en **HU-101-ORQ** | SI |
| `X-Origin-Bank` | String (header) | Banco de origen | SI |
| `X-Destination-Bank` | String (header) | Banco destino | SI |
| `obj_operacion` | Object | Campos funcionales | SI |

**Ejemplo:**
```json
{
  "operacion": "DESBLOQUEO_TD_PIN",
  "X-Origin-Bank": "...",
  "X-Destination-Bank": "BAVV",
  "obj_operacion": { "...": "..." }
}
```

> **Nota:** Los campos de `obj_operacion` son referenciales. El ADP recibe `obj_operacion` como tipo genérico (`Object`) — no valida sus campos internos ni lo implementa como clase Java campo a campo. La validación es responsabilidad del servicio bancario.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/avv/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente, los cuales varían según banco y operación (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** El adaptador invoca el servicio `WRBA_CanalOtros_BloqTempMedios` (PFBA_CanalOtros295) vía REST POST con `indBloqueo: "N"` y `tipoProducto: "D"`.
- **CA-03:** `TipoCanal` = `"OFI"` (fijo).
- **CA-04:** El ADP no valida los campos de `obj_operacion`.
- **CA-05:** `codRespuesta` = 0 → `200 OK`.
- **CA-06:** `codRespuesta` ≠ 0 → `422` con `mensajeRespuesta` del banco.
- **CA-07:** Timeout → `504`. Error → `502`.
- **CA-08:** Credenciales en variables de ambiente.
- **CA-09:** Circuit Breaker (Resilience4j) activo en el consumo del servicio AVV.
- **CA-10:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-11:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

---

## Caminos Alternativos y Excepciones

| ID | Condición | Comportamiento |
|---|---|---|
| ALT-00  | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. Verificación defensiva: el ORQ no debería enrutar operaciones no soportadas a este ADP. |

---

## Servicio AVV

### Endpoints

| Ambiente | URL |
|----------|-----|
| DEV      | `https://10.10.10.201:543/PFBA_CanalOtros295/WRBA_CanalOtros_BloqTempMedios` |
| QA       | `https://10.10.9.200:543/PFBA_CanalOtros295/WRBA_CanalOtros_BloqTempMedios` |
| PRD      | `https://10.10.21.10:543/PFBA_CanalOtros295/WRBA_CanalOtros_BloqTempMedios` |

**Método:** POST  
**Content-Type:** application/json

### Request AVV

| Campo                    | Tipo    | Fuente / Valor                                     | Obligatorio |
|--------------------------|---------|----------------------------------------------------|-------------|
| `TipoCanal`              | String  | `"OFI"` (fijo)                                     | NO          |
| `identificacionDispositivo` | String | IP del servidor/pod AKS (variable de ambiente)   | NO          |
| `fechaTransaccion`       | String  | Fecha actual                                       | NO          |
| `tipoDocumento`          | String  | Mapeado del orquestador                            | NO          |
| `nroDocumento`           | Integer | `numeroDocumento` del orquestador                  | NO          |
| `indBloqueo`             | String  | **`"N"`** (fijo para desbloqueo)                   | SI          |
| `tipoProducto`           | String  | **`"D"`** (fijo — tarjeta débito)                  | NO          |
| `nroMedioManejo`         | Integer | Número de tarjeta (de `obj_operacion`)             | NO          |
| `fechaFinal`             | String  | Vacío — no aplica para desbloqueo                  | NO          |

> Todos los campos del contrato YAML son opcionales en el esquema, pero operativamente `indBloqueo`, `tipoProducto` y `nroMedioManejo` son los campos funcionales clave.

### Respuesta AVV

| Campo              | Tipo    | Descripción                            |
|--------------------|---------|----------------------------------------|
| `codRespuesta`     | Integer | `0` = éxito; otro = error              |
| `mensajeRespuesta` | String  | Descripción del resultado              |
| `nroAutorizacion`  | Integer | Número de autorización                 |
| `nroSecuencia`     | Integer | Número de secuencia                    |

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `DESBLOQUEO_TD_PIN` | `BAVV` | `PFBA_CanalOtros295 / WRBA_CanalOtros_BloqTempMedios / FMBA_BloqTempMedios` (`indBloqueo=N`) |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo          | Valor fijo | Descripción                             |
|----------------|------------|-----------------------------------------|
| `indBloqueo`   | `N`        | Indica desbloqueo (no bloqueo)          |
| `tipoProducto` | `D`        | Tarjeta débito                          |
| `TipoCanal`    | `OFI`      | Canal Oficinas                          |

### Mapeo de campos

| Campo `obj_operacion`   | Campo banco (`BloqTempMedios`) | Notas                         |
|-------------------------|-------------------------------|-------------------------------|
| `numeroDocumento`       | `nroDocumento`                | Número de documento del cliente|
| Número de tarjeta       | `nroMedioManejo`              | De `obj_operacion`            |
| Tipo de documento       | `tipoDocumento`               | Mapeo de tipos si aplica      |

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** `indBloqueo` siempre se envía como `"N"` para esta transacción de desbloqueo.
- **RO-03:** `tipoProducto` siempre se envía como `"D"` (tarjeta débito).
- **RO-04:** La verificación previa del tipo de bloqueo (PIN errado) es responsabilidad del frontend/ORQ antes de invocar este adaptador.
- **RO-05:** Los números de tarjeta (TD) circulan completos en el flujo funcional. El enmascaramiento se aplica **únicamente en logs** (últimos 4 dígitos visibles).
- **RO-06:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **RO-07:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.

---

## Consideraciones No Funcionales

- **Circuit Breaker:** Resilience4j activo en el consumo del servicio AVV.
- **Credenciales:** En variables de ambiente — nunca en código.

---

## Mapeo de Respuesta → Orquestador

| Condición                        | HTTP al ORQ | Body                                                   |
|----------------------------------|-------------|--------------------------------------------------------|
| `codRespuesta` = `0`             | `200`       | `{ estadoActual: "ACTIVA", mensajeRespuesta: "..." }`  |
| `codRespuesta` ≠ `0`             | `422`       | `{ error: mensajeRespuesta }`                          |
| Timeout                          | `504`       | `{ error: "Timeout al comunicarse con AVV" }`          |
| Error de comunicación            | `502`       | `{ error: "Error en servicio AVV" }`                   |

---

## Dependencias

- **ORQ padre:** `ofic-actualizaciones-orq`

---

## Preguntas Abiertas

| # | Pregunta | Impacto |
|---|----------|---------|
| 1 | ¿El servicio `BloqTempMedios` cubre específicamente bloqueos por PIN errado o solo bloqueos voluntarios temporales? | Define si este servicio es el correcto para el caso de uso |
| 2 | ¿Se necesita verificar previamente que el tipo de bloqueo de la tarjeta es "PIN errado" antes de llamar al servicio? | Define si hay una consulta previa necesaria |

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

El ADP NO reenvía los headers del ORQ directamente al banco. Para la combinación `DESBLOQUEO_TD_PIN + BAVV`, el ADP determina qué headers requiere el servicio bancario específico y construye únicamente esos.

### Nivel 3 — Headers enviados al banco

#### DESBLOQUEO_TD_PIN → FMBA_BloqTempMedios / PFBA_CanalOtros295 (REST)

Los headers requeridos por este servicio bancario se obtienen de la documentación técnica del banco (contrato del servicio). El ADP reenvía al banco únicamente los headers definidos en ese contrato — los de valor fijo se configuran como variables de ambiente y los de contexto se propagan desde el request entrante. El ADP no valida su presencia: si el llamador omite un header requerido, el banco retorna el error correspondiente.

---

## Tecnología a Usar

| Componente  | Tecnología   | Versión | Nota                                                                            |
|-------------|--------------|---------|---------------------------------------------------------------------------------|
| Mensajería  | AWS SQS FIFO | —       | Cola de auditoría y observabilidad — `avc-everest-pt-logs.fifo` |


---

## Definition of Ready


- [ ] Confirmación con AVV que `BloqTempMedios` con `indBloqueo: "N"` cubre el caso de PIN errado
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Adaptador REST implementado
- [ ] Circuit Breaker (Resilience4j) configurado
- [ ] Pruebas unitarias (cobertura ≥ 90%) y de integración aprobadas
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada — request y response encolados en cada invocación (clave PinPad excluida del mensaje de auditoría donde aplique)
