# HU-101: Orquestador — Consulta General de Cliente y Productos

## Metadatos

| Campo          | Valor                                                                 |
|----------------|-----------------------------------------------------------------------|
| ID             | HU-101                                                                |
| ID Servicio    | SFA-007                                                               |
| Épica          | Épica 1 — Consultas P1                                                |
| Componente     | Orquestador de Consultas                                              |
| Sprint         | Por definir                                                           |
| Prioridad      | Alta (P1)                                                             |
| Estimación     | Por estimar                                                           |
| Estado         | Pendiente                                                             |
| Autor          | Por definir                                                           |
| Fecha          | 2026-08-19                                                            |
| Última revisión | 2026-08-20 — alineado con doc SFA-007 v1.0                          |
| HUs hijas      | HU-101-ADP-BDB · HU-101-ADP-AVV · HU-101-ADP-OCC · HU-101-ADP-BPO   |

---

## Audiencias

| Rol / Audiencia        | Cómo interactúa                                                                                   |
|------------------------|---------------------------------------------------------------------------------------------------|
| Asesor de oficina      | Ingresa el documento del cliente; el sistema muestra el resumen de sus productos y datos básicos  |
| Desarrollador Backend  | Implementa el orquestador: valida el request, resuelve el adaptador por banco y consolida la respuesta |
| QA / Tester            | Valida el enrutamiento correcto por banco, el manejo de errores y la estructura de respuesta      |
| Usuario Funcional      | Aprueba que el resumen de productos y datos de cliente que llega al front sea completo y correcto |

---

## Historia de Usuario

**Como** componente orquestador del canal Oficinas/Barra,  
**quiero** recibir una solicitud de consulta general de cliente y productos con el banco de destino identificado,  
**para** enrutar la petición al adaptador correspondiente, obtener la respuesta del banco y devolverla al consumidor.

---

## Contexto de Negocio

El flujo de Consulta General (SFA-007) es el punto de entrada para la atención del cliente en oficina. El asesor selecciona el banco, el tipo de documento e ingresa el número de documento del cliente. El sistema devuelve: datos básicos del cliente (nombre, documento, segmento) y el resumen de todos sus productos (cuentas, CDT, carteras y tarjetas de crédito).

**Validación de identidad parametrizable:** Everest evalúa la configuración de la transacción SFA-007 antes de enviar la consulta. Si la parametrización lo exige, habilita el lector de huellas y valida la identidad con el banco autorizador antes de continuar. Si no aplica, el flujo avanza directamente a la consulta.

Dado que cada banco (AVV, BdB, OCC, BPO) expone servicios distintos (SOAP/REST, contratos diferentes), el orquestador actúa como fachada genérica y delega la ejecución al adaptador del banco indicado. El orquestador **no conoce** los detalles del protocolo ni del contrato de cada banco — esa responsabilidad es del adaptador.

---

## Criterios de Aceptación

- **CA-01:** El orquestador expone un endpoint `POST` que acepta el request genérico con los campos `banco`, `operacion` y `obj_operacion`.
- **CA-02:** El campo `banco` es obligatorio. Si está ausente o tiene un valor no reconocido, el orquestador retorna `400` con un mensaje descriptivo.
- **CA-03:** El campo `operacion` debe tener el valor `CONSULTA_GENERAL_CLIENTE_PRODUCTOS`. Si no coincide, retorna `400`.
- **CA-04:** Los campos `tipoDocumento` y `numeroDocumento` dentro de `obj_operacion` son obligatorios. Si están ausentes retorna `400`.
- **CA-05:** Antes de invocar al adaptador, el orquestador consulta la parametrización de SFA-007 para determinar si la transacción requiere validación de identidad. Si aplica y la validación no fue completada exitosamente, retorna `403` con el motivo.
- **CA-06:** El orquestador resuelve qué adaptador invocar a partir del valor de `banco` (BOGOTA → adaptador BdB; VILLAS → adaptador AVV; OCCIDENTE → adaptador OCC; POPULAR → adaptador BPO).
- **CA-07:** El orquestador invoca al adaptador correspondiente pasándole el contenido de `obj_operacion`.
- **CA-08:** La respuesta que devuelve el adaptador se retorna al consumidor **sin transformación adicional** en el orquestador (la transformación es responsabilidad del adaptador).
- **CA-09:** Si el adaptador retorna respuesta parcial (E4), el orquestador la propaga incluyendo el indicador de bloque faltante — no la convierte en error.
- **CA-10:** Si el adaptador retorna un error de negocio o técnico (timeout, fault, etc.), el orquestador lo propaga con el mismo código HTTP y estructura de error estándar.
- **CA-11:** El orquestador registra trazabilidad completa: usuario, rol, fecha, hora, oficina, banco consultado, documento del cliente consultado, tiempo de respuesta del adaptador y código de resultado.

