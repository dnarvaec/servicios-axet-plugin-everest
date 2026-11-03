# Análisis Técnico — API Everest (Colección Postman)

> **Última actualización:** 2026-08-11 — sincronización de headers contra la colección
> "ATH APIs Collection" vigente (carpeta `EVEREST`): se eliminaron del Excel `X-IP-client`
> y `X-Device-ID` (legado de versiones obsoletas, ya no aparecen en la colección), y se
> agregaron los headers que este documento ya listaba como esperados pero que faltaban
> en `datadriven.xlsx` (`X-IdentSerialNum`/`X-GovIssueIdentType` en CONSULTA_FACTURA;
> los mismos + `X-SessKey`/`X-Language`/`X-LegalName`/`X-Name`/`X-Version` en PAGO_FACTURA;
> `X-SessKey`/`X-Language`/`X-LegalName`/`X-Name`/`X-Version` en PAGO_OBLIGACIONES).
> `Authorization` se dejó intacto tal cual estaba (ver §5, A-01) — pendiente de decisión
> del equipo, no es un hardcodeo a corregir todavía.
>
> **Fuente vigente:** colección "ATH APIs Collection" (carpeta `EVEREST`), que reemplaza
> a la colección original "Everest AVC" (`_postman_id`: `0a81c3f3-0d5f-4501-9bce-7080baefa8f7`).
> Todos los valores de este documento fueron validados contra el mock real
> (`https://d2q3sea1wnkwiy.cloudfront.net`).

---

## 1. Resumen General

| # | Operación | Endpoint | Método | Backend real ATH (referencia, sandbox) |
|---|-----------|----------|--------|------------------------------------------|
| 1 | RETIRO | `/api/v1/pagos/retiro` | POST | `Accounts_Withdrawal` |
| 2 | DEPOSITO | `/api/v1/pagos/deposito` | POST | `Accounts_Deposit` |
| 3 | CONSULTA_FACTURA | `/everest/orq/consultas/api/v1/consulta` | POST | `Payments_Billers` |
| 4 | PAGO_FACTURA | `/api/v1/pagos/pago-factura` | POST | `Payments_Billers` |
| 5 | PAGO_OBLIGACIONES | `/api/v1/pagos/pago-obligaciones` | POST | `Loans_Payments` |

- **Base URL (mock):** `https://d2q3sea1wnkwiy.cloudfront.net` (AWS CloudFront)
- **Protocolo:** HTTPS — todas las peticiones
- **Formato de datos:** JSON
- **Autenticación actual (mock):** Bearer estático (variable de entorno o hardcodeado según endpoint, ver §5)
- **Autenticación futura (backend real):** OAuth2 `client_credentials` (`POST .../v1/Authentication/oauth2/token`) — no aplica aún al mock

> Las carpetas `Accounts_Withdrawal`, `Accounts_Deposit`, `Payments_Billers` y
> `Loans_Payments` (colección ATH) documentan el **backend real** detrás de cada mock,
> en el ambiente sandbox de ATH (`appsptqa.ath.com.co`). Son referencia para una futura
> migración — no forman parte de la automatización actual, que apunta solo al mock CloudFront.

---

## 2. Contrato por Endpoint

### 2.1 RETIRO

**URL:** `https://d2q3sea1wnkwiy.cloudfront.net/api/v1/pagos/retiro`
**Método:** POST

#### Headers
| Header | Valor de referencia | Nota |
|--------|---------------------|------|
| Content-Type | `application/json` | |
| Accept | `application/json` | |
| Authorization | Bearer (variable de entorno) | ✅ Correcto |
| X-Transaction-Id | valor de prueba | |
| X-RqUID | incremental `001001` | |
| X-Channel | `ATM` | |
| X-CompanyId | `BANCO_BOGOTA` | |
| X-IPAddr | IP de prueba | |
| X-NextDt / X-ClientDt | fecha/hora vigente | |
| X-CustIdentType | `CC` | |
| X-CustIdentNum | valor de prueba | |
| X-SessKey | valor de prueba | |
| X-Language | `ES` | |
| X-CustLoginId | valor de prueba | |
| X-IBM-Client-Id | `ccc7806154afefbbe6a3c1c2a2ffb8e8` | |

