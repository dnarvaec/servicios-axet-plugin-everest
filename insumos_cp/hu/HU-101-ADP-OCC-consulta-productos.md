# HU-101-ADP-OCC: Adaptador Banco de Occidente — Consulta de Productos

## Metadatos

| Campo          | Valor                                                  |
|----------------|--------------------------------------------------------|
| ID             | HU-101-ADP-OCC                                         |
| Épica          | Épica 1 — Consultas P1                                 |
| Componente     | Adaptador OCC — Consulta Productos                     |
| Microservicio  | `ofic-consultas-adp-bocc`                              |
| Sprint         | Por definir                                            |
| Prioridad      | Alta (P1)                                              |
| Estimación     | Por estimar                                            |
| Estado         | **Desarrollada**                                       |
| HU Padre       | HU-101-ORQ                                             |
| Autor          | Por definir                                            |
| Fecha          | 2026-08-19                                             |
| Última revisión | 2026-09-10 — servicio actualizado a T1 Everest `BalanceGroupedByProductRequest` (reemplaza `ESB_ACE12_ConsultaDeProductos`); endpoint y namespace IFX documentados; respuesta incluye `AcctId`+`AcctType` por producto (obligatorios — requeridos como input por T2/detalladas) |

---

## Audiencias

| Rol / Audiencia       | Cómo interactúa                                                                                                   |
|-----------------------|-------------------------------------------------------------------------------------------------------------------|
| Desarrollador Backend | Implementa el adaptador: invoca T1 `BalanceGroupedByProductRequest` del servicio Everest OCC y transforma la respuesta |
| QA / Tester           | Valida la llamada SOAP al servicio Everest OCC, el namespace IFX y el mapeo de campos                            |
| Integrador OCC        | Provee acceso al endpoint Everest `BalanceInquirySvc` / `BalanceInquiryPort` en los ambientes DES/CAL/PRD         |

---

## Historia de Usuario

**Como** microservicio `ofic-consultas-adp-bocc` (Adaptador Banco de Occidente),
**quiero** recibir la operación `CONSULTA_PRODUCTOS` desde el orquestador `ofic-consultas-orq`,
**para** invocar el servicio Everest `BalanceInquirySvc` / `getBalanceByProduct` (trama T1 agrupada) de OCC, obtener el resumen de todos los productos del cliente y retornar el resultado al orquestador.

---

## Contexto de Negocio

OCC expone la consulta de productos del cliente a través del servicio Everest `BalanceInquirySvc` — la trama T1 (`BalanceGroupedByProductRequest`) retorna todos los productos agrupados por tipo para un cliente identificado por documento. Este servicio reemplaza el legacy `ESB_ACE12_ConsultaDeProductos` que pasaba por el middleware BOCC-ACE12.

La respuesta T1 incluye para cada producto: `AcctId` (número de cuenta/obligación), `AcctType` (tipo de producto según catálogo OCC), un saldo resumen (`AcctBal`) y la fecha del último movimiento. El `AcctId` + `AcctType` de cada producto son el input requerido para la consulta detallada T2 (ver **HU-102-ADP-OCC-consulta-detallada**).

> **Nota:** La consulta de datos del cliente (nombre, segmento) es un servicio separado — ver `HU-101-ADP-OCC-consulta-cliente.md` (operación `CONSULTA_CLIENTE`).

