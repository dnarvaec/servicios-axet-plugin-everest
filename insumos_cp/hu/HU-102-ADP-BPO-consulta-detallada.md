# HU-102-ADP-BPO: Adaptador Banco Popular — Consulta Detallada (TC / CDT / Ahorro / Corriente)

## Metadatos

| Campo          | Valor                                                           |
|----------------|-----------------------------------------------------------------|
| ID             | HU-102-ADP-BPO                                                  |
| Épica          | Épica 1 — Consultas P1                                          |
| Componente     | Adaptador BPO — Consulta Detallada                              |
| Microservicio  | `ofic-consultas-adp-bpop`                                       |
| Sprint         | Por definir                                                     |
| Prioridad      | Alta (P1)                                                       |
| Estimación     | Por estimar                                                     |
| Estado         | **Parcial** — TC y CDT implementados; CARTERA pendiente AcctType BPO |
| HU Padre       | HU-102-ORQ / HU-103-ORQ / HU-104-ORQ                           |
| Autor          | Por definir                                                     |
| Fecha          | 2026-09-14                                                      |
| Última revisión | 2026-09-14 — creada; reemplaza HU-102-ADP-BPO-cartera-detallada (DEPRECADO), HU-103-ADP-BPO-tc-detallada (DEPRECADO) y HU-104-ADP-BPO-cdt-detallado (DEPRECADO); consolida `CONSULTA_DETALLADA_TC` + `CONSULTA_DETALLADA_CDT` en un único adaptador T2 Everest; gap de cartera BPO documentado como pendiente confirmación AcctType; canal "Oficinas Aval" pendiente de control de cambios en ESB/BUS |

---

> **Reemplaza:** `HU-102-ADP-BPO-cartera-detallada.md`, `HU-103-ADP-BPO-tc-detallada.md` y `HU-104-ADP-BPO-cdt-detallado.md` (todas DEPRECADAS). El servicio Everest T2 de BPO cubre `CCA` (TC) y `CDT` (FlexCube) en un único endpoint. `CONSULTA_DETALLADA_CARTERA` está pendiente de confirmar AcctType con BPO (no identificado en el contrato T2 entregado).

---

## Audiencias

| Rol / Audiencia       | Cómo interactúa                                                                                                          |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------|
| Desarrollador Backend | Implementa el adaptador: invoca T2 `BalanceByProductRequest` del servicio Everest BPO con `AcctId` + `AcctType`         |
| QA / Tester           | Valida la llamada SOAP T2, el mapeo de campos por `AcctType` y el modelo normalizado por tipo de producto               |
| Integrador BPO        | Provee acceso al endpoint Everest `BalanceInquirySvc` y ejemplos de respuesta T2 para CCA y CDT                        |

---

## Historia de Usuario

**Como** microservicio `ofic-consultas-adp-bpop` (Adaptador Banco Popular),
**quiero** recibir las operaciones `CONSULTA_DETALLADA_TC` o `CONSULTA_DETALLADA_CDT` desde el orquestador `ofic-consultas-orq`,
**para** invocar el servicio Everest `BalanceInquirySvc` / `getBalanceByProduct` (trama T2 por producto) de BPO con el `AcctId` y `AcctType` del producto específico, obtener el detalle de saldos y retornar el resultado normalizado.

---

## Contexto de Negocio

BPO expone la consulta detallada de un producto específico a través del servicio Everest `BalanceInquirySvc` — la trama T2 (`BalanceByProductRequest`) retorna el detalle de saldos de una cuenta identificada por `AcctId + AcctType`. El servicio cubre TC (`CCA`) y CDT (`CDT` via FlexCube) en el mismo endpoint y operación SOAP.

| Operación                    | `AcctType`(s) cubiertos | Producto              | Estado           |
|------------------------------|-------------------------|-----------------------|------------------|
| `CONSULTA_DETALLADA_TC`      | `CCA`                   | Tarjeta de Crédito    | Confirmado       |
| `CONSULTA_DETALLADA_CDT`     | `CDT`                   | CDT (FlexCube)        | Confirmado       |
| `CONSULTA_DETALLADA_CARTERA` | Pendiente confirmar     | Cartera/Crédito       | **PENDIENTE BPO** |

El `AcctId` y `AcctType` del producto a consultar se obtienen de la respuesta de `CONSULTA_PRODUCTOS` T1 (ver **HU-101-ADP-BPO-consulta-productos**) — el front los recibe de ahí y los pasa al ORQ en la solicitud de detallada.

