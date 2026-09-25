# HU-203-ADP-AVV: Adaptador AV Villas — Actualización de Datos del Cliente

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-203-ADP-AVV                                              |
| ID Servicio    | SFA-027                                                     |
| Épica          | Épica 3 — Actualización de Datos (P2)                       |
| Componente     | Adaptador AVV — Actualización de Datos                      |
| Microservicio  | `ofic-actualizaciones-adp-bavv`                             |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P2)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | **Desarrollada**                                            |
| HU Padre       | HU-203-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-21                                                  |
| Última revisión | 2026-09-03 — campo operacion agregado; identificación de servicio por operacion+banco documentada; masking solo en logs; gestión de headers documentada; cola SQS FIFO de auditoría documentada; OperacionEnum definido localmente en cada microservicio con valores canónicos de HU-101-ORQ; operación no soportada: excepción + 400 documentada |

---

## Historia de Usuario

**Como** microservicio `ofic-actualizaciones-adp-bavv`,  
**quiero** recibir del orquestador (`ofic-actualizaciones-orq`) la solicitud de actualización de datos del cliente de AV Villas,  
**para** invocar el servicio REST `PJBA_Crm_actualizarDatosCliente` de AVV y retornar el resultado normalizado.

---

## Contexto de Negocio

AVV expone el servicio `PJBA_Crm_actualizarDatosCliente` vía ESB interno (`esb.bancoavvillas.net`). El adaptador debe construir el request AVV a partir del request normalizado del orquestador, incluyendo los campos del encabezado técnico (codRedOrigen, canal, dispositivo, tokens, funcionario, oficina) y los datos del cliente a actualizar.

**Middleware:** Datapower Interno → ESB AVV → ICBS (z/OS)  
**Protocolo:** REST POST  
**Contrato:** YAML documentado en `Servicios_SolOfi/WRBA_Crm_actualizarDatosCliente.yaml`

