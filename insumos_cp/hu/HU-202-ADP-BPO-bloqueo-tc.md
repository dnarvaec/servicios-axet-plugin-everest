# HU-202-ADP-BPO: Adaptador Banco Popular — Bloqueo TC

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-202-ADP-BPO                                             |
| ID Servicio    | SFA-010                                                     |
| Épica          | Épica 2 — Mantenimiento Tarjeta Crédito (P2)                |
| Componente     | Adaptador BPO — Bloqueo TC                                  |
| Microservicio  | `ofic-actualizaciones-adp-bpop`                             |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P2)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | Pendiente                                                   |
| HU Padre       | HU-202-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-21                                                  |
| Última revisión | 2026-09-03 — campo operacion agregado; identificación de servicio por operacion+banco documentada; masking solo en logs; gestión de headers documentada; cola SQS FIFO de auditoría documentada; OperacionEnum definido localmente en cada microservicio con valores canónicos de HU-101-ORQ; operación no soportada: excepción + 400 documentada |

---

## Historia de Usuario

**Como** microservicio `ofic-actualizaciones-adp-bpop`,  
**quiero** recibir del orquestador (`ofic-actualizaciones-orq`) la solicitud de bloqueo de tarjeta de crédito de Banco Popular,  
**para** invocar el servicio `SrvCodeCardBlock / modCodeCardBlock` de BPO (sistema FirstData) y retornar el resultado normalizado.

---

## Contexto de Negocio

BPO expone el bloqueo de TC a través de un sistema interno alternativo (no Sofia), con backend FirstData. El servicio `SrvCodeCardBlock` / `modCodeCardBlock` permite bloquear (`AcctType=B`) y desbloquear (`AcctType=U`) tarjetas de crédito.

> **Nota:** BPO confirmó explícitamente que el servicio de tarjeta crédito **no opera a través de Sofia**, sino a través de un sistema interno alternativo.  
> — *Ricardo Amézquita (BPO), Reunión Alineación Funcional TX No Monetarias, 6 de agosto de 2026*

