# HU-203-ADP-BPO: Adaptador Banco Popular — Actualización de Datos del Cliente

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-203-ADP-BPO                                              |
| ID Servicio    | SFA-027                                                     |
| Épica          | Épica 3 — Actualización de Datos (P2)                       |
| Componente     | Adaptador BPO — Actualización de Datos                      |
| Microservicio  | `ofic-actualizaciones-adp-bpop`                             |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P2)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | Pendiente                                                    |
| HU Padre       | HU-203-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-21                                                  |
| Última revisión | 2026-09-15 — contrato BPO recibido; servicio corregido a `MaintainGrupoAval / maintainGrupoAvalParty` (IBM MDM via IIB); endpoints actualizados con IPs reales de IIB; campos obligatorios del request SOAP documentados completos; estado actualizado a Pendiente; PROD aún pendiente de confirmar puertos exactos |

---

## Historia de Usuario

**Como** microservicio `ofic-actualizaciones-adp-bpop`,
**quiero** recibir del orquestador (`ofic-actualizaciones-orq`) la solicitud de actualización de datos del cliente de Banco Popular,
**para** invocar el servicio SOAP `MaintainGrupoAval / maintainGrupoAvalParty` de BPO vía IIB y retornar el resultado normalizado.

---

## Contexto de Negocio

BPO expone la actualización de datos del cliente a través del servicio SOAP `MaintainGrupoAval / maintainGrupoAvalParty`, desplegado en IBM Integration Bus (IIB). El servicio actualiza datos de persona natural en el MDM (IBM MDM) del banco, incluyendo información de contacto, comunicaciones, datos financieros, laborales y otros atributos del cliente.

El targetNamespace del WSDL es `urn://grupoaval.com/accounts/v1/MaintainGrupoAval` y el binding es `MaintainGrupoAvalBindingSOAP`.

