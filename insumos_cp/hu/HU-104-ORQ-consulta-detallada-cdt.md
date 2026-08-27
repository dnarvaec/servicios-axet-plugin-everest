# HU-104-ORQ: Orquestador — Consulta Detallada de CDT

## Metadatos

| Campo            | Valor                                                        |
|------------------|--------------------------------------------------------------|
| ID               | HU-104-ORQ                                                   |
| ID Servicio      | SFA-008                                                      |
| Épica            | Épica 1 — Consultas P1                                       |
| Componente       | Orquestador — Consulta Detallada de CDT                      |
| Microservicio    | `ms-consultas-oficinas` (mismo que HU-101, HU-102, HU-103)   |
| Sprint           | Por definir                                                  |
| Prioridad        | Alta (P1)                                                    |
| Estimación       | Por estimar                                                  |
| Estado           | Pendiente                                                    |
| Autor            | Por definir                                                  |
| Fecha            | 2026-08-20                                                   |
| Última revisión  | 2026-08-20                                                   |

---

## Audiencias

| Rol / Audiencia       | Cómo interactúa                                                                                             |
|-----------------------|-------------------------------------------------------------------------------------------------------------|
| Asesor bancario       | Desde la pantalla de detalle de CDT (luego de la consulta general), solicita la información completa del CDT |
| Desarrollador Backend | Implementa el endpoint en `ms-consultas-oficinas` y la lógica de enrutamiento                               |
| QA / Tester           | Valida enrutamiento, validación de campos, escenarios de error y respuesta normalizada                      |

---

## Historia de Usuario

**Como** asesor bancario autenticado en el canal Oficinas,  
**quiero** consultar el detalle completo de un CDT del cliente en la entidad seleccionada,  
**para** obtener monto, tasa, fecha de vencimiento y condiciones del certificado para orientar al cliente.

---

## Contexto de Negocio

Nuevo endpoint dentro de `ms-consultas-oficinas`. El flujo típico: el asesor realiza la consulta general (HU-101) y obtiene el inventario de CDTs; desde esa vista selecciona un CDT para ver su detalle.

La consulta es no monetaria y de solo lectura. La validación de identidad es parametrizable.

> **Nota BPO:** No existe documentación de servicio de CDT detallado para BPO. El adaptador HU-104-ADP-BPO queda bloqueado hasta que BPO confirme o desarrolle el servicio. El orquestador retorna `503` para BPO en esta operación mientras el gap esté activo.

> **Nota AVV:** Se debe confirmar si `getBalanceByProduct` (código CDA) cubre el detalle de CDT en AVV.

---

## Criterios de Aceptación

- **CA-01:** El endpoint recibe `banco`, `tipoDocumento`, `numeroDocumento` y `numeroProducto`. Todos obligatorios.
- **CA-02:** El orquestador evalúa la primera condición: consulta la parametrización de la transacción para determinar si SFA-008 requiere validación de identidad. Si no la requiere, continúa directamente.
- **CA-03:** Si la parametrización exige validación, el orquestador evalúa la segunda condición: verifica si el cliente ya fue validado durante la interacción actual (por esta u otra transacción). Si existe validación previa, la reutiliza y continúa. Si no existe validación previa y el resultado de la nueva validación no es exitoso, retorna `403` con código `IDENTIDAD_NO_VALIDADA`.
- **CA-04:** La validación de identidad se gestiona por interacción con el cliente, no por transacción.
- **CA-05:** Enruta al adaptador según `banco` (`BDB`, `AVV`, `OCC`, `BPO`).
- **CA-06:** Si el banco es `BPO`, retorna `503` con mensaje `"Servicio no disponible para esta entidad"` hasta resolver el gap.
- **CA-07:** Retorna la respuesta normalizada del adaptador sin modificar datos de negocio.
- **CA-08:** Registra trazabilidad: usuario, rol, fecha, hora, oficina, banco, cliente y número de producto.
- **CA-09:** Si el adaptador retorna respuesta parcial con `bloquesFaltantes`, la propaga sin convertir en error.
- **CA-10:** El `user_id` se extrae siempre del JWT — nunca del body.
- **CA-11:** Prerequisito: debe existir una consulta general vigente (SFA-007 / HU-101) y un CDT seleccionado.

---

## Inputs

### Request body

```json
{
  "banco": "BDB",
  "tipoDocumento": "CC",
  "numeroDocumento": "12345678",
  "numeroProducto": "CDT-123456"
}
```