> **Nota:** Los productos de tipo `LEASO` y `LEASOF` (Leasing) se incluyen en el resumen T1. Créditos con número de obligación que empieza en 180 o 190 son Leasing según el catálogo OCC.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-consultas-orq` mediante `POST /api/v1/everst/ofi/occ/adp/consulta`: la `operacion = CONSULTA_PRODUCTOS`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente, los cuales varían según banco y operación (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** El adaptador invoca `BalanceInquirySvc` / `BalanceInquiryPort` / `getBalanceByProduct` con la trama T1 (`BalanceGroupedByProductRequest`) usando el documento del cliente para obtener todos los productos agrupados.
- **CA-03:** El adaptador retorna la lista de productos al ORQ — cada producto incluye: `AcctId`, `AcctType`, saldo resumen (`AcctBal`) y fecha del último movimiento. Los campos `AcctId` y `AcctType` son **obligatorios** en la respuesta: son el input necesario para la consulta detallada T2 (**HU-102-ADP-OCC-consulta-detallada**).
- **CA-04:** Si el servicio Everest retorna error de negocio (StatusCode ≠ 0), el adaptador lo mapea a la estructura estándar y lo propaga al orquestador.
- **CA-05:** El adaptador no realiza lógica de negocio adicional — solo invoca y transforma.
- **CA-06:** El ADP no valida los campos de `obj_operacion`. La validación es responsabilidad del servicio del banco.
- **CA-07:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-08:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

---

## Inputs

### Recibidos del Orquestador

El ADP recibe la siguiente información del ORQ (`ofic-consultas-orq`):

```json
{
  "operacion": "CONSULTA_PRODUCTOS",
  "obj_operacion": {
    "tipoDocumento": "CC",
    "numeroDocumento": "12345678"
  }
}
```

> Los campos `X-Origin-Bank` y `X-Destination-Bank` se reciben como HTTP headers.

| Campo | Tipo | Descripción | Obligatorio |
|---|---|---|---|
| `operacion` | `OperacionEnum` | Identificador de la operación. Junto con `X-Destination-Bank` determina el servicio bancario a invocar. Recibido como `OperacionEnum` desde el ORQ — no re-parsear el String. Ver definición completa en **HU-101-ORQ** | SI |
| `X-Origin-Bank` | String (header) | Banco de origen | SI |
| `X-Destination-Bank` | String (header) | Banco destino (`BOCC`) | SI |
| `obj_operacion` | Object | Campos funcionales | SI |

**Campos de `obj_operacion`:**

| Campo             | Tipo   | Descripción                        | Obligatorio | Ejemplo             |
|-------------------|--------|------------------------------------|-------------|---------------------|
| `tipoDocumento`   | String | Tipo de documento del cliente      | SI          | `CC`, `CE`, `NIT`   |
| `numeroDocumento` | String | Número de documento del cliente    | SI          | `12345678`          |

> **Nota:** Los campos de `obj_operacion` son referenciales. El ADP recibe `obj_operacion` como tipo genérico (`Object`) — no valida sus campos internos ni lo implementa como clase Java campo a campo. La validación es responsabilidad del servicio bancario.

---

## Servicio de OCC Invocado

### Trama T1 — Consulta Agrupada de Productos

| Tipo | Servicio / Puerto / Operación | Protocolo | Endpoint DES/CAL | Endpoint PRD |
|------|-------------------------------|-----------|------------------|--------------|
| SOAP | `BalanceInquirySvc` / `BalanceInquiryPort` / `getBalanceByProduct` | SOAP 1.1 | `https://boc201.tesdmz.app.bancodeoccidente.net:4805/accounts/BalanceInquiry` | `https://boc201.prddmz.app.bancodeoccidente.net:4805/accounts/BalanceInquiry` |

- **Mensaje de entrada:** `BalanceGroupedByProductRequest` (`BalGroupedInqRq`)
- **Mensaje de salida:** `BalanceGroupedByProductResponse` (`BalGroupedInqRs`)
- **Namespace principal:** `urn://grupoaval.com/accounts/v1/`
- **Namespaces IFX:** `urn://grupoaval.com/xsd/ifx/` y `urn://grupoaval.com/xsd/ifx/v2/`
- **WSDL:** `model/BalanceInquiry.wsdl`

---

## Outputs

### Productos retornados al ORQ

El ADP retorna la lista de productos del cliente. Por cada producto (`ProductType`):

| Campo        | Origen SOAP                       | Descripción                                                                     |
|--------------|-----------------------------------|---------------------------------------------------------------------------------|
| `acctId`     | `DepAcctId.AcctId`                | Número de cuenta/obligación — **obligatorio; requerido como input por T2**      |
| `acctType`   | `DepAcctId.AcctType`              | Tipo de producto OCC — **obligatorio; requerido como input por T2**             |
| `acctCur`    | `DepAcctId.AcctCur`               | Moneda (`COP`)                                                                  |
| `balType`    | `AcctBal.BalType`                 | Tipo de saldo resumen (depende del `AcctType` — ver tabla siguiente)            |
| `balAmount`  | `AcctBal.CurAmt.Amt`              | Monto del saldo resumen                                                         |
| `lastTrnDt`  | `LastTrnDt`                       | Fecha del último movimiento                                                     |
| `statusCode` | `Status.StatusCode`               | Código de estado del producto (`0` = exitoso)                                   |