> **Nota PROD:** Los nodos de PROD están identificados (10.212.12.30, 10.212.12.32, 10.212.12.35) pero el puerto HTTPS exacto requiere confirmación con BPO.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/boc/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los campos requeridos por el servicio bancario correspondiente (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** El adaptador invoca `MaintainGrupoAval / maintainGrupoAvalParty` de BPO via SOAP con el envelope construido según las Reglas de Integración.
- **CA-03:** Si BPO retorna respuesta exitosa → el ADP retorna la respuesta normalizada al ORQ.
- **CA-04:** Si BPO retorna error de negocio → el ADP mapea al código HTTP estándar correspondiente y retorna al ORQ.
- **CA-05:** Circuit Breaker activo en el consumo del servicio BPO.
- **CA-06:** Credenciales en variables de ambiente — nunca hardcodeadas.
- **CA-07:** Registra en Elastic ante error de conectividad o servicio.
- **CA-08:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-09:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

---

## Inputs

### Recibidos del Orquestador

El ADP recibe del orquestador: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`.

```json
{
  "operacion": "ACTUALIZACION_DATOS",
  "obj_operacion": {
    "banco": "BPO",
    "tipoDocumento": "CC",
    "numeroDocumento": "12345678",
    "datosActualizar": {
      "celular": "3101234567",
      "correoElectronico": "cliente@email.com"
    }
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

| Campo          | Valor                                                |
|----------------|------------------------------------------------------|
| Tipo           | SOAP                                                 |
| Servicio       | `MaintainGrupoAval`                                  |
| Operación SOAP | `maintainGrupoAvalParty`                             |
| Namespace      | `urn://grupoaval.com/accounts/v1/MaintainGrupoAval`  |
| Binding        | `MaintainGrupoAvalBindingSOAP`                       |
| Middleware     | IBM IIB (Integration Bus)                            |
| Backend        | IBM MDM (Master Data Management)                     |

### Endpoints

| Ambiente | URL                                                                         | Nota |
|----------|-----------------------------------------------------------------------------|------|
| DEV      | `https://10.200.157.5:7942/GatewayWebServiceBPOP/Https/Maintenance/`       | Puerto y ruta desde WSDL |
| QA       | `https://10.200.157.61:7907/GatewayWebServiceBPOP/Https/Maintenance/`      | Nodo 1 |
| QA       | `https://10.200.157.58:7907/GatewayWebServiceBPOP/Https/Maintenance/`      | Nodo 2 |
| PROD     | `https://10.212.12.30:7907/GatewayWebServiceBPOP/Https/Maintenance/`       | Nodo 1 — puerto HTTPS a confirmar con BPO |
| PROD     | `https://10.212.12.32:7907/GatewayWebServiceBPOP/Https/Maintenance/`       | Nodo 2 — puerto HTTPS a confirmar con BPO |
| PROD     | `https://10.212.12.35:7907/GatewayWebServiceBPOP/Https/Maintenance/`       | Nodo 3 — puerto HTTPS a confirmar con BPO |

> **Nota:** Adicionalmente existen endpoints HTTP sin TLS (puerto 7906) en DEV/QA/PROD. Usar siempre HTTPS en ambientes no-dev.

---

## Estructura del Request SOAP

El envelope SOAP se construye sobre el elemento raíz `main:maintainGrupoAvalParty`. A continuación se listan los campos obligatorios según la especificación técnica de BPO.

### Campos del Header SOAP

| XPath (relativo a `main:maintainGrupoAvalParty`) | Descripción | Obligatorio | Valor / Origen |
|---|---|---|---|
| `ifx:RqUID` | Identificador único de transacción | SI | Generado por ADP (UUID v4 o secuencial) |
| `ifx:MsgRqHdr/ifx:ClientApp/ifx:Org` | Organización consumidora | SI | Constante: `BPOP` |
| `ifx:MsgRqHdr/ifx:ClientApp/ifx:Name` | Nombre del canal | SI | Constante: `Canales` |
| `ifx:MsgRqHdr/v2:Channel` | Canal de origen | SI | Variable de ambiente (canal Oficinas) |
| `ifx:MsgRqHdr/ifx:BankInfo/ifx:BankId` | Código del banco | SI | Variable de ambiente (código BPO) |
| `ifx:MsgRqHdr/v2:ClientDt` | Timestamp de la petición | SI | Fecha/hora actual con milisegundos |
| `ifx:MsgRqHdr/v2:IPAddr` | IP de origen del asesor | NO | Contexto AKS / IP del pod |
| `ifx:MsgRqHdr/ifx:UserId/ifx:GovIssueIdent/ifx:GovIssueIdentType` | Tipo de documento del operador | SI | JWT del asesor — tipo documento |
| `ifx:MsgRqHdr/ifx:UserId/ifx:GovIssueIdent/ifx:IdentSerialNum` | Número de documento del operador | SI | JWT del asesor — número documento |
| `ifx:MsgRqHdr/v2:Reverse` | Indicador de reversa | SI | Constante: `false` |
| `ifx:MsgRqHdr/v2:Language` | Idioma | SI | Constante: `ES` |
| `ifx:MsgRqHdr/ifx:CustId/ifx:GovIssueIdent/ifx:GovIssueIdentType` | Tipo de documento del CLIENTE | SI | `obj_operacion.tipoDocumento` |
| `ifx:MsgRqHdr/ifx:CustId/ifx:GovIssueIdent/ifx:IdentSerialNum` | Número de documento del CLIENTE | SI | `obj_operacion.numeroDocumento` |
| `main:TCRMService/main:RequestControl/main:requestID` | Número único de transacción (máx. 18 dígitos) | SI | Generado por ADP |

### Datos de actualización

Los datos a actualizar se envían en la estructura `main:TCRMObject / XPartyAssociationBObj` del request. Los campos exactos dependen del catálogo habilitado por BPO para el canal Oficinas (información de contacto, preferencias de comunicación, datos financieros, laborales, etc.). El ADP construye únicamente los nodos correspondientes a los campos presentes en `obj_operacion.datosActualizar`.

---

## Outputs

> El ADP retorna la respuesta del banco directamente — no hay transformación a un modelo normalizado propio.

### Modelo normalizado de salida al ORQ

| Campo              | Tipo   | Descripción                               |
|--------------------|--------|-------------------------------------------|
| `resultado`        | String | Confirmación de actualización exitosa     |
| `mensajeRespuesta` | String | Mensaje descriptivo del resultado         |

### Mapeo de errores BPO → estándar

| Condición BPO                      | Código HTTP al ORQ | Descripción |
|------------------------------------|--------------------|-------------|
| Respuesta exitosa                  | `200`              | Actualización exitosa |
| Error de negocio / datos inválidos | `400`              | Datos inválidos en la solicitud |
| Cliente no encontrado              | `400`              | Cliente no encontrado en BPO |
| Timeout / sin respuesta IIB        | `504`              | Timeout del servicio BPO |
| Error interno IIB                  | `502`              | Error interno en BPO |

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `ACTUALIZACION_DATOS` | `BPOP` | `MaintainGrupoAval / maintainGrupoAvalParty` — SOAP via IIB — IBM MDM |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo XPath (relativo a `main:maintainGrupoAvalParty`) | Valor fijo | Descripción |
|---|---|---|
| `ifx:MsgRqHdr/ifx:ClientApp/ifx:Org` | `BPOP` | Organización consumidora |
| `ifx:MsgRqHdr/ifx:ClientApp/ifx:Name` | `Canales` | Nombre del canal |
| `ifx:MsgRqHdr/v2:Reverse` | `false` | No es una reversa |
| `ifx:MsgRqHdr/v2:Language` | `ES` | Idioma español |

### Mapeo de campos

| Campo obj_operacion / contexto | Campo SOAP (XPath relativo) | Notas |
|---|---|---|
| `obj_operacion.tipoDocumento` | `ifx:MsgRqHdr/ifx:CustId/ifx:GovIssueIdent/ifx:GovIssueIdentType` | Tipo de documento del CLIENTE |
| `obj_operacion.numeroDocumento` | `ifx:MsgRqHdr/ifx:CustId/ifx:GovIssueIdent/ifx:IdentSerialNum` | Número de documento del CLIENTE |
| JWT asesor — tipo documento | `ifx:MsgRqHdr/ifx:UserId/ifx:GovIssueIdent/ifx:GovIssueIdentType` | Tipo de documento del OPERADOR |
| JWT asesor — número documento | `ifx:MsgRqHdr/ifx:UserId/ifx:GovIssueIdent/ifx:IdentSerialNum` | Número de documento del OPERADOR |
| Generado por ADP | `ifx:RqUID` | UUID v4 único por petición |
| Generado por ADP | `main:TCRMService/main:RequestControl/main:requestID` | ID de transacción, máx. 18 dígitos |
| Fecha/hora actual con ms | `ifx:MsgRqHdr/v2:ClientDt` | Timestamp de la petición |
| IP del pod AKS | `ifx:MsgRqHdr/v2:IPAddr` | IP de origen (opcional) |
| `obj_operacion.datosActualizar.*` | `main:TCRMObject/XPartyAssociationBObj/...` | Datos de actualización — estructura completa según catálogo BPO |

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** El ADP construye el envelope SOAP enviando únicamente los nodos correspondientes a los campos presentes en `obj_operacion.datosActualizar` — no incluye nodos vacíos.
- **RO-03:** `ifx:RqUID` y `main:requestID` son generados por el ADP en cada petición. No se propagan del ORQ.
- **RO-04:** El Circuit Breaker se activa ante fallos o timeouts del servicio BPO.
- **RO-05:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`). Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU.
- **RO-06:** La URL base del servicio bancario es variable de ambiente. Nunca se hardcodea en el código.

---

## Caminos Alternativos y Excepciones

| ID | Condición | Comportamiento |
|---|---|---|
| ALT-00 | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. |
| ALT-01 | Error de negocio / datos inválidos en BPO | ADP retorna `400` al ORQ con detalle del error bancario |
| ALT-02 | Cliente no encontrado en MDM | ADP retorna `400` al ORQ |
| ALT-03 | Timeout conectividad IIB | ADP retorna `504` al ORQ y registra en Elastic |
| ALT-04 | Error interno IIB | ADP retorna `502` al ORQ y registra en Elastic |

---

## Tecnología a Usar

| Componente      | Tecnología          | Versión     | Nota |
|-----------------|---------------------|-------------|------|
| Lenguaje        | Java                | 17          | Arquetipo base ACE |
| Framework       | Spring Boot         | 3.x         | |
| Cliente SOAP    | Spring-WS           | 3.x         | Para `MaintainGrupoAval` |
| Marshalling     | JAXB                | 4.0.2       | Generado desde WSDL `maintainGrupoAval.wsdl` |
| Circuit Breaker | Resilience4j        | —           | Activo en todos los consumos externos |
| Logs            | Elastic             | —           | |
| Mensajería      | AWS SQS FIFO        | —           | Cola de auditoría — `avc-everest-pt-logs.fifo` |

---

## Dependencias

| HU         | Relación |
|------------|----------|
| HU-203-ORQ | Padre — `ofic-actualizaciones-orq` |

---

## Preguntas Abiertas

| # | Pregunta | Impacto |
|---|----------|---------|
| 1 | ¿Cuál es el puerto HTTPS exacto en QA y PROD? (7907 asumido por analogía con DEV) | Define la URL de conexión en QA y PROD |
| 2 | ¿Qué campos de `datosActualizar` están habilitados para el canal Oficinas en BPO? | Define el alcance del mapeo en `TCRMObject/XPartyAssociationBObj` |
| 3 | ¿Requiere whitelist de IPs de pods AKS en el IIB de BPO? | Define el proceso de onboarding técnico |

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

El ADP NO reenvía los headers HTTP del ORQ al banco. La información de contexto (operador, cliente, canal) se mapea dentro del envelope SOAP según las Reglas de Integración.

### Nivel 3 — Campos de contexto enviados al banco (dentro del SOAP envelope)

#### ACTUALIZACION_DATOS → MaintainGrupoAval / maintainGrupoAvalParty (SOAP)

| Origen | Campo SOAP (XPath relativo a `main:maintainGrupoAvalParty`) | Valor |
|--------|-------------------------------------------------------------|-------|
| JWT asesor — tipo documento | `ifx:MsgRqHdr/ifx:UserId/ifx:GovIssueIdent/ifx:GovIssueIdentType` | Tipo documento del operador |
| JWT asesor — número documento | `ifx:MsgRqHdr/ifx:UserId/ifx:GovIssueIdent/ifx:IdentSerialNum` | Número documento del operador |
| `obj_operacion.tipoDocumento` | `ifx:MsgRqHdr/ifx:CustId/ifx:GovIssueIdent/ifx:GovIssueIdentType` | Tipo documento del cliente |
| `obj_operacion.numeroDocumento` | `ifx:MsgRqHdr/ifx:CustId/ifx:GovIssueIdent/ifx:IdentSerialNum` | Número documento del cliente |
| IP del pod AKS | `ifx:MsgRqHdr/v2:IPAddr` | IP de origen (opcional) |
| Variable de ambiente | `ifx:MsgRqHdr/ifx:BankInfo/ifx:BankId` | Código del banco BPO |
| Variable de ambiente | `ifx:MsgRqHdr/v2:Channel` | Canal Oficinas |
| Constante `BPOP` | `ifx:MsgRqHdr/ifx:ClientApp/ifx:Org` | Organización |
| Constante `Canales` | `ifx:MsgRqHdr/ifx:ClientApp/ifx:Name` | Nombre del canal |

---

## Definition of Ready

- [x] Servicio documentado: `MaintainGrupoAval / maintainGrupoAvalParty` (IBM MDM via IIB)
- [x] Endpoints DEV y QA identificados
- [x] Campos obligatorios del request SOAP documentados
- [x] WSDL disponible: `Documentacion/V2/4. BPO/Actualizacion de Datos/maintainGrupoAval.wsdl`
- [ ] Catálogo de campos actualizables desde canal Oficinas confirmado
- [ ] Puerto HTTPS de QA y PROD confirmado con BPO
- [ ] Prerequisitos de seguridad confirmados (whitelist IPs AKS si aplica)
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Clases JAXB generadas desde `maintainGrupoAval.wsdl`
- [ ] Cliente Spring-WS para `maintainGrupoAvalParty` implementado
- [ ] Envelope SOAP construido con todos los campos obligatorios
- [ ] Mapeo de campos desde JWT y `obj_operacion` implementado
- [ ] Mapeo de errores BPO → HTTP estándar implementado
- [ ] Circuit Breaker activo
- [ ] Pruebas unitarias (cobertura >= 90%)
- [ ] Prueba de integración contra BPO en QA
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada
