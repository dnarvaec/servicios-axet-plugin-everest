# HU-303-ADP-AVV: Adaptador AV Villas — Activación de Plástico TD

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-303-ADP-AVV                                              |
| ID Servicio    | SFA-009 (P3 — AC01)                                         |
| Épica          | Épica 4 — Mantenimiento Tarjeta Débito P3                   |
| Componente     | Adaptador AVV — Activación Plástico TD                      |
| Microservicio  | `ofic-actualizaciones-adp-bavv`                             |
| Sprint         | Por definir                                                 |
| Prioridad      | Media (P3)                                                  |
| Estimación     | Por estimar                                                 |
| Estado         | **Pendiente implementación**                                |
| HU Padre       | HU-303-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-21                                                  |
| Última revisión | 2026-09-03 — campo operacion agregado; identificación de servicio por operacion+banco documentada; masking solo en logs; gestión de headers documentada; cola SQS FIFO de auditoría documentada; OperacionEnum definido localmente en cada microservicio con valores canónicos de HU-101-ORQ; operación no soportada: excepción + 400 documentada |

---

## Historia de Usuario

**Como** adaptador AVV del microservicio `ofic-actualizaciones-adp-bavv`,  
**quiero** invocar la operación `modCardPswd` del servicio SOAP `PFBA_Multiaplicacion70` de AV Villas  
**para** activar el plástico de una tarjeta débito del cliente, en respuesta a la solicitud recibida del orquestador `ofic-actualizaciones-orq`.

---

## Contexto de Negocio

Para AVV, la operación de Activación de Plástico TD utiliza el **mismo servicio que la Asignación de Clave TD** (`HU-301-ADP-AVV`): la operación `modCardPswd` del servicio `WSBA_Multiaplicacion_asignarClaveTarjetas` (plataforma `PFBA_Multiaplicacion70`), con `AcctType=SDA`. Confirmado por `WS_Everest.xlsx` (misma fila de la hoja de servicios).

**Middleware:** Datapower Interno → ESB AVV → Entirex → z/OS (ICBS)  
**Protocolo:** SOAP  
**WSDL:** `CardPswdAssignmentSvc.wsdl`  
**Tipo de cuenta:** `AcctType=SDA` (cuenta de ahorros)  
**Dependencia de periférico:** PinPad físico — gestionado por Everest antes de invocar este adaptador. El bloque PIN ya llega cifrado en `OTPInfo` desde el frontend.

**Prerequisito:** Antes de invocar `modCardPswd`, el adaptador consulta los datos de la tarjeta mediante el servicio `WSBA_Multiaplicacion_ConsultarTarjetas` (plataforma `PFBA_Multiaplicacion95`).