---

## Inputs

### Request Body

```json
{
  "banco": "BOGOTA",
  "operacion": "CONSULTA_GENERAL_CLIENTE_PRODUCTOS",
  "obj_operacion": {
    "tipoDocumento": "CC",
    "numeroDocumento": "12345678"
  }
}
```

### Parámetros del body

| Campo          | Tipo   | Descripción                                    | Obligatorio | Valores posibles                          |
|----------------|--------|------------------------------------------------|-------------|-------------------------------------------|
| `banco`        | String | Identificador del banco destino                | SI          | `BOGOTA`, `VILLAS`, `OCCIDENTE`, `POPULAR`|
| `operacion`    | String | Código de la operación a ejecutar              | SI          | `CONSULTA_GENERAL_CLIENTE_PRODUCTOS`      |
| `obj_operacion`| Object | Payload de la consulta                         | SI          | Ver campos a continuación                 |

#### Campos de `obj_operacion`

| Campo            | Tipo   | Descripción                        | Obligatorio | Ejemplo    |
|------------------|--------|------------------------------------|-------------|------------|
| `tipoDocumento`  | String | Tipo de documento del cliente      | SI          | `CC`, `CE`, `NIT` |
| `numeroDocumento`| String | Número de documento del cliente    | SI          | `12345678` |

> Campos adicionales pueden requerirse según el banco — los adaptadores documentan el contrato específico de cada entidad.

### Headers Requeridos

> Los headers requeridos son variables y dependen de lo que solicite cada banco. Se definirán durante el diseño de cada adaptador en coordinación con el equipo de integración de cada entidad.

---

## Outputs

### Respuesta exitosa — estructura provisional

La respuesta es la que retorne el adaptador invocado. Estructura de referencia actual:

```json
{
  "Status": {
    "StatusCode": 200,
    "ServerStatusCode": "[código interno del banco]",
    "ServerStatusDesc": "[descripción del banco]",
    "Severity": "Info",
    "StatusDesc": "Consulta exitosa"
  },
  "EndDt": "[timestamp de respuesta]"
}
```

> **Nota:** La estructura completa del `data` de respuesta está pendiente de definición por cada banco. Las HUs de adaptador (HU-101-ADP-*) definen el modelo de datos específico de cada banco. La estructura de `Status` se considera **provisional** hasta que el equipo confirme el contrato definitivo.

### Respuestas de error del orquestador

| Código HTTP | Condición                                         | Respuesta                                                   |
|-------------|---------------------------------------------------|-------------------------------------------------------------|
| `400`       | `banco` ausente, inválido o `operacion` no reconocida | `{"Status":{"StatusCode":400,"StatusDesc":"Parámetros de entrada inválidos"}}` |
| `401`       | JWT ausente o inválido                            | `{"Status":{"StatusCode":401,"StatusDesc":"No autorizado"}}` |
| `404`       | No existe adaptador configurado para el banco     | `{"Status":{"StatusCode":404,"StatusDesc":"Banco no configurado"}}` |
| `504`       | Timeout del adaptador o del banco destino         | `{"Status":{"StatusCode":504,"StatusDesc":"Timeout de respuesta del banco"}}` |
| `500`       | Error interno del orquestador                     | `{"Status":{"StatusCode":500,"StatusDesc":"Error interno del orquestador"}}` |