#### Body
| Campo | Ejemplo | Descripción |
|-------|---------|-------------|
| `banco` | `BANCO_BOGOTA` | Identificador del banco |
| `operacion` | `RETIRO` | Tipo de operación |
| `operacionobj.NetworkTrnInfo.OriginatorName` | `BMOB` | Nombre del originador |
| `operacionobj.NetworkTrnInfo.OriginatorType` | `021` | Código de originador ATM (ISO 8583) |
| `operacionobj.NetworkTrnInfo.TerminalId` | `00BOG138` | ID del terminal ATM |
| `operacionobj.NetworkTrnInfo.NetworkRefId` | `7946` | Referencia de red |
| `operacionobj.NetworkTrnInfo.TeminalSequence` | `6032` | Secuencia del terminal (nombre de campo real del API, con typo) |
| `operacionobj.NetworkTrnInfo.IncocredCode` | `457896` | Código interno de red Incocred |
| `operacionobj.NetworkTrnInfo.PostAddr.{Addr1,StateProv}` | — | Dirección del ATM |
| `operacionobj.PartyAcctRelInfo.DepAcctIdFrom.DepAcctId.AcctKey` | Track 2 de tarjeta | PAN + fecha venc. + datos adicionales |
| `operacionobj.PartyAcctRelInfo.CardAcctIdFrom.CardAcctId.AcctId` | PAN | Dato sensible PCI-DSS |
| `operacionobj.DepAcctId.{AcctType,BankInfo.BankId}` | — | Cuenta destino |
| `operacionobj.ContactInfo.PhoneNum.{PhoneType,Phone}` | — | Teléfono de contacto |
| `operacionobj.CurAmt.{Amt,CurCode}` | `20000.00` / `COP` | Monto del retiro |
| `operacionobj.Fee.CurAmt.{Amt,CurCode}` | `1800.00` / `COP` | Comisión |
| `operacionobj.OTPInfo.{OtpType,OtpValue}` | `OTP` / valor | Exclusivo de RETIRO |

> **Nota de seguridad (validada en vivo):** en una muestra más reciente de la colección,
> `AcctKey`, `Phone` y `OtpValue` aparecen como tokens JWE cifrados en vez de texto plano.
> El mock acepta **ambos formatos indistintamente** (no valida cifrado). Si el proyecto
> migra al backend real de ATH, es probable que el cifrado sí sea obligatorio.

---

### 2.2 DEPOSITO

**URL:** `https://d2q3sea1wnkwiy.cloudfront.net/api/v1/pagos/deposito`
**Método:** POST

Headers idénticos a RETIRO (ver §2.1), con `X-RqUID` incremental `002001`.

#### Body — Diferencias respecto a RETIRO
| Campo | RETIRO | DEPOSITO |
|-------|--------|----------|
| `operacion` | `RETIRO` | `DEPOSITO` |
| `NetworkTrnInfo.OriginatorType` | `021` | `010` |
| `DepAcctId.AcctId` | ❌ Ausente | ✅ Presente (cuenta destino explícita) |
| `OTPInfo` | ✅ Presente | ❌ Ausente (no requiere OTP) |

> Los campos sensibles (`AcctKey`, `Phone`) se mantienen en texto plano en todas las
> muestras conocidas de DEPOSITO — sin cifrado JWE, a diferencia de RETIRO.

---

### 2.3 CONSULTA_FACTURA

**URL:** `https://d2q3sea1wnkwiy.cloudfront.net/everest/orq/consultas/api/v1/consulta`
**Método:** POST

> ⚠️ Único endpoint con path `/everest/orq/consultas/...` — el resto usa `/api/v1/pagos/...`.

#### Headers
| Header | Valor de referencia | Nota |
|--------|---------------------|------|
| Content-Type / Accept | `application/json` | |
| Authorization | `Bearer x` | ⚠️ Hardcodeado — pendiente migrar a variable de entorno |
| X-RqUID | incremental `003001` | |
| X-Channel | `CBV` | Canal de recaudo (no ATM) |
| X-CompanyId | `00010016` | |
| X-IdentSerialNum / X-GovIssueIdentType | valores de prueba | Presentes en esta y otras TX |
| X-IPAddr, X-NextDt, X-IBM-Client-Id | — | |

