# HU-302-ADP-BPO: Adaptador Banco Popular — Desbloqueo TD por PIN Errado

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-302-ADP-BPO                                              |
| ID Servicio    | SFA-009 (P3 — DB01)                                         |
| Épica          | Épica 4 — Mantenimiento Tarjeta Débito P3                   |
| Componente     | Adaptador BPO — Desbloqueo TD PIN Errado                    |
| Microservicio  | `ofic-actualizaciones-adp-bpop`                             |
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

**Como** adaptador BPO del microservicio `ofic-actualizaciones-adp-bpop`,  
**quiero** invocar la operación `UnlockDebitCardBySofia` del servicio `SrvUnlockDebitCardAdd` de Banco Popular con `idUnlock=6`  
**para** desbloquear una tarjeta débito bloqueada por PIN errado, en respuesta a la solicitud recibida del orquestador `ofic-actualizaciones-orq`.

---

## Contexto de Negocio

BPO expone el servicio SOAP `SrvUnlockDebitCardAdd / UnlockDebitCardBySofia` (código TDMDT) para desbloqueo de tarjeta débito. El WSDL está documentado en `wsdls_QA/UnlockDebitCard.wsdl`.

El campo `idUnlock=6` corresponde al tipo de desbloqueo **Pin Errado** — valor **confirmado**.

**Middleware:** Datapower Interno (AAA Policy + IP whitelist)  
**Protocolo:** SOAP  
**Seguridad:** TLS 1.0/1.1/1.2, AAA Policy DataPower, IP whitelist (`IPControlAccessSofiaTarjetadebitoAstFrontendInternal.xml`)

**Prerequisito:** Consulta previa con `QueryDebitCardCustomer` (TDCTS) para verificar el campo `ErrorPinAttempt` y confirmar que el bloqueo es efectivamente por PIN errado antes de invocar el desbloqueo.

### Valores posibles de `idUnlock`

| Valor | Significado          |
|-------|----------------------|
| 1     | Robo                 |
| 2     | Pérdida              |
| 3     | Vencimiento          |
| 4     | Solicitud            |
| 5     | Preventivo           |
| **6** | **Pin Errado** ← usar este |
| 7     | Deterioro            |

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
  "X-Destination-Bank": "BPOP",
  "obj_operacion": { "...": "..." }
}
```

> **Nota:** Los campos de `obj_operacion` son referenciales. El ADP recibe `obj_operacion` como tipo genérico (`Object`) — no valida sus campos internos ni lo implementa como clase Java campo a campo. La validación es responsabilidad del servicio bancario.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/boc/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente, los cuales varían según banco y operación (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** El adaptador invoca la operación `UnlockDebitCardBySofia` vía SOAP con `idUnlock=6` (Pin Errado — confirmado).
- **CA-03:** El adaptador construye el encabezado de seguridad BPO (AAA Policy).
- **CA-04:** Antes de invocar `UnlockDebitCardBySofia`, el adaptador consulta el estado de la tarjeta vía `QueryDebitCardCustomer` (TDCTS) para verificar `ErrorPinAttempt`.
- **CA-05:** El ADP no valida los campos de `obj_operacion`.
- **CA-06:** Respuesta exitosa del banco → `200 OK`.
- **CA-07:** Error de negocio del banco → `422`.
- **CA-08:** Timeout → `504`. Error de comunicación → `502`.
- **CA-09:** Credenciales en variables de ambiente.
- **CA-10:** IPs de los pods AKS registradas en la whitelist BPO antes del despliegue.
- **CA-11:** Circuit Breaker (Resilience4j) activo en todos los consumos externos (consulta previa y desbloqueo).
- **CA-12:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-13:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

---

## Caminos Alternativos y Excepciones

| ID | Condición | Comportamiento |
|---|---|---|
| ALT-00  | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. Verificación defensiva: el ORQ no debería enrutar operaciones no soportadas a este ADP. |

---

## Servicio BPO

### Prerequisito — QueryDebitCardCustomer (TDCTS)

Antes de invocar `UnlockDebitCardBySofia`, se verifica el estado de la tarjeta:

| Campo en respuesta  | Uso |
|---------------------|-----|
| `ErrorPinAttempt`   | Confirma que el bloqueo es por PIN errado — debe ser `true` |

### Operación Principal — UnlockDebitCardBySofia (TDMDT)

| Campo       | Valor                   |
|-------------|-------------------------|
| Servicio    | `SrvUnlockDebitCardAdd` |
| Operación   | `UnlockDebitCardBySofia`|
| WSDL        | `wsdls_QA/UnlockDebitCard.wsdl` |
| Código TDMDT| `SrvUnlockDebitCard`    |

### Endpoints

| Ambiente    | URL |
|-------------|-----|
| QA interno  | `https://qa.dp.int.ssl.sofia.bpop:55612/prodschnsmngt/SSL/UnlockDebitCardBySofia` |
| QA externo  | `https://qa.dp.ext.athssl.bpop:55623/prodschnsmngt/SSL/UnlockDebitCardBySofia` |
| PRD         | `https://prd.dp.int.ssl.sofia.bpop:55612/prodschnsmngt/SSL/UnlockDebitCardBySofia` |