---

## Reglas de Negocio

1. **RN-01:** El orquestador es **stateless** — no almacena ni cachea la respuesta de la consulta.
2. **RN-02:** El enrutamiento al adaptador se resuelve **exclusivamente** por el campo `banco`. No hay lógica de negocio adicional en el orquestador.
3. **RN-03:** El orquestador **no transforma** el payload de `obj_operacion` antes de enviarlo al adaptador.
4. **RN-04:** El orquestador **no transforma** la respuesta del adaptador antes de devolverla al consumidor.
5. **RN-05:** El orquestador debe ser extensible — agregar un nuevo banco debe requerir solo registrar el nuevo adaptador sin modificar la lógica central.
6. **RN-06:** La validación de identidad es **parametrizable** — el orquestador consulta la configuración de SFA-007 para determinar si debe exigirse antes de enviar la consulta al adaptador.
7. **RN-07:** Si la parametrización exige validación de identidad y ésta no fue completada exitosamente, la consulta **no se envía** al adaptador.
8. **RN-08:** La operación es de **solo lectura** — no modifica datos del cliente ni de sus productos.
9. **RN-09:** La trazabilidad es **obligatoria** — el orquestador registra: usuario, rol, fecha, hora, oficina, banco consultado y referencia del cliente consultado.
10. **RN-10:** Los números de tarjeta de crédito deben mostrarse **enmascarados** en la respuesta. Los números de cuenta se muestran según la política de cada entidad.

---

## Caminos Alternativos y Excepciones

| ID      | Condición                                                         | Comportamiento esperado                                                 |
|---------|-------------------------------------------------------------------|-------------------------------------------------------------------------|
| ALT-01  | `banco` con valor no registrado en el catálogo                   | Retorna `400` con mensaje "Banco no reconocido: {valor}"                |
| ALT-02  | `operacion` con valor distinto al esperado                        | Retorna `400` con mensaje "Operación no soportada: {valor}"             |
| ALT-03  | Datos incompletos en `obj_operacion` (tipoDocumento o numeroDocumento ausentes) | Retorna `400` con campos faltantes identificados              |
| ALT-04  | Cliente no encontrado en el banco seleccionado (E1)               | El adaptador retorna código de negocio; el orquestador lo propaga       |
| ALT-05  | Respuesta parcial del banco — un bloque no pudo consultarse (E4)  | El orquestador propaga la respuesta parcial con el bloque faltante identificado — **no la convierte en error** |
| ALT-06  | Validación de identidad requerida por parametrización y no completada (E6) | Retorna `403` — la consulta no se envía al adaptador            |
| EXC-01  | El adaptador no responde en el tiempo configurado (E5)            | Retorna `504` y registra timeout en log Elastic                         |
| EXC-02  | El adaptador retorna un error de negocio del banco                | El orquestador propaga el error sin modificarlo                         |
| EXC-03  | Banco temporalmente no disponible (E3)                            | Retorna `503` — permite reintentar sin duplicar registros               |
| EXC-04  | Error inesperado dentro del orquestador                           | Retorna `500` y registra stack trace en Elastic                         |

---

## Tecnología a Usar

