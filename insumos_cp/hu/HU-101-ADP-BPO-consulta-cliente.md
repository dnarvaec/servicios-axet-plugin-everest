# HU-101-ADP-BPO: Adaptador Banco Popular — Consulta de Datos del Cliente

## Metadatos

| Campo          | Valor                                                  |
|----------------|--------------------------------------------------------|
| ID             | HU-101-ADP-BPO-CLIENTE                                  |
| Épica          | Épica 1 — Consultas P1                                 |
| Componente     | Adaptador BPO — Consulta Cliente                       |
| Sprint         | Por definir                                            |
| Prioridad      | Alta (P1)                                              |
| Estimación     | Por estimar                                            |
| Estado         | Pendiente                                              |
| Microservicio  | `ofic-consultas-adp-bpop`                              |
| HU Padre       | HU-101-ORQ                                             |
| Autor          | Por definir                                            |
| Fecha          | 2026-09-03                                             |
| Última revisión | 2026-09-03 — HU creada; separación de CONSULTA_CLIENTE y CONSULTA_PRODUCTOS; cola SQS FIFO de auditoría documentada; OperacionEnum definido localmente en cada microservicio con valores canónicos de HU-101-ORQ; operación no soportada: excepción + 400 documentada |

## Audiencias

| Rol / Audiencia       | Cómo interactúa                                                                                         |
|-----------------------|---------------------------------------------------------------------------------------------------------|
| Desarrollador Backend | Implementa el adaptador: invoca el servicio SOAP `GetCustomerMDM` de BPO y transforma la respuesta      |
| QA / Tester           | Valida que el adaptador llame correctamente al servicio KK107 de BPO, gestione TLS y mapee los campos   |
| Integrador BPO        | Provee WSDL, certificados TLS y whitelist IP en Datapower interno de BPO para `GetCustomerMDM`          |

## Historia de Usuario

**Como** ADP `ofic-consultas-adp-bpop` del canal Oficinas para Banco Popular,
**quiero** recibir la operación `CONSULTA_CLIENTE` con `obj_operacion` proveniente del orquestador,
**para** invocar el servicio SOAP `GetCustomerMDM` (código KK107) / `GetCustomerMDMBySofia.wsdl` de BPO, obtener los datos del cliente y retornar la respuesta normalizada al orquestador.

## Contexto de Negocio

BPO expone el servicio SOAP `GetCustomerMDM` (código KK107, WSDL `GetCustomerMDMBySofia.wsdl`) para obtener los datos básicos del cliente. Este servicio pasa por el Datapower interno de BPO con autenticación AAA Policy y whitelist de IPs. Es independiente del servicio de consulta de productos. El adaptador debe invocar este servicio y mapear la respuesta al modelo normalizado del canal Oficinas.

**Nota:** Para la consulta de productos de BPO, ver `HU-101-ADP-BPO-consulta-productos.md` (operación `CONSULTA_PRODUCTOS`).

