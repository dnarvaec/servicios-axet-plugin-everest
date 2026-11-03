# HU-302-ADP-BDB: Adaptador Banco de Bogotá — Desbloqueo TD por PIN Errado

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-302-ADP-BDB                                              |
| ID Servicio    | SFA-009 (P3 — DB01)                                         |
| Épica          | Épica 4 — Mantenimiento Tarjeta Débito P3                   |
| Componente     | Adaptador BdB — Desbloqueo TD PIN Errado                    |
| Microservicio  | `ofic-actualizaciones-adp-bbog`                             |
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

**Como** adaptador BdB del microservicio `ofic-actualizaciones-adp-bbog`,  
**quiero** invocar `PUT /V1/product/debitcard/status-unlock` de la API `customer_debit_card_management` de Banco de Bogotá  
**para** desbloquear una tarjeta débito bloqueada por PIN errado, en respuesta a la solicitud recibida del orquestador `ofic-actualizaciones-orq`.

---

## Contexto de Negocio

BdB expone la operación de desbloqueo TD vía la API REST `customer_debit_card_management`, mismo API Gateway que se usa para el bloqueo definitivo (HU-201-ADP-BDB). El endpoint de desbloqueo es `PUT /V1/product/debitcard/status-unlock`.

**Middleware:** AWS API Gateway ECS (canales digitales)  
**Protocolo:** REST PUT  
**Expuesto:** Sí — dominio público AWS, autenticado por `x-api-key`.

> **SOAP como contingencia:** Existe la operación SOAP `AccountDebitCardStatusModify/modDebitCardPINStatus` vía AWS VPC Endpoint, pero no es accesible externamente. Se documenta solo como referencia técnica para contingencias dentro de la VPC BdB.

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
  "X-Destination-Bank": "BBOG",
  "obj_operacion": { "...": "..." }
}
```

> **Nota:** Los campos de `obj_operacion` son referenciales. El ADP recibe `obj_operacion` como tipo genérico (`Object`) — no valida sus campos internos ni lo implementa como clase Java campo a campo. La validación es responsabilidad del servicio bancario.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/bog/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente, los cuales varían según banco y operación (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** El adaptador invoca `PUT /V1/product/debitcard/status-unlock` con el `debitCardNumber` en el body.
- **CA-03:** Todos los headers requeridos se incluyen: `x-api-key`, `X-RqUID`, `X-Channel`, `X-IPAddr`, `X-Name`, `X-CustIdentNum`, `X-CustIdentType`, `X-NetworkOwner`, `X-TerminalId`.
- **CA-04:** `x-api-key` proviene de variables de ambiente — nunca en código.
- **CA-05:** `X-CustIdentNum` = `numeroDocumento` del orquestador; `X-CustIdentType` = tipo de documento.
- **CA-06:** `X-RqUID` se genera en el adaptador como UUID único por llamada.
- **CA-07:** El ADP no valida los campos de `obj_operacion`.
- **CA-08:** Respuesta HTTP 200 del banco → `200 OK` al orquestador.
- **CA-09:** Respuesta HTTP 408 del banco → `504` (timeout). Respuesta HTTP 409 business error → `422`.
- **CA-10:** Otras respuestas de error → `502`.
- **CA-11:** Circuit Breaker (Resilience4j) activo en el consumo del servicio BdB.
- **CA-12:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-13:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

---

## Caminos Alternativos y Excepciones

| ID | Condición | Comportamiento |
|---|---|---|
| ALT-00  | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. Verificación defensiva: el ORQ no debería enrutar operaciones no soportadas a este ADP. |

---

## Servicio BdB

### Endpoints

| Ambiente | URL |
|----------|-----|
| DEV      | No documentado |
| QA       | `https://api-clients.labdigitalbdbtvsqa.com/customer_debit_card_management/V1/product/debitcard/status-unlock` |
| PRD      | `https://alb-0.labdigitalbdbtvs.com:10929/customer_debit_card_management/V1/product/debitcard/status-unlock` |

**Método:** PUT  
**Content-Type:** application/json

### Headers requeridos

| Header            | Descripción                                         | Fuente              |
|-------------------|-----------------------------------------------------|---------------------|
| `x-api-key`       | API Key del canal Oficinas                          | Variable de ambiente |
| `X-RqUID`         | UUID único por transacción                          | Generado en adaptador |
| `X-Channel`       | Canal origen                                        | Variable de ambiente |
| `X-IPAddr`        | IP del servidor/pod AKS                             | Variable de ambiente |
| `X-Name`          | Nombre del canal                                    | Variable de ambiente |
| `X-CustIdentNum`  | Número de documento del cliente                     | Del orquestador      |
| `X-CustIdentType` | Tipo de documento del cliente                       | Del orquestador      |
| `X-NetworkOwner`  | Propietario de la red                               | Variable de ambiente |
| `X-TerminalId`    | Identificador del terminal                          | Variable de ambiente |