| Componente        | Tecnología        | Versión  | Nota                                   |
|-------------------|-------------------|----------|----------------------------------------|
| Lenguaje          | Java              | 21       |                                        |
| Framework         | Spring Boot       | 3.2.6    |                                        |
| Contenedores      | Docker            | —        |                                        |
| Orquestador PT    | AKS               | —        | AZ-EU-PV-PT-CE-PO-AKS-01              |
| Orquestador QA    | AKS               | —        | AZ-EU-PV-QA-CE-PO-AKS-01              |
| Orquestador PRD   | AKS               | —        | AZ-EU-PV-PRD-CE-PO-AKS-01             |
| Logs              | Elastic           | —        |                                        |
| Patrón de diseño  | Adapter / Strategy| —        | Un adaptador por banco                 |

---

## Endpoint del Orquestador

| Método | Ruta                                                      | Propósito                                   |
|--------|-----------------------------------------------------------|---------------------------------------------|
| `POST` | `/ofi-orq-consultas/v1/ejecutar`                          | Ejecutar operación de consulta por banco    |

> El nombre del servicio y la ruta exacta están **pendientes de confirmación** con el equipo de arquitectura.

---

## Dependencias

### HUs relacionadas

| HU                  | Relación         | Descripción                                                          |
|---------------------|------------------|----------------------------------------------------------------------|
| HU-101-ADP-BDB      | Hija             | Adaptador para Banco de Bogotá                                       |
| HU-101-ADP-AVV      | Hija             | Adaptador para AV Villas                                             |
| HU-101-ADP-OCC      | Hija             | Adaptador para Banco de Occidente                                    |
| HU-101-ADP-BPO      | Hija             | Adaptador para Banco Popular                                         |
| HU-T02              | Prerrequisito    | Validación de identidad biométrica (el orquestador asume que ya fue validada antes de ser invocado) |

### Servicios externos

| Servicio           | Tipo     | Propósito                                            |
|--------------------|----------|------------------------------------------------------|
| Adaptadores banco  | Interno  | Componentes que abstraen la comunicación con cada banco |

---

## Seguridad

- **Rol requerido:** Asesor autenticado (`asesor` / rol por definir). Cualquier otro rol recibe `403`.
- **Autenticación:** Bearer Token JWT. El `user_id` del asesor se extrae del token — nunca del body.
- **Validación adicional:** El campo `banco` solo puede contener valores del catálogo interno — nunca se pasa sin validar a la capa de adaptadores.
- **Validación de identidad:** Si la parametrización de SFA-007 la exige, el flujo de validación biométrica (lector de huellas) debe completarse antes de invocar el adaptador.
- **Enmascaramiento:** El orquestador debe verificar que los números de TC en la respuesta del adaptador estén enmascarados antes de retornarlos al consumidor.

---

## Consideraciones No Funcionales

| Atributo            | Valor / Descripción                                        |
|---------------------|------------------------------------------------------------|
| Tiempo de respuesta | Dependiente del banco destino — a definir por SLA          |
| Timeout adaptador   | Por configurar (sugerido: 10–30 s según banco)             |
| Disponibilidad      | Por definir                                                |
| Cacheado            | NO — las consultas son en tiempo real                      |
| Idempotencia        | SI — es una operación de lectura                          |
| Namespace AKS       | Por definir                                                |

---

## Escenarios Gherkin