> **Riesgo de infraestructura:** BPO requiere que las IPs de los pods AKS estén registradas en la whitelist del Datapower. Los pods AKS usan IPs dinámicas — la coordinación con el equipo de infraestructura debe iniciarse en paralelo al desarrollo. Verificar si se puede usar NAT o IP fija de salida.

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-consultas-orq` mediante `POST /api/v1/everst/ofi/boc/adp/consulta`: `operacion = CONSULTA_CLIENTE`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente, los cuales varían según banco y operación (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** El adaptador invoca el servicio SOAP `GetCustomerMDM` (KK107) de BPO con los campos de identificación del cliente.
- **CA-03:** El adaptador transforma la respuesta de BPO al modelo de datos normalizado del canal Oficinas para datos del cliente.
- **CA-04:** Si BPO retorna un SOAP Fault o error de negocio, el adaptador lo mapea a la estructura de error estándar y lo propaga al orquestador.
- **CA-05:** El adaptador gestiona los certificados TLS según el ambiente (QA vs PRD).
- **CA-06:** El adaptador no realiza ninguna lógica de negocio adicional — solo invoca el servicio, transforma y retorna.
- **CA-07:** El ADP no valida los campos recibidos en `obj_operacion`.
- **CA-08:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola está **PENDIENTE POR DEFINIR**.
- **CA-09:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

## Inputs

### Recibidos del Orquestador

```json
{
  "operacion": "CONSULTA_CLIENTE",
  "obj_operacion": {
    "tipoDocumento": "CC",
    "numeroDocumento": "12345678"
  }
}
```

| Campo | Tipo | Descripción | Obligatorio |
|---|---|---|---|
| `operacion` | `OperacionEnum` | `CONSULTA_CLIENTE` — identifica la operación junto con `X-Destination-Bank = BPOP`. Recibido como `OperacionEnum` desde el ORQ — no re-parsear el String. Ver definición completa en **HU-101-ORQ** | SI |
| `X-Origin-Bank` | String (header) | Banco de origen | SI |
| `X-Destination-Bank` | String (header) | Confirma que es BPOP | SI |
| `obj_operacion` | Object | Campos funcionales de la operación | SI |
| `obj_operacion.tipoDocumento` | String | Tipo de documento del cliente | NO |
| `obj_operacion.numeroDocumento` | String | Número de documento del cliente | NO |

> **Nota:** Los campos de `obj_operacion` son referenciales. El ADP recibe `obj_operacion` como tipo genérico (`Object`) — no valida sus campos internos ni lo implementa como clase Java campo a campo. La validación es responsabilidad del servicio bancario.

## Servicio BPO Invocado

| Servicio / Código | WSDL | Tipo | Endpoint QA | Endpoint PRD |
|---|---|---|---|---|
| `GetCustomerMDM` / KK107 | `GetCustomerMDMBySofia.wsdl` | SOAP | `https://qa.dp.int.ssl.sofia.bpop:55612/Inquiries/SSL/GetCustomerMDMBySofia` | PENDIENTE POR DEFINIR |

**Certificado QA:** `datapower.servint.pruebas`
**Certificado PRD:** `prd.dp.int.ssl.sofia.bpop`
**TLS QA:** 1.0 / 1.1 / 1.2
**TLS PRD:** 1.2 / 1.3

> **Nota sobre URL QA:** El endpoint QA usa hostname DNS (`qa.dp.int.ssl.sofia.bpop`). Verificar resolución DNS desde los pods AKS.

## Outputs

### Datos del cliente a retornar al ORQ (normalizado)

- Nombre completo
- Tipo y número de documento
- Segmento — **PENDIENTE POR CONFIRMAR:** ¿`GetCustomerMDM` retorna el segmento del cliente?
- Datos adicionales — según respuesta del servicio BPO

> **PENDIENTE POR DEFINIR:** Mapeo exacto de campos de respuesta BPO → modelo normalizado. Requiere documentación del contrato SOAP `GetCustomerMDM` y WSDL `GetCustomerMDMBySofia`.

### Mapeo de errores BPO → estructura estándar

| Error BPO | Código HTTP a retornar | StatusDesc |
|---|---|---|
| SOAP Fault — cliente no encontrado | `206` | "Cliente no encontrado en BPO" |
| Error de certificado TLS | `502` | "Error de certificado TLS con BPO" |
| IP no autorizada (whitelist) | `502` | "IP no autorizada en Datapower BPO" |
| Timeout del servicio | `504` | "Timeout del servicio BPO" |
| Error interno del servicio | `502` | "Error en el servicio del banco" |

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `CONSULTA_CLIENTE` | `BPOP` | `GetCustomerMDM` (KK107) / `GetCustomerMDMBySofia` (SOAP) |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

**PENDIENTE POR DEFINIR:** Constantes y campos de protocolo requeridos en el SOAP envelope al servicio `GetCustomerMDM`. Confirmar con BPO si existen campos fijos en el WSDL.

### Mapeo de campos

**PENDIENTE POR DEFINIR:** Mapeo de `obj_operacion` → SOAP request BPO y SOAP response BPO → modelo normalizado. Requiere WSDL `GetCustomerMDMBySofia`.

| Campo obj_operacion | Campo BPO | Notas |
|---|---|---|
| `tipoDocumento` | PENDIENTE POR DEFINIR | Confirmar homologación de tipos de documento con BPO |
| `numeroDocumento` | PENDIENTE POR DEFINIR | Confirmar nombre del campo en el contrato BPO |

### Reglas de orquestación

