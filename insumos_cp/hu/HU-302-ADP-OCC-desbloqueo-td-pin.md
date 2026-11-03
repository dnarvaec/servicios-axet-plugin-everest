# HU-302-ADP-OCC: Adaptador Banco de Occidente — Desbloqueo TD por PIN Errado

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-302-ADP-OCC                                              |
| ID Servicio    | SFA-009 (P3 — DB01)                                         |
| Épica          | Épica 4 — Mantenimiento Tarjeta Débito P3                   |
| Componente     | Adaptador OCC — Desbloqueo TD PIN Errado                    |
| Microservicio  | `ofic-actualizaciones-adp-bocc`                             |
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

**Como** adaptador OCC del microservicio `ofic-actualizaciones-adp-bocc`,  
**quiero** invocar la operación `ActivarTarjetaDebitoCarton` del servicio SOAP `ESB_ACE12_AdministracionTarjetaDebitoCarton` de Banco de Occidente con `BloqueoMtvo` vacío  
**para** desbloquear una tarjeta débito bloqueada por PIN errado, en respuesta a la solicitud recibida del orquestador `ofic-actualizaciones-orq`.

---

## Contexto de Negocio

OCC usa la operación SOAP `ActivarTarjetaDebitoCarton` del servicio `ESB_ACE12_AdministracionTarjetaDebitoCarton` para reactivar una tarjeta débito bloqueada. Para el caso específico de desbloqueo por PIN errado, el campo `BloqueoMtvo` se envía **vacío** — esto indica al backend Flexcube una reactivación sin causal de bloqueo activo.

**Middleware:** Datapower Interno → BOCC-ACE12 (ESB) → Flexcube (`FCUBSDCardService/DCardStatChange`)  
**Protocolo:** SOAP  
**Pantallas SOFIA:** C8023 (Desbloqueo Manual TD) y C8024 (Desbloqueo Manual TD Seguridad)  
**WSDL:** Documentado

> **Prerequisito recomendado:** Consulta previa `ESB_IntegracionConsultarDatosBasicosTDC/consultarDatosBasicosTarjetaDebitoCarton` → Flexcube `FCUBSDCardService/QueryDCMaintenance` para verificar el estado de la tarjeta antes del desbloqueo.

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
  "X-Destination-Bank": "BOCC",
  "obj_operacion": { "...": "..." }
}
```

> **Nota:** Los campos de `obj_operacion` son referenciales. El ADP recibe `obj_operacion` como tipo genérico (`Object`) — no valida sus campos internos ni lo implementa como clase Java campo a campo. La validación es responsabilidad del servicio bancario.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/occ/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente, los cuales varían según banco y operación (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** El adaptador invoca la operación `ActivarTarjetaDebitoCarton` vía SOAP.
- **CA-03:** El campo `BloqueoMtvo` se envía **vacío** para indicar desbloqueo por PIN errado.
- **CA-04:** `Usrio` en el encabezado se extrae del JWT — nunca del body.
- **CA-05:** El ADP no valida los campos de `obj_operacion`.
- **CA-06:** Respuesta con `RtaCod` "0000" → `200 OK`.
- **CA-07:** Respuesta con `RtaCod` distinto → `422`.
- **CA-08:** Timeout → `504`. Fallo de comunicación → `502`.
- **CA-09:** Credenciales en variables de ambiente.
- **CA-10:** Circuit Breaker (Resilience4j) activo en el consumo del servicio OCC.
- **CA-11:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-12:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

---

## Caminos Alternativos y Excepciones

| ID | Condición | Comportamiento |
|---|---|---|
| ALT-00  | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. Verificación defensiva: el ORQ no debería enrutar operaciones no soportadas a este ADP. |

---

## Servicio OCC

### Endpoints

| Ambiente  | URL |
|-----------|-----|
| DES       | `https://boc201.des.app.bancodeoccidente.net:4806/ActivacionTarjetaDebitoCartonService/ActivarTarjetaDebitoCartonPort` |
| CAL (QA)  | `http://boc201.tesint.app.bancodeoccidente.net:7805/ActivacionTarjetaDebitoCartonService/ActivarTarjetaDebitoCartonPort` |
| PRD       | `http://boc201.prdint.app.bancodeoccidente.net:7805/ActivacionTarjetaDebitoCartonService/ActivarTarjetaDebitoCartonPort` |

**Protocolo:** SOAP  
**Operación:** `ActivarTarjetaDebitoCarton`  
**Backend:** Flexcube `FCUBSDCardService/DCardStatChange`

### Estructura del request SOAP

```xml
<EncabezadoEntrada>
  <AplCod><!-- Código de aplicación --></AplCod>
  <TrmnalId><!-- Terminal ID --></TrmnalId>
  <SesionId><!-- ID de sesión --></SesionId>
  <PtcionId><!-- UUID de la petición --></PtcionId>
  <Usrio><!-- user_id del JWT --></Usrio>
  <PtcionFecha><!-- Fecha/hora --></PtcionFecha>
</EncabezadoEntrada>
<Cuerpo>
  <OficinaCodigo><!-- Código de la oficina --></OficinaCodigo>
  <Producto><!-- Número de tarjeta --></Producto>
  <ProductoEstado><!-- Estado destino: ACTIVA --></ProductoEstado>
  <BloqueoMtvo><!-- VACÍO para desbloqueo por PIN errado --></BloqueoMtvo>
  <TrjtaTipo><!-- Tipo de tarjeta débito --></TrjtaTipo>
</Cuerpo>
```