> **Canal "Oficinas Aval":** La incorporación del canal Oficinas en T2 requiere control de cambios en ESB/BUS de BPO (acuerdo 04/09/2026 con Cristian Chayanne Gomez Ortega). El valor del campo `Channel` para este canal está pendiente de definición.

> **Gap cartera BPO:** El contrato T2 entregado por BPO documenta `SDA`, `DDA`, `CCA` y `CDT` como AcctTypes soportados. No se identifica un AcctType equivalente a cartera/crédito (como `DLA` en OCC). BPO debe confirmar si existe AcctType para cartera en T2 o si la consulta detallada de cartera va por un servicio diferente.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-consultas-orq` mediante `POST /api/v1/everst/ofi/bpop/adp/consulta`: la `operacion` (`CONSULTA_DETALLADA_TC` o `CONSULTA_DETALLADA_CDT`), los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente, los cuales varían según banco y operación (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** El adaptador invoca `BalanceInquirySvc` / `BalanceInquiryPort` / `getBalanceByProduct` con la trama T2 (`BalanceByProductRequest`) usando `acctId` + `acctType` del producto específico.
- **CA-03:** El adaptador transforma la respuesta T2 al modelo normalizado, incluyendo todos los campos `AcctBal` retornados por el banco para el `AcctType` consultado.
- **CA-04:** Si el servicio Everest retorna error de negocio (StatusCode ≠ 0) o el producto no existe, el adaptador lo mapea a la estructura estándar y lo propaga al orquestador.
- **CA-05:** El adaptador no realiza lógica de negocio adicional — solo invoca y transforma.
- **CA-06:** El ADP no valida los campos de `obj_operacion`. La validación es responsabilidad del servicio del banco.
- **CA-07:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-08:** Si el valor de `operacion` recibido no corresponde a ninguno de los valores que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ.

---

## Inputs

### Recibidos del Orquestador

El ADP recibe la siguiente información del ORQ (`ofic-consultas-orq`):

```json
{
  "operacion": "CONSULTA_DETALLADA_TC",
  "obj_operacion": {
    "tipoDocumento": "CC",
    "numeroDocumento": "12345678",
    "acctId": "5391689991756210",
    "acctType": "CCA"
  }
}
```

> Los campos `X-Origin-Bank` y `X-Destination-Bank` se reciben como HTTP headers.

| Campo | Tipo | Descripción | Obligatorio |
|---|---|---|---|
| `operacion` | `OperacionEnum` | Identificador de la operación. Junto con `X-Destination-Bank` determina el servicio bancario a invocar. Recibido como `OperacionEnum` desde el ORQ — no re-parsear el String. Ver definición completa en **HU-101-ORQ** | SI |
| `X-Origin-Bank` | String (header) | Banco de origen | SI |
| `X-Destination-Bank` | String (header) | Banco destino (`BPOP`) | SI |
| `obj_operacion` | Object | Campos funcionales | SI |

**Campos de `obj_operacion`:**

| Campo             | Tipo   | Descripción                                                                     | Obligatorio | Ejemplo                          |
|-------------------|--------|---------------------------------------------------------------------------------|-------------|----------------------------------|
| `tipoDocumento`   | String | Tipo de documento del cliente                                                   | SI          | `CC`, `CE`, `NIT`                |
| `numeroDocumento` | String | Número de documento del cliente                                                 | SI          | `12345678`                       |
| `acctId`          | String | Número de cuenta/producto — obtenido de la respuesta T1 (`CONSULTA_PRODUCTOS`) | SI          | `5391689991756210`               |
| `acctType`        | String | Tipo de producto BPO — obtenido de la respuesta T1 (`CONSULTA_PRODUCTOS`)      | SI          | `CCA`, `CDT`                     |

> `acctId` y `acctType` provienen de la respuesta T1 de `CONSULTA_PRODUCTOS` (**HU-101-ADP-BPO-consulta-productos**). El front los obtiene de ahí y los pasa al ORQ en el request de detallada.

> **Nota:** Los campos de `obj_operacion` son referenciales. El ADP recibe `obj_operacion` como tipo genérico (`Object`) — no valida sus campos internos ni lo implementa como clase Java campo a campo. La validación es responsabilidad del servicio bancario.

---

## Servicio de BPO Invocado

### Trama T2 — Consulta Detallada por Producto

| Tipo | Servicio / Puerto / Operación | Protocolo | Endpoint DEV/QA | Endpoint PRD |
|------|-------------------------------|-----------|------------------|--------------|
| SOAP | `BalanceInquirySvc` / `BalanceInquiryPort` / `getBalanceByProduct` | SOAP 1.1 | Variable de ambiente | Variable de ambiente |

- **Mensaje de entrada:** `BalanceByProductRequest` (`BalInqRq`)
- **Mensaje de salida:** `BalanceByProductResponse` (`BalInqRs`)
- **Namespace principal:** `urn://grupoaval.com/accounts/v1/`
- **Namespaces IFX:** `urn://grupoaval.com/xsd/ifx/` y `urn://grupoaval.com/xsd/ifx/v2/`
- **WSDL:** `model/BalanceInquiry.wsdl` (mismo que T1 — stubs Java compartidos)
- **Path servicio:** `/accounts/SSL/BalanceInquiry`