#### Body
| Campo | Ejemplo | Nota |
|-------|---------|------|
| `banco` | `bbogota` | ⚠️ En minúsculas — único endpoint con esta variante |
| `operacion` | `CONSULTA_FACTURA` | |
| `obj_operacion` | objeto | ⚠️ Único endpoint que usa esta clave (el resto usa `operacionobj`) |
| `obj_operacion.NetwokInfo.{NetworkOwner,NetworkRefId}` | — | ⚠️ Typo `NetwokInfo` (falta la 'r') — nombre real del campo del API |
| `obj_operacion.Transaction.TrnRqUID` | Controla el mock — ver §7 catálogo de estados | Idempotencia |
| `obj_operacion.Transaction.{TrnSrc,TerminalSequence}` | — | |
| `obj_operacion.Agreement.{AgrmId,InvoiceNum,ExpDt,CSPRefId,DepAcctId}` | — | Datos del convenio a consultar |
| `obj_operacion.InvoiceSender.{AcctPayAcct,SvcId,InvSndrPmtInfo.POSEntryMode,AgrmType}` | — | |
| `obj_operacion.PSPCity.CityId` | `11001` | Código DANE |
| `obj_operacion.LocationInfo.GeoLocation` | — | Dirección física |

---

### 2.4 PAGO_FACTURA

**URL:** `https://d2q3sea1wnkwiy.cloudfront.net/api/v1/pagos/pago-factura`
**Método:** POST

#### Headers
| Header | Valor de referencia | Nota |
|--------|---------------------|------|
| Content-Type / Accept | `application/json` | |
| Authorization | `Bearer x` | ⚠️ Hardcodeado — pendiente migrar a variable de entorno |
| X-Transaction-Id | valor de prueba | |
| X-RqUID | incremental `003001` (paso 2 del flujo) | |
| X-Channel | `CBV` | |
| X-CompanyId | `00010016` | |
| X-IdentSerialNum / X-GovIssueIdentType / X-SessKey / X-Language / X-LegalName / X-Name / X-Version | valores de prueba | Headers de contexto del corresponsal (CBV) |
| X-IPAddr, X-NextDt, X-IBM-Client-Id | — | |

> El mock de CloudFront **no valida el contenido** de estos headers (confirmado en vivo)
> — solo importa que estén presentes los que el endpoint marca como requeridos.

#### Body
| Campo | Ejemplo | Nota |
|-------|---------|------|
| `banco` | `BANCO_BOGOTA` | |
| `operacion` | `PAGO_FACTURA` | |
| `operacionobj.NetwokInfo.{NetworkRefId,NetworkOwner}` | — | ⚠️ Mismo typo `NetwokInfo` que CONSULTA_FACTURA |
| `operacionobj.Transaction.{TrnRqUID,TrnSrc,TerminalSequence}` | — | |
| `operacionobj.Transaction.RefInfo[0].{RefId,RefType}` | — | Referencia de pago |
| `operacionobj.TotalCurAmt.{Amt,CurCode}` | `10000.00` / `170` | ⚠️ `CurCode` numérico (`170`), no ISO (`COP`) — así responde el API real |
| `operacionobj.Agreement.{NIE,AgrmId,InvoiceNum,ExpDt,DepAcctId}` | — | |
| `operacionobj.InvoiceSender.{AcctPayAcct,InvSndrPmtInfo.POSEntryMode,SvcId}` | — | |
| `operacionobj.PSPCity.CityId` / `operacionobj.LocationInfo.GeoLocation` | — | |
| `operacionobj.AcctBal[]` (array) | `{Desc, CurAmt}` | Balances asociados |
| `operacionobj.PartyAcctRelRec` *(opcional)* | `{PartyAcctRelId, TINInfo, OpenDt, ClosedDt, BankAcctStatus, AcctBal}` | Campo visto en muestras recientes; el mock responde 200 sin él — no se agrega a `TestData.java` salvo que una HU lo requiera |

---

### 2.5 PAGO_OBLIGACIONES

**URL:** `https://d2q3sea1wnkwiy.cloudfront.net/api/v1/pagos/pago-obligaciones`
**Método:** POST

