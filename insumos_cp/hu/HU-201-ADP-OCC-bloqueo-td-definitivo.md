# HU-201-ADP-OCC: Adaptador Banco de Occidente — Bloqueo TD Definitivo

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-201-ADP-OCC                                              |
| ID Servicio    | SFA-009                                                     |
| Épica          | Épica 2 — Mantenimiento Tarjeta Débito (P2)                 |
| Componente     | Adaptador OCC — Bloqueo TD Definitivo                       |
| Microservicio  | `ofic-actualizaciones-adp-bocc`                             |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P2)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | Pendiente                                                   |
| HU Padre       | HU-201-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-21                                                  |
| Última revisión | 2026-09-03 — campo operacion agregado; identificación de servicio por operacion+banco documentada; masking solo en logs; gestión de headers documentada; cola SQS FIFO de auditoría documentada; OperacionEnum definido localmente en cada microservicio con valores canónicos de HU-101-ORQ; operación no soportada: excepción + 400 documentada |

---

## Historia de Usuario

**Como** microservicio `ofic-actualizaciones-adp-bocc`,  
**quiero** recibir del orquestador (`ofic-actualizaciones-orq`) la solicitud de bloqueo definitivo de tarjeta débito de Banco de Occidente,  
**para** invocar el servicio SOAP `BloquearTarjetaDebitoCarton` de OCC y retornar el resultado normalizado.

---

## Contexto de Negocio

OCC expone el bloqueo/cancelación de TD a través del servicio SOAP `ESB_ACE12_BloqueoCancelacionTarjetaDebito` via Datapower Interno → BOCC-ACE12 → Flexcube. El banco confirmó explícitamente que **solo se realizan bloqueos definitivos desde oficina** — el servicio aplica directamente al caso de uso P2.