> **Nota:** Solo el endpoint PRD está documentado en el YAML. DEV y QA no tienen entradas de servidor definidas. El patrón en otros servicios AVV usa IPs privadas `10.x.x.x` en DEV/QA con la misma estructura de path — confirmar con AVV.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/avv/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente, los cuales varían según banco y operación (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** El adaptador construye el request AVV incluyendo todos los campos obligatorios del encabezado técnico: `codRedOrigen`="AVV", `tipoCanalDispositivo`="OFI", `tipoCanalLocalizacion`="V", `identificacionDispositivo` (IP del servidor), `tokenUsuario`, `tokenGrupo`, `fechaTransaccion`, `horaTransaccion`, `idFuncionario`, `oficina`, `tipoDocumento`, `nroDocumento`.
- **CA-03:** Los valores `tokenUsuario` y `tokenGrupo` provienen del contexto de autenticación del asesor (no se pasan por el request del orquestador; se obtienen del JWT o del contexto de sesión).
- **CA-04:** El `idFuncionario` se extrae del JWT — nunca del body.
- **CA-05:** Los campos de `datosActualizar` del orquestador se mapean a los campos opcionales del request AVV según la tabla de mapeo.
- **CA-06:** Campos no enviados en `datosActualizar` se omiten del request AVV (no se envían en null ni vacíos).
- **CA-07:** El adaptador invoca `POST {URL}/actualizarDatosCliente` con los campos mapeados.
- **CA-08:** Respuesta AVV `codRespuesta`="0" → `200 OK` al orquestador con `{ codRespuesta: "0", mensajeRespuesta: "Transaccion Exitosa" }`.
- **CA-09:** Respuesta AVV `codRespuesta` ≠ "0" → `422` al orquestador con el mensaje de error del banco.
- **CA-10:** Timeout de conexión AVV → `504`.
- **CA-11:** Error de comunicación inesperado → `502`.
- **CA-12:** Circuit Breaker activo en el consumo del servicio AVV.
- **CA-13:** Credenciales (`tokenGrupo`) en variables de ambiente — nunca en código.
- **CA-14:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-15:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

---

## Caminos Alternativos y Excepciones

| ID | Condición | Comportamiento |
|---|---|---|
| ALT-00  | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. Verificación defensiva: el ORQ no debería enrutar operaciones no soportadas a este ADP. |

---

## Inputs

### Recibidos del Orquestador

El ADP recibe del orquestador: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`.

```json
{
  "operacion": "ACTUALIZACION_DATOS",
  "obj_operacion": {
    "banco": "AVV",
    "tipoDocumento": "CC",
    "numeroDocumento": "86068761",
    "datosActualizar": {
      "celular": "3101234567",
      "correoElectronico": "cliente@email.com",
      "direccionDomicilio": "CL 26 NO 13 45",
      "ciudadDomicilio": "11001",
      "ingresosMensuales": 4500000,
      "nombre1": "WILSON",
      "apellido1": "RODRIGUEZ"
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

## Servicio AVV

### Endpoint

| Ambiente | URL |
|----------|-----|
| DEV      | No documentado (patrón: `http://10.x.x.x:{puerto}/PJBA_Crm_actualizarDatosCliente/WRBA_Crm_actualizarDatosCliente/resources/actualizarDatosCliente`) |
| QA       | No documentado — confirmar con AVV |
| PRD      | `https://esb.bancoavvillas.net:543/PJBA_Crm_actualizarDatosCliente/WRBA_Crm_actualizarDatosCliente/resources/actualizarDatosCliente` |

**Método:** POST  
**Content-Type:** application/json

### Request AVV (campos obligatorios del encabezado)

| Campo                    | Tipo    | Máx | Fuente / Valor                                | Obligatorio |
|--------------------------|---------|-----|-----------------------------------------------|-------------|
| `codRedOrigen`           | String  | 3   | `"AVV"` (fijo)                                | SI          |
| `tipoCanalDispositivo`   | String  | 3   | `"OFI"` (fijo — canal oficinas)               | SI          |
| `tipoCanalLocalizacion`  | String  | 1   | `"V"` (fijo)                                  | SI          |
| `identificacionDispositivo` | String | 15 | IP del servidor/pod AKS (variable de ambiente) | SI          |
| `tokenUsuario`           | String  | 2048 | JWT del asesor (contexto de sesión)          | SI          |
| `tokenGrupo`             | String  | 2048 | Token de grupo (variable de ambiente)        | SI          |
| `fechaTransaccion`       | String  | 16  | Fecha actual: `"DD-MM-YYYY"`                  | SI          |
| `horaTransaccion`        | String  | 16  | Hora actual: `"HH:mm:ss.sssZ"`               | SI          |
| `idFuncionario`          | String  | 13  | Extraído del JWT (`user_id`)                  | SI          |
| `oficina`                | String  | 3   | Código de oficina del asesor (JWT/contexto)   | SI          |
| `tipoDocumento`          | String  | 1   | Mapeado desde orquestador (ver tabla)         | SI          |
| `nroDocumento`           | String  | 16  | `numeroDocumento` del orquestador             | SI          |

### Mapeo de `tipoDocumento`

| Orquestador | AVV | Descripción       |
|-------------|-----|-------------------|
| `CC`        | `C` | Cédula de ciudadanía |
| `CE`        | `E` | Cédula de extranjería |
| `NIT`       | `N` | NIT                |
| `TI`        | `T` | Tarjeta de identidad |

### Catálogo de campos actualizables (`datosActualizar`)

| Campo orquestador       | Campo AVV               | Tipo    | Máx | Descripción                          |
|-------------------------|-------------------------|---------|-----|--------------------------------------|
| `nombre1`               | `nombre1`               | String  | 80  | Primer nombre                        |
| `nombre2`               | `nombre2`               | String  | 80  | Segundo nombre                       |
| `apellido1`             | `apellido1`             | String  | 80  | Primer apellido                      |
| `apellido2`             | `apellido2`             | String  | 80  | Segundo apellido                     |
| `sexo`                  | `sexo`                  | String  | 1   | M / F / U                            |
| `fechaNacimiento`       | `fechaNacimiento`       | Integer | —   | Formato YYYYMMDD (ej: 19851024)      |
| `ciudadNacimiento`      | `ciudadNacimiento`      | String  | 5   | Código DIVIPOLA                      |
| `paisNacimiento`        | `paisNacimiento`        | String  | 3   | Código país (ej: 170 = Colombia)     |
| `estadoCivil`           | `estadoCivil`           | String  | 1   | Código estado civil                  |
| `nivelEstudios`         | `nivelEstudios`         | String  | 1   | Código nivel de estudios             |
| `profesion`             | `profesion`             | String  | 5   | Código CIIU profesión                |
| `indicadorHabeas`       | `indicadorHabeas`       | String  | 1   | S / N                                |
| `telefonoDomicilio`     | `telefonoDomicilio`     | String  | 15  | Teléfono fijo                        |
| `direccionDomicilio`    | `direccionDomicilio`    | String  | 100 | Dirección completa                   |
| `nombreBarrio`          | `nombreBarrio`          | String  | 50  | Nombre del barrio                    |
| `ciudadDomicilio`       | `ciudadDomicilio`       | String  | 5   | Código DIVIPOLA ciudad               |
| `celular`               | `celular`               | String  | 15  | Número celular                       |
| `correoElectronico`     | `correoElectronico`     | String  | 80  | Email                                |
| `ingresosMensuales`     | `ingresosMensuales`     | Number  | —   | Ingresos mensuales                   |
| `otrosIngresos`         | `otrosIngresos`         | Number  | —   | Otros ingresos                       |
| `detalleOtrosIngresos`  | `detalleOtrosIngresos`  | String  | 40  | Descripción otros ingresos           |
| `totalEgresos`          | `totalEgresos`          | Number  | —   | Total egresos                        |
| `activos`               | `activos`               | Number  | —   | Total activos                        |
| `pasivos`               | `pasivos`               | Number  | —   | Total pasivos                        |
| `origenFondos`          | `origenFondos`          | String  | 50  | Origen de fondos                     |
| `nombreEmpresa`         | `nombreEmpresa`         | String  | 40  | Nombre empresa empleadora            |
| `cargoAsignado`         | `cargoAsignado`         | String  | 30  | Cargo actual                         |
| `salario`               | `salario`               | Number  | —   | Salario                              |
| `telefonoEmpresa`       | `telefonoEmpresa`       | String  | 15  | Teléfono empresa                     |
| `direccionEmpresa`      | `direccionEmpresa`      | String  | 100 | Dirección empresa                    |
| `ciudadEmpresa`         | `ciudadEmpresa`         | String  | 5   | Ciudad empresa (DIVIPOLA)            |

> Los campos de beneficiario, referencias, productos en el exterior, PEP, FATCA y otros campos sensibles de compliance están disponibles en el contrato AVV pero deben revisarse con el equipo de producto y cumplimiento antes de exponerlos en el canal Oficinas.

### Respuesta AVV

| Campo                   | Tipo    | Descripción                                |
|-------------------------|---------|--------------------------------------------|
| `codRespuesta`          | String  | `"0"` = éxito; cualquier otro = error      |
| `mensajeRespuesta`      | String  | Descripción del resultado                  |
| `costoTransaccion`      | String  | Costo de la transacción (informativo)      |
| `idFuncionario`         | String  | Echo del funcionario                       |
| `oficina`               | String  | Echo de la oficina                         |
| `fechaTransaccion`      | Integer | Fecha procesada                            |
| `horaTransaccion`       | Integer | Hora procesada                             |

---

## Mapeo de Respuesta → Orquestador

| Condición                          | HTTP al ORQ | Body                                             |
|------------------------------------|-------------|--------------------------------------------------|
| `codRespuesta` = `"0"`             | `200`       | `{ codRespuesta: "0", mensajeRespuesta: "..." }` |
| `codRespuesta` ≠ `"0"`             | `422`       | `{ error: mensajeRespuesta }`                    |
| Timeout de conexión                | `504`       | `{ error: "Timeout al comunicarse con AVV" }`    |
| Error de comunicación inesperado   | `502`       | `{ error: "Error en servicio AVV" }`             |

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `ACTUALIZACION_DATOS` | `BAVV` | `PJBA_Crm_actualizarDatosCliente / actualizarDatosCliente` — REST disponible |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo                   | Valor fijo | Descripción                                   |
|-------------------------|-----------|-----------------------------------------------|
| `codRedOrigen`          | `"AVV"`   | Código de red origen (constante fija)         |
| `tipoCanalDispositivo`  | `"OFI"`   | Canal oficinas (constante fija)               |
| `tipoCanalLocalizacion` | `"V"`     | Tipo de localización (constante fija)         |

### Mapeo de campos

| Campo obj_operacion   | Campo AVV             | Notas                                                      |
|-----------------------|-----------------------|------------------------------------------------------------|
| `tipoDocumento: CC`   | `tipoDocumento: "C"`  | Cédula de ciudadanía                                       |
| `tipoDocumento: CE`   | `tipoDocumento: "E"`  | Cédula de extranjería                                      |
| `tipoDocumento: NIT`  | `tipoDocumento: "N"`  | NIT                                                        |
| `tipoDocumento: TI`   | `tipoDocumento: "T"`  | Tarjeta de identidad                                       |
| `numeroDocumento`     | `nroDocumento`        | Mapeo directo                                              |
| `datosActualizar.*`   | Campos opcionales AVV | Ver tabla de catálogo de campos actualizables en el servicio |

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** `idFuncionario` se extrae del JWT — nunca del body del request.
- **RO-03:** Solo los campos presentes en `datosActualizar` se incluyen en el request AVV. No enviar campos ausentes como null o vacío.
- **RO-04:** Credenciales (`tokenGrupo`, IP del dispositivo, certificados TLS) en variables de ambiente — nunca hardcodeadas.
- **RO-05:** Registrar trazabilidad con los campos que fueron efectivamente enviados al banco.
- **RO-06:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`). Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU.
- **RO-07:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.

---

## Tecnología a Usar

| Componente     | Tecnología   | Versión | Nota                                          |
|----------------|--------------|---------|-----------------------------------------------|
| Lenguaje       | Java         | 21      |                                               |
| Framework      | Spring Boot  | 3.5.13   |                                               |
| HTTP Client    | Retrofit 2.11.0 + OkHttp 4.12.0    |  2.11.0 / 4.12.0       | TLS sobre `esb.bancoavvillas.net:543`         |
| Circuit Breaker| Resilience4j | —       | Activo en todos los consumos externos         |
| Logs           | Elastic      | —       |                                               |
| Mensajería     | AWS SQS FIFO | —       | Cola de auditoría y observabilidad — `avc-everest-pt-logs.fifo` |


---

## Preguntas Abiertas

| # | Pregunta | Impacto |
|---|----------|---------|
| 1 | ¿Cuáles son las URLs DEV y QA del servicio? (Solo PRD documentado) | Define ambientes de desarrollo y pruebas |
| 2 | ¿El `tokenUsuario` es el JWT del asesor o un token específico de AVV? | Define cómo construir el encabezado |
| 3 | ¿El `tokenGrupo` es un token fijo del canal Oficinas o se genera por sesión? | Define configuración en variables de ambiente |
| 4 | ¿La actualización de campos de compliance (PEP, FATCA, beneficiarios) está en alcance para el canal Oficinas? | Define el catálogo completo de campos actualizables |
| 5 | ¿Existe lista blanca de campos que el canal Oficinas puede modificar vs. campos restringidos? | Define validaciones en el adaptador |

---

## Dependencias

| HU         | Relación |
|------------|----------|
| HU-203-ORQ | Padre — `ofic-actualizaciones-orq` |

---

## Gestión de Headers

### Nivel 1 — Headers recibidos del ORQ

El ADP recibe del ORQ los siguientes headers de contexto, propagados sin modificación:

| Header | Descripción |
|--------|-------------|
| `Authorization` | Bearer JWT del asesor |
| `X-Trace-Id` | ID de traza para correlación de logs |
| `X-Origin-Bank` | Banco de origen de la operación |
| `X-Destination-Bank` | Confirma que el banco destino es `BAVV` |

### Nivel 2 — Selección y transformación en el ADP

El ADP NO reenvía los headers del ORQ directamente al banco. Para la combinación `ACTUALIZACION_DATOS + BAVV`, el ADP determina qué headers requiere el servicio bancario específico y construye únicamente esos.

### Nivel 3 — Headers enviados al banco

#### ACTUALIZACION_DATOS → PJBA_Crm_actualizarDatosCliente / actualizarDatosCliente (REST)

Los headers requeridos por este servicio bancario se obtienen de la documentación técnica del banco (contrato del servicio). El ADP reenvía al banco únicamente los headers definidos en ese contrato — los de valor fijo se configuran como variables de ambiente y los de contexto se propagan desde el request entrante. El ADP no valida su presencia: si el llamador omite un header requerido, el banco retorna el error correspondiente.

---

## Definition of Ready


- [ ] URLs DEV y QA confirmadas con AVV
- [ ] Alcance de campos actualizables aprobado por producto y cumplimiento
- [ ] Mecanismo de `tokenUsuario`/`tokenGrupo` confirmado
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Adaptador REST implementado con mapeo completo de campos
- [ ] Encabezado técnico AVV construido dinámicamente
- [ ] Manejo de errores (`codRespuesta` ≠ "0", timeout, error) implementado
- [ ] Pruebas unitarias (cobertura ≥ 90%)
- [ ] Pruebas de integración con ambiente DEV/QA AVV aprobadas
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada — request y response encolados en cada invocación