| Campo             | Tipo   | Descripción                                | Obligatorio |
|-------------------|--------|--------------------------------------------|-------------|
| `banco`           | String | Código del banco destino                   | SI          |
| `tipoDocumento`   | String | Tipo de documento del cliente              | SI          |
| `numeroDocumento` | String | Número de documento del cliente            | SI          |
| `numeroProducto`  | String | Número o referencia del CDT a consultar    | SI          |

### Headers

| Header           | Descripción                          | Obligatorio |
|------------------|--------------------------------------|-------------|
| `Authorization`  | Bearer JWT del asesor autenticado    | SI          |
| `X-Trace-Id`     | ID de traza                          | SI          |

---

## Outputs

### Respuesta exitosa (200)

```json
{
  "statusCode": "200",
  "statusDesc": "OK",
  "data": {
    "numeroProducto": "CDT-123456",
    "monto": 20000000.00,
    "tasaEA": 12.5,
    "fechaApertura": "2025-03-01",
    "fechaVencimiento": "2026-03-01",
    "plazosDias": 365,
    "periodicidadIntereses": "AL_VENCIMIENTO",
    "interesesAcumulados": 2500000.00,
    "estado": "VIGENTE"
  }
}
```

### Errores

| Código HTTP | statusDesc                            | Condición                                     |
|-------------|---------------------------------------|-----------------------------------------------|
| `400`       | Campos obligatorios faltantes         | Falta banco / documento / numeroProducto      |
| `403`       | Identidad no validada                 | Parametrización exige validación no completada|
| `404`       | CDT no encontrado                     | El banco no encontró el producto              |
| `503`       | Servicio no disponible para BPO       | Gap técnico BPO                               |
| `502`       | Error en el servicio del banco        | El adaptador retornó error                    |
| `504`       | Timeout del servicio del banco        | El adaptador excedió tiempo de respuesta      |

---

## Reglas de Negocio

1. **RN-01:** `user_id` del JWT — nunca del body.
2. **RN-02:** Operación de solo lectura.
3. **RN-03:** La validación de identidad es parametrizable y se gestiona por interacción, no por transacción. Dos condiciones: (1) la configuración de SFA-008 debe exigir validación y (2) el cliente no debe haber sido validado durante la interacción actual por ninguna transacción. Solo si ambas condiciones se cumplen y la nueva validación falla, la consulta no se envía al banco.
4. **RN-04:** No transforma datos de negocio del adaptador.
5. **RN-05:** Trazabilidad obligatoria.
6. **RN-06:** Credenciales en variables de ambiente.
7. **RN-07:** Banco `BPO` retorna `503` mientras el gap esté activo.

---

## Caminos Alternativos y Excepciones

| ID      | Condición                                           | Comportamiento esperado                                               |
|---------|-----------------------------------------------------|-----------------------------------------------------------------------|
| ALT-01  | Campo obligatorio faltante                          | Retorna `400` con detalle del campo                                   |
| ALT-02  | Banco no válido                                     | Retorna `400`                                                         |
| ALT-03  | Banco = BPO (gap activo)                            | Retorna `503` con mensaje de servicio no disponible                   |
| ALT-04  | Identidad no validada                               | Retorna `403` con código `IDENTIDAD_NO_VALIDADA`                      |
| ALT-05  | CDT no encontrado                                   | Propaga `404` del adaptador                                           |
| ALT-06  | Respuesta parcial (bloquesFaltantes)                | Propaga sin convertir en error                                        |
| EXC-01  | Banco no disponible (503 del adaptador)             | Propaga `503`                                                         |
| EXC-02  | Timeout                                             | Propaga `504`                                                         |
| EXC-03  | Error interno orquestador                           | Retorna `500` y registra en Elastic                                   |

---

## Tecnología a Usar

| Componente     | Tecnología        | Versión | Nota                                              |
|----------------|-------------------|---------|---------------------------------------------------|
| Lenguaje       | Java              | 21      |                                                   |
| Framework      | Spring Boot       | 3.2.6   |                                                   |
| Despliegue     | Docker / AKS      | —       | Mismo pod que HU-101/102/103 (`ms-consultas-oficinas`) |
| Logs           | Elastic           | —       |                                                   |

---

## Endpoints

| Método | Ruta                    | Propósito                          |
|--------|-------------------------|------------------------------------|
| `POST` | `/consultas/v1/cdt`     | Consultar detalle de un CDT        |

---

## Modelo de Datos