```gherkin
Feature: Orquestador de Consulta General Cliente y Productos
  Como componente orquestador del canal Oficinas
  Quiero enrutar solicitudes de consulta general al adaptador correcto
  Para retornar al asesor la información del cliente y sus productos

  Background:
    Given el orquestador está operativo
    And el asesor está autenticado con un JWT válido

  # =================== ENRUTAMIENTO CORRECTO ===================

  Scenario: Enrutar solicitud al adaptador de Banco de Bogotá
    Given se recibe un request con banco "BOGOTA" y operacion "CONSULTA_GENERAL_CLIENTE_PRODUCTOS"
    When el orquestador procesa el request
    Then invoca al adaptador de Banco de Bogotá (HU-101-ADP-BDB)
    And retorna la respuesta del adaptador sin modificarla

  Scenario: Enrutar solicitud al adaptador de AV Villas
    Given se recibe un request con banco "VILLAS" y operacion "CONSULTA_GENERAL_CLIENTE_PRODUCTOS"
    When el orquestador procesa el request
    Then invoca al adaptador de AV Villas (HU-101-ADP-AVV)
    And retorna la respuesta del adaptador sin modificarla

  Scenario: Enrutar solicitud al adaptador de Banco de Occidente
    Given se recibe un request con banco "OCCIDENTE" y operacion "CONSULTA_GENERAL_CLIENTE_PRODUCTOS"
    When el orquestador procesa el request
    Then invoca al adaptador de Banco de Occidente (HU-101-ADP-OCC)

  Scenario: Enrutar solicitud al adaptador de Banco Popular
    Given se recibe un request con banco "POPULAR" y operacion "CONSULTA_GENERAL_CLIENTE_PRODUCTOS"
    When el orquestador procesa el request
    Then invoca al adaptador de Banco Popular (HU-101-ADP-BPO)

  # =================== VALIDACIONES ===================

  Scenario: Request sin campo banco
    Given se recibe un request sin el campo "banco"
    When el orquestador valida el request
    Then retorna HTTP 400
    And el body contiene StatusCode 400 y mensaje descriptivo

  Scenario: Request con banco no registrado
    Given se recibe un request con banco "INEXISTENTE"
    When el orquestador valida el request
    Then retorna HTTP 400
    And el mensaje indica "Banco no reconocido: INEXISTENTE"

  Scenario: Request sin tipoDocumento o numeroDocumento
    Given se recibe un request sin el campo "numeroDocumento" en obj_operacion
    When el orquestador valida los campos obligatorios
    Then retorna HTTP 400
    And el mensaje identifica el campo faltante

  # =================== VALIDACIÓN DE IDENTIDAD PARAMETRIZABLE ===================

  Scenario: Flujo bloqueado — validación de identidad requerida y pendiente
    Given la configuración de SFA-007 requiere validación biométrica
    And no existe validación previa del cliente en la interacción actual
    When el asesor intenta avanzar hacia la consulta general
    Then Everest habilita el mecanismo de validación de identidad (lector de huellas)
    And el flujo queda bloqueado — el asesor no puede continuar sin completar la validación
    And no se envía ninguna solicitud al banco

  Scenario: Flujo bloqueado — validación biométrica fallida
    Given la configuración de SFA-007 requiere validación biométrica
    And no existe validación previa del cliente en la interacción actual
    And el asesor ejecutó la validación biométrica sin éxito
    When el asesor intenta continuar
    Then el flujo permanece bloqueado
    And no se envía ninguna solicitud al banco

  Scenario: Consulta exitosa — validación biométrica completada
    Given la configuración de SFA-007 requiere validación biométrica
    And no existe validación previa del cliente en la interacción actual
    And el asesor completa la validación biométrica exitosamente
    When el flujo se desbloquea y el asesor envía la solicitud
    Then el orquestador enruta al adaptador correspondiente
    And retorna la respuesta del adaptador con StatusCode 200

  Scenario: Parametrización no requiere validación de identidad
    Given la configuración de SFA-007 no requiere validación biométrica
    When el asesor envía la solicitud de consulta general
    Then el orquestador enruta directamente al adaptador sin solicitar validación

  # =================== RESPUESTA PARCIAL ===================

  Scenario: Adaptador retorna respuesta parcial
    Given el adaptador de Banco de Bogotá retorna datos del cliente pero no pudo obtener un bloque de productos
    When el orquestador recibe la respuesta parcial
    Then propaga la respuesta con el bloque faltante identificado
    And no la convierte en error

  # =================== ERRORES DEL ADAPTADOR ===================

  Scenario: El adaptador retorna timeout
    Given el adaptador de Banco de Bogotá no responde en el tiempo configurado
    When el orquestador espera la respuesta
    Then retorna HTTP 504
    And registra el evento de timeout en Elastic

  Scenario: El adaptador retorna un error de negocio del banco
    Given el adaptador retorna un error con StatusCode de negocio
    When el orquestador recibe la respuesta del adaptador
    Then propaga el error sin modificarlo al consumidor

  # =================== SEGURIDAD ===================

  Scenario: Request sin JWT
    Given se recibe un request sin header Authorization
    When el orquestador valida la autenticación
    Then retorna HTTP 401
```