- **RO-01:** El adaptador invoca el servicio BPO usando credenciales y certificados configurados en variables de ambiente — nunca hardcodeados.
- **RO-02:** El certificado TLS debe corresponder al ambiente activo (QA: `datapower.servint.pruebas` / PRD: `prd.dp.int.ssl.sofia.bpop`).
- **RO-03:** El adaptador no filtra ni modifica los datos retornados por BPO — solo los mapea al modelo normalizado.
- **RO-04:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-05:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. El nombre de la cola está **PENDIENTE POR DEFINIR**. Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU.
- **RO-06:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.

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

El ADP NO reenvía los headers del ORQ directamente al banco. Para cada combinación `operacion + banco destino`, el ADP:
1. Identifica el servicio bancario correspondiente.
2. Determina qué headers requiere ese servicio.
3. Construye o transforma los headers necesarios.
4. Envía al banco **únicamente** los headers definidos por el contrato técnico.

### Nivel 3 — Headers enviados al banco

#### CONSULTA_CLIENTE → GetCustomerMDM (KK107) / GetCustomerMDMBySofia (SOAP)

Los headers requeridos por este servicio bancario se obtienen de la documentación técnica del banco (contrato del servicio). El ADP reenvía al banco únicamente los headers definidos en ese contrato — los de valor fijo se configuran como variables de ambiente y los de contexto se propagan desde el request entrante. El ADP no valida su presencia: si el llamador omite un header requerido, el banco retorna el error correspondiente.

## Caminos Alternativos y Excepciones

| ID | Condición | Comportamiento esperado |
|---|---|---|
| ALT-00  | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. Verificación defensiva: el ORQ no debería enrutar operaciones no soportadas a este ADP. |
| ALT-01 | SOAP Fault — cliente no encontrado en BPO | Retorna código de negocio correspondiente |
| EXC-01 | Timeout en llamada SOAP a BPO | Retorna `504` al orquestador |
| EXC-02 | Error de certificado TLS (vencido o incorrecto) | Retorna `502` y alerta en Elastic |
| EXC-03 | IP del pod AKS no está en la whitelist de BPO | Retorna `502` con mensaje de IP no autorizada |

## Tecnología a Usar

| Componente | Tecnología | Versión | Nota |
|---|---|---|---|
| Lenguaje | Java | 21 | |
| Framework | Spring Boot | 3.5.13 | |
| Cliente SOAP | Spring-WS 3.x + JAXB 4.0.2 | 3.x / 4.0.2 | Para el servicio SOAP de BPO |
| Circuit Breaker | Resilience4j | — | Para consumos hacia BPO |
| TLS | Keystore JKS | — | Certificados por ambiente gestionados por Infra |
| Logs | Elastic | — | |
| Mensajería     | AWS SQS FIFO | —       | Cola de auditoría y observabilidad — nombre **PENDIENTE POR DEFINIR** |


## Consideraciones No Funcionales

- **Circuit Breaker:** Habilitado en todos los consumos hacia servicios de BPO (Resilience4j).
- **Certificados TLS:** Deben cargarse en el Keystore del servicio según el ambiente. Gestión a cargo del equipo de infraestructura.

## Dependencias

| HU | Relación | Descripción |
|---|---|---|
| HU-101-ORQ | Padre | Orquestador que invoca este adaptador |
| HU-101-ADP-BPO-consulta-productos | Complementaria | Adaptador para `CONSULTA_PRODUCTOS` BPO |

## Servicios externos (BPO)

| Servicio | Código | WSDL | Endpoint QA | Endpoint PRD |
|---|---|---|---|---|
| `GetCustomerMDM` | KK107 | `GetCustomerMDMBySofia.wsdl` | `https://qa.dp.int.ssl.sofia.bpop:55612/Inquiries/SSL/GetCustomerMDMBySofia` | PENDIENTE POR DEFINIR |

## Seguridad

- **Autenticación BPO:** AAA Policy del Datapower — gestionada por certificado TLS de cliente.
- **Whitelist IP:** Las IPs de los pods AKS deben estar registradas en el Datapower de BPO. Los pods AKS usan IPs dinámicas — verificar si se usa NAT o IP fija de salida. **Riesgo:** Coordinación con Infra requerida antes de pruebas en PT.
- **Certificados:** Deben cargarse en el Keystore del servicio según el ambiente. Gestión a cargo del equipo de infraestructura.
- **TLS:** Versiones soportadas: 1.0/1.1/1.2 en QA y 1.2/1.3 en PRD.