### Request body

```json
{
  "debitCardNumber": "6013679045160937"
}
```

> El número de tarjeta se extrae de `obj_operacion` — se envía el número real (no enmascarado) hacia el servicio BdB.

### Mapeo de Errores BdB → Orquestador

| HTTP BdB | HTTP ORQ | Motivo                           |
|----------|----------|----------------------------------|
| 200      | 200      | Desbloqueo exitoso               |
| 408      | 504      | Timeout BdB                      |
| 409      | 422      | Error de negocio BdB             |
| 4xx otro | 400      | Error en el request              |
| 5xx      | 502      | Error en el servicio del banco   |

---

## Referencia SOAP (contingencia — no implementar como principal)

| Campo         | Valor |
|---------------|-------|
| Servicio      | `AccountDebitCardStatusModify` |
| Operación     | `modDebitCardPINStatus` |
| URL (todos ambientes) | `http://vpce-096b03cc10b6c6fc8-4hb9vqom.vpce-svc-0ccf78a08235e209d.us-east-1.vpce.amazonaws.com:3590/accounts/AccountDebitCardStatusModify` |
| Accesible     | No — solo dentro de VPC BdB |
| Ficha técnica | No desarrollada en documentación disponible |

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `DESBLOQUEO_TD_PIN` | `BBOG` | `customer_debit_card_management PUT /V1/product/debitcard/status-unlock` |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo       | Valor fijo | Descripción                           |
|-------------|------------|---------------------------------------|
| `X-Channel` | Canal Oficinas | Valor de variable de ambiente    |

### Mapeo de campos

| Campo `obj_operacion`   | Campo banco (`status-unlock`)  | Notas                                  |
|-------------------------|-------------------------------|----------------------------------------|
| Número de tarjeta       | `debitCardNumber` (body)      | Número real, no enmascarado            |
| `numeroDocumento`       | `X-CustIdentNum` (header)     | Número de documento del cliente        |
| Tipo de documento       | `X-CustIdentType` (header)    | Tipo de documento del cliente          |

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** `x-api-key` en variables de ambiente — nunca en código.
- **RO-03:** `X-RqUID` generado por el adaptador — UUID único por llamada.
- **RO-04:** El número de tarjeta real (no enmascarado) se usa en el body hacia BdB. El ORQ puede retornar el número enmascarado — el ADP debe usar el número real de `obj_operacion`.
- **RO-05:** Los números de tarjeta (TD) circulan completos en el flujo funcional. El enmascaramiento se aplica **únicamente en logs** (últimos 4 dígitos visibles).
- **RO-06:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **RO-07:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.

---

## Consideraciones No Funcionales

- **Circuit Breaker:** Resilience4j activo en el consumo del servicio BdB.
- **Credenciales:** `x-api-key` en variables de ambiente — nunca en código.

---

## Dependencias

- **ORQ padre:** `ofic-actualizaciones-orq`

---

## Preguntas Abiertas

| # | Pregunta | Impacto |
|---|----------|---------|
| 1 | ¿El endpoint de desbloqueo valida que el bloqueo sea específicamente por PIN errado, o acepta cualquier tipo de bloqueo? | Define si se necesita validación previa del tipo de bloqueo |
| 2 | ¿La `x-api-key` para desbloqueo es la misma que para bloqueo TD o requiere una nueva? | Define configuración de credenciales |

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

El ADP NO reenvía los headers del ORQ directamente al banco. Para la combinación `DESBLOQUEO_TD_PIN + BBOG`, el ADP determina qué headers requiere el servicio bancario específico y construye únicamente esos.

### Nivel 3 — Headers enviados al banco

#### DESBLOQUEO_TD_PIN → customer_debit_card_management PUT /V1/product/debitcard/status-unlock (REST)

Los headers requeridos por este servicio bancario se obtienen de la documentación técnica del banco (contrato del servicio). El ADP reenvía al banco únicamente los headers definidos en ese contrato — los de valor fijo se configuran como variables de ambiente y los de contexto se propagan desde el request entrante. El ADP no valida su presencia: si el llamador omite un header requerido, el banco retorna el error correspondiente.

---

## Tecnología a Usar

| Componente  | Tecnología   | Versión | Nota                                                                            |
|-------------|--------------|---------|---------------------------------------------------------------------------------|
| Mensajería  | AWS SQS FIFO | —       | Cola de auditoría y observabilidad — `avc-everest-pt-logs.fifo` |


---

## Definition of Ready


- [ ] `x-api-key` para operación de desbloqueo confirmada con BdB
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Adaptador REST implementado
- [ ] Manejo de errores BdB implementado (408→504, 409→422)
- [ ] Circuit Breaker (Resilience4j) configurado
- [ ] Pruebas unitarias (cobertura ≥ 90%) y de integración QA aprobadas
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada — request y response encolados en cada invocación (clave PinPad excluida del mensaje de auditoría donde aplique)
