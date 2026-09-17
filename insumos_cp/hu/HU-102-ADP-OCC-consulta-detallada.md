# HU-102-ADP-OCC: Adaptador Banco de Occidente — Consulta Detallada (Cartera / TC / CDT)

## Metadatos

| Campo          | Valor                                                           |
|----------------|-----------------------------------------------------------------|
| ID             | HU-102-ADP-OCC                                                  |
| Épica          | Épica 1 — Consultas P1                                          |
| Componente     | Adaptador OCC — Consulta Detallada                              |
| Microservicio  | `ofic-consultas-adp-bocc`                                       |
| Sprint         | Por definir                                                     |
| Prioridad      | Alta (P1)                                                       |
| Estimación     | Por estimar                                                     |
| Estado         | **Desarrollada**                                                |
| HU Padre       | HU-102-ORQ / HU-103-ORQ / HU-104-ORQ                           |
| Autor          | Por definir                                                     |
| Fecha          | 2026-09-10                                                      |
| Última revisión | 2026-09-10 — creada; reemplaza HU-102-ADP-OCC-cartera-detallada (BLOQUEADA); consolida `CONSULTA_DETALLADA_CARTERA` + `CONSULTA_DETALLADA_TC` + `CONSULTA_DETALLADA_CDT` en un único adaptador T2 Everest; gap técnico de cartera OCC resuelto; operación no soportada: excepción + 400 documentada |

---

> **Reemplaza:** `HU-102-ADP-OCC-cartera-detallada.md` (BLOQUEADA — gap técnico). El servicio Everest T2 cubre DLA, LOC, CCA y CDA en un único endpoint. Las HUs `HU-103-ADP-OCC-tc-detallada` y `HU-104-ADP-OCC-cdt-detallado` quedan DEPRECADAS — ver esas HUs para el historial.

---

## Audiencias

| Rol / Audiencia       | Cómo interactúa                                                                                                          |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------|
| Desarrollador Backend | Implementa el adaptador: invoca T2 `BalanceByProductRequest` del servicio Everest OCC con `AcctId` + `AcctType`         |
| QA / Tester           | Valida la llamada SOAP T2, el mapeo de campos por `AcctType` y el modelo normalizado por tipo de producto               |
| Integrador OCC        | Provee acceso al endpoint Everest `BalanceInquirySvc` y ejemplos de respuesta T2 para DLA, CCA y CDA                   |

---

## Historia de Usuario

**Como** microservicio `ofic-consultas-adp-bocc` (Adaptador Banco de Occidente),
**quiero** recibir las operaciones `CONSULTA_DETALLADA_CARTERA`, `CONSULTA_DETALLADA_TC` o `CONSULTA_DETALLADA_CDT` desde el orquestador `ofic-consultas-orq`,
**para** invocar el servicio Everest `BalanceInquirySvc` / `getBalanceByProduct` (trama T2 por producto) de OCC con el `AcctId` y `AcctType` del producto específico, obtener el detalle de saldos y retornar el resultado normalizado.

---

## Contexto de Negocio

OCC expone la consulta detallada de un producto específico a través del servicio Everest `BalanceInquirySvc` — la trama T2 (`BalanceByProductRequest`) retorna el detalle de saldos de una cuenta identificada por `AcctId + AcctType`. Este servicio cubre las tres operaciones de consulta detallada de P1 usando el mismo endpoint y operación SOAP; únicamente el `AcctType` en el request varía según el tipo de producto.

| Operación                   | `AcctType`(s) cubiertos      | Producto                        |
|-----------------------------|------------------------------|---------------------------------|
| `CONSULTA_DETALLADA_CARTERA` | `DLA`, `LOC`, `LEASO`, `LEASOF` | Crédito, Rotativo, Leasing   |
| `CONSULTA_DETALLADA_TC`     | `CCA`                        | Tarjeta de Crédito              |
| `CONSULTA_DETALLADA_CDT`    | `CDA`                        | CDT                             |

El `AcctId` y `AcctType` del producto a consultar se obtienen de la respuesta de `CONSULTA_PRODUCTOS` T1 (ver **HU-101-ADP-OCC-consulta-productos**) — el front los recibe de ahí y los pasa al ORQ en la solicitud de detallada.

> **GAP RESUELTO:** La HU anterior `HU-102-ADP-OCC-cartera-detallada` estaba bloqueada porque OCC no tenía web service para cartera. El servicio Everest T2 cubre `DLA`, `LOC`, `LEASO` y `LEASOF` en el mismo endpoint.