> El endpoint y servicio T2 son idénticos a T1 (**HU-101-ADP-BPO-consulta-productos**). La diferencia está en el mensaje de entrada: T2 usa `BalanceByProductRequest` con `DepAcctId` (`AcctId` + `AcctType`) para identificar un producto específico, mientras T1 usa `BalanceGroupedByProductRequest` con `GovIssueIdent` para obtener todos los productos de un cliente.

---

## Outputs

### Saldos detallados por tipo de producto (T2)

El ADP retorna la lista de `AcctBal` del producto consultado (`PartyAcctRelRec`). Los campos dependen del `AcctType`:

#### AcctType = CCA (Tarjeta de Crédito) — CONFIRMADO

| `AcctBal.BalType`                             | Descripción                              |
|-----------------------------------------------|------------------------------------------|
| `Cupo_disponible_compras_pesos`               | Cupo disponible para compras             |
| `Cupo_disponible_avances_pesos`               | Cupo disponible para avances             |
| `Saldo_mora_pesos`                            | Saldo en mora                            |
| `Pago_total_pesos`                            | Pago total                               |
| `Cupo_total`                                  | Cupo total asignado                      |
| `Saldo_actual`                                | Saldo actual                             |
| `Valor_pago_minimo`                           | Valor del pago mínimo                    |
| `Compras_y_avances_pendientes_por_posteo`     | Compras y avances pendientes de posteo   |
| `Pagos_pendientes_por_posteo`                 | Pagos pendientes de posteo               |

Campos adicionales de `PartyAcctRelRec` para CCA:
| Campo              | Descripción                        |
|--------------------|------------------------------------|
| `MinAmtDue.Amt`    | Pago mínimo                        |
| `DueDt`            | Fecha de corte                     |
| `BankAcctStatus.BankAcctStatusCode` | Estado de la cuenta (`N` = Normal) |

#### AcctType = CDT (CDT FlexCube) — CONFIRMADO

| `AcctBal.BalType`           | Descripción                                              |
|-----------------------------|----------------------------------------------------------|
| `Valor_constitucion`        | Valor de constitución del CDT                            |
| `Tasa_Nominal`              | Tasa nominal (también en `CurRate`)                      |
| `Interes_pagado`            | Interés pagado                                           |
| `Retefuente`                | Retención en la fuente                                   |
| `Intereses_causados`        | Intereses causados                                       |
| `Cuenta_para_abonos`        | Cuenta a abonar intereses (en `Desc`)                    |

Campos adicionales de `PartyAcctRelRec` para CDT:
| Campo                   | Descripción                                    |
|-------------------------|------------------------------------------------|
| `FullName`              | Nombre del titular                             |
| `OpenDt`                | Fecha de apertura                              |
| `ClosedDt`              | Fecha de vencimiento                           |
| `LastSettlementDt`      | Última fecha de abono (opcional)               |
| `Term/Count` (1°)       | Plazo en días (MB) o meses (PB)                |
| `Term/TermUnits`        | `Days` (MB) o `Month` (PB)                    |
| `Term/Count` (2°)       | Periodicidad de pago                           |
| `PaymentForm`           | Forma de pago                                  |

#### AcctType = SDA (Ahorros) — Referencial

