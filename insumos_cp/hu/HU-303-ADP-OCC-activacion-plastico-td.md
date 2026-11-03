# HU-303-ADP-OCC: Adaptador Banco de Occidente — Activación de Plástico TD

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-303-ADP-OCC                                              |
| ID Servicio    | SFA-009 (P3 — AC01)                                         |
| Épica          | Épica 4 — Mantenimiento Tarjeta Débito P3                   |
| Componente     | Adaptador OCC — Activación Plástico TD                      |
| Microservicio  | `ofic-actualizaciones-adp-bocc`                             |
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

**Como** adaptador OCC del microservicio `ofic-actualizaciones-adp-bocc`,  
**quiero** invocar la operación `AsociarPlasticoTarjetaDebito` del servicio SOAP `AsociacionPlasticoTarjetaDebitoService` de Banco de Occidente  
**para** activar y asociar el plástico de una tarjeta débito al cliente, en respuesta a la solicitud recibida del orquestador `ofic-actualizaciones-orq`.

---

## Contexto de Negocio

OCC expone dos servicios SOAP para la activación de plástico TD que se invocan en secuencia:

1. **Principal:** `AsociacionPlasticoTarjetaDebitoService/AsociarPlasticoTarjetaDebito` — asocia el plástico físico a la cuenta del cliente y retorna `NumeroTarjetaRealce`.
2. **Secundario:** `RegistroTransaccionesOficinaService/registrarTransaccionesOficina` — registra la transacción en el sistema de productividad de oficinas (apoyo operativo).

**Middleware:** Datapower Interno → BOCC-ACE12 (ESB) → Flexcube  
**Protocolo:** SOAP  
**WSDL:** Documentado para ambos servicios.

> **Comportamiento ante fallo del servicio secundario:** Si `registrarTransaccionesOficina` falla después de que `AsociarPlasticoTarjetaDebito` fue exitoso, la operación principal NO se revierte. Se registra la incidencia en logs y se retorna el resultado de la operación principal al orquestador.

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
  "X-Destination-Bank": "BOCC",
  "obj_operacion": { "...": "..." }
}
```

> **Nota:** Los campos de `obj_operacion` son referenciales. El ADP recibe `obj_operacion` como tipo genérico (`Object`) — no valida sus campos internos ni lo implementa como clase Java campo a campo. La validación es responsabilidad del servicio bancario.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/occ/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente, los cuales varían según banco y operación (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** El adaptador invoca primero `AsociarPlasticoTarjetaDebito` vía SOAP.
- **CA-03:** Si `AsociarPlasticoTarjetaDebito` es exitoso, invoca `registrarTransaccionesOficina` como paso de soporte.
- **CA-04:** El `Usrio` del encabezado se extrae del JWT — nunca del body.
- **CA-05:** El ADP no valida los campos de `obj_operacion`.
- **CA-06:** Respuesta exitosa de `AsociarPlasticoTarjetaDebito`: retorna `200 OK` con `NumeroTarjetaRealce`.
- **CA-07:** Si `AsociarPlasticoTarjetaDebito` falla → `422`. No se invoca `registrarTransaccionesOficina`.
- **CA-08:** Si `registrarTransaccionesOficina` falla después de éxito principal → registrar en logs/Elastic, retornar `200 OK` de todas formas.
- **CA-09:** Timeout en operación principal → `504`. Timeout en secundaria no bloquea la respuesta al ORQ.
- **CA-10:** Credenciales en variables de ambiente.
- **CA-11:** Circuit Breaker (Resilience4j) activo en ambos consumos externos (servicio principal y secundario).
- **CA-12:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. La clave cifrada del PinPad **NUNCA** se incluye en el mensaje de auditoría. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-13:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

---

## Caminos Alternativos y Excepciones

| ID | Condición | Comportamiento |
|---|---|---|
| ALT-00  | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. Verificación defensiva: el ORQ no debería enrutar operaciones no soportadas a este ADP. |

---

## Servicio OCC — Principal: AsociarPlasticoTarjetaDebito

### Endpoints

| Ambiente  | URL |
|-----------|-----|
| DES       | `https://boc201.des.app.bancodeoccidente.net:4806/AsociacionPlasticoTarjetaDebitoService/AsociacionPlasticoTarjetaDebitoPort` |
| CAL (QA)  | `http://boc201.tesint.app.bancodeoccidente.net:7805/AsociacionPlasticoTarjetaDebitoService/AsociacionPlasticoTarjetaDebitoPort` |
| PRD       | `http://boc201.prdint.app.bancodeoccidente.net:7805/AsociacionPlasticoTarjetaDebitoService/AsociacionPlasticoTarjetaDebitoPort` |

