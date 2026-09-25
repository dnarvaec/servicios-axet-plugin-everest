# HU-201-ADP-BPO: Adaptador Banco Popular — Bloqueo TD Definitivo

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-201-ADP-BPO                                              |
| ID Servicio    | SFA-009                                                     |
| Épica          | Épica 2 — Mantenimiento Tarjeta Débito (P2)                 |
| Componente     | Adaptador BPO — Bloqueo TD Definitivo                       |
| Microservicio  | `ofic-actualizaciones-adp-bpop`                             |
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

**Como** microservicio `ofic-actualizaciones-adp-bpop`,  
**quiero** recibir del orquestador (`ofic-actualizaciones-orq`) la solicitud de bloqueo definitivo de tarjeta débito de Banco Popular,  
**para** invocar el servicio SOAP `LockDebitCard / LockDebitCardBySofia` de BPO (TDMDT) y retornar el resultado normalizado.

---

## Contexto de Negocio

BPO expone el bloqueo de TD a través del servicio SOAP `LockDebitCard` (`LockDebitCardBySofia`) del grupo TDMDT, accesible vía Datapower Interno con AAA Policy y control por IP whitelist. El campo `idLock` determina el tipo de bloqueo (1=Robo, 2=Pérdida, 3=Vencimiento, 4=Solicitud, 5=Preventivo, 6=Pin Errado, 7=Deterioro).

El flujo requiere dos pasos previos: (1) verificación de identidad del cliente con `GetCustomerMDM` (KK107) y (2) consulta de tarjetas del cliente vía `QueryDebitCardCustomer` (TDCTS). Ambos prerequisitos deben ejecutarse dentro del flujo del canal antes de invocar el bloqueo.