| `AcctBal.BalType`   | Descripción          |
|---------------------|----------------------|
| `Saldo_disponible`  | Saldo disponible     |
| `Saldo_actual`      | Saldo actual         |
| `Saldo_ayer`        | Saldo del día anterior |
| `Saldo_canje`       | Saldo en canje       |

#### AcctType = DDA (Corriente) — Referencial

Los campos de `BalType` para DDA son los mismos que SDA más saldos de sobregiro. Confirmar con BPO los campos exactos.

#### CONSULTA_DETALLADA_CARTERA — PENDIENTE CONFIRMAR CON BPO

> El contrato T2 entregado por BPO no identifica un AcctType para cartera/crédito. BPO debe confirmar si existe AcctType para este tipo de producto (equivalente a `DLA` u otro) o si la consulta detallada de cartera utiliza un servicio distinto. Hasta confirmar, `CONSULTA_DETALLADA_CARTERA` para BPO retorna error técnico documentado.

### Mapeo de errores BPO → estructura estándar

| Error BPO                              | Código HTTP | StatusDesc                              |
|----------------------------------------|-------------|------------------------------------------|
| StatusCode ≠ 0 — producto no encontrado | `404`       | "Producto no encontrado en BPO"         |
| StatusCode ≠ 0 — error de negocio      | `206`       | StatusDesc del banco                    |
| StatusCode 1160                        | `404`       | "No existe información para los criterios seleccionados" |
| Error de conectividad Everest          | `502`       | "Error de conectividad con BPO"         |
| Timeout del servicio SOAP              | `504`       | "Timeout del servicio BPO"              |
| Error interno BPO                      | `502`       | "Error en el servicio del banco"        |

---

## Reglas de Integración

### Identificación de servicio

| operacion                     | X-Destination-Bank | Servicio bancario                                                                                            | `AcctType` esperado |
|-------------------------------|--------------------|--------------------------------------------------------------------------------------------------------------|---------------------|
| `CONSULTA_DETALLADA_TC`       | `BPOP`             | `BalanceInquirySvc` / `BalanceInquiryPort` / `getBalanceByProduct` — T2 (`BalanceByProductRequest`)         | `CCA`               |
| `CONSULTA_DETALLADA_CDT`      | `BPOP`             | `BalanceInquirySvc` / `BalanceInquiryPort` / `getBalanceByProduct` — T2 (`BalanceByProductRequest`)         | `CDT`               |
| `CONSULTA_DETALLADA_CARTERA`  | `BPOP`             | Pendiente confirmar AcctType con BPO                                                                        | Pendiente confirmar |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo SOAP                   | Valor               | Descripción                                                                             |
|------------------------------|---------------------|-----------------------------------------------------------------------------------------|
| `MsgRqHdr.BankInfo.BankId`   | `0002`              | BankId fijo BPO                                                                         |
| `MsgRqHdr.ClientApp.Org`     | `BPOP`              | Constante fija para identificar el banco en Everest                                     |
| `MsgRqHdr.ClientApp.Name`    | Pendiente confirmar | Ejemplos usan `MB` o `PB`; confirmar valor para canal "Oficinas Aval"                   |
| `MsgRqHdr.Channel`           | Pendiente confirmar | Canal "Oficinas Aval" requiere control de cambios en ESB/BUS (ver Consideraciones.txt) |
| `MsgRqHdr.BankInfo.BankIdType` | `1`               | Jornada normal                                                                          |
| `MsgRqHdr.KeyAcctId`         | `1`                 | Señal supervisión SI(1)                                                                 |
| `MsgRqHdr.Reverse`           | `false`             | Valor fijo                                                                              |
| `MsgRqHdr.Language`          | `es_CO`             | Valor fijo                                                                              |
| `BalInqRq.RqUID`             | Generado            | UUID o número de transacción generado por el ADP para correlación                      |

### Mapeo de campos canal → BPO (T2 Request)

| Campo canal (`obj_operacion`) | Campo SOAP BPO       | Elemento XML                                                                             |
|-------------------------------|----------------------|------------------------------------------------------------------------------------------|
| `tipoDocumento`               | Tipo de documento    | `CustId.GovIssueIdent.GovIssueIdentType` y `MsgRqHdr.UserId.GovIssueIdent.GovIssueIdentType` |
| `numeroDocumento`             | Número de documento  | `CustId.GovIssueIdent.IdentSerialNum` y `MsgRqHdr.UserId.GovIssueIdent.IdentSerialNum`  |
| `acctId`                      | Número de cuenta     | `DepAcctId.AcctId`                                                                       |
| `acctType`                    | Tipo de producto     | `DepAcctId.AcctType`                                                                     |

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
| `X-Destination-Bank` | Confirma que el banco destino es `BPOP` |

