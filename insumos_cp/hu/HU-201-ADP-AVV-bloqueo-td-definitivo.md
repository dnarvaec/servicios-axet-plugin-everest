# HU-201-ADP-AVV: Adaptador AV Villas — Bloqueo TD Definitivo

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-201-ADP-AVV                                              |
| ID Servicio    | SFA-009                                                     |
| Épica          | Épica 2 — Mantenimiento Tarjeta Débito (P2)                 |
| Componente     | Adaptador AVV — Bloqueo TD Definitivo                       |
| Microservicio  | `ofic-actualizaciones-adp-bavv`                             |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P2)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | **Desarrollada**                                             |
| HU Padre       | HU-201-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-21                                                  |
| Última revisión | 2026-09-03 — campo operacion agregado; identificación de servicio por operacion+banco documentada; masking solo en logs; gestión de headers documentada; cola SQS FIFO de auditoría documentada; OperacionEnum definido localmente en cada microservicio con valores canónicos de HU-101-ORQ; operación no soportada: excepción + 400 documentada |

---

## Historia de Usuario

**Como** microservicio `ofic-actualizaciones-adp-bavv`,  
**quiero** recibir del orquestador (`ofic-actualizaciones-orq`) la solicitud de bloqueo definitivo de tarjeta débito de AV Villas,  
**para** invocar el servicio REST de AVV con `indBloqueo=S` y retornar el resultado normalizado al orquestador.

---

## Contexto de Negocio

El único servicio documentado para bloqueo de medios en AVV es `PFBA_CanalOtros295/WRBA_CanalOtros_BloqTempMedios`. El nombre del servicio sugiere bloqueo temporal, pero podría soportar bloqueo definitivo mediante el campo `indBloqueo=S`.

> **[!] PENDIENTE CONFIRMACIÓN AVV:** Confirmar con AVV si `PFBA_CanalOtros295/WRBA_CanalOtros_BloqTempMedios` con `indBloqueo=S` aplica para bloqueo TD definitivo (por Robo/Pérdida/Fraude). Hasta obtener confirmación, esta HU permanece en estado pendiente.

**Middleware:** Datapower Interno → ESB AVV  
**Protocolo:** REST

---

## Criterios de Aceptación

> Condicionados a la confirmación de AVV sobre el servicio.

- **CA-01:** El adaptador recibe del orquestador `ofic-actualizaciones-orq` mediante `POST /api/v1/everst/ofi/avv/adp/actualizacion`: la `operacion`, los headers `X-Origin-Bank` y `X-Destination-Bank`, y el contenido de `obj_operacion`. Adicionalmente, el ADP gestiona los headers requeridos por el servicio bancario correspondiente, los cuales varían según banco y operación (ver sección Gestión de Headers y documentación del banco).
- **CA-02:** Una vez confirmado el servicio, el adaptador recibe el contenido de `obj_operacion` proveniente del ORQ e invoca el servicio REST de AVV.
- **CA-03:** El campo `indBloqueo=S` se envía como constante en el request.
- **CA-04:** Transforma la respuesta al modelo normalizado.
- **CA-05:** Mapea errores del banco al código HTTP estándar.
- **CA-06:** Circuit Breaker activo en el consumo del servicio AVV.
- **CA-07:** Registra en Elastic ante error de conectividad o servicio.
- **CA-08:** El adaptador publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response obtenido del banco (o el error, en caso de fallo) antes de retornar la respuesta al orquestador. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`).
- **CA-09:** Si el valor de `operacion` recibido no corresponde al/los valor(es) que este ADP soporta, el ADP lanza `IllegalArgumentException` y retorna `400` al ORQ. El ADP no procesa silenciosamente operaciones inesperadas.

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

## Servicio de AVV a Invocar

| Campo               | Valor                                                                       |
|---------------------|-----------------------------------------------------------------------------|
| Tipo                | REST                                                                        |
| API                 | `PFBA_CanalOtros295`                                                        |
| Recurso             | `WRBA_CanalOtros_BloqTempMedios` / `FMBA_BloqTempMedios`                   |
| Método              | POST (a confirmar con AVV)                                                  |
| Campo clave         | `indBloqueo=S`                                                              |

> **[!] Confirmar con AVV:** El nombre del servicio indica "bloqueo temporal". Validar que `indBloqueo=S` efectúa un bloqueo definitivo para las causales Robo/Pérdida/Fraude desde el canal Oficinas.

### Endpoints

| Ambiente | URL |
|----------|-----|
| DEV      | `https://10.10.10.201:543/PFBA_CanalOtros295/WRBA_CanalOtros_BloqTempMedios` |
| QA       | `https://10.10.9.200:543/PFBA_CanalOtros295/WRBA_CanalOtros_BloqTempMedios` |
| PRD      | `https://10.10.21.10:543/PFBA_CanalOtros295/WRBA_CanalOtros_BloqTempMedios` |

---

## Reglas de Integración

### Identificación de servicio

| operacion | X-Destination-Bank | Servicio bancario |
|---|---|---|
| `BLOQUEO_TD_DEFINITIVO` | `BAVV` | `PFBA_CanalOtros295 / WRBA_CanalOtros_BloqTempMedios / FMBA_BloqTempMedios` (`indBloqueo=S`) — [!] PENDIENTE CONFIRMACIÓN AVV |