## Preguntas Abiertas

| # | Pregunta | Impacto |
|---|---|---|
| 1 | ¿`GetCustomerMDM` retorna el segmento del cliente? | Afecta el modelo de datos normalizado |
| 2 | ¿El endpoint QA es accesible por hostname desde pods AKS? (Confirmar resolución DNS de `qa.dp.int.ssl.sofia.bpop`) | Bloquea pruebas en PT |
| 3 | ¿Cuál es la URL PRD definitiva? | Necesario para configuración de PRD |
| 4 | ¿Los pods AKS tienen IP fija de salida o se debe configurar NAT para la whitelist de BPO? | Bloquea conectividad en todos los ambientes |
| 5 | ¿Qué campos retorna `GetCustomerMDM` en la respuesta SOAP? | Define el modelo de datos normalizado |
| 6 | ¿El WSDL `GetCustomerMDMBySofia.wsdl` está disponible para descarga? | Bloquea la generación de stubs Java |

## Escenarios Gherkin

```gherkin
Feature: Adaptador BPO — Consulta de Datos del Cliente
  Background:
    Given el adaptador BPO está configurado con credenciales y certificados válidos
    And la IP del servicio está en la whitelist de BPO
    And el servicio GetCustomerMDM de BPO está disponible

  Scenario: Consulta exitosa de datos del cliente
    Given el adaptador recibe tipoDocumento "CC" y numeroDocumento "12345678"
    When invoca el servicio SOAP GetCustomerMDM de BPO
    Then obtiene los datos del cliente (nombre, documento, segmento)
    And retorna la respuesta normalizada al orquestador con StatusCode 200

  Scenario: SOAP Fault — cliente no encontrado en BPO
    Given el adaptador recibe un número de documento que no existe en BPO
    When invoca el servicio GetCustomerMDM
    Then BPO retorna un SOAP Fault de cliente no encontrado
    And el adaptador mapea el fault al código de error estándar

  Scenario: IP del servicio no está en whitelist de BPO
    Given la IP del pod AKS no está registrada en el Datapower de BPO
    When el adaptador intenta invocar el servicio
    Then recibe un error de conexión rechazada
    And retorna 502 al orquestador con mensaje "IP no autorizada en Datapower BPO"
    And registra la alerta en Elastic

  Scenario: Certificado TLS vencido
    Given el certificado de ambiente está vencido
    When el adaptador establece la conexión TLS con BPO
    Then el handshake falla
    And retorna 502 al orquestador con mensaje "Error de certificado TLS con BPO"

  Scenario: Timeout del servicio BPO
    Given el servicio SOAP de BPO no responde en el tiempo configurado
    When el adaptador espera la respuesta
    Then retorna un error de timeout (504) al orquestador
    And registra el evento en Elastic
```

## Definition of Ready


- [ ] WSDL `GetCustomerMDMBySofia.wsdl` obtenido del equipo BPO y procesable para stubs Java
- [ ] Campos de request y response de `GetCustomerMDM` definidos y acordados
- [ ] Confirmado si `GetCustomerMDM` retorna el segmento del cliente
- [ ] URL PRD definitiva confirmada con BPO
- [ ] IPs de salida de los pods AKS identificadas y registradas en la whitelist de BPO
- [ ] Certificados TLS por ambiente obtenidos y cargados en Keystore
- [ ] Conectividad de red desde pods AKS hacia Datapower BPO confirmada en PT
- [ ] HU-101-ORQ en estado "En desarrollo" o "Completada"

## Definition of Done

- [ ] WSDL `GetCustomerMDMBySofia.wsdl` obtenido y stubs Java generados
- [ ] Implementación del cliente SOAP hacia BPO `GetCustomerMDM`
- [ ] Certificados TLS por ambiente cargados en Keystore
- [ ] IPs de los pods AKS registradas en whitelist de BPO
- [ ] Mapeo de respuesta BPO → modelo normalizado implementado
- [ ] Manejo de SOAP Faults, errores de TLS, whitelist y timeouts
- [ ] Pruebas unitarias del mapeo (cobertura ≥ 90%)
- [ ] Prueba de integración contra BPO en ambiente PT
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada — request y response encolados en cada invocación
