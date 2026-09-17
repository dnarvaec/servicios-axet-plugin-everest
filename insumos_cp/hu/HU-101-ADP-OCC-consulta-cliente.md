# HU-101-ADP-OCC: Adaptador Banco de Occidente — Consulta de Datos del Cliente

## Metadatos

| Campo          | Valor                                                  |
|----------------|--------------------------------------------------------|
| ID             | HU-101-ADP-OCC-CLIENTE                                  |
| Épica          | Épica 1 — Consultas P1                                 |
| Componente     | Adaptador OCC — Consulta Cliente                       |
| Sprint         | Por definir                                            |
| Prioridad      | Alta (P1)                                              |
| Estimación     | Por estimar                                            |
| Estado         | Pendiente                                              |
| Microservicio  | `ofic-consultas-adp-bocc`                              |
| HU Padre       | HU-101-ORQ                                             |
| Autor          | Por definir                                            |
| Fecha          | 2026-09-03                                             |
| Última revisión | 2026-09-03 — HU creada; separación de CONSULTA_CLIENTE y CONSULTA_PRODUCTOS; cola SQS FIFO de auditoría documentada; OperacionEnum definido localmente en cada microservicio con valores canónicos de HU-101-ORQ; operación no soportada: excepción + 400 documentada |

## Audiencias

| Rol / Audiencia       | Cómo interactúa                                                                                      |
|-----------------------|------------------------------------------------------------------------------------------------------|
| Desarrollador Backend | Implementa el adaptador: invoca el servicio SOAP de datos de cliente de OCC y transforma la respuesta |
| QA / Tester           | Valida que el adaptador llame correctamente al servicio SOAP OCC y mapee los campos esperados        |
| Integrador OCC        | Provee WSDL, credenciales y acceso al Datapower interno BOCC-ACE12 para `ConsultaClientePort`        |

## Historia de Usuario

**Como** ADP `ofic-consultas-adp-bocc` del canal Oficinas para Banco de Occidente,
**quiero** recibir la operación `CONSULTA_CLIENTE` con `obj_operacion` proveniente del orquestador,
**para** invocar el servicio SOAP `ConsultaClientePort/consultarDatosBasicos` de OCC, obtener los datos del cliente y retornar la respuesta normalizada al orquestador.

## Contexto de Negocio

OCC expone el servicio SOAP `ConsultaClientePort/consultarDatosBasicos` para obtener los datos básicos del cliente. Este servicio pasa por el middleware BOCC-ACE12 y es independiente del servicio de consulta de productos. El adaptador debe invocar este servicio y mapear la respuesta al modelo normalizado del canal Oficinas.

**Nota:** Para la consulta de productos de OCC, ver `HU-101-ADP-OCC-consulta-productos.md` (operación `CONSULTA_PRODUCTOS`).

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-consultas-orq` mediante `POST /api/v1/everst/ofi/occ/adp/consulta`: `operacion = CONSULTA_CLIENTE`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente, los cuales varían según banco y operación (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** El adaptador invoca el servicio SOAP `ConsultaClientePort/consultarDatosBasicos` de OCC con los campos de identificación del cliente.
- **CA-03:** El adaptador transforma la respuesta de OCC al modelo de datos normalizado del canal Oficinas para datos del cliente.
- **CA-04:** Si OCC retorna un SOAP Fault o error de negocio, el adaptador lo mapea a la estructura de error estándar y lo propaga al orquestador.
- **CA-05:** El adaptador no realiza ninguna lógica de negocio adicional — solo invoca el servicio, transforma y retorna.
- **CA-06:** El ADP no valida los campos recibidos en `obj_operacion`.
- **CA-07:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola está **PENDIENTE POR DEFINIR**.
- **CA-08:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

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
| `operacion` | `OperacionEnum` | `CONSULTA_CLIENTE` — identifica la operación junto con `X-Destination-Bank = BOCC`. Recibido como `OperacionEnum` desde el ORQ — no re-parsear el String. Ver definición completa en **HU-101-ORQ** | SI |
| `X-Origin-Bank` | String (header) | Banco de origen | SI |
| `X-Destination-Bank` | String (header) | Confirma que es BOCC | SI |
| `obj_operacion` | Object | Campos funcionales de la operación | SI |
| `obj_operacion.tipoDocumento` | String | Tipo de documento del cliente | NO |
| `obj_operacion.numeroDocumento` | String | Número de documento del cliente | NO |

> **Nota:** Los campos de `obj_operacion` son referenciales. El ADP recibe `obj_operacion` como tipo genérico (`Object`) — no valida sus campos internos ni lo implementa como clase Java campo a campo. La validación es responsabilidad del servicio bancario.

## Servicio OCC Invocado

| Servicio / Operación | Tipo | URL DES | URL QA (CAL) | URL PRD |
|---|---|---|---|---|
| `ConsultaClientePort` / `consultarDatosBasicos` | SOAP | `https://boc201.des.app.bancodeoccidente.net:4806/ConsultaClienteService/ConsultaClientePort` | `http://boc201.tesint.app.bancodeoccidente.net:7805/ConsultaClienteService/ConsultaClientePort` | `http://boc201.prdint.app.bancodeoccidente.net:7805/ConsultaClienteService/ConsultaClientePort` |