| Entidad (log)          | Campos                                                                                    |
|------------------------|-------------------------------------------------------------------------------------------|
| `TrazabilidadConsulta` | usuarioId, rol, oficina, banco, tipoDocumento, numeroDocumento, numeroProducto, fechaHora, resultado |

---

## Dependencias

| HU / Componente      | Relación     | Descripción                                              |
|----------------------|--------------|----------------------------------------------------------|
| HU-101-ORQ           | Relacionada  | Consulta general que provee el `numeroProducto` al asesor|
| HU-104-ADP-BDB       | Hijo         | Adaptador BdB                                            |
| HU-104-ADP-AVV       | Hijo         | Adaptador AVV                                            |
| HU-104-ADP-OCC       | Hijo         | Adaptador OCC                                            |
| HU-104-ADP-BPO       | Hijo (GAP)   | Adaptador BPO — bloqueado por gap técnico                |

---

## Seguridad

- **Autenticación:** Bearer Token JWT. `user_id` del token.
- **Validación de identidad:** Parametrizable.
- **Credenciales:** En variables de ambiente.

---

## Escenarios Gherkin

```gherkin
Feature: Orquestador — Consulta Detallada de CDT
  Background:
    Given el asesor está autenticado con JWT válido
    And el microservicio ms-consultas-oficinas está disponible

  Scenario: Consulta exitosa sin validación de identidad
    Given la parametrización no requiere validación de identidad
    And el banco "BDB" está disponible
    When el asesor envía banco "BDB", documento y numeroProducto "CDT-123456"
    Then el orquestador enruta al adaptador BdB
    And retorna el detalle con StatusCode 200
    And registra la trazabilidad

  Scenario: Consulta exitosa — validación reutilizada de la interacción actual
    Given la parametrización requiere validación de identidad
    And el cliente ya fue validado durante la interacción actual por otra transacción
    When el asesor selecciona el CDT a consultar
    Then Everest reutiliza la validación existente y habilita el flujo
    And el asesor envía la solicitud al orquestador
    And el orquestador enruta al adaptador BdB y retorna el detalle

  Scenario: Flujo bloqueado — validación de identidad requerida y pendiente
    Given la parametrización requiere validación de identidad
    And no existe validación previa del cliente en la interacción actual
    When el asesor intenta avanzar hacia la consulta del CDT
    Then Everest habilita el mecanismo de validación de identidad (lector de huellas)
    And el flujo queda bloqueado — el asesor no puede continuar sin completar la validación
    And no se envía ninguna solicitud al banco

  Scenario: Flujo bloqueado — validación biométrica fallida
    Given la parametrización requiere validación de identidad
    And no existe validación previa del cliente en la interacción actual
    And el asesor ejecutó la validación biométrica sin éxito
    When el asesor intenta continuar
    Then el flujo permanece bloqueado
    And no se envía ninguna solicitud al banco

  Scenario: Banco BPO — gap técnico activo
    Given el banco seleccionado es "BPO"
    When el asesor envía la solicitud
    Then el orquestador retorna 503 con mensaje de servicio no disponible

  Scenario: CDT no encontrado
    Given el banco "OCC" está disponible
    When el asesor envía un numeroProducto que no existe
    Then el orquestador retorna 404

  Scenario: Campo obligatorio faltante
    Given el request no incluye "numeroProducto"
    When el asesor envía la solicitud
    Then retorna 400 con detalle del campo faltante
```

---

## Notas Técnicas

- Este endpoint se implementa en `ms-consultas-oficinas`. No se requiere nuevo microservicio.
- El gap de BPO (CDT sin documentación) debe resolverse con el equipo de BPO. Mientras tanto, el orquestador retorna 503 para BPO en esta operación.

---

## Definition of Ready

- [ ] Modelo de respuesta normalizado de CDT definido y acordado
- [ ] Mecanismo de parametrización de identidad validado
- [ ] Campos de trazabilidad definidos
- [ ] Comportamiento del gap BPO documentado y aprobado (retornar 503)
- [ ] Al menos un adaptador listo para prueba (BDB u OCC)
- [ ] HU-101-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Endpoint `POST /consultas/v1/cdt` implementado
- [ ] Evaluación de parametrización de identidad implementada
- [ ] Enrutamiento por banco implementado (BDB, AVV, OCC, BPO=503)
- [ ] Trazabilidad implementada
- [ ] Pruebas unitarias (≥ 80%)
- [ ] Prueba de integración con al menos un adaptador en PT
- [ ] Aprobado por QA y product owner