**Saldo resumen por tipo de producto (AcctBal en T1):**

| AcctType | Producto                              | `BalType` en T1         | Estado         |
|----------|---------------------------------------|-------------------------|----------------|
| DDA      | Corriente                             | `Saldo_actual`          | Confirmado     |
| SDA      | Ahorros                               | Pendiente confirmar     | —              |
| KBO      | Kubo                                  | Pendiente confirmar     | —              |
| AFC      | AFC                                   | Pendiente confirmar     | —              |
| DLA      | Crédito / Cartera                     | `Saldo_fecha`           | Confirmado     |
| LEASO    | Leasing Operativo                     | Pendiente confirmar     | —              |
| LEASOF   | Leasing Financiero                    | Pendiente confirmar     | —              |
| LOC      | Rotativo                              | `Cupo_disponible`       | Confirmado     |
| CCA      | Tarjeta de Crédito                    | `Pago_total`            | Confirmado     |
| CDA      | CDT                                   | Pendiente confirmar     | —              |
| DDAEUR   | Corriente Moneda Extranjera (EUR)     | Pendiente confirmar     | —              |
| DDAUSD   | Corriente Moneda Extranjera (USD)     | Pendiente confirmar     | —              |

> Confirmados a partir del contrato T1 entregado por OCC: DDA, DLA, LOC, CCA. Los demás están en el catálogo pero sin ejemplo de respuesta T1 disponible.

### Mapeo de errores OCC → estructura estándar

| Error OCC                               | Código HTTP | StatusDesc                              |
|-----------------------------------------|-------------|-----------------------------------------|
| StatusCode ≠ 0 — cliente no encontrado  | `206`        | "Cliente no encontrado en OCC"          |
| StatusCode ≠ 0 — sin productos          | `206`        | "El cliente no tiene productos en OCC"  |
| Error de conectividad Everest           | `502`        | "Error de conectividad con OCC"         |
| Timeout del servicio SOAP               | `504`        | "Timeout del servicio OCC"              |
| Error interno OCC                       | `502`        | "Error en el servicio del banco"        |

---

## Reglas de Integración

### Identificación de servicio

| operacion            | X-Destination-Bank | Servicio bancario                                                                                              |
|----------------------|--------------------|---------------------------------------------------------------------------------------------------------------|
| `CONSULTA_PRODUCTOS` | `BOCC`             | `BalanceInquirySvc` / `BalanceInquiryPort` / `getBalanceByProduct` — Trama T1 (`BalanceGroupedByProductRequest`) |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo SOAP                           | Valor                  | Descripción                                                                                          |
|--------------------------------------|------------------------|------------------------------------------------------------------------------------------------------|
| `MsgRqHdr.BankInfo.BankId`           | `0023`                 | BankId fijo OCC                                                                                      |
| `MsgRqHdr.ClientApp.Name`            | Pendiente confirmar    | Valor en ejemplos: `PB` (T1/AFC) y `MB` (T2/LOC) — confirmar cuál usar para canal Oficinas          |
| `MsgRqHdr.Channel`                   | Pendiente confirmar    | Todos los ejemplos usan `MB` — confirmar si canal Oficinas requiere un valor diferente               |
| `MsgRqHdr.Reverse`                   | `false`                | Valor fijo                                                                                           |
| `MsgRqHdr.Language`                  | `es_CO`                | Valor fijo                                                                                           |
| `BalGroupedInqRq.RqUID`              | Generado               | UUID o número de transacción generado por el ADP para correlación                                    |

### Mapeo de campos canal → OCC (T1 Request)