> **Nota sobre URLs:** Las URLs indicadas son referenciales. El path exacto del endpoint SOAP debe confirmarse con OCC. Los hosts documentados corresponden al patrón establecido para servicios SOAP de este banco.

## Outputs

### Datos del cliente a retornar al ORQ (normalizado)

- Nombre completo
- Tipo y número de documento
- Segmento
- Datos básicos adicionales — según respuesta del servicio OCC

> **PENDIENTE POR DEFINIR:** Mapeo exacto de campos de respuesta OCC → modelo normalizado. Requiere documentación del contrato SOAP `consultarDatosBasicos` y WSDL de `ConsultaClientePort`.

### Mapeo de errores OCC → estructura estándar

| Error OCC | Código HTTP a retornar | StatusDesc |
|---|---|---|
| SOAP Fault — cliente no encontrado | `206` | "Cliente no encontrado en OCC" |
| Error de autenticación BOCC-ACE12 | `502` | "Error de autenticación con banco" |
| Timeout del servicio | `504` | "Timeout del servicio OCC" |
| Error interno del servicio | `502` | "Error en el servicio del banco" |

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `CONSULTA_CLIENTE` | `BOCC` | `ConsultaClientePort` / `consultarDatosBasicos` (SOAP) |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

**PENDIENTE POR DEFINIR:** Constantes y campos de protocolo requeridos en el SOAP envelope al servicio `consultarDatosBasicos`. Confirmar con OCC si existen campos fijos de protocolo en la llamada SOAP.

### Mapeo de campos

**PENDIENTE POR DEFINIR:** Mapeo de `obj_operacion` → SOAP request OCC y SOAP response OCC → modelo normalizado. Requiere WSDL y documentación del contrato.

| Campo obj_operacion | Campo OCC | Notas |
|---|---|---|
| `tipoDocumento` | PENDIENTE POR DEFINIR | Confirmar nombre del campo y homologación de tipos de documento con OCC |
| `numeroDocumento` | PENDIENTE POR DEFINIR | Confirmar nombre del campo en el contrato OCC |

### Reglas de orquestación

- **RO-01:** El adaptador invoca el servicio OCC usando credenciales configuradas en variables de ambiente.
- **RO-02:** El adaptador no filtra ni modifica los datos retornados por OCC — solo los mapea al modelo normalizado.
- **RO-03:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-04:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. El nombre de la cola está **PENDIENTE POR DEFINIR**. Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU.
- **RO-05:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.

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

El ADP NO reenvía los headers del ORQ directamente al banco. Para cada combinación `operacion + banco destino`, el ADP:
1. Identifica el servicio bancario correspondiente.
2. Determina qué headers requiere ese servicio.
3. Construye o transforma los headers necesarios.
4. Envía al banco **únicamente** los headers definidos por el contrato técnico.

### Nivel 3 — Headers enviados al banco

#### CONSULTA_CLIENTE → ConsultaClientePort / consultarDatosBasicos (SOAP)

Los headers requeridos por este servicio bancario se obtienen de la documentación técnica del banco (contrato del servicio). El ADP reenvía al banco únicamente los headers definidos en ese contrato — los de valor fijo se configuran como variables de ambiente y los de contexto se propagan desde el request entrante. El ADP no valida su presencia: si el llamador omite un header requerido, el banco retorna el error correspondiente.

## Caminos Alternativos y Excepciones

| ID | Condición | Comportamiento esperado |
|---|---|---|
| ALT-00  | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. Verificación defensiva: el ORQ no debería enrutar operaciones no soportadas a este ADP. |
| ALT-01 | SOAP Fault — cliente no encontrado en OCC | Retorna código de negocio correspondiente |
| EXC-01 | Timeout en llamada SOAP a OCC | Retorna `504` al orquestador |
| EXC-02 | Error de certificado TLS con Datapower BOCC-ACE12 | Retorna `502` y registra en Elastic |

## Tecnología a Usar