#### Headers
| Header | Valor de referencia | Nota |
|--------|---------------------|------|
| Content-Type / Accept | `application/json` | |
| Authorization | Bearer (variable de entorno) | ✅ Correcto |
| X-Transaction-Id | valor de prueba | |
| X-RqUID | incremental `004001` | |
| X-Channel | `CBV` | |
| X-CompanyId | `00010016` | |
| X-IPAddr | IP de prueba | |
| X-NextDt | fecha vigente | |
| **X-ClientDt** | fecha (cualquier formato) | ⚠️ **Header requerido por presencia** — si se omite, el mock responde `HTTP 400 "Header requerido ausente: X-ClientDt"`. No valida el formato del valor. |
| X-IdentSerialNum / X-GovIssueIdentType | valores de prueba | |
| X-SessKey / X-Language / X-LegalName / X-Name / X-Version | valores de prueba | Headers de contexto del corresponsal — agregados 2026-08-11, alineados con la colección ATH vigente |
| X-IBM-Client-Id | — | |

#### Body
| Campo | Ejemplo | Nota |
|-------|---------|------|
| `banco` | `BANCO_BOGOTA` | |
| `operacion` | `PAGO_OBLIGACIONES` | |
| `operacionobj.NetworkTrnInfo.{OriginatorName,OriginatorType,TerminalId,NetworkRefId,TeminalSequence,PostAddr}` | — | Igual convención que RETIRO |
| `operacionobj.LoanPmtInfo.DepAcctIdFrom.DepAcctId.{AcctType,AcctKey}` | Track 2 | Cuenta origen |
| `operacionobj.LoanPmtInfo.DepAcctIdTo.DepAcctId.{AcctId,BankInfo.BankId}` | — | Cuenta destino (obligación) |
| `operacionobj.LoanPmtInfo.CurAmt.{Amt,CurCode}` | `20000.00` / `COP` | Monto |
| `operacionobj.LoanPmtInfo.{LoanPmtType,LoanPmtComplement}` | `CCA` / `7946` | Tipo y complemento del pago |
| `operacionobj.LoanPmtInfo.CardAcctIdFrom.CardAcctId.AcctId` | PAN | |

---

## 3. Matriz Comparativa de Headers

| Header | RETIRO | DEPOSITO | CONSULTA_FACTURA | PAGO_FACTURA | PAGO_OBLIGACIONES |
|--------|:------:|:--------:|:----------------:|:------------:|:-----------------:|
| Content-Type / Accept | ✅ | ✅ | ✅ | ✅ | ✅ |
| Authorization (variable de entorno) | ✅ | ✅ | ❌ hardcoded | ❌ hardcoded | ✅ |
| X-Transaction-Id | ✅ | ✅ | ❌ | ✅ | ✅ |
| X-RqUID | ✅ | ✅ | ✅ | ✅ | ✅ |
| X-Channel | `ATM` | `ATM` | `CBV` | `CBV` | `CBV` |
| X-CompanyId | `BANCO_BOGOTA` | `BANCO_BOGOTA` | `00010016` | `00010016` | `00010016` |
| X-ClientDt | ✅ | ✅ | ✅ | ❌ | ✅ **(requerido)** |
| X-CustIdentType / X-CustIdentNum | ✅ | ✅ | ✅ | ❌ | ❌ |
| X-SessKey / X-Language | ✅ | ✅ | ❌ | ✅ | ✅ |
| X-CustLoginId | ✅ | ✅ | ❌ | ❌ | ❌ |
| X-LegalName / X-Name / X-Version | ❌ | ❌ | ❌ | ✅ | ✅ |
| X-IdentSerialNum / X-GovIssueIdentType | ❌ | ❌ | ✅ | ✅ | ✅ |
| X-IBM-Client-Id | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 4. Matriz Comparativa de Body