### Nivel 2 — Selección y transformación en el ADP

El ADP NO reenvía los headers del ORQ directamente al banco. Para cada operación detallada + BPOP, el ADP construye los campos de protocolo SOAP requeridos por el contrato Everest y envía únicamente esos.

### Nivel 3 — Headers enviados al banco

#### CONSULTA_DETALLADA_* → BalanceInquirySvc / getBalanceByProduct T2 (SOAP)

Los parámetros de protocolo del mensaje SOAP se derivan del contrato Everest de BPO. Las constantes de mapeo (BankId, Channel, etc.) se configuran como variables de ambiente. Los campos de contexto (tipoDocumento, numeroDocumento, acctId, acctType) se obtienen del request entrante.

---

## Caminos Alternativos y Excepciones

| ID     | Condición                                              | Comportamiento esperado                                                                                |
|--------|--------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| ALT-00 | Valor de `operacion` no esperado por este ADP          | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. Verificación defensiva: el ORQ no debería enrutar operaciones no soportadas a este ADP. |
| ALT-01 | StatusCode ≠ 0 en respuesta Everest (negocio)          | Mapear a estructura estándar y retornar al orquestador                                                |
| ALT-02 | Producto no encontrado en BPO                          | Retorna `404` al orquestador                                                                          |
| EXC-01 | Timeout en la llamada SOAP                             | Retorna `504` al orquestador                                                                          |
| EXC-02 | Error de conectividad con Everest BPO                  | Retorna `502` y registra en Elastic                                                                   |

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
| HU-101-ADP-BPO-consulta-productos | Prerequisito  | Provee `AcctId` y `AcctType` que se usan como input en esta HU (T1 → T2)                       |

### Servicios externos (BPO)

| Servicio                                                           | Tipo | Endpoint DEV/QA         | Endpoint PRD            |
|--------------------------------------------------------------------|------|-------------------------|-------------------------|
| `BalanceInquirySvc` / `BalanceInquiryPort` / `getBalanceByProduct` | SOAP | Variable de ambiente    | Variable de ambiente    |

---

## Preguntas Abiertas

| # | Pregunta                                                                                                | Impacto                                                    |
|---|---------------------------------------------------------------------------------------------------------|------------------------------------------------------------|
| 1 | ¿Existe un `AcctType` para cartera/crédito en T2 BPO? (equivalente a `DLA` en OCC)                    | Bloquea documentación e implementación de `CONSULTA_DETALLADA_CARTERA` |
| 2 | ¿Cuál es el valor de `Channel` para el canal "Oficinas Aval" en Everest BPO?                           | Bloquea construcción del SOAP envelope en T1 y T2          |
| 3 | ¿Cuáles son los endpoints DEV/QA/PRD del servicio Everest BPO?                                         | Necesario para variables de ambiente                       |
| 4 | ¿Cuál es el mecanismo de autenticación del endpoint Everest BPO (certificado mTLS, WS-Security, token)? | Bloquea implementación                                     |
| 5 | ¿Hay conectividad de red desde los ambientes del canal Oficinas hacia el endpoint Everest BPO?          | Bloquea pruebas en PT                                      |
| 6 | ¿Los campos `AcctBal.BalType` para `CDT` en T2 de BPO usan plazo en días (MB) o en meses (PB)?        | Afecta el modelo de respuesta para CDT                     |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador BPO — Consulta Detallada T2 Everest (TC / CDT)
  Como adaptador de Banco Popular
  Quiero invocar el servicio Everest T2 con AcctId + AcctType del producto
  Para retornar el detalle de saldos del producto al orquestador

  Background:
    Given el adaptador BPO está configurado con credenciales válidas
    And hay conectividad con el servicio Everest BalanceInquirySvc de BPO

  Scenario: Consulta detallada exitosa — Tarjeta de Crédito (CCA)
    Given el adaptador recibe operacion "CONSULTA_DETALLADA_TC", acctId "5391689991756210" y acctType "CCA"
    When invoca getBalanceByProduct T2 en BPO
    Then obtiene AcctBal con cupo_disponible_compras_pesos, cupo_total, saldo_actual, valor_pago_minimo, DueDt y MinAmtDue
    And retorna la respuesta al orquestador con StatusCode 200

  Scenario: Consulta detallada exitosa — CDT (FlexCube)
    Given el adaptador recibe operacion "CONSULTA_DETALLADA_CDT", acctId "12345678" y acctType "CDT"
    When invoca getBalanceByProduct T2 en BPO
    Then obtiene AcctBal con Valor_constitucion, Tasa_Nominal, Intereses_causados, OpenDt y ClosedDt
    And retorna la respuesta al orquestador con StatusCode 200

  Scenario: Producto no encontrado
    Given el servicio Everest T2 retorna StatusCode de producto no encontrado
    When el adaptador procesa el error
    Then retorna 404 al orquestador

  Scenario: operacion no soportada por este ADP
    Given el adaptador recibe una operacion distinta de CONSULTA_DETALLADA_TC y CONSULTA_DETALLADA_CDT
    When el adaptador verifica la operacion
    Then lanza IllegalArgumentException y retorna 400 al ORQ

  Scenario: Timeout en servicio BPO
    Given el servicio SOAP de BPO no responde en el tiempo configurado
    When el adaptador espera la respuesta
    Then retorna 504 al orquestador
    And registra el evento en Elastic