| Campo canal (`obj_operacion`) | Campo SOAP OCC       | Elemento XML                                           |
|-------------------------------|----------------------|--------------------------------------------------------|
| `tipoDocumento`               | Tipo de documento    | `MsgRqHdr.UserId.GovIssueIdent.GovIssueIdentType`     |
| `numeroDocumento`             | Número de documento  | `MsgRqHdr.UserId.GovIssueIdent.IdentSerialNum`        |

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre `obj_operacion`. Los campos se envían al banco tal como los recibe del ORQ.
- **RO-02:** Credenciales y endpoints configurados por variable de ambiente.
- **RO-03:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`). Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU.
- **RO-04:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.
- **RO-05:** La respuesta debe incluir `AcctId` y `AcctType` por cada producto — son el input requerido por la consulta detallada T2 (**HU-102-ADP-OCC-consulta-detallada**). No omitirlos del modelo de respuesta normalizado.

---

## Gestión de Headers

### Nivel 1 — Headers recibidos del ORQ

El ADP recibe del ORQ los siguientes headers de contexto, propagados sin modificación:

| Header               | Descripción                             |
|----------------------|-----------------------------------------|
| `Authorization`      | Bearer JWT del asesor                   |
| `X-Trace-Id`         | ID de traza para correlación de logs    |
| `X-Origin-Bank`      | Banco de origen de la operación         |
| `X-Destination-Bank` | Confirma que el banco destino es `BOCC` |

### Nivel 2 — Selección y transformación en el ADP

El ADP NO reenvía los headers del ORQ directamente al banco. Para `CONSULTA_PRODUCTOS + BOCC`, el ADP construye los campos de protocolo SOAP requeridos por el contrato Everest y envía únicamente esos.

### Nivel 3 — Headers enviados al banco

#### CONSULTA_PRODUCTOS → BalanceInquirySvc / getBalanceByProduct T1 (SOAP)

Los parámetros de protocolo del mensaje SOAP se derivan del contrato Everest de OCC. Las constantes de mapeo (BankId, Channel, etc.) se configuran como variables de ambiente. Los campos de contexto (tipoDocumento, numeroDocumento) se obtienen del request entrante.

---

## Caminos Alternativos y Excepciones

| ID     | Condición                                              | Comportamiento esperado                                                                                |
|--------|--------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| ALT-00 | Valor de `operacion` no esperado por este ADP          | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. Verificación defensiva: el ORQ no debería enrutar operaciones no soportadas a este ADP. |
| ALT-01 | StatusCode ≠ 0 en respuesta Everest (negocio)          | Mapear a estructura estándar y retornar al orquestador                                                |
| ALT-02 | Cliente sin productos en OCC                           | Retorna código de negocio de OCC (lista vacía o StatusCode específico)                                |
| EXC-01 | Timeout en la llamada SOAP                             | Retorna `504` al orquestador                                                                          |
| EXC-02 | Error de conectividad con Everest OCC                  | Retorna `502` y registra en Elastic                                                                   |

---

## Tecnología a Usar

| Componente      | Tecnología                         | Versión     | Nota                                                                    |
|-----------------|------------------------------------|-------------|-------------------------------------------------------------------------|
| Lenguaje        | Java                               | 21          |                                                                         |
| Framework       | Spring Boot                        | 3.5.13      |                                                                         |
| Cliente SOAP    | Spring-WS 3.x + JAXB 4.0.2        | 3.x / 4.0.2 | Para `BalanceInquirySvc` T1 (Everest)                                   |
| Circuit Breaker | Resilience4j                       | —           | Aplicado a todos los consumos SOAP externos                             |
| Logs            | Elastic                            | —           |                                                                         |
| Mensajería      | AWS SQS FIFO                       | —           | Cola de auditoría y observabilidad — `avc-everest-pt-logs.fifo`         |

---

## Dependencias

### HUs relacionadas

| HU / Componente                      | Relación      | Descripción                                                                          |
|--------------------------------------|---------------|--------------------------------------------------------------------------------------|
| `ofic-consultas-orq`                 | Padre         | Orquestador que invoca este adaptador                                                |
| HU-101-ADP-OCC-consulta-cliente      | Complementaria | Adaptador para `CONSULTA_CLIENTE` OCC                                               |
| HU-102-ADP-OCC-consulta-detallada    | Dependiente   | Usa `AcctId` + `AcctType` de la respuesta de esta HU como input para T2             |

### Servicios externos (OCC)

| Servicio                                                          | Tipo | Endpoint DES/CAL                                                                     | Endpoint PRD                                                                       |
|-------------------------------------------------------------------|------|--------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| `BalanceInquirySvc` / `BalanceInquiryPort` / `getBalanceByProduct` | SOAP | `https://boc201.tesdmz.app.bancodeoccidente.net:4805/accounts/BalanceInquiry`       | `https://boc201.prddmz.app.bancodeoccidente.net:4805/accounts/BalanceInquiry`     |

---

## Preguntas Abiertas