> **Contrato compartido:** El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en cada microservicio con los valores canónicos de **HU-101-ORQ**, sección _Enum de Operaciones_. El ADP recibe el valor ya convertido desde el ORQ — nunca comparar contra String literals en código de producción.

### Constantes de mapeo

| Campo        | Valor fijo | Descripción                                                        |
|--------------|-----------|---------------------------------------------------------------------|
| `indBloqueo` | `S`       | Indicador de bloqueo — confirmar si aplica para bloqueo definitivo |

### Mapeo de campos

| Campo obj_operacion | Campo AVV             | Notas                                                          |
|---------------------|-----------------------|----------------------------------------------------------------|
| `tipoDocumento`     | PENDIENTE POR DEFINIR | Confirmar codificación AVV para tipo de documento              |
| `numeroDocumento`   | PENDIENTE POR DEFINIR | Confirmar nombre del campo en el contrato AVV                  |
| `numeroTarjeta`     | PENDIENTE POR DEFINIR | Confirmar si recibe número enmascarado o completo              |
| `causal`            | PENDIENTE POR DEFINIR | Confirmar si la causal (BL01/BL02/BL03) se mapea a un campo del request AVV |

### Reglas de orquestación

- **RO-01:** El ADP no realiza validaciones funcionales sobre los campos recibidos en `obj_operacion`.
- **RO-02:** El contrato completo del servicio (campos de request/response) queda PENDIENTE CONFIRMACIÓN AVV.
- **RO-03:** El Circuit Breaker se activa ante fallos o timeouts del servicio AVV.
- **RO-04:** Los números de tarjeta circulan completos en el flujo funcional (entre ORQ, ADP y servicio bancario). El enmascaramiento se aplica **únicamente en logs** (Elastic): últimos 4 dígitos visibles (ejemplo: `****5678`). Nunca ofuscar el número real en el payload funcional.
- **RO-05:** El ADP publica en la cola SQS FIFO de auditoría el request recibido del ORQ y el response (o error) del banco, antes de retornar al ORQ. La cola es de tipo FIFO. El nombre de la cola es `avc-everest-pt-logs.fifo` (propiedad `messaging.sqs-queue-name`). Los mensajes de auditoría aplican las mismas reglas de enmascaramiento que los logs de esta HU.
- **RO-06:** La URL base y el path del servicio bancario son variables de ambiente independientes. Nunca se hardcodean en el código.

---

## Caminos Alternativos y Excepciones

| ID      | Condición                                     | Comportamiento                                                                                                                                       |
|---------|-----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| ALT-00  | Valor de `operacion` no esperado por este ADP | El ADP lanza `IllegalArgumentException` → retorna `400` al ORQ. Verificación defensiva: el ORQ no debería enrutar operaciones no soportadas a este ADP. |

---

## Tecnología a Usar

| Componente      | Tecnología   | Versión | Nota                                          |
|-----------------|--------------|---------|-----------------------------------------------|
| Lenguaje        | Java         | 17      | Arquetipo base ACE                            |
| Framework       | Spring Boot  | 3.x     |                                               |
| Cliente REST    | Retrofit 2.11.0 + OkHttp 4.12.0    |  2.11.0 / 4.12.0       | Para servicio AVV                             |
| Circuit Breaker | Resilience4j | —       | Activo en todos los consumos externos         |
| Logs            | Elastic      | —       |                                               |
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
| 1 | ¿`PFBA_CanalOtros295/WRBA_CanalOtros_BloqTempMedios` con `indBloqueo=S` aplica para bloqueo TD definitivo? | Define si la HU puede implementarse con este servicio |
| 2 | ¿Cuál es el contrato completo del servicio (campos de request y response)? | Define la implementación del adaptador |
| 3 | ¿Cuál es la codificación de causales en AVV para Robo/Pérdida/Fraude? | Define el mapeo causal → campo AVV |
| 4 | ¿Hay conectividad confirmada desde pods AKS hacia el ESB de AVV? | Bloquea pruebas en PT |

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

El ADP NO reenvía los headers del ORQ directamente al banco. Para la combinación `BLOQUEO_TD_DEFINITIVO + BAVV`, el ADP determina qué headers requiere el servicio bancario específico y construye únicamente esos.

### Nivel 3 — Headers enviados al banco

#### BLOQUEO_TD_DEFINITIVO → PFBA_CanalOtros295 / FMBA_BloqTempMedios (REST) — [!] PENDIENTE CONFIRMACIÓN AVV

Los headers requeridos por este servicio bancario se obtienen de la documentación técnica del banco (contrato del servicio). El ADP reenvía al banco únicamente los headers definidos en ese contrato — los de valor fijo se configuran como variables de ambiente y los de contexto se propagan desde el request entrante. El ADP no valida su presencia: si el llamador omite un header requerido, el banco retorna el error correspondiente.

---

## Definition of Ready


- [ ] AVV confirma que el servicio `PFBA_CanalOtros295` aplica para bloqueo TD definitivo
- [ ] Contrato completo del servicio documentado (campos request/response)
- [ ] Credenciales y certificados disponibles en PT
- [ ] Conectividad de red desde AKS hacia ESB AVV confirmada
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Servicio AVV confirmado y contrato documentado
- [ ] Reglas de Integración completas con mapeo de campos y causales
- [ ] Adaptador implementado y probado
- [ ] Pruebas de integración en PT aprobadas
- [ ] Aprobado por QA
- [ ] Publicación en cola SQS FIFO configurada e implementada — request y response encolados en cada invocación