```

---

## Notas Técnicas

- El WSDL `model/BalanceInquiry.wsdl` es compartido por T1 y T2. Los stubs Java generados para **HU-101-ADP-BPO-consulta-productos** incluyen también las clases de T2 — no se requiere un WSDL separado.
- Los `acctId` de tipo `CCA` (tarjetas de crédito) son números de 16 dígitos. Aplicar masking en logs y SQS — últimos 4 dígitos visibles (`*******5678`).
- El flujo T1 → T2 es el flujo normal de consulta detallada: el asesor primero invoca `CONSULTA_PRODUCTOS` (T1) para obtener la lista de productos con sus `AcctId` y `AcctType`, luego selecciona un producto y el front invoca `CONSULTA_DETALLADA_*` (T2) pasando el `AcctId` + `AcctType` del producto seleccionado.
- La incorporación del canal "Oficinas Aval" en Everest BPO requiere control de cambios previo en el ESB/BUS de BPO. Coordinar con BPO antes de iniciar el sprint de implementación.

---

## Definition of Ready

> La HU puede entrar a sprint solo cuando los ítems marcados con (*) están cumplidos.

- [ ] (*) WSDL `BalanceInquiry.wsdl` de Everest BPO obtenido y procesable
- [ ] (*) Mecanismo de autenticación del endpoint Everest confirmado
- [ ] (*) Conectividad de red desde pods AKS hacia endpoint Everest BPO confirmada en PT
- [ ] (*) Canal "Oficinas Aval" habilitado en ESB/BUS de BPO (control de cambios aprobado)
- [ ] (*) Valores de `ClientApp.Name` y `Channel` para canal Oficinas confirmados con BPO
- [ ] (*) HU-101-ADP-BPO-consulta-productos en estado "En desarrollo" o "Completada" (prerequisito funcional — T1 provee los AcctId/AcctType)
- [ ] Campos T2 confirmados para `CDT` — plazo en días o meses según canal
- [ ] AcctType para cartera confirmado con BPO (o descartado si no aplica via T2)
- [ ] Modelo de respuesta normalizado definido y acordado con el orquestador
- [ ] HU-102-ORQ, HU-103-ORQ y HU-104-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación de story points asignada por el equipo
- [ ] Aprobada por líder técnico y product owner

---

## Definition of Done

- [ ] WSDL de Everest BPO obtenido y stubs Java generados (compartidos con HU-101-ADP-BPO-consulta-productos)
- [ ] Conectividad de red con Everest BPO confirmada en PT
- [ ] Implementación de la llamada SOAP T2 a `getBalanceByProduct` para CCA y CDT
- [ ] Mapeo de respuesta T2 → modelo normalizado implementado para CCA y CDT
- [ ] Masking de `acctId` para `CCA` en logs y SQS — validado en pruebas
- [ ] Pruebas unitarias (cobertura >= 90%)
- [ ] Prueba de integración contra Everest BPO en PT para al menos CCA y CDT
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada — request y response encolados en cada invocación