---

## Notas Técnicas

- El enrutamiento banco → adaptador debe resolverse vía inyección de dependencias (Spring `@Qualifier` / Strategy pattern) para facilitar extensibilidad.
- La estructura de `Status` en la respuesta es **provisional** — el contrato definitivo aún no está cerrado con el equipo. Las HUs de adaptadores referencian esta misma estructura.
- El orquestador **no debe** conocer los endpoints de los bancos — esa información vive en los adaptadores y en su configuración de ambiente.
- Los timeouts por banco deben ser configurables por variable de ambiente, no hardcodeados.
- El log en Elastic debe incluir: `banco`, `operacion`, `X-Trace-Id`, tiempo de respuesta del adaptador (ms), `StatusCode` resultante.

---

## Definition of Ready

> La HU puede entrar a sprint solo cuando **todos** los ítems están cumplidos.

- [ ] Contrato del request (`banco`, `operacion`, `tipoDocumento`, `numeroDocumento`) definido y aprobado
- [ ] Valores válidos del campo `banco` confirmados (`BOGOTA`, `VILLAS`, `OCCIDENTE`, `POPULAR`)
- [ ] Código de operación `CONSULTA_GENERAL_CLIENTE_PRODUCTOS` confirmado con el equipo
- [ ] Ruta del endpoint del orquestador confirmada con el equipo de arquitectura
- [ ] Mecanismo de enrutamiento (Strategy / Spring Qualifier) acordado con el equipo técnico
- [ ] Los 4 adaptadores de banco (HU-101-ADP-*) identificados y sus contratos de interfaz definidos
- [ ] Estructura de error estándar del orquestador definida y aprobada
- [ ] Mecanismo de evaluación de parametrización SFA-007 (identidad requerida/no requerida) definido con el equipo de parametrización
- [ ] Fuente de parametrización de validación de identidad identificada (BD, servicio, config)
- [ ] Comportamiento de respuesta parcial (E4) acordado con el equipo funcional: ¿qué bloque(s) pueden venir incompletos?
- [ ] Política de enmascaramiento de TC y cuentas definida por banco
- [ ] Campos de trazabilidad obligatorios (usuario, rol, oficina, banco, cliente) acordados con el equipo de auditoría
- [ ] Estimación de story points asignada por el equipo
- [ ] Aprobada por líder técnico y product owner

---

## Definition of Done

- [ ] Endpoint `POST /ofi-orq-consultas/v1/ejecutar` implementado y funcionando
- [ ] Enrutamiento correcto a los 4 adaptadores verificado
- [ ] Validación de `banco`, `operacion`, `tipoDocumento` y `numeroDocumento` implementada
- [ ] Evaluación de parametrización SFA-007 implementada (validación de identidad requerida/no requerida)
- [ ] Manejo de respuesta parcial (E4) implementado — propaga sin convertir en error
- [ ] Manejo de timeout y propagación de errores del adaptador
- [ ] Enmascaramiento de números TC verificado en la respuesta
- [ ] Trazabilidad obligatoria implementada (usuario, rol, fecha, hora, oficina, banco, cliente)
- [ ] Logging en Elastic con los campos requeridos
- [ ] Pruebas unitarias del enrutamiento (cobertura ≥ 80%)
- [ ] Pruebas de integración contra al menos 1 adaptador real en PT
- [ ] Aprobado por QA
- [ ] Aprobado por usuario funcional