> **Nota:** Los contratos SOAP (campos de request/response) del WSDL `LockDebitCard.wsdl` deben obtenerse de BPO. El mapeo de causales BL01/BL02/BL03 → `idLock` está propuesto pero requiere confirmación con BPO.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/boc/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente, los cuales varían según banco y operación (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** El adaptador recibe el contenido de `obj_operacion` proveniente del ORQ e invoca el prerequisito `GetCustomerMDM` (KK107) para verificar la identidad del cliente.
- **CA-03:** El adaptador invoca el prerequisito `QueryDebitCardCustomer` (TDCTS) para obtener el identificador interno de la tarjeta en BPO.
- **CA-04:** El bloqueo solo se ejecuta si ambos prerequisitos retornan respuesta exitosa.
- **CA-05:** Invoca la operación SOAP `LockDebitCardBySofia` del servicio TDMDT con el `idLock` correspondiente a la causal.
- **CA-06:** Incluye los headers de seguridad requeridos por el Datapower de BPO (AAA Policy).
- **CA-07:** Si BPO confirma el bloqueo exitoso, transforma la respuesta al modelo normalizado.
- **CA-08:** Si BPO retorna error de tarjeta no encontrada, mapea a `404`.
- **CA-09:** Si BPO retorna error de IP no autorizada (whitelist), mapea a `502` y alerta en Elastic.
- **CA-10:** Si BPO no responde a tiempo, mapea a `504`.
- **CA-11:** Circuit Breaker activo en todos los consumos externos (prerequisitos y bloqueo).
- **CA-12:** Credenciales y certificados TLS en variables de ambiente — nunca hardcodeados.
- **CA-13:** La IP del pod AKS debe estar en la whitelist de BPO para que las llamadas sean aceptadas.
- **CA-14:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-15:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

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

## Servicio de BPO a Invocar

### LockDebitCard (TDMDT) — Bloqueo definitivo

| Campo               | Valor                                                                      |
|---------------------|----------------------------------------------------------------------------|
| Tipo                | SOAP                                                                       |
| Código interno      | `TDMDT`                                                                    |
| Operación           | `LockDebitCard` / `SrvLockDebitCardAdd` / `LockDebitCardBySofia`           |
| WSDL                | `TarjetaDebito/LockDebitCard.wsdl`                                         |
| WSP interno         | `wsp.sofia.debitcard.frontend.internal`                                    |
| Seguridad           | AAA Policy (DataPower) + Control por IP (whitelist) + TLS 1.0/1.1/1.2     |
| Certificado QA      | `CN=datapower.servint.pruebas`                                             |

### Endpoints

| Ambiente | URL |
|----------|-----|
| QA       | `https://qa.dp.int.ssl.sofia.bpop:55612/prodschnsmngt/SSL/LockDebitCardBySofia` |
| PRD      | `https://prd.dp.int.ssl.sofia.bpop:55612/prodschnsmngt/SSL/LockDebitCardBySofia` |

### Prerequisitos del flujo TDMDT

| Paso | Operación               | Código | Tipo | Endpoint QA                                                                  | Propósito |
|------|-------------------------|--------|------|-------------------------------------------------------------------------------|-----------|
| 1    | `GetCustomerMDM`        | KK107  | SOAP | `https://qa.dp.int.ssl.sofia.bpop:55612/Inquiries/SSL/GetCustomerMDMBySofia` | Verificar identidad del cliente |
| 2    | `QueryDebitCardCustomer`| TDCTS  | SOAP | PENDIENTE POR DEFINIR                                                         | Obtener identificador interno de la tarjeta en BPO |

> **Nota:** Los contratos SOAP de `LockDebitCard` (campos de request/response) se deben obtener del WSDL `LockDebitCard.wsdl`.

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `BLOQUEO_TD_DEFINITIVO` | `BPOP` | `LockDebitCard / SrvLockDebitCardAdd / LockDebitCardBySofia` (código TDMDT) — SOAP interno |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo  | Valor fijo | Descripción |
|--------|-----------|-------------|
| — | PENDIENTE POR DEFINIR | El contrato del WSDL `LockDebitCard.wsdl` debe confirmarse con BPO |

### Mapeo de campos

| Campo obj_operacion | Campo BPO             | Notas                                                                             |
|---------------------|-----------------------|-----------------------------------------------------------------------------------|
| `causal`            | `idLock`              | Ver tabla de mapeo a continuación — **PENDIENTE CONFIRMAR MAPEO EXACTO con BPO** |
| `numeroTarjeta`     | PENDIENTE POR DEFINIR | Requiere identificador interno obtenido vía `QueryDebitCardCustomer` (TDCTS)      |
| `tipoDocumento`     | PENDIENTE POR DEFINIR | Confirmar nombre de campo en contrato `LockDebitCard`                             |
| `numeroDocumento`   | PENDIENTE POR DEFINIR | Confirmar nombre de campo en contrato `LockDebitCard`                             |

**Mapeo de causales → `idLock` (PENDIENTE CONFIRMAR MAPEO EXACTO con BPO):**

| Causal Canal Oficinas | Descripción | `idLock` propuesto | Descripción BPO                                |
|-----------------------|-------------|--------------------|------------------------------------------------|
| `BL01`                | Robo        | 1 o 2              | 1=Robo, 2=Pérdida — PENDIENTE CONFIRMAR        |
| `BL02`                | Pérdida     | 2                  | 2=Pérdida — PENDIENTE CONFIRMAR                |
| `BL03`                | Fraude      | 4 o 5              | 4=Solicitud, 5=Preventivo — PENDIENTE CONFIRMAR|

Valores documentados de `idLock`: 1=Robo, 2=Pérdida, 3=Vencimiento, 4=Solicitud, 5=Preventivo, 6=Pin Errado, 7=Deterioro.

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** El ADP ejecuta el prerequisito `GetCustomerMDM` (KK107) para verificar la identidad del cliente antes del bloqueo.
- **RO-03:** El ADP ejecuta el prerequisito `QueryDebitCardCustomer` (TDCTS) para obtener el identificador interno de la tarjeta en BPO.
- **RO-04:** El bloqueo solo se ejecuta si ambos prerequisitos retornan respuesta exitosa.
- **RO-05:** Credenciales y certificados TLS en variables de ambiente — nunca hardcodeados.
- **RO-06:** El certificado TLS usado debe corresponder al ambiente activo (QA o PRD).
- **RO-07:** La IP del pod AKS debe estar registrada en la whitelist de BPO — coordinar con infraestructura.
- **RO-08:** Los números de tarjeta circulan completos en el flujo funcional (entre ORQ, ADP y servicio bancario). El enmascaramiento se aplica **únicamente en logs** (Elastic): últimos 4 dígitos visibles (ejemplo: `****5678`). Nunca ofuscar el número real en el payload funcional.
- **RO-09:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`). Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU.
- **RO-10:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.

---

## Outputs

> **Nota:** El ADP retorna la respuesta del banco directamente — no hay transformación a un modelo normalizado propio. Los campos listados son referenciales según el contrato del banco.

### Modelo normalizado de salida

| Campo           | Tipo   | Descripción                          |
|-----------------|--------|--------------------------------------|
| `numeroTarjeta` | String | Número enmascarado                   |
| `estadoActual`  | String | `BLOQUEADA`                          |
| `causal`        | String | Causal del bloqueo (BL01/BL02/BL03)  |
| `fechaBloqueo`  | String | Timestamp de la operación            |

### Mapeo de errores BPO → estándar

| Error BPO                          | Código HTTP | StatusDesc                                  |
|------------------------------------|-------------|---------------------------------------------|
| Tarjeta no encontrada              | `404`       | "Tarjeta no encontrada en BPO"              |
| IP no autorizada (whitelist)       | `502`       | "IP no autorizada en Datapower BPO"         |
| Error de certificado TLS           | `502`       | "Error de certificado TLS con BPO"          |
| Timeout                            | `504`       | "Timeout del servicio BPO"                  |
| Error de negocio BPO               | `422`       | "Error de negocio BPO"                      |

---

## Caminos Alternativos y Excepciones

| ID      | Condición                                     | Comportamiento                                                                                                                                       |
|---------|-----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| ALT-00  | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. Verificación defensiva: el ORQ no debería enrutar operaciones no soportadas a este ADP. |

---

## Tecnología a Usar

| Componente      | Tecnología   | Versión | Nota                                                    |
|-----------------|--------------|---------|----------------------------------------------------------|
| Lenguaje        | Java         | 17      | Arquetipo base ACE                                       |
| Framework       | Spring Boot  | 3.x     |                                                          |
| Cliente SOAP    | Spring-WS 3.x + JAXB 4.0.2 | 3.x / 4.0.2       | Para `LockDebitCardBySofia` y prerequisitos TDCTS/KK107  |
| TLS             | Keystore JKS | —       | Certificados por ambiente gestionados por Infra          |
| Circuit Breaker | Resilience4j | —       | Activo en todos los consumos externos                    |
| Logs            | Elastic      | —       |                                                          |
| Mensajería     | AWS SQS FIFO | —       | Cola de auditoría y observabilidad — `avc-everest-pt-logs.fifo` |


---

## Dependencias

| HU         | Relación |
|------------|----------|
| HU-201-ORQ | Padre — `ofic-actualizaciones-orq` |

---

## Preguntas Abiertas

| # | Pregunta | Impacto |
|---|----------|---------|
| 1 | ¿Cuáles son los campos de request/response del WSDL `LockDebitCard.wsdl`? | Sin esto no se puede implementar el adaptador |
| 2 | ¿Las IPs de salida de los pods AKS están registradas en la whitelist de BPO? | Bloquea toda integración |
| 3 | ¿Cuál es el endpoint de `QueryDebitCardCustomer` (TDCTS)? | Define el prerequisito paso 2 |
| 4 | ¿El mapeo causal → `idLock` propuesto (BL01→1/2, BL02→2, BL03→4/5) es correcto? | Define el mapeo en las Reglas de Integración |
| 5 | ¿Cuál es el endpoint de producción para `QueryDebitCardCustomer` (TDCTS)? | Bloquea despliegue a PRD |
| 6 | ¿El prerequisito `GetCustomerMDM` (KK107) ya fue implementado en el flujo P1 o es nuevo? | Define si reutilizar o implementar nuevo |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador BPO — Bloqueo TD Definitivo
  Background:
    Given el adaptador BPO está configurado con certificados TLS válidos
    And la IP del servicio está en la whitelist de BPO
    And hay conectividad con el Datapower de BPO

  Scenario: Bloqueo exitoso
    Given el adaptador recibe tipoDocumento "CC", numeroDocumento "12345678" y causal "BL01"
    And el prerequisito GetCustomerMDM (KK107) retornó verificación exitosa
    And el prerequisito QueryDebitCardCustomer (TDCTS) retornó el identificador interno de la tarjeta
    When invoca LockDebitCardBySofia en BPO con idLock correspondiente a BL01
    Then BPO retorna confirmación del bloqueo
    And el adaptador retorna la respuesta normalizada con estadoActual "BLOQUEADA"

  Scenario: IP del servicio no está en whitelist de BPO
    Given la IP del pod AKS no está registrada en el Datapower de BPO
    When el adaptador intenta invocar el servicio
    Then recibe un error de conexión rechazada
    And retorna 502 al orquestador con mensaje "IP no autorizada en Datapower BPO"

  Scenario: Timeout del servicio
    Given el servicio de BPO no responde en el tiempo configurado
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
| `X-Destination-Bank` | Confirma que el banco destino es `BPOP` |

### Nivel 2 — Selección y transformación en el ADP

El ADP NO reenvía los headers del ORQ directamente al banco. Para la combinación `BLOQUEO_TD_DEFINITIVO + BPOP`, el ADP determina qué headers requiere el servicio bancario específico y construye únicamente esos.

### Nivel 3 — Headers enviados al banco

#### BLOQUEO_TD_DEFINITIVO → LockDebitCard / SrvLockDebitCardAdd / LockDebitCardBySofia (SOAP)

Los headers requeridos por este servicio bancario se obtienen de la documentación técnica del banco (contrato del servicio). El ADP reenvía al banco únicamente los headers definidos en ese contrato — los de valor fijo se configuran como variables de ambiente y los de contexto se propagan desde el request entrante. El ADP no valida su presencia: si el llamador omite un header requerido, el banco retorna el error correspondiente.

---

## Definition of Ready


- [ ] WSDL `LockDebitCard.wsdl` disponible y documentado (campos de request/response)
- [ ] Mapeo de causales (BL01/BL02/BL03) → `idLock` confirmado con BPO
- [ ] Endpoint de `QueryDebitCardCustomer` (TDCTS) documentado (QA y PRD)
- [ ] IPs de salida de pods AKS registradas en la whitelist de BPO
- [ ] Certificados TLS por ambiente disponibles en PT
- [ ] Conectividad de red desde pods AKS hacia Datapower BPO confirmada
- [ ] HU-201-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Cliente SOAP `LockDebitCardBySofia` implementado
- [ ] Prerequisitos `GetCustomerMDM` (KK107) y `QueryDebitCardCustomer` (TDCTS) integrados en el flujo
- [ ] Reglas de Integración completas con mapeo de causales → `idLock` confirmado
- [ ] Certificados TLS por ambiente cargados en Keystore
- [ ] IPs de los pods AKS registradas en whitelist de BPO
- [ ] Número de tarjeta enmascarado en respuesta
- [ ] Manejo de errores y timeouts implementado
- [ ] Pruebas unitarias (cobertura ≥ 90%)
- [ ] Prueba de integración contra BPO en QA
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada — request y response encolados en cada invocación