| Campo / Objeto | RETIRO | DEPOSITO | CONSULTA_FACTURA | PAGO_FACTURA | PAGO_OBLIGACIONES |
|----------------|:------:|:--------:|:----------------:|:------------:|:-----------------:|
| `banco` | `BANCO_BOGOTA` | `BANCO_BOGOTA` | `bbogota` ⚠️ | `BANCO_BOGOTA` | `BANCO_BOGOTA` |
| Clave objeto principal | `operacionobj` | `operacionobj` | `obj_operacion` ⚠️ | `operacionobj` | `operacionobj` |
| Bloque de red | `NetworkTrnInfo` | `NetworkTrnInfo` | `NetwokInfo` ⚠️ | `NetwokInfo` ⚠️ | `NetworkTrnInfo` |
| Información de cuenta | `PartyAcctRelInfo` | `PartyAcctRelInfo` | — | — | `LoanPmtInfo` |
| Bloque de transacción | — | — | `Transaction` | `Transaction` | — |
| `Agreement` / `InvoiceSender` | — | — | ✅ | ✅ | — |
| `OTPInfo` | ✅ | ❌ | ❌ | ❌ | ❌ |
| `CurAmt` directo | ✅ | ✅ | — | `TotalCurAmt` | — |
| `CurAmt` en `LoanPmtInfo` | — | — | — | — | ✅ |
| `Fee` | ✅ | ✅ | — | — | — |
| `AcctBal` (array) | — | — | — | ✅ | — |
| `PartyAcctRelRec` (opcional) | — | — | — | ✅ | — |
| `PSPCity` / `LocationInfo` | — | — | ✅ | ✅ | — |
| Moneda (`CurCode`) | `COP` | `COP` | — | `170` ⚠️ | `COP` |

---

## 5. Inconsistencias Vigentes (no bloquean la automatización)

Estas son particularidades reales del API que **deben respetarse tal cual** en el código
(no se "corrigen" porque son el contrato real del backend):

| ID | Descripción | Afecta |
|----|-------------|--------|
| I-01 | Clave del objeto de operación: `operacionobj` vs `obj_operacion` | CONSULTA_FACTURA vs el resto |
| I-02 | Nombre del bloque de red: `NetworkTrnInfo` vs `NetwokInfo` (typo real del API) | CONSULTA_FACTURA, PAGO_FACTURA |
| I-03 | Nombre del campo de secuencia: `TeminalSequence` (typo real) vs `TerminalSequence` | RETIRO/DEPOSITO/PAGO_OBLIGACIONES vs CONSULTA_FACTURA/PAGO_FACTURA |
| I-04 | `banco` en minúsculas (`bbogota`) solo en CONSULTA_FACTURA | CONSULTA_FACTURA |
| I-05 | URL de CONSULTA_FACTURA usa path distinto (`/everest/orq/...`) | CONSULTA_FACTURA |
| I-06 | `CurCode` numérico (`170`) en vez de ISO (`COP`) | PAGO_FACTURA |
| A-01 | `Authorization: Bearer x` hardcodeado (no variable de entorno) | CONSULTA_FACTURA, PAGO_FACTURA |
| F-01 | Fechas de ejemplo vencidas (`ExpDt: 2020-*`) en los payloads de muestra | CONSULTA_FACTURA, PAGO_FACTURA |

> Los siguientes hallazgos de la auditoría original **ya fueron validados en vivo y
> descartados** por no tener efecto funcional en el mock: valores de `X-Channel`,
> `X-CompanyId`, `X-IdentSerialNum`, `X-GovIssueIdentType` (el mock no valida su
> contenido), y el formato/cifrado de `AcctKey`/`Phone`/`OtpValue` en RETIRO.

---

## 6. Dominio de Negocio

### 6.1 Flujo ATM (canal `ATM`)

```
[Cliente ATM]
    ├─► RETIRO            → /api/v1/pagos/retiro            (requiere OTP)
    ├─► DEPOSITO          → /api/v1/pagos/deposito           (sin OTP, cuenta destino explícita)
    └─► PAGO_OBLIGACIONES → /api/v1/pagos/pago-obligaciones  (pago de créditos/préstamos)
```

### 6.2 Flujo de Recaudo (canal `CBV`) — dos pasos

```
[Canal CBV / POS]
    ├─► PASO 1: CONSULTA_FACTURA → /everest/orq/consultas/api/v1/consulta
    │           (verifica existencia y estado de la factura)
    └─► PASO 2: PAGO_FACTURA     → /api/v1/pagos/pago-factura
                (ejecuta el pago con los datos obtenidos en la consulta)
```

### 6.3 Significado de Campos Clave