> **Nota:** Los endpoints y la estructura de servicio son idénticos a los de `HU-301-ADP-AVV` (Asignación Clave TD). Reutilizar la misma integración SOAP con los mismos parámetros.

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
  "operacion": "ACTIVACION_PLASTICO_TD",
  "X-Origin-Bank": "...",
  "X-Destination-Bank": "BAVV",
  "obj_operacion": { "...": "..." }
}
```

> **Nota:** Los campos de `obj_operacion` son referenciales. El ADP recibe `obj_operacion` como tipo genérico (`Object`) — no valida sus campos internos ni lo implementa como clase Java campo a campo. La validación es responsabilidad del servicio bancario.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/avv/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente, los cuales varían según banco y operación (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** El adaptador invoca la operación `modCardPswd` del servicio `WSBA_Multiaplicacion_asignarClaveTarjetas` (plataforma `PFBA_Multiaplicacion70`) vía SOAP.
- **CA-03:** El campo `AcctType` se envía con valor `"SDA"` (fijo — cuenta de ahorros).
- **CA-04:** El bloque PIN cifrado se mapea al campo `OTPInfo` del request SOAP — nunca se registra en logs ni trazabilidad.
- **CA-05:** Antes de invocar `modCardPswd`, el adaptador consulta los datos de la tarjeta vía `WSBA_Multiaplicacion_ConsultarTarjetas` (PFBA_Multiaplicacion95). Si la consulta falla, el flujo se interrumpe y se retorna error al ORQ.
- **CA-06:** El ADP no valida los campos de `obj_operacion`.
- **CA-07:** Respuesta exitosa del banco → `200 OK` al orquestador.
- **CA-08:** Error de negocio del banco → `422` con el mensaje de error AVV.
- **CA-09:** Timeout → `504`. Error de comunicación → `502`.
- **CA-10:** Credenciales en variables de ambiente — nunca en código.
- **CA-11:** Circuit Breaker (Resilience4j) activo en todos los consumos externos (consulta previa y operación principal).
- **CA-12:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. La clave cifrada del PinPad **NUNCA** se incluye en el mensaje de auditoría. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-13:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

---

## Caminos Alternativos y Excepciones

| ID | Condición | Comportamiento |
|---|---|---|
| ALT-00  | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. Verificación defensiva: el ORQ no debería enrutar operaciones no soportadas a este ADP. |

---

## Servicio AVV

### Prerequisito — Consulta de Tarjeta

| Campo      | Valor                                    |
|------------|------------------------------------------|
| Plataforma | `PFBA_Multiaplicacion95`                 |
| Servicio   | `WSBA_Multiaplicacion_ConsultarTarjetas` |

### Operación Principal — Activación de Plástico

| Campo      | Valor                                       |
|------------|---------------------------------------------|
| Plataforma | `PFBA_Multiaplicacion70`                    |
| Servicio   | `WSBA_Multiaplicacion_asignarClaveTarjetas` |
| Operación  | `modCardPswd`                               |
| WSDL       | `CardPswdAssignmentSvc.wsdl`                |

> **Mismo servicio que HU-301-ADP-AVV.** Reutilizar la integración existente.

### Endpoints

| Ambiente | URL base              |
|----------|-----------------------|
| DEV      | `10.10.10.201:443`    |
| QA       | `10.10.9.200:443`     |
| PRD      | `10.10.21.10:443`     |

**Protocolo:** SOAP

### Campo clave del request

| Campo      | Valor / Fuente                            | Notas                       |
|------------|-------------------------------------------|-----------------------------|
| `AcctType` | `"SDA"` (fijo)                            | Cuenta de ahorros débito    |
| `OTPInfo`  | Bloque PIN cifrado de `obj_operacion`     | NO registrar en logs        |

> Revisar `CardPswdAssignmentSvc.wsdl` para la estructura completa del request SOAP.

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `ACTIVACION_PLASTICO_TD` | `BAVV` | `PFBA_Multiaplicacion70 / WSBA_Multiaplicacion_asignarClaveTarjetas / modCardPswd` (`AcctType=SDA`) — mismo servicio que ASIGNACION_CLAVE_TD |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo      | Valor fijo | Descripción                    |
|------------|------------|--------------------------------|
| `AcctType` | `SDA`      | Tipo de cuenta — ahorros débito|

### Mapeo de campos

| Campo `obj_operacion`          | Campo banco (`modCardPswd`) | Notas                                    |
|--------------------------------|-----------------------------|------------------------------------------|
| Bloque PIN cifrado (`OTPInfo`) | `OTPInfo`                   | Bloque PIN cifrado; NO registrar en logs |

> Mapeo completo de campos pendiente de revisión del WSDL `CardPswdAssignmentSvc.wsdl`. Idéntico a HU-301-ADP-AVV.

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** Antes de invocar `modCardPswd`, el ADP consulta los datos de la tarjeta vía `WSBA_Multiaplicacion_ConsultarTarjetas` (PFBA_Multiaplicacion95). Si la consulta falla, el flujo se interrumpe y se retorna error al ORQ.
- **RO-03:** El bloque PIN cifrado (`OTPInfo`) nunca se registra en logs ni en trazabilidad.
- **RO-04:** Este flujo utiliza el mismo servicio AVV que HU-301 (Asignación Clave TD) — reutilizar la integración existente.
- **RO-05:** Los números de tarjeta (TD) circulan completos en el flujo funcional. El enmascaramiento se aplica **únicamente en logs** (últimos 4 dígitos visibles).
- **RO-06:** La clave cifrada proveniente de PinPad **NUNCA se registra en logs** — ni siquiera parcialmente. Solo se registra que el campo fue recibido.
- **RO-07:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. La clave cifrada del PinPad **NUNCA** se incluye en el mensaje de auditoría — ni parcialmente. Los números de tarjeta se enmascaran (últimos 4 dígitos visibles). El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **RO-08:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.

---

## Consideraciones No Funcionales

- **Circuit Breaker:** Resilience4j activo en todos los consumos externos (PFBA_Multiaplicacion95 y PFBA_Multiaplicacion70).
- **Seguridad:** `OTPInfo` (bloque PIN cifrado) nunca se registra en logs ni trazabilidad.
- **Credenciales:** En variables de ambiente — nunca en código.

---

## Mapeo de Respuesta → Orquestador

| Condición                          | HTTP al ORQ | Body                                                          |
|------------------------------------|-------------|---------------------------------------------------------------|
| Respuesta exitosa AVV              | `200`       | Confirmación de activación de plástico                        |
| Error de negocio AVV               | `422`       | `{ error: mensajeErrorAVV }`                                  |
| Timeout de conexión                | `504`       | `{ error: "Timeout al comunicarse con AVV" }`                 |
| Error de comunicación inesperado   | `502`       | `{ error: "Error en servicio AVV" }`                          |

---

## Dependencias

- **ORQ padre:** `ofic-actualizaciones-orq`
- **Consulta previa (prerequisito):** PFBA_Multiaplicacion95 / WSBA_Multiaplicacion_ConsultarTarjetas (AVV)
- **Servicio compartido con:** HU-301-ADP-AVV (mismo servicio PFBA_Multiaplicacion70/modCardPswd)
- **PinPad:** Periférico gestionado por Everest — el bloque PIN llega cifrado al ADP

---

## Preguntas Abiertas

| # | Pregunta | Impacto |
|---|----------|---------|
| 1 | ¿Cuál es la estructura completa del request SOAP de `modCardPswd` para activación de plástico (todos los campos del WSDL)? | Define el mapeo completo |
| 2 | ¿La lógica de activación de plástico usa exactamente los mismos parámetros que la asignación de clave, o hay diferencias en el request? | Define si se puede reutilizar la integración de HU-301 |

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

El ADP NO reenvía los headers del ORQ directamente al banco. Para la combinación `ACTIVACION_PLASTICO_TD + BAVV`, el ADP determina qué headers requiere el servicio bancario específico y construye únicamente esos.

### Nivel 3 — Headers enviados al banco

#### Prerequisito: WSBA_Multiaplicacion_ConsultarTarjetas → PFBA_Multiaplicacion95 (SOAP)

Los headers requeridos por este servicio bancario se obtienen de la documentación técnica del banco (contrato del servicio). El ADP reenvía al banco únicamente los headers definidos en ese contrato — los de valor fijo se configuran como variables de ambiente y los de contexto se propagan desde el request entrante. El ADP no valida su presencia: si el llamador omite un header requerido, el banco retorna el error correspondiente.

#### ACTIVACION_PLASTICO_TD → modCardPswd / PFBA_Multiaplicacion70 (SOAP)

Los headers requeridos por este servicio bancario se obtienen de la documentación técnica del banco (contrato del servicio). El ADP reenvía al banco únicamente los headers definidos en ese contrato — los de valor fijo se configuran como variables de ambiente y los de contexto se propagan desde el request entrante. El ADP no valida su presencia: si el llamador omite un header requerido, el banco retorna el error correspondiente.

---

## Tecnología a Usar

| Componente  | Tecnología   | Versión | Nota                                                                            |
|-------------|--------------|---------|---------------------------------------------------------------------------------|
| Mensajería  | AWS SQS FIFO | —       | Cola de auditoría y observabilidad — `avc-everest-pt-logs.fifo` |


---

## Definition of Ready


- [ ] Confirmación con AVV que `modCardPswd` cubre activación de plástico (misma operación que HU-301)
- [ ] WSDL `CardPswdAssignmentSvc.wsdl` revisado con estructura completa del request
- [ ] Periférico PinPad disponible en DEV/QA para pruebas de integración
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Adaptador SOAP implementado con Spring-WS 3.x + JAXB 4.0.2 (reutilizando integración de HU-301-ADP-AVV)
- [ ] Consulta previa PFBA_Multiaplicacion95 implementada como prerequisito
- [ ] `OTPInfo` (bloque PIN) nunca registrado en logs
- [ ] Circuit Breaker (Resilience4j) configurado en ambos consumos externos
- [ ] Pruebas unitarias (cobertura ≥ 90%) y de integración DEV/QA aprobadas
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada — request y response encolados en cada invocación (clave PinPad excluida del mensaje de auditoría donde aplique)