**Operación:** `AsociarPlasticoTarjetaDebito`

### Estructura del request SOAP (AsociarPlastico)

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
  <TrjtaNro><!-- Número de tarjeta / nroMedioManejo --></TrjtaNro>
  <Tipododeplastico><!-- Tipo de plástico --></Tipododeplastico>
  <VenctoFecha><!-- Fecha de vencimiento del plástico --></VenctoFecha>
  <EsPrincipal><!-- Indicador si es la tarjeta principal --></EsPrincipal>
  <PrdctoMedioTipo><!-- Tipo de medio/producto --></PrdctoMedioTipo>
  <OficinaCodigo><!-- Código de oficina --></OficinaCodigo>
  <ClienteNombre><!-- Nombre del cliente --></ClienteNombre>
</Cuerpo>
```

### Respuesta (AsociarPlastico)

| Campo                | Descripción                                    |
|----------------------|------------------------------------------------|
| `RtaCod`             | `"0000"` = éxito; otro = error                 |
| `RtaDesc`            | Descripción del resultado                      |
| `NumeroTarjetaRealce`| Número de tarjeta asignado (enmascarar en resp al ORQ) |

---

## Servicio OCC — Secundario: RegistroTransaccionesOficina

### Endpoints

| Ambiente  | URL |
|-----------|-----|
| DES       | `https://boc201.des.app.bancodeoccidente.net:4806/Productividad/RegistroTransaccionesOficinaPortTypeImplService` |
| CAL (QA)  | `http://boc201.tesint.app.bancodeoccidente.net:7805/Productividad/RegistroTransaccionesOficinaPortTypeImplService` |
| PRD       | `http://boc201.prdint.app.bancodeoccidente.net:7805/Productividad/RegistroTransaccionesOficinaPortTypeImplService` |

**Operación:** `registrarTransaccionesOficina`

> **Propósito:** Registra la transacción en el sistema de productividad de oficinas de OCC (seguimiento operativo). Su falla no invalida la operación principal.

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `ACTIVACION_PLASTICO_TD` | `BOCC` | `AsociacionPlasticoTarjetaDebitoService / AsociarPlasticoTarjetaDebito` |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

> No hay constantes de valor fijo documentadas para este servicio. Los valores de campos como `Tipododeplastico` y `EsPrincipal` se confirmarán con el WSDL.

### Mapeo de campos

| Campo `obj_operacion` | Campo banco (`AsociarPlasticoTarjetaDebito`) | Notas                                   |
|-----------------------|---------------------------------------------|-----------------------------------------|
| Número de tarjeta     | `TrjtaNro` (cuerpo)                         | nroMedioManejo                          |
| Código de oficina     | `OficinaCodigo` (cuerpo)                    | Del contexto del asesor                 |
| Nombre del cliente    | `ClienteNombre` (cuerpo)                    | De consulta previa (HU-101)             |
| user_id (JWT)         | `Usrio` (encabezado)                        | Nunca del body                          |

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** `Usrio` se extrae exclusivamente del JWT — nunca del body de la solicitud.
- **RO-03:** Si `AsociarPlasticoTarjetaDebito` falla, no se invoca `registrarTransaccionesOficina` y se retorna `422` al ORQ.
- **RO-04:** Si `registrarTransaccionesOficina` falla después de un éxito del servicio principal, se registra en logs/Elastic y se retorna `200 OK` al ORQ de todas formas. La operación principal no se revierte.
- **RO-05:** `NumeroTarjetaRealce` se enmascara antes de retornar al ORQ.
- **RO-06:** Los números de tarjeta (TD) circulan completos en el flujo funcional. El enmascaramiento se aplica **únicamente en logs** (últimos 4 dígitos visibles).
- **RO-07:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. La clave cifrada del PinPad **NUNCA** se incluye en el mensaje de auditoría — ni parcialmente. Los números de tarjeta se enmascaran (últimos 4 dígitos visibles). El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **RO-08:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.

---