> **[!] Pendiente contrato:** El contrato completo del servicio (campos de request/response) debe confirmarse con el punto de contacto técnico en BPO (Neton).

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/boc/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente, los cuales varían según banco y operación (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** El adaptador recibe el contenido de `obj_operacion` proveniente del ORQ e invoca `SrvCodeCardBlock / modCodeCardBlock` de BPO.
- **CA-03:** El campo `AcctType=B` se envía como constante para bloqueo de la tarjeta.
- **CA-04:** Mapea la causal del canal Oficinas (`BL01`, `BL02`, `BL03`) al campo correspondiente en el request de BPO (PENDIENTE CONFIRMAR con BPO).
- **CA-05:** Si BPO confirma el bloqueo exitoso, transforma la respuesta al modelo normalizado.
- **CA-06:** Si BPO retorna error de tarjeta no encontrada, mapea a `404`.
- **CA-07:** Si BPO no responde a tiempo, mapea a `504`.
- **CA-08:** Circuit Breaker activo en el consumo del servicio BPO.
- **CA-09:** Credenciales en variables de ambiente — nunca hardcodeadas.
- **CA-10:** Registra en Elastic ante error de conectividad o servicio.
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

## Servicio de BPO a Invocar

| Campo      | Valor |
|------------|-------|
| Tipo       | SOAP (sistema interno FirstData — no Sofia) |
| Servicio   | `SrvCodeCardBlock` |
| Operación  | `modCodeCardBlock` |
| Backend    | FirstData |

### Endpoints

| Ambiente | URL |
|----------|-----|
| DEV      | `https://10.213.81.69:55681/cardsManagement/v1/BlockUnblockTC/CreditCard` |
| QA       | `https://qa.dp.ext.servext.bpop:55681/cardsManagement/v1/BlockUnblockTC/CreditCard` |
| PRD      | `10.213.133.10:55544/sofia/tarjetaExpress` |

### Campo clave

| Campo      | Valor | Descripción                 |
|------------|-------|-----------------------------|
| `AcctType` | `B`   | Block — bloqueo de tarjeta  |
| `AcctType` | `U`   | Unblock — desbloqueo        |

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `BLOQUEO_TC` | `BPOP` | `SrvCodeCardBlock / modCodeCardBlock` — SOAP (sistema interno FirstData) |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo      | Valor fijo | Descripción                                                |
|------------|-----------|-------------------------------------------------------------|
| `AcctType` | `B`       | Bloqueo de tarjeta (constante fija para esta operación)     |

### Mapeo de campos

| Campo obj_operacion | Campo BPO             | Notas                                                            |
|---------------------|-----------------------|------------------------------------------------------------------|
| `numeroTarjeta`     | PENDIENTE POR DEFINIR | Confirmar si recibe número enmascarado o token interno           |
| `tipoDocumento`     | PENDIENTE POR DEFINIR | Confirmar campo y codificación en contrato del servicio          |
| `numeroDocumento`   | PENDIENTE POR DEFINIR | Confirmar campo en contrato del servicio                         |
| `causal`            | PENDIENTE POR DEFINIR | Confirmar si la causal (BL01/BL02/BL03) se mapea a un campo del request |

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** El campo `AcctType=B` se envía como constante en toda invocación de bloqueo TC.
- **RO-03:** El contrato completo del request/response queda PENDIENTE POR CONFIRMAR con BPO (Neton).
- **RO-04:** El Circuit Breaker se activa ante fallos o timeouts del servicio BPO.
- **RO-05:** Los números de tarjeta circulan completos en el flujo funcional (entre ORQ, ADP y servicio bancario). El enmascaramiento se aplica **únicamente en logs** (Elastic): últimos 4 dígitos visibles (ejemplo: `****5678`). Nunca ofuscar el número real en el payload funcional.
- **RO-06:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`). Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU.
- **RO-07:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.

---

## Outputs

> **Nota:** El ADP retorna la respuesta del banco directamente — no hay transformación a un modelo normalizado propio. Los campos listados son referenciales según el contrato del banco.

### Modelo normalizado de salida

| Campo           | Tipo   | Descripción                          |
|-----------------|--------|--------------------------------------|
| `numeroTarjeta` | String | Número enmascarado                   |
| `estadoActual`  | String | `BLOQUEADA`                          |
| `causal`        | String | Causal del bloqueo (BL01/BL02/BL03)  |
| `fechaBloqueo`  | String | Timestamp de la operación            |

### Mapeo de errores BPO → estándar

| Error BPO              | Código HTTP | StatusDesc                           |
|------------------------|-------------|--------------------------------------|
| Tarjeta no encontrada  | `404`       | "Tarjeta no encontrada en BPO"       |
| Timeout                | `504`       | "Timeout del servicio BPO"           |
| Error de conectividad  | `502`       | "Error de conectividad con BPO"      |
| Error de negocio BPO   | `422`       | "Error de negocio BPO"               |

---

## Caminos Alternativos y Excepciones

| ID      | Condición                                     | Comportamiento                                                                                                                                       |
|---------|-----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| ALT-00  | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. Verificación defensiva: el ORQ no debería enrutar operaciones no soportadas a este ADP. |

---

## Tecnología a Usar

| Componente      | Tecnología        | Versión | Nota                                          |
|-----------------|-------------------|---------|-----------------------------------------------|
| Lenguaje        | Java              | 17      | Arquetipo base ACE                            |
| Framework       | Spring Boot       | 3.x     |                                               |
| Cliente REST    | Retrofit 2.11.0 + OkHttp 4.12.0 | 2.11.0 / 4.12.0 | Confirmar protocolo REST exacto con BPO |
| Cliente SOAP    | Spring-WS 3.x + JAXB 4.0.2 | 3.x / 4.0.2 | Confirmar protocolo SOAP exacto con BPO |
| Circuit Breaker | Resilience4j      | —       | Activo en todos los consumos externos         |
| Logs            | Elastic           | —       |                                               |
| Mensajería     | AWS SQS FIFO | —       | Cola de auditoría y observabilidad — `avc-everest-pt-logs.fifo` |


---

## Dependencias

| HU         | Relación |
|------------|----------|
| HU-202-ORQ | Padre — `ofic-actualizaciones-orq` |

---

## Preguntas Abiertas

| # | Pregunta | Impacto |
|---|----------|---------|
| 1 | ¿Cuál es el contrato completo del servicio `SrvCodeCardBlock` (campos de request/response)? | Bloquea la implementación |
| 2 | ¿El campo `causal` (BL01/BL02/BL03) tiene correspondencia en el request del servicio? | Define el mapeo de causales |
| 3 | ¿La tarjeta se identifica por número enmascarado o token interno? | Define el manejo de `numeroTarjeta` |
| 4 | ¿Requiere prerequisito de consulta de tarjeta (similar a TD con TDCTS)? | Define si hay pasos previos al bloqueo |
| 5 | ¿Hay conectividad confirmada desde pods AKS hacia `qa.dp.ext.servext.bpop:55681`? | Bloquea pruebas en PT |

---

## Gestión de Headers

### Nivel 1 — Headers recibidos del ORQ

El ADP recibe del ORQ los siguientes headers de contexto, propagados sin modificación:

| Header | Descripción |
|--------|-------------|
| `Authorization` | Bearer JWT del asesor |
| `X-Trace-Id` | ID de traza para correlación de logs |
| `X-Origin-Bank` | Banco de origen de la operación |
| `X-Destination-Bank` | Confirma que el banco destino es `BPOP` |

### Nivel 2 — Selección y transformación en el ADP

El ADP NO reenvía los headers del ORQ directamente al banco. Para la combinación `BLOQUEO_TC + BPOP`, el ADP determina qué headers requiere el servicio bancario específico y construye únicamente esos.

### Nivel 3 — Headers enviados al banco

#### BLOQUEO_TC → SrvCodeCardBlock / modCodeCardBlock (SOAP)

Los headers requeridos por este servicio bancario se obtienen de la documentación técnica del banco (contrato del servicio). El ADP reenvía al banco únicamente los headers definidos en ese contrato — los de valor fijo se configuran como variables de ambiente y los de contexto se propagan desde el request entrante. El ADP no valida su presencia: si el llamador omite un header requerido, el banco retorna el error correspondiente.

---

## Definition of Ready


- [ ] Contrato completo del servicio `SrvCodeCardBlock` confirmado con BPO (Neton)
- [ ] Mapeo de campos documentado
- [ ] Conectividad desde AKS hacia endpoint BPO TC confirmada
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Contrato del servicio documentado y acordado
- [ ] Reglas de Integración completas
- [ ] Adaptador implementado y probado
- [ ] Pruebas de integración en PT aprobadas
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada — request y response encolados en cada invocación