> **Pendiente con OCC:** Los campos detallados T2 para `DLA`, `CCA` y `CDA` requieren ejemplos de respuesta que OCC debe confirmar. Solo `LOC` y `DDA` están confirmados a partir de los contratos entregados. El servicio y endpoint son comunes para todos.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-consultas-orq` mediante `POST /api/v1/everst/ofi/occ/adp/consulta`: la `operacion` (`CONSULTA_DETALLADA_CARTERA`, `CONSULTA_DETALLADA_TC` o `CONSULTA_DETALLADA_CDT`), los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente, los cuales varían según banco y operación (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** El adaptador invoca `BalanceInquirySvc` / `BalanceInquiryPort` / `getBalanceByProduct` con la trama T2 (`BalanceByProductRequest`) usando `acctId` + `acctType` del producto específico.
- **CA-03:** El adaptador transforma la respuesta T2 al modelo normalizado, incluyendo todos los campos `AcctBal` retornados por el banco para el `AcctType` consultado.
- **CA-04:** Si el servicio Everest retorna error de negocio (StatusCode ≠ 0) o el producto no existe, el adaptador lo mapea a la estructura estándar y lo propaga al orquestador.
- **CA-05:** El adaptador no realiza lógica de negocio adicional — solo invoca y transforma.
- **CA-06:** El ADP no valida los campos de `obj_operacion`. La validación es responsabilidad del servicio del banco.
- **CA-07:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-08:** Si el valor de `operacion` recibido no corresponde a ninguno de los valores que este ADP soporta (`CONSULTA_DETALLADA_CARTERA`, `CONSULTA_DETALLADA_TC`, `CONSULTA_DETALLADA_CDT`), el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ.

---

## Inputs

### Recibidos del Orquestador

El ADP recibe la siguiente información del ORQ (`ofic-consultas-orq`):

```json
{
  "operacion": "CONSULTA_DETALLADA_CARTERA",
  "obj_operacion": {
    "tipoDocumento": "CC",
    "numeroDocumento": "12345678",
    "acctId": "79956499218",
    "acctType": "LOC"
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

| Campo             | Tipo   | Descripción                                                                     | Obligatorio | Ejemplo                          |
|-------------------|--------|---------------------------------------------------------------------------------|-------------|----------------------------------|
| `tipoDocumento`   | String | Tipo de documento del cliente                                                   | SI          | `CC`, `CE`, `NIT`                |
| `numeroDocumento` | String | Número de documento del cliente                                                 | SI          | `12345678`                       |
| `acctId`          | String | Número de cuenta/obligación — obtenido de la respuesta T1 (`CONSULTA_PRODUCTOS`) | SI        | `79956499218`                    |
| `acctType`        | String | Tipo de producto OCC — obtenido de la respuesta T1 (`CONSULTA_PRODUCTOS`)       | SI          | `DLA`, `LOC`, `CCA`, `CDA`, `LEASO`, `LEASOF` |

> `acctId` y `acctType` provienen de la respuesta T1 de `CONSULTA_PRODUCTOS` (**HU-101-ADP-OCC-consulta-productos**). El front los obtiene de ahí y los pasa al ORQ en el request de detallada.

> **Nota:** Los campos de `obj_operacion` son referenciales. El ADP recibe `obj_operacion` como tipo genérico (`Object`) — no valida sus campos internos ni lo implementa como clase Java campo a campo. La validación es responsabilidad del servicio bancario.

---

## Servicio de OCC Invocado

### Trama T2 — Consulta Detallada por Producto

| Tipo | Servicio / Puerto / Operación | Protocolo | Endpoint DES/CAL | Endpoint PRD |
|------|-------------------------------|-----------|------------------|--------------|
| SOAP | `BalanceInquirySvc` / `BalanceInquiryPort` / `getBalanceByProduct` | SOAP 1.1 | `https://boc201.tesdmz.app.bancodeoccidente.net:4805/accounts/BalanceInquiry` | `https://boc201.prddmz.app.bancodeoccidente.net:4805/accounts/BalanceInquiry` |

- **Mensaje de entrada:** `BalanceByProductRequest` (`BalInqRq`)
- **Mensaje de salida:** `BalanceByProductResponse` (`BalInqRs`)
- **Namespace principal:** `urn://grupoaval.com/accounts/v1/`
- **Namespaces IFX:** `urn://grupoaval.com/xsd/ifx/` y `urn://grupoaval.com/xsd/ifx/v2/`
- **WSDL:** `model/BalanceInquiry.wsdl` (mismo que T1 — stubs Java compartidos)

> El endpoint y servicio T2 son idénticos a T1 (**HU-101-ADP-OCC-consulta-productos**). La diferencia está en el mensaje de entrada: T2 usa `BalanceByProductRequest` con `DepAcctId` (`AcctId` + `AcctType`) para identificar un producto específico, mientras T1 usa `BalanceGroupedByProductRequest` con `GovIssueIdent` para obtener todos los productos de un cliente.

---

## Outputs

### Saldos detallados por tipo de producto (T2)

El ADP retorna la lista de `AcctBal` del producto consultado (`PartyAcctRelRec`). Los campos dependen del `AcctType`:

#### AcctType = LOC (Rotativo) — CONFIRMADO

| `AcctBal.BalType`    | Descripción                         |
|----------------------|-------------------------------------|
| `Cupo_aprobado`      | Cupo total aprobado                 |
| `Cupo_disponible`    | Cupo disponible                     |
| `Fecha_limite_pago`  | Fecha límite de pago (`ExpDt`)      |
| `Pago_minimo_fecha`  | Pago mínimo a la fecha              |
| `Saldo_actual`       | Saldo actual utilizado              |

#### AcctType = DDA (Corriente) — CONFIRMADO (referencia técnica; operación detallada no es P1)

| `AcctBal.BalType`             | Descripción                         |
|-------------------------------|-------------------------------------|
| `Saldo_ayer`                  | Saldo del día anterior              |
| `Saldo_disponible`            | Saldo disponible                    |
| `Saldo_canje`                 | Saldo en canje                      |
| `Saldo_actual`                | Saldo actual                        |
| `Cupos_aprobado_sobregiro`    | Cupo aprobado de sobregiro          |
| `Cupo_disponible_sobregiro`   | Cupo disponible de sobregiro        |
| `Disponible_sobregiro_canje`  | Disponible sobregiro en canje       |
| `Cupo_aprobado_canje`         | Cupo aprobado en canje              |
| `Remesas`                     | Remesas                             |
| `Cupo_aprobado_remesas`       | Cupo aprobado de remesas            |
| `Saldo_Congelado_GMF`         | Saldo congelado por GMF             |
| `OverDraftDays`               | Días de sobregiro                   |
| `StatusOverDraft`             | Estado del sobregiro                |

#### AcctType = DLA (Crédito / Cartera) — PENDIENTE CONFIRMAR CON OCC

> Los campos `BalType` específicos para DLA en T2 están pendientes de confirmar. OCC debe proveer un ejemplo de respuesta T2 con `AcctType = DLA`.

#### AcctType = LEASO / LEASOF (Leasing) — PENDIENTE CONFIRMAR CON OCC

> Los campos `BalType` específicos para Leasing en T2 están pendientes. OCC debe proveer ejemplos de respuesta T2 para Leasing Operativo y Financiero.

#### AcctType = CCA (Tarjeta de Crédito) — PENDIENTE CONFIRMAR CON OCC

> Los campos `BalType` específicos para TC en T2 están pendientes de confirmar. OCC debe proveer un ejemplo de respuesta T2 con `AcctType = CCA`.

#### AcctType = CDA (CDT) — PENDIENTE CONFIRMAR CON OCC

> Los campos `BalType` específicos para CDT en T2 están pendientes de confirmar. OCC debe proveer un ejemplo de respuesta T2 con `AcctType = CDA`.

### Mapeo de errores OCC → estructura estándar

| Error OCC                              | Código HTTP | StatusDesc                              |
|----------------------------------------|-------------|------------------------------------------|
| StatusCode ≠ 0 — producto no encontrado | `404`       | "Producto no encontrado en OCC"         |
| StatusCode ≠ 0 — error de negocio      | `206`       | StatusDesc del banco                    |
| Error de conectividad Everest          | `502`       | "Error de conectividad con OCC"         |
| Timeout del servicio SOAP              | `504`       | "Timeout del servicio OCC"              |
| Error interno OCC                      | `502`       | "Error en el servicio del banco"        |

---

## Reglas de Integración

### Identificación de servicio

| operacion                     | X-Destination-Bank | Servicio bancario                                                                                            | `AcctType` esperado          |
|-------------------------------|--------------------|--------------------------------------------------------------------------------------------------------------|------------------------------|
| `CONSULTA_DETALLADA_CARTERA`  | `BOCC`             | `BalanceInquirySvc` / `BalanceInquiryPort` / `getBalanceByProduct` — T2 (`BalanceByProductRequest`)         | `DLA`, `LOC`, `LEASO`, `LEASOF` |
| `CONSULTA_DETALLADA_TC`       | `BOCC`             | `BalanceInquirySvc` / `BalanceInquiryPort` / `getBalanceByProduct` — T2 (`BalanceByProductRequest`)         | `CCA`                        |
| `CONSULTA_DETALLADA_CDT`      | `BOCC`             | `BalanceInquirySvc` / `BalanceInquiryPort` / `getBalanceByProduct` — T2 (`BalanceByProductRequest`)         | `CDA`                        |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo SOAP                   | Valor               | Descripción                                                                             |
|------------------------------|---------------------|-----------------------------------------------------------------------------------------|
| `MsgRqHdr.BankInfo.BankId`   | `0023`              | BankId fijo OCC                                                                         |
| `MsgRqHdr.ClientApp.Name`    | Pendiente confirmar | Confirmar con OCC para canal Oficinas (ejemplos: `PB` y `MB`)                          |
| `MsgRqHdr.Channel`           | Pendiente confirmar | Todos los ejemplos usan `MB` — confirmar si canal Oficinas requiere valor diferente     |
| `MsgRqHdr.Reverse`           | `false`             | Valor fijo                                                                              |
| `MsgRqHdr.Language`          | `es_CO`             | Valor fijo                                                                              |
| `BalInqRq.RqUID`             | Generado            | UUID o número de transacción generado por el ADP para correlación                      |

### Mapeo de campos canal → OCC (T2 Request)

| Campo canal (`obj_operacion`) | Campo SOAP OCC       | Elemento XML                                                                             |
|-------------------------------|----------------------|------------------------------------------------------------------------------------------|
| `tipoDocumento`               | Tipo de documento    | `CustId.GovIssueIdent.GovIssueIdentType` y `MsgRqHdr.UserId.GovIssueIdent.GovIssueIdentType` |
| `numeroDocumento`             | Número de documento  | `CustId.GovIssueIdent.IdentSerialNum` y `MsgRqHdr.UserId.GovIssueIdent.IdentSerialNum` |
| `acctId`                      | Número de cuenta     | `DepAcctId.AcctId`                                                                       |
| `acctType`                    | Tipo de producto     | `DepAcctId.AcctType`                                                                     |

> `CustId.GovIssueIdent.GovOrg` se mapea con el mismo valor que `GovIssueIdentType` del documento (ejemplo del contrato: `GovOrg = CC` cuando `GovIssueIdentType = CC`).

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre `obj_operacion`. Los campos se envían al banco tal como los recibe del ORQ.
- **RO-02:** Credenciales y endpoints configurados por variable de ambiente.
- **RO-03:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`). Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU.
- **RO-04:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.
- **RO-05:** Los números de tarjeta (`acctId` de tipo `CCA`) circulan completos en el flujo funcional. Masking ÚNICAMENTE en logs y auditoría SQS: últimos 4 dígitos visibles (`*******5678`).

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

El ADP NO reenvía los headers del ORQ directamente al banco. Para cada operación detallada + BOCC, el ADP construye los campos de protocolo SOAP requeridos por el contrato Everest y envía únicamente esos.

### Nivel 3 — Headers enviados al banco

#### CONSULTA_DETALLADA_* → BalanceInquirySvc / getBalanceByProduct T2 (SOAP)

Los parámetros de protocolo del mensaje SOAP se derivan del contrato Everest de OCC. Las constantes de mapeo (BankId, Channel, etc.) se configuran como variables de ambiente. Los campos de contexto (tipoDocumento, numeroDocumento, acctId, acctType) se obtienen del request entrante.

---

## Caminos Alternativos y Excepciones

| ID     | Condición                                              | Comportamiento esperado                                                                                |
|--------|--------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| ALT-00 | Valor de `operacion` no esperado por este ADP          | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. Verificación defensiva: el ORQ no debería enrutar operaciones no soportadas a este ADP. |
| ALT-01 | StatusCode ≠ 0 en respuesta Everest (negocio)          | Mapear a estructura estándar y retornar al orquestador                                                |
| ALT-02 | Producto no encontrado en OCC                          | Retorna `404` al orquestador                                                                          |
| EXC-01 | Timeout en la llamada SOAP                             | Retorna `504` al orquestador                                                                          |
| EXC-02 | Error de conectividad con Everest OCC                  | Retorna `502` y registra en Elastic                                                                   |

---

## Tecnología a Usar

| Componente      | Tecnología                  | Versión     | Nota                                                                    |
|-----------------|-----------------------------|-------------|-------------------------------------------------------------------------|
| Lenguaje        | Java                        | 21          |                                                                         |
| Framework       | Spring Boot                 | 3.5.13      |                                                                         |
| Cliente SOAP    | Spring-WS 3.x + JAXB 4.0.2 | 3.x / 4.0.2 | Para `BalanceInquirySvc` T2 (Everest) — stubs compartidos con T1        |
| Circuit Breaker | Resilience4j                | —           | Aplicado a todos los consumos SOAP externos                             |
| Logs            | Elastic                     | —           |                                                                         |
| Mensajería      | AWS SQS FIFO                | —           | Cola de auditoría y observabilidad — `avc-everest-pt-logs.fifo`         |

---

## Dependencias

### HUs relacionadas

| HU / Componente                   | Relación      | Descripción                                                                                     |
|-----------------------------------|---------------|-------------------------------------------------------------------------------------------------|
| `ofic-consultas-orq`              | Padre         | Orquestador que invoca este adaptador (HU-102-ORQ, HU-103-ORQ, HU-104-ORQ)                    |
| HU-101-ADP-OCC-consulta-productos | Prerequisito  | Provee `AcctId` y `AcctType` que se usan como input en esta HU (T1 → T2)                       |

### Servicios externos (OCC)

| Servicio                                                           | Tipo | Endpoint DES/CAL                                                                     | Endpoint PRD                                                                      |
|--------------------------------------------------------------------|------|--------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| `BalanceInquirySvc` / `BalanceInquiryPort` / `getBalanceByProduct` | SOAP | `https://boc201.tesdmz.app.bancodeoccidente.net:4805/accounts/BalanceInquiry`       | `https://boc201.prddmz.app.bancodeoccidente.net:4805/accounts/BalanceInquiry`    |

---

## Preguntas Abiertas

| # | Pregunta                                                                                                | Impacto                                                    |
|---|---------------------------------------------------------------------------------------------------------|------------------------------------------------------------|
| 1 | ¿Cuáles son los campos `AcctBal.BalType` que retorna T2 para `AcctType = DLA`?                         | Bloquea documentación y pruebas para `CONSULTA_DETALLADA_CARTERA` con crédito |
| 2 | ¿Cuáles son los campos `AcctBal.BalType` que retorna T2 para `AcctType = CCA`?                         | Bloquea documentación y pruebas para `CONSULTA_DETALLADA_TC` |
| 3 | ¿Cuáles son los campos `AcctBal.BalType` que retorna T2 para `AcctType = CDA`?                         | Bloquea documentación y pruebas para `CONSULTA_DETALLADA_CDT` |
| 4 | ¿`AcctType = LEASO` y `LEASOF` tienen respuesta T2 con los mismos campos que DLA, o diferentes?        | Afecta el modelo de respuesta para leasing                 |
| 5 | ¿Qué valor usar para `ClientApp.Name` y `Channel` en canal Oficinas?                                   | Afecta mapeo de constantes                                 |
| 6 | ¿Hay conectividad de red desde los ambientes del canal Oficinas hacia el endpoint Everest OCC?          | Bloquea pruebas en PT                                      |
| 7 | ¿Cuál es el mecanismo de autenticación del endpoint Everest (certificado mTLS, WS-Security, token)?     | Bloquea implementación                                     |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador OCC — Consulta Detallada T2 Everest (Cartera / TC / CDT)
  Como adaptador de Banco de Occidente
  Quiero invocar el servicio Everest T2 con AcctId + AcctType del producto
  Para retornar el detalle de saldos del producto al orquestador

  Background:
    Given el adaptador OCC está configurado con credenciales válidas
    And hay conectividad con el servicio Everest BalanceInquirySvc de OCC

  Scenario: Consulta detallada exitosa — Rotativo (LOC)
    Given el adaptador recibe operacion "CONSULTA_DETALLADA_CARTERA", acctId "79956499218" y acctType "LOC"
    When invoca getBalanceByProduct T2 en OCC
    Then obtiene AcctBal con Cupo_aprobado, Cupo_disponible, Fecha_limite_pago, Pago_minimo_fecha y Saldo_actual
    And retorna la respuesta al orquestador con StatusCode 200

  Scenario: Consulta detallada exitosa — Tarjeta de Crédito (CCA)
    Given el adaptador recibe operacion "CONSULTA_DETALLADA_TC", acctId "4899250012682818" y acctType "CCA"
    When invoca getBalanceByProduct T2 en OCC
    Then obtiene la lista de AcctBal del producto CCA
    And retorna la respuesta al orquestador con StatusCode 200

  Scenario: Producto no encontrado
    Given el servicio Everest T2 retorna StatusCode de producto no encontrado
    When el adaptador procesa el error
    Then retorna 404 al orquestador

  Scenario: operacion no soportada por este ADP
    Given el adaptador recibe una operacion distinta de CONSULTA_DETALLADA_CARTERA, CONSULTA_DETALLADA_TC y CONSULTA_DETALLADA_CDT
    When el adaptador verifica la operacion
    Then lanza IllegalArgumentException y retorna 400 al ORQ

  Scenario: Timeout en servicio OCC
    Given el servicio SOAP de OCC no responde en el tiempo configurado
    When el adaptador espera la respuesta
    Then retorna 504 al orquestador
    And registra el evento en Elastic
```

---

## Notas Técnicas

- El WSDL `model/BalanceInquiry.wsdl` es compartido por T1 y T2. Los stubs Java generados para **HU-101-ADP-OCC-consulta-productos** incluyen también las clases de T2 — no se requiere un WSDL separado.
- Los `acctId` de tipo `CCA` (tarjetas de crédito) son números de 16 dígitos. Aplicar masking en logs y SQS — últimos 4 dígitos visibles (`*******5678`).
- El campo `CustId.GovIssueIdent.GovOrg` en el request T2 se mapea con el mismo valor que `GovIssueIdentType` (ejemplo del contrato: `GovOrg = CC` cuando `GovIssueIdentType = CC`).
- El flujo T1 → T2 es el flujo normal de consulta detallada: el asesor primero invoca `CONSULTA_PRODUCTOS` (T1) para obtener la lista de productos con sus `AcctId` y `AcctType`, luego selecciona un producto y el front invoca `CONSULTA_DETALLADA_*` (T2) pasando el `AcctId` + `AcctType` del producto seleccionado.

---

## Definition of Ready

> La HU puede entrar a sprint solo cuando los ítems marcados con (*) están cumplidos. Los ítems de confirmación de campos por AcctType pueden quedar pendientes para el tipo específico a implementar en ese sprint.

- [ ] (*) WSDL `BalanceInquiry.wsdl` de Everest OCC obtenido y procesable
- [ ] (*) Mecanismo de autenticación del endpoint Everest confirmado
- [ ] (*) Conectividad de red desde pods AKS hacia endpoint Everest OCC confirmada en PT
- [ ] (*) Valores de `ClientApp.Name` y `Channel` para canal Oficinas confirmados con OCC
- [ ] (*) HU-101-ADP-OCC-consulta-productos en estado "En desarrollo" o "Completada" (prerequisito funcional — T1 provee los AcctId/AcctType)
- [ ] Campos T2 confirmados para `DLA` (cartera) — necesario para completar `CONSULTA_DETALLADA_CARTERA` con crédito
- [ ] Campos T2 confirmados para `CCA` (TC) — necesario para completar `CONSULTA_DETALLADA_TC`
- [ ] Campos T2 confirmados para `CDA` (CDT) — necesario para completar `CONSULTA_DETALLADA_CDT`
- [ ] Modelo de respuesta normalizado definido y acordado con el orquestador
- [ ] HU-102-ORQ, HU-103-ORQ y HU-104-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación de story points asignada por el equipo
- [ ] Aprobada por líder técnico y product owner

---

## Definition of Done

- [ ] WSDL de Everest OCC obtenido y stubs Java generados (compartidos con HU-101-ADP-OCC-consulta-productos)
- [ ] Conectividad de red con Everest OCC confirmada en PT
- [ ] Implementación de la llamada SOAP T2 a `getBalanceByProduct` para los AcctTypes confirmados
- [ ] Mapeo de respuesta T2 → modelo normalizado implementado para cada AcctType cubierto
- [ ] Masking de `acctId` para `CCA` en logs y SQS — validado en pruebas
- [ ] Pruebas unitarias (cobertura ≥ 90%)
- [ ] Prueba de integración contra Everest OCC en PT para al menos un AcctType confirmado
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada — request y response encolados en cada invocación