Las acciones Flexcube soportadas incluyen CN (Cancelación definitiva), RC (BREX — bloqueo con reexpedición) y BL/DV (BSRE — bloqueo sin reexpedición). Para el canal Oficinas se usará CN (cancelación definitiva) con las causales homologadas.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/occ/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente, los cuales varían según banco y operación (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** El adaptador recibe el contenido de `obj_operacion` proveniente del ORQ e invoca la operación SOAP `BloquearTarjetaDebitoCarton` del servicio `BloqueoCancelacionTajetaDebitoCartonService`.
- **CA-03:** Construye el request con los campos del encabezado (`AplCod`, `TrmnalId`, `SesionId`, `PtcionId`, `Usrio`, `PtcionFecha`) y cuerpo (`OficinaCodigo`, `Producto`, `ProductoEstado`, `BloqueoTipo`, `TrjtaTipo`).
- **CA-04:** Mapea la causal del canal Oficinas (`BL01`, `BL02`, `BL03`) al `BloqueoTipo` de OCC según las Reglas de Integración.
- **CA-05:** Si OCC retorna `RtaCod: "0000"` → operación exitosa.
- **CA-06:** Si OCC retorna código de error de tarjeta no encontrada, mapea a `404`.
- **CA-07:** Si OCC no responde a tiempo, mapea a `504`.
- **CA-08:** Circuit Breaker activo en el consumo del servicio OCC.
- **CA-09:** Transforma la respuesta al modelo normalizado.
- **CA-10:** Credenciales en variables de ambiente.
- **CA-11:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-12:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

---

## Inputs

### Recibidos del Orquestador

El ADP recibe del orquestador: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`.

```json
{
  "operacion": "BLOQUEO_TD_DEFINITIVO",
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

| Campo               | Valor                                                    |
|---------------------|----------------------------------------------------------|
| Tipo                | SOAP                                                     |
| Nombre del servicio | `BloqueoCancelacionTajetaDebitoCartonService`            |
| Service Port        | `BloqueoCancelacionTajetaDebitoCartonPort`               |
| Operación           | `BloquearTarjetaDebitoCarton`                            |
| Middleware          | Datapower Interno → BOCC-ACE12                           |

### Endpoints

| Ambiente | URL |
|----------|-----|
| DES      | `https://boc201.des.app.bancodeoccidente.net:4806/BloqueoCancelacionTajetaDebitoCartonService/BloqueoCancelacionTajetaDebitoCartonPort` |
| CAL (QA) | `http://boc201.tesint.app.bancodeoccidente.net:7805/BloqueoCancelacionTajetaDebitoCartonService/BloqueoCancelacionTajetaDebitoCartonPort` |
| PROD     | `http://boc201.prdint.app.bancodeoccidente.net:7805/BloqueoCancelacionTajetaDebitoCartonService/BloqueoCancelacionTajetaDebitoCartonPort` |

### SOAP Request — Encabezado (`EncabezadoEntrada`)

| Campo         | Tipo   | Ejemplo                | Descripción                              |
|---------------|--------|------------------------|------------------------------------------|
| `AplCod`      | String | `"84"`                 | Código de la aplicación consumidora      |
| `TrmnalId`    | String | `"OFICINAS-AKS-01"`    | ID del terminal AKS que ejecuta la TX    |
| `SesionId`    | String | `"1"`                  | ID de sesión                             |
| `PtcionId`    | String | `"20260821103000001"`  | ID único de la petición (timestamp+seq)  |
| `Usrio`       | String | `"asesor@banco.com"`   | Usuario ejecutor (del JWT)               |
| `PtcionFecha` | String | `"2026-08-21T10:30:00"`| Fecha y hora de la petición (ISO 8601)   |

### SOAP Request — Cuerpo (`BloquearTarjetaDebitoCartonEntrada`)

| Campo           | Tipo    | Ejemplo              | Obligatorio | Descripción                                   |
|-----------------|---------|----------------------|-------------|-----------------------------------------------|
| `OficinaCodigo` | String  | `"230"`              | Sí          | Código de la oficina que realiza el bloqueo   |
| `Producto`      | String  | `"5307100045685945"` | Sí          | Número de tarjeta débito a bloquear           |
| `ProductoEstado`| String  | `"2"`                | Sí          | Estado a asignar (código Flexcube)            |
| `BloqueoTipo`   | String  | `"56"`               | Sí          | Código del tipo de bloqueo/cancelación        |
| `CancelMtvo`    | String  | `""`                 | No          | Motivo de cancelación (puede enviarse vacío)  |
| `TrjtaTipo`     | String  | `"1"`                | Sí          | Tipo de tarjeta                               |

### Mapeo causal → BloqueoTipo OCC

| Causal Canal Oficinas | Descripción | Causal Flexcube OCC      | BloqueoTipo OCC       | Acción Flexcube              |
|-----------------------|-------------|--------------------------|------------------------|------------------------------|
| `BL01`                | Robo        | 2 (Pérdida/Robo)         | PENDIENTE CONFIRMAR   | CN (Cancelación definitiva)  |
| `BL02`                | Pérdida     | 2 (Pérdida/Robo)         | PENDIENTE CONFIRMAR   | CN (Cancelación definitiva)  |
| `BL03`                | Fraude      | 10 (Seguridad)           | PENDIENTE CONFIRMAR   | CN (Cancelación definitiva)  |

> **Pendiente:** Confirmar con OCC el código exacto de `BloqueoTipo` para cada causal y el valor de `ProductoEstado` para bloqueo definitivo. Causales Flexcube documentadas: 2=Pérdida/Robo, 10=Seguridad.

---

## Outputs

> **Nota:** El ADP retorna la respuesta del banco directamente — no hay transformación a un modelo normalizado propio. Los campos listados son referenciales según el contrato del banco.

### SOAP Response — Encabezado (`EncabezadoSalida`)

| Campo               | Tipo   | Descripción                                  |
|---------------------|--------|----------------------------------------------|
| `PtcionId`          | String | ID de petición correlacionado con el request |
| `RtaCod`            | String | `"0000"` = exitoso                           |
| `RtaMnsje`          | String | Mensaje descriptivo del resultado            |

### SOAP Response — Datos (`BloquearTarjetaDebitoCartonSalida`)

| Campo                   | Tipo   | Descripción                                    |
|-------------------------|--------|------------------------------------------------|
| `SecuenciaIdentificador`| String | Identificador de la secuencia generada por OCC |
| `TrjtaNro`              | String | Número de tarjeta resultado de la operación    |

### Modelo normalizado de salida

| Campo           | Tipo   | Descripción                                     |
|-----------------|--------|-------------------------------------------------|
| `numeroTarjeta` | String | Número enmascarado                              |
| `estadoActual`  | String | `BLOQUEADA`                                     |
| `causal`        | String | Causal del bloqueo (BL01/BL02/BL03)             |
| `fechaBloqueo`  | String | Timestamp de la operación                       |
| `consecutivoOCC`| String | `SecuenciaIdentificador` retornado por OCC      |

### Mapeo de errores OCC → estándar

| Error OCC                      | Código HTTP | StatusDesc                             |
|--------------------------------|-------------|----------------------------------------|
| Tarjeta no encontrada          | `404`        | "Tarjeta no encontrada en OCC"         |
| Estado incompatible            | `422`        | "Estado de tarjeta no permite bloqueo" |
| Error de conectividad          | `502`        | "Error de conectividad con OCC"        |
| Timeout                        | `504`        | "Timeout del servicio OCC"             |

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `BLOQUEO_TD_DEFINITIVO` | `BOCC` | `ESB_ACE12_BloqueoCancelacionTarjetaDebito / bloquearTarjetaDebitoCarton` — SOAP interno |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo        | Valor fijo            | Descripción                                                     |
|--------------|-----------------------|-----------------------------------------------------------------|
| `AplCod`     | `"84"`                | Código de la aplicación consumidora (fijo)                      |
| `TrjtaTipo`  | PENDIENTE CONFIRMAR   | Tipo de tarjeta débito — confirmar valor fijo con OCC           |
| Acción Flexcube | `CN`              | Cancelación definitiva (fija para todas las causales de bloqueo definitivo) |

### Mapeo de campos

| Campo obj_operacion | Campo OCC          | Notas                                                                        |
|---------------------|--------------------|------------------------------------------------------------------------------|
| `numeroTarjeta`     | `Producto`         | PENDIENTE CONFIRMAR: ¿número enmascarado o completo?                         |
| `causal`            | Causal Flexcube / `BloqueoTipo` | Ver tabla de mapeo de causales en sección de servicio      |
| `tipoDocumento`     | PENDIENTE POR DEFINIR | Confirmar si se incluye en el request OCC                              |
| `numeroDocumento`   | PENDIENTE POR DEFINIR | Confirmar si se incluye en el request OCC                              |

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** El campo `Usrio` del encabezado SOAP se obtiene del JWT — nunca del body del request.
- **RO-03:** `PtcionId` debe ser único por petición.
- **RO-04:** Credenciales en variables de ambiente — nunca hardcodeadas.
- **RO-05:** El número de tarjeta retornado en la respuesta debe estar enmascarado.
- **RO-06:** Los números de tarjeta circulan completos en el flujo funcional (entre ORQ, ADP y servicio bancario). El enmascaramiento se aplica **únicamente en logs** (Elastic): últimos 4 dígitos visibles (ejemplo: `****5678`). Nunca ofuscar el número real en el payload funcional.
- **RO-07:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`). Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU.
- **RO-08:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.

---

## Caminos Alternativos y Excepciones

| ID      | Condición                                     | Comportamiento                                                                                                                                       |
|---------|-----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| ALT-00  | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. Verificación defensiva: el ORQ no debería enrutar operaciones no soportadas a este ADP. |

---

## Tecnología a Usar

| Componente     | Tecnología   | Versión | Nota                                   |
|----------------|--------------|---------|----------------------------------------|
| Lenguaje       | Java         | 21      |                                        |
| Framework      | Spring Boot  | 3.5.13   |                                        |
| Cliente SOAP   | Spring-WS 3.x + JAXB 4.0.2 | 3.x / 4.0.2       | Para `BloquearTarjetaDebitoCarton`     |
| Circuit Breaker| Resilience4j | —       | Activo en todos los consumos externos  |
| Logs           | Elastic      | —       |                                        |
| Mensajería     | AWS SQS FIFO | —       | Cola de auditoría y observabilidad — `avc-everest-pt-logs.fifo` |


---

## Dependencias

| HU         | Relación |
|------------|----------|
| HU-201-ORQ | Padre — `ofic-actualizaciones-orq` |

---

## Preguntas Abiertas

| # | Pregunta                                                                          | Impacto                                         |
|---|-----------------------------------------------------------------------------------|-------------------------------------------------|
| 1 | ¿Cuál es el código de `BloqueoTipo` para cada causal (Robo/Pérdida/Fraude)?       | Define el mapeo en el adaptador                 |
| 2 | ¿Cuál es el valor de `ProductoEstado` para bloqueo definitivo?                    | Define el campo `ProductoEstado` en el request  |
| 3 | ¿El campo `Producto` recibe el número enmascarado o el número completo de TD?     | Define cómo se envía `numeroTarjeta` al SOAP    |
| 4 | ¿Hay conectividad confirmada desde pods AKS hacia BOCC-ACE12 (Datapower OCC)?    | Bloquea pruebas en PT                           |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador OCC — Bloqueo TD Definitivo
  Background:
    Given el adaptador OCC está configurado con credenciales válidas
    And hay conectividad con el BOCC-ACE12 de OCC

  Scenario: Bloqueo exitoso
    Given el adaptador recibe tipoDocumento "CC", numeroDocumento "12345678" y causal "BL01"
    When invoca BloquearTarjetaDebitoCarton en OCC
    Then OCC retorna RtaCod "0000"
    And el adaptador retorna la respuesta normalizada con estadoActual "BLOQUEADA"

  Scenario: Tarjeta no encontrada
    Given el adaptador recibe un numeroTarjeta que no existe en OCC
    When invoca el servicio SOAP
    Then OCC retorna error de tarjeta no encontrada
    And el adaptador retorna 404 al orquestador

  Scenario: Timeout
    Given el servicio OCC no responde en el tiempo configurado
    When el adaptador espera la respuesta
    Then retorna 504 al orquestador
    And registra el evento en Elastic
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

El ADP NO reenvía los headers del ORQ directamente al banco. Para la combinación `BLOQUEO_TD_DEFINITIVO + BOCC`, el ADP determina qué headers requiere el servicio bancario específico y construye únicamente esos.

### Nivel 3 — Headers enviados al banco

#### BLOQUEO_TD_DEFINITIVO → ESB_ACE12_BloqueoCancelacionTarjetaDebito / bloquearTarjetaDebitoCarton (SOAP)

Los headers requeridos por este servicio bancario se obtienen de la documentación técnica del banco (contrato del servicio). El ADP reenvía al banco únicamente los headers definidos en ese contrato — los de valor fijo se configuran como variables de ambiente y los de contexto se propagan desde el request entrante. El ADP no valida su presencia: si el llamador omite un header requerido, el banco retorna el error correspondiente.

---

## Definition of Ready


- [ ] Valores de `BloqueoTipo` y `ProductoEstado` confirmados con OCC para cada causal
- [ ] WSDL del servicio confirmado y accesible
- [ ] Conectividad de red desde AKS hacia BOCC-ACE12 confirmada
- [ ] HU-201-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Cliente SOAP `BloquearTarjetaDebitoCarton` implementado
- [ ] Mapeo causal → BloqueoTipo implementado
- [ ] Encabezado SOAP construido con datos del JWT y contexto de ejecución
- [ ] Número de tarjeta enmascarado en respuesta
- [ ] Manejo de errores y timeouts implementado
- [ ] Pruebas unitarias (cobertura ≥ 90%)
- [ ] Prueba de integración contra OCC en DES o CAL
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada — request y response encolados en cada invocación