> **Clave técnica:** `BloqueoMtvo` vacío es el discriminante del caso PIN errado frente a otros tipos de desbloqueo en Flexcube.

### Respuesta OCC

| Campo    | Descripción                        |
|----------|------------------------------------|
| `RtaCod` | `"0000"` = éxito; otro = error     |
| `RtaDesc`| Descripción del resultado          |

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `DESBLOQUEO_TD_PIN` | `BOCC` | `ESB_ACE12_AdministracionTarjetaDebitoCarton / ActivarTarjetaDebitoCarton` (`BloqueoMtvo=""`) |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo         | Valor fijo | Descripción                                              |
|---------------|------------|----------------------------------------------------------|
| `BloqueoMtvo` | `""` (vacío) | Campo vacío indica desbloqueo por PIN errado en Flexcube|

### Mapeo de campos

| Campo `obj_operacion` | Campo banco (`ActivarTarjetaDebitoCarton`) | Notas                         |
|-----------------------|-------------------------------------------|-------------------------------|
| Número de tarjeta     | `Producto` (cuerpo)                       | Número de tarjeta débito      |
| Código de oficina     | `OficinaCodigo` (cuerpo)                  | Del contexto del asesor       |
| user_id (JWT)         | `Usrio` (encabezado)                      | Nunca del body                |

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** `BloqueoMtvo` siempre se envía vacío para esta transacción — discriminante del tipo de desbloqueo en Flexcube.
- **RO-03:** `Usrio` se extrae exclusivamente del JWT — nunca del body de la solicitud.
- **RO-04:** El prerequisito de consulta previa (estado de la tarjeta) es recomendado — confirmar con OCC si es obligatorio para el canal Oficinas.
- **RO-05:** Los números de tarjeta (TD) circulan completos en el flujo funcional. El enmascaramiento se aplica **únicamente en logs** (últimos 4 dígitos visibles).
- **RO-06:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **RO-07:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.

---

## Consideraciones No Funcionales

- **Circuit Breaker:** Resilience4j activo en el consumo del servicio OCC.
- **Credenciales:** En variables de ambiente — nunca en código.

---

## Mapeo de Respuesta → Orquestador

| Condición                    | HTTP al ORQ | Body                                             |
|------------------------------|-------------|--------------------------------------------------|
| `RtaCod` = `"0000"`          | `200`       | `{ estadoActual: "ACTIVA", mensajeRespuesta: RtaDesc }` |
| `RtaCod` ≠ `"0000"`          | `422`       | `{ error: RtaDesc }`                             |
| Timeout                      | `504`       | `{ error: "Timeout al comunicarse con OCC" }`    |
| Fallo de comunicación        | `502`       | `{ error: "Error en servicio OCC" }`             |

---

## Dependencias

- **ORQ padre:** `ofic-actualizaciones-orq`

---

## Preguntas Abiertas

| # | Pregunta | Impacto |
|---|----------|---------|
| 1 | ¿Cuál es el valor de `ProductoEstado` para indicar que la tarjeta debe quedar ACTIVA? | Define el valor del campo en el request |
| 2 | ¿`TrjtaTipo` tiene un valor estándar para TD en OCC? | Define el valor del campo |
| 3 | ¿El prerequisito de consulta previa es obligatorio o es recomendado? | Define si el adaptador debe llamar al servicio de consulta antes |

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

El ADP NO reenvía los headers del ORQ directamente al banco. Para la combinación `DESBLOQUEO_TD_PIN + BOCC`, el ADP determina qué headers requiere el servicio bancario específico y construye únicamente esos.

### Nivel 3 — Headers enviados al banco

#### DESBLOQUEO_TD_PIN → ActivarTarjetaDebitoCarton / ESB_ACE12_AdministracionTarjetaDebitoCarton (SOAP)

Los headers requeridos por este servicio bancario se obtienen de la documentación técnica del banco (contrato del servicio). El ADP reenvía al banco únicamente los headers definidos en ese contrato — los de valor fijo se configuran como variables de ambiente y los de contexto se propagan desde el request entrante. El ADP no valida su presencia: si el llamador omite un header requerido, el banco retorna el error correspondiente.

---

## Tecnología a Usar

| Componente  | Tecnología   | Versión | Nota                                                                            |
|-------------|--------------|---------|---------------------------------------------------------------------------------|
| Mensajería  | AWS SQS FIFO | —       | Cola de auditoría y observabilidad — `avc-everest-pt-logs.fifo` |


---

## Definition of Ready


- [ ] WSDL completo revisado con los valores de `ProductoEstado` y `TrjtaTipo`
- [ ] Confirmación de que `BloqueoMtvo` vacío es correcto para PIN errado
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Adaptador SOAP implementado con Spring-WS 3.x + JAXB 4.0.2
- [ ] Circuit Breaker (Resilience4j) configurado
- [ ] Pruebas unitarias (cobertura ≥ 90%) y de integración DES/CAL aprobadas
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada — request y response encolados en cada invocación (clave PinPad excluida del mensaje de auditoría donde aplique)