## Consideraciones No Funcionales

- **Circuit Breaker:** Resilience4j activo en ambos consumos externos (servicio principal y secundario).
- **Credenciales:** En variables de ambiente — nunca en código.

---

## Mapeo de Respuesta → Orquestador

| Condición                                           | HTTP al ORQ | Body |
|-----------------------------------------------------|-------------|------|
| `RtaCod` = `"0000"` (AsociarPlastico)               | `200`       | `{ numeroTarjetaRealce: "****", mensajeRespuesta: RtaDesc }` |
| `RtaCod` ≠ `"0000"` (AsociarPlastico)               | `422`       | `{ error: RtaDesc }` |
| Fallo de RegistroTransacciones (post-éxito)         | `200`       | `{ numeroTarjetaRealce: "****", mensajeRespuesta: "..." }` + log error secundario |
| Timeout (AsociarPlastico)                           | `504`       | `{ error: "Timeout al comunicarse con OCC" }` |
| Fallo de comunicación                               | `502`       | `{ error: "Error en servicio OCC" }` |

---

## Dependencias

- **ORQ padre:** `ofic-actualizaciones-orq`

---

## Preguntas Abiertas

| # | Pregunta | Impacto |
|---|----------|---------|
| 1 | ¿Cuál es el valor de `Tipododeplastico` para tarjeta débito estándar? | Define el mapeo del campo |
| 2 | ¿`VenctoFecha` viene del inventario del plástico o se calcula (fecha actual + N años)? | Define de dónde obtener el campo |
| 3 | ¿`EsPrincipal` debe ser siempre verdadero para el primer plástico? | Define el valor |
| 4 | ¿`ClienteNombre` viene de la consulta general previa (HU-101) o debe consultarse aquí? | Define la dependencia |
| 5 | ¿El `NumeroTarjetaRealce` es el número completo o ya enmascarado? | Define si se debe enmascarar antes de retornar |

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

El ADP NO reenvía los headers del ORQ directamente al banco. Para la combinación `ACTIVACION_PLASTICO_TD + BOCC`, el ADP determina qué headers requiere el servicio bancario específico y construye únicamente esos.

### Nivel 3 — Headers enviados al banco

#### ACTIVACION_PLASTICO_TD → AsociarPlasticoTarjetaDebito / AsociacionPlasticoTarjetaDebitoService (SOAP)

Los headers requeridos por este servicio bancario se obtienen de la documentación técnica del banco (contrato del servicio). El ADP reenvía al banco únicamente los headers definidos en ese contrato — los de valor fijo se configuran como variables de ambiente y los de contexto se propagan desde el request entrante. El ADP no valida su presencia: si el llamador omite un header requerido, el banco retorna el error correspondiente.

#### Secundario → registrarTransaccionesOficina / RegistroTransaccionesOficinaService (SOAP)

Los headers requeridos por este servicio bancario se obtienen de la documentación técnica del banco (contrato del servicio). El ADP reenvía al banco únicamente los headers definidos en ese contrato — los de valor fijo se configuran como variables de ambiente y los de contexto se propagan desde el request entrante. El ADP no valida su presencia: si el llamador omite un header requerido, el banco retorna el error correspondiente.

---

## Tecnología a Usar

| Componente  | Tecnología   | Versión | Nota                                                                            |
|-------------|--------------|---------|---------------------------------------------------------------------------------|
| Mensajería  | AWS SQS FIFO | —       | Cola de auditoría y observabilidad — `avc-everest-pt-logs.fifo` |


---

## Definition of Ready


- [ ] WSDL completo de `AsociarPlasticoTarjetaDebito` revisado con campos opcionales/obligatorios confirmados
- [ ] Comportamiento ante fallo de `registrarTransaccionesOficina` aprobado por producto
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Adaptador SOAP implementado con Spring-WS 3.x + JAXB 4.0.2 — dos llamadas secuenciales
- [ ] Lógica de fallo en servicio secundario implementada (log + continuar)
- [ ] `NumeroTarjetaRealce` enmascarado en respuesta
- [ ] Circuit Breaker (Resilience4j) configurado en ambos consumos
- [ ] Pruebas unitarias (cobertura ≥ 90%) y de integración DES/CAL aprobadas
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada — request y response encolados en cada invocación (clave PinPad excluida del mensaje de auditoría donde aplique)