| Componente | Tecnología | Versión | Nota |
|---|---|---|---|
| Lenguaje | Java | 21 | |
| Framework | Spring Boot | 3.5.13 | |
| Cliente SOAP | Spring-WS 3.x + JAXB 4.0.2 | 3.x / 4.0.2 | Para el servicio SOAP de OCC |
| Circuit Breaker | Resilience4j | — | Para consumos hacia OCC |
| Logs | Elastic | — | |
| Mensajería     | AWS SQS FIFO | —       | Cola de auditoría y observabilidad — nombre **PENDIENTE POR DEFINIR** |


## Consideraciones No Funcionales

- **Circuit Breaker:** Habilitado en todos los consumos hacia servicios de OCC (Resilience4j).
- **WSDL:** El WSDL de `ConsultaClientePort` debe procesarse para generar los stubs Java — coordinar con el equipo de OCC.

## Dependencias

| HU | Relación | Descripción |
|---|---|---|
| HU-101-ORQ | Padre | Orquestador que invoca este adaptador |
| HU-101-ADP-OCC-consulta-productos | Complementaria | Adaptador para `CONSULTA_PRODUCTOS` OCC |

## Servicios externos (OCC)

| Servicio | Tipo | URL QA (CAL) | URL PRD |
|---|---|---|---|
| `ConsultaClientePort/consultarDatosBasicos` | SOAP | `http://boc201.tesint.app.bancodeoccidente.net:7805/ConsultaClienteService/ConsultaClientePort` | `http://boc201.prdint.app.bancodeoccidente.net:7805/ConsultaClienteService/ConsultaClientePort` |

## Seguridad

- **Credenciales hacia OCC:** Almacenadas en variables de ambiente. Nunca en código.
- **TLS:** Las llamadas a BOCC-ACE12 utilizan TLS. Certificados gestionados por el equipo de infraestructura.

## Preguntas Abiertas

| # | Pregunta | Impacto |
|---|---|---|
| 1 | ¿Cuál es el namespace y el SOAPAction del WSDL de `ConsultaClientePort`? | Necesario para construir el SOAP envelope |
| 2 | ¿Qué campos retorna `consultarDatosBasicos` en la respuesta? | Define el modelo de datos normalizado |
| 3 | ¿Qué headers HTTP requiere el servicio SOAP de OCC? (SOAPAction, Content-Type, otros) | Necesario para implementar |
| 4 | ¿El servicio OCC usa autenticación básica, API key, o certificado de cliente? | Bloquea la configuración de credenciales |
| 5 | ¿`consultarDatosBasicos` retorna el segmento del cliente? | Afecta el modelo de datos normalizado |
| 6 | ¿Hay conectividad de red desde pods AKS hacia Datapower BOCC-ACE12? | Bloquea pruebas en PT |

## Escenarios Gherkin

```gherkin
Feature: Adaptador OCC — Consulta de Datos del Cliente
  Background:
    Given el adaptador OCC está configurado con credenciales válidas
    And el servicio ConsultaClientePort/consultarDatosBasicos de OCC está disponible

  Scenario: Consulta exitosa de datos del cliente
    Given el adaptador recibe tipoDocumento "CC" y numeroDocumento "12345678"
    When invoca el servicio SOAP consultarDatosBasicos de OCC
    Then obtiene los datos del cliente (nombre, documento, segmento)
    And retorna la respuesta normalizada al orquestador con StatusCode 200

  Scenario: SOAP Fault — cliente no encontrado en OCC
    Given el adaptador recibe un número de documento que no existe en OCC
    When invoca el servicio consultarDatosBasicos
    Then OCC retorna un SOAP Fault de cliente no encontrado
    And el adaptador mapea el fault al código de error estándar

  Scenario: Timeout del servicio OCC
    Given el servicio de OCC no responde en el tiempo configurado
    When el adaptador espera la respuesta
    Then retorna un error de timeout (504) al orquestador
    And registra el evento en Elastic
```

## Definition of Ready


- [ ] WSDL de `ConsultaClientePort` obtenido y procesable para generación de stubs Java
- [ ] Campos de request y response de `consultarDatosBasicos` definidos y acordados
- [ ] SOAPAction y namespace del WSDL confirmados
- [ ] Headers HTTP requeridos por el servicio confirmados
- [ ] Credenciales disponibles en PT
- [ ] Conectividad de red desde pods AKS hacia Datapower BOCC-ACE12 confirmada en PT
- [ ] HU-101-ORQ en estado "En desarrollo" o "Completada"

## Definition of Done

- [ ] Stubs Java generados a partir del WSDL de `ConsultaClientePort`
- [ ] Implementación del cliente SOAP hacia OCC `consultarDatosBasicos`
- [ ] Mapeo de respuesta OCC → modelo normalizado implementado
- [ ] Manejo de SOAP Faults, errores y timeouts
- [ ] Pruebas unitarias del mapeo (cobertura ≥ 90%)
- [ ] Prueba de integración contra OCC en ambiente PT
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada — request y response encolados en cada invocación