| Campo | Significado |
|-------|-------------|
| `AcctType: DDA` | Demand Deposit Account (cuenta de ahorros o corriente) |
| `AcctType: CCA` | Credit Card Account (tarjeta de crédito) |
| `AcctKey` | Track 2 de tarjeta magnética: `PAN=FechaVen+Datos_adicionales` |
| `OriginatorType: 021` | Código de originador ATM (ISO 8583) |
| `OriginatorType: 010` | Código de originador para depósito en ATM |
| `BankId: 00010016` | Código del Banco de Bogotá |
| `X-IBM-Client-Id` | Client ID de IBM API Connect (gateway) |
| `IncocredCode` | Código interno de red Incocred (red de cajeros) |
| `CityId: 11001` | Código DANE de Bogotá D.C. |
| `POSEntryMode: 010` | Modo entrada POS: tarjeta leída manualmente |
| `TrnRqUID` | Transaction Request Unique Identifier (idempotencia; controla el mock en TX-03/TX-04) |

---

## 7. Catálogo Oficial de Códigos de Estado (Fuente Única)

> Esta tabla es la **única fuente de verdad** del proyecto Everest para el mapeo de
> códigos de estado. Ningún otro archivo (agentes, `.feature`, Java, Excel) debe
> redeclararla — solo referenciarla por sección (`§7`).

| codigo_estado_banco | estado_corporativo | Se activa con (TX-03/TX-04, campo `TrnRqUID`) |
|---|---|---|
| 200 | EXITOSA | valor real de negocio (no MOCK) |
| 204 | REVERSADA | `MOCK-204` |
| 100 | FALLIDA_NEGOCIO | `MOCK-100` |
| 300 | FALLIDA_TECNICA | `MOCK-300` |
| 600 | FALLIDA_ENTIDAD | `MOCK-600` |
| 700 | FALLIDA_GENERAL | `MOCK-700` |
| 900 | PENDIENTE | `MOCK-900` |
| 901 | TIMEOUT | `MOCK-901` |

**Reglas de interpretación (no negociables):**
- El HTTP Status Code y el campo `StatusCode` del body son validaciones **independientes**; uno nunca determina el otro.
- Estos códigos son la fuente oficial — no se normalizan, sustituyen ni reinterpretan con convenciones REST estándar.
- Si la API responde con un código fuera de este catálogo, se reporta la inconsistencia al usuario — nunca se corrige automáticamente.

---

## 8. Seguridad

| Aspecto | Estado | Nota |
|---------|--------|------|
| Token Bearer en RETIRO/DEPOSITO/PAGO_OBLIGACIONES | ✅ Variable de entorno | Correcto |
| Token Bearer en CONSULTA_FACTURA / PAGO_FACTURA | ⚠️ Hardcodeado (`Bearer x`) | Pendiente migrar a variable de entorno |
| PAN / Track 2 en body | Texto plano en la mayoría de muestras; cifrado JWE visto en RETIRO | Dato sensible PCI-DSS — el mock acepta ambos formatos |
| Número de cuenta en CONSULTA_FACTURA | ✅ Enmascarado (`*****4207`) | Correcto |
| HTTPS obligatorio | ✅ Todas las peticiones | Correcto |
| Autenticación futura (backend real) | OAuth2 `client_credentials` | No aplica aún al mock |

---

## 9. Notas para Automatización

- Variables necesarias: `bearer_token`, `base_url = https://d2q3sea1wnkwiy.cloudfront.net`, `ibm_client_id = ccc7806154afefbbe6a3c1c2a2ffb8e8`.
- `X-ClientDt` es requerido por **presencia** en PAGO_OBLIGACIONES (no por formato) — no omitirlo en `TestData.java`.
- En TX-03/TX-04, `TrnRqUID` controla el estado funcional retornado por el mock (ver §7).
- Todos los endpoints son mocks; usar `RestAssured.useRelaxedHTTPSValidation()` (proxy NTT/corporativo).
- No agregar `PartyAcctRelRec` a `TestData.java`/`datadriven.xlsx` salvo que una HU lo requiera explícitamente (el mock no lo exige).

Flujo de prueba sugerido:
```
Flujo ATM:      RETIRO → DEPOSITO → PAGO_OBLIGACIONES
Flujo Recaudo:  CONSULTA_FACTURA → PAGO_FACTURA (usa datos capturados en el paso 1)
```