**Protocolo:** SOAP  
**Seguridad:** TLS, AAA Policy DataPower, IP whitelist

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `DESBLOQUEO_TD_PIN` | `BPOP` | `SrvUnlockDebitCardAdd / UnlockDebitCardBySofia` (`idUnlock=6` para PIN errado) — código TDMDT |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo      | Valor fijo | Descripción                                     |
|------------|------------|-------------------------------------------------|
| `idUnlock` | `6`        | Tipo de desbloqueo: Pin Errado (CONFIRMADO)     |

### Mapeo de campos

| Campo `obj_operacion` | Campo banco (`UnlockDebitCardBySofia`) | Notas                          |
|-----------------------|---------------------------------------|--------------------------------|
| Número de tarjeta     | Campo de identificación tarjeta       | Según estructura del WSDL      |

> Mapeo completo pendiente de revisión del WSDL `UnlockDebitCard.wsdl`.

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** `idUnlock` siempre se envía como `6` para esta transacción (Pin Errado — confirmado).
- **RO-03:** Antes de invocar `UnlockDebitCardBySofia`, el ADP consulta `QueryDebitCardCustomer` (TDCTS) para verificar `ErrorPinAttempt=true`. Confirmar con BPO si este prerequisito es obligatorio u opcional para el canal Oficinas.
- **RO-04:** Credenciales y configuración de seguridad (AAA Policy) en variables de ambiente.
- **RO-05:** Los números de tarjeta (TD) circulan completos en el flujo funcional. El enmascaramiento se aplica **únicamente en logs** (últimos 4 dígitos visibles).
- **RO-06:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **RO-07:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.

---

## Consideraciones No Funcionales

- **Circuit Breaker:** Resilience4j activo en todos los consumos externos (TDCTS y TDMDT).
- **Seguridad:** TLS 1.0/1.1/1.2 + AAA Policy DataPower + IP whitelist.
- **Credenciales:** En variables de ambiente — nunca en código.

---

## Mapeo de Respuesta → Orquestador

| Condición                        | HTTP al ORQ | Body                                             |
|----------------------------------|-------------|--------------------------------------------------|
| Respuesta exitosa BPO            | `200`       | `{ estadoActual: "ACTIVA", mensajeRespuesta: "..." }` |
| Error de negocio BPO             | `422`       | `{ error: mensajeBPO }`                          |
| Timeout                          | `504`       | `{ error: "Timeout al comunicarse con BPO" }`    |
| Fallo de comunicación            | `502`       | `{ error: "Error en servicio BPO" }`             |

---

## Dependencias

- **ORQ padre:** `ofic-actualizaciones-orq`
- **Consulta previa (prerequisito):** `QueryDebitCardCustomer` (TDCTS) — verificar `ErrorPinAttempt`

---

## Preguntas Abiertas

| # | Pregunta | Impacto |
|---|----------|---------|
| 1 | ¿El prerequisito `QueryDebitCardCustomer` (TDCTS) es obligatorio u opcional para el canal Oficinas? | Define si hay una llamada previa requerida |
| 2 | ¿Las IPs de los pods AKS ya están registradas en la whitelist BPO, o debe gestionarse por separado para este servicio? | Define el proceso de onboarding técnico |

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

El ADP NO reenvía los headers del ORQ directamente al banco. Para la combinación `DESBLOQUEO_TD_PIN + BPOP`, el ADP determina qué headers requiere el servicio bancario específico y construye únicamente esos.

### Nivel 3 — Headers enviados al banco

#### DESBLOQUEO_TD_PIN → UnlockDebitCardBySofia / SrvUnlockDebitCardAdd (SOAP)

Los headers requeridos por este servicio bancario se obtienen de la documentación técnica del banco (contrato del servicio). El ADP reenvía al banco únicamente los headers definidos en ese contrato — los de valor fijo se configuran como variables de ambiente y los de contexto se propagan desde el request entrante. El ADP no valida su presencia: si el llamador omite un header requerido, el banco retorna el error correspondiente.

---

## Tecnología a Usar

| Componente  | Tecnología   | Versión | Nota                                                                            |
|-------------|--------------|---------|---------------------------------------------------------------------------------|
| Mensajería  | AWS SQS FIFO | —       | Cola de auditoría y observabilidad — `avc-everest-pt-logs.fifo` |


---

## Definition of Ready


- [ ] Prerequisito `QueryDebitCardCustomer` definido como obligatorio u opcional
- [ ] IPs AKS en whitelist BPO confirmadas
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Adaptador SOAP implementado con Spring-WS 3.x + JAXB 4.0.2
- [ ] `idUnlock=6` (Pin Errado) configurado como constante
- [ ] Consulta previa TDCTS implementada
- [ ] Circuit Breaker (Resilience4j) configurado en ambos consumos externos
- [ ] IPs de pods AKS registradas en whitelist BPO
- [ ] Pruebas unitarias (cobertura ≥ 90%) y de integración QA aprobadas
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada — request y response encolados en cada invocación (clave PinPad excluida del mensaje de auditoría donde aplique)