| # | Pregunta                                                                                                                | Impacto                                   |
|---|-------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| 1 | ¿Qué valor usar para `ClientApp.Name` en el canal Oficinas? Ejemplos: `PB` (T1/AFC) y `MB` (T2/LOC)                  | Afecta mapeo de constantes                |
| 2 | ¿Qué valor usar para `Channel` en el canal Oficinas? Todos los ejemplos usan `MB`                                      | Afecta mapeo de constantes                |
| 3 | ¿Cuál es el `BalType` de saldo resumen T1 para: SDA, KBO, AFC, LEASO, LEASOF, CDA?                                    | Afecta el modelo de respuesta             |
| 4 | ¿Hay conectividad de red desde los ambientes del canal Oficinas hacia el endpoint Everest OCC?                         | Bloquea pruebas en PT                     |
| 5 | ¿Cuál es el mecanismo de autenticación del endpoint Everest (certificado mTLS, WS-Security, token)?                    | Bloquea implementación                    |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador OCC — Consulta de Productos (T1 Everest)
  Como adaptador de Banco de Occidente
  Quiero invocar el servicio Everest T1 de productos de OCC
  Para retornar el resumen de todos los productos del cliente al orquestador

  Background:
    Given el adaptador OCC está configurado con credenciales válidas
    And hay conectividad con el servicio Everest BalanceInquirySvc de OCC

  Scenario: Consulta exitosa de productos
    Given el adaptador recibe tipoDocumento "CC" y numeroDocumento "12345678"
    When invoca getBalanceByProduct T1 en OCC
    Then obtiene la lista de ProductType con AcctId, AcctType y saldo resumen por producto
    And retorna la respuesta al orquestador con StatusCode 200

  Scenario: Cliente sin productos
    Given el servicio Everest T1 retorna lista vacía de ProductType
    When el adaptador procesa la respuesta
    Then retorna la lista vacía al orquestador

  Scenario: Error de negocio en Everest
    Given el servicio Everest retorna StatusCode distinto de 0
    When el adaptador procesa el error
    Then retorna el error mapeado al orquestador

  Scenario: Timeout en servicio OCC
    Given el servicio SOAP de OCC no responde en el tiempo configurado
    When el adaptador espera la respuesta
    Then retorna 504 al orquestador
    And registra el evento en Elastic
```

---

## Notas Técnicas

- El servicio Everest usa SOAP 1.1 con namespaces IFX Grupo Aval (`urn://grupoaval.com/accounts/v1/` y los namespaces IFX). Verificar que los stubs Java se generen con los namespaces correctos desde el WSDL `model/BalanceInquiry.wsdl`.
- El mismo WSDL aplica para T1 y T2 — los stubs generados para esta HU son reutilizados por **HU-102-ADP-OCC-consulta-detallada**.
- El `AcctId` y `AcctType` por producto son obligatorios en el modelo de respuesta normalizado — son el input que el front debe pasar en la solicitud de consulta detallada T2.

---

## Definition of Ready

> La HU puede entrar a sprint solo cuando **todos** los ítems están cumplidos.

- [ ] WSDL `BalanceInquiry.wsdl` de Everest OCC obtenido y procesable
- [ ] Mecanismo de autenticación del endpoint Everest confirmado (certificado mTLS, WS-Security, token)
- [ ] Conectividad de red desde pods AKS hacia endpoint Everest OCC confirmada en PT
- [ ] Valores de `ClientApp.Name` y `Channel` para canal Oficinas confirmados con OCC
- [ ] `BalType` de saldo resumen T1 confirmado para SDA, KBO, AFC, LEASO, LEASOF, CDA
- [ ] Modelo de respuesta normalizada definido y acordado con el orquestador
- [ ] HU-101-ORQ (`ofic-consultas-orq`) en estado "En desarrollo" o "Completada"
- [ ] Estimación de story points asignada por el equipo
- [ ] Aprobada por líder técnico y product owner

---

## Definition of Done

- [ ] WSDL de Everest OCC obtenido y stubs Java generados (reutilizados por HU-102-ADP-OCC-consulta-detallada)
- [ ] Conectividad de red con Everest OCC confirmada en PT
- [ ] Implementación de la llamada SOAP T1 a `getBalanceByProduct`
- [ ] Respuesta incluye `AcctId` y `AcctType` por cada producto
- [ ] Pruebas unitarias (cobertura ≥ 90%)
- [ ] Prueba de integración contra Everest OCC en PT
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada — request y response encolados en cada invocación
