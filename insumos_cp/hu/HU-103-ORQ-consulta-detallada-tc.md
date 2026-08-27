# HU-103-ORQ: Orquestador — Consulta Detallada de Tarjeta de Crédito

## Metadatos

| Campo            | Valor                                                        |
|------------------|--------------------------------------------------------------|
| ID               | HU-103-ORQ                                                   |
| ID Servicio      | SFA-008                                                      |
| Épica            | Épica 1 — Consultas P1                                       |
| Componente       | Orquestador — Consulta Detallada de TC                       |
| Microservicio    | `ms-consultas-oficinas` (mismo que HU-101 y HU-102)          |
| Sprint           | Por definir                                                  |
| Prioridad        | Alta (P1)                                                    |
| Estimación       | Por estimar                                                  |
| Estado           | Pendiente                                                    |
| Autor            | Por definir                                                  |
| Fecha            | 2026-08-20                                                   |
| Última revisión  | 2026-08-20                                                   |

---

## Audiencias

| Rol / Audiencia       | Cómo interactúa                                                                                              |
|-----------------------|--------------------------------------------------------------------------------------------------------------|
| Asesor bancario       | Desde la pantalla de detalle de TC (luego de la consulta general), solicita información completa de la tarjeta |
| Desarrollador Backend | Implementa el endpoint del orquestador y la lógica de enrutamiento hacia el adaptador del banco               |
| QA / Tester           | Valida el enrutamiento, la validación de campos, los escenarios de error y la respuesta normalizada           |

---

## Historia de Usuario

**Como** asesor bancario autenticado en el canal Oficinas,  
**quiero** consultar el detalle completo de una tarjeta de crédito del cliente en la entidad seleccionada,  
**para** obtener cupo disponible, saldo, fecha de corte, pago mínimo y movimientos que me permitan orientar al cliente con precisión.

---

## Contexto de Negocio

Este endpoint se implementa dentro del microservicio `ms-consultas-oficinas`. El flujo típico es: el asesor realiza la consulta general (HU-101) y obtiene el inventario de tarjetas; desde esa vista selecciona una TC para ver el detalle completo.

La TC es un producto de **sensibilidad alta** (según SFA-007). El número de tarjeta se retorna siempre enmascarado. La validación de identidad es parametrizable al igual que en las demás consultas P1.

> **Nota AVV:** Se debe confirmar con AVV si `getBalanceByProduct` (código CCA) retorna el nivel de detalle requerido o si existe otro servicio específico para TC detallada.

---

## Criterios de Aceptación

- **CA-01:** El endpoint recibe el payload con `banco`, `tipoDocumento`, `numeroDocumento` y `referenciaTarjeta`. Todos son obligatorios.
- **CA-02:** El orquestador evalúa la primera condición: consulta la parametrización de la transacción para determinar si SFA-008 requiere validación de identidad. Si no la requiere, continúa directamente.
- **CA-03:** Si la parametrización exige validación, el orquestador evalúa la segunda condición: verifica si el cliente ya fue validado durante la interacción actual (por esta u otra transacción). Si existe validación previa, la reutiliza y continúa. Si no existe validación previa y el resultado de la nueva validación no es exitoso, retorna `403` con código `IDENTIDAD_NO_VALIDADA`.
- **CA-04:** La validación de identidad se gestiona por interacción con el cliente, no por transacción.
- **CA-05:** El orquestador enruta al adaptador correspondiente según `banco` (`BDB`, `AVV`, `OCC`, `BPO`).
- **CA-06:** El número de tarjeta se retorna siempre enmascarado en la respuesta normalizada.
- **CA-07:** El orquestador retorna la respuesta normalizada del adaptador sin modificar los datos de negocio.
- **CA-08:** Registra la trazabilidad: usuario, rol, fecha, hora, oficina, banco, cliente y referencia de tarjeta.
- **CA-09:** Si el adaptador retorna respuesta parcial con `bloquesFaltantes`, el orquestador la propaga sin convertirla en error.
- **CA-10:** El `user_id` se extrae siempre del JWT — nunca del body.
- **CA-11:** Prerequisito: debe existir una consulta general vigente (SFA-007 / HU-101) y una tarjeta de crédito seleccionada.

---

## Inputs

### Request body

```json
{
  "banco": "BDB",
  "tipoDocumento": "CC",
  "numeroDocumento": "12345678",
  "referenciaTarjeta": "************1234"
}
```

| Campo               | Tipo   | Descripción                                              | Obligatorio |
|---------------------|--------|----------------------------------------------------------|-------------|
| `banco`             | String | Código del banco destino                                 | SI          |
| `tipoDocumento`     | String | Tipo de documento del cliente                            | SI          |
| `numeroDocumento`   | String | Número de documento del cliente                          | SI          |
| `referenciaTarjeta` | String | Referencia de la tarjeta (número enmascarado o token)    | SI          |

> La naturaleza exacta de `referenciaTarjeta` (número enmascarado vs identificador interno) está **pendiente de definición** con cada banco.

### Headers

| Header           | Descripción                                    | Obligatorio |
|------------------|------------------------------------------------|-------------|
| `Authorization`  | Bearer JWT del asesor autenticado              | SI          |
| `X-Trace-Id`     | ID de traza para correlación de logs           | SI          |

---

## Outputs

### Respuesta exitosa (200)

```json
{
  "statusCode": "200",
  "statusDesc": "OK",
  "data": {
    "referenciaTarjeta": "************1234",
    "franquicia": "VISA",
    "estado": "ACTIVA",
    "cupoAprobado": 5000000.00,
    "cupoDisponible": 3200000.00,
    "saldoTotal": 1800000.00,
    "saldoDiferido": 400000.00,
    "cuotasDiferidas": 3,
    "tasaInteres": 28.5,
    "saldoMora": 0.00,
    "diasMora": 0,
    "fechaCorte": "2026-09-05",
    "fechaProximoPago": "2026-09-20",
    "pagoMinimo": 180000.00,
    "pagoTotal": 1800000.00
  }
}
```

### Errores

| Código HTTP | statusDesc                            | Condición                                      |
|-------------|---------------------------------------|------------------------------------------------|
| `400`       | Campos obligatorios faltantes         | Falta banco / documento / referenciaTarjeta    |
| `403`       | Identidad no validada                 | Parametrización exige validación no completada |
| `404`       | Tarjeta no encontrada                 | El banco no encontró la referencia de tarjeta  |
| `502`       | Error en el servicio del banco        | El adaptador retornó error                     |
| `504`       | Timeout del servicio del banco        | El adaptador excedió tiempo de respuesta       |

---

## Reglas de Negocio

1. **RN-01:** El `user_id` se extrae siempre del JWT — nunca del body.
2. **RN-02:** El número de tarjeta se retorna siempre **enmascarado** en la respuesta normalizada.
3. **RN-03:** La validación de identidad es parametrizable y se gestiona por interacción, no por transacción. Dos condiciones: (1) la configuración de SFA-008 debe exigir validación y (2) el cliente no debe haber sido validado durante la interacción actual por ninguna transacción. Solo si ambas condiciones se cumplen y la nueva validación falla, la consulta no se envía al banco.
4. **RN-04:** El orquestador no transforma datos de negocio — solo normaliza la envoltura de respuesta.
5. **RN-05:** Trazabilidad obligatoria: usuario, rol, fecha, hora, oficina, banco, cliente y referencia de tarjeta.
6. **RN-06:** Credenciales siempre en variables de ambiente.

---

## Caminos Alternativos y Excepciones

| ID      | Condición                                              | Comportamiento esperado                                                   |
|---------|--------------------------------------------------------|---------------------------------------------------------------------------|
| ALT-01  | Campo obligatorio faltante en el request               | Retorna `400` con detalle del campo faltante                              |
| ALT-02  | Banco enviado no está en la lista válida               | Retorna `400` con mensaje de banco no soportado                           |
| ALT-03  | Identidad no validada (parametrización lo exige)       | Retorna `403` con código `IDENTIDAD_NO_VALIDADA`                          |
| ALT-04  | Tarjeta no encontrada en el banco                     | Propaga el `404` del adaptador al canal                                   |
| ALT-05  | Respuesta parcial del adaptador (bloquesFaltantes)    | Propaga la respuesta parcial — no convierte en error                      |
| EXC-01  | Banco no disponible (adaptador retorna 503)            | Propaga `503` al canal                                                    |
| EXC-02  | Timeout en el adaptador                               | Propaga `504` al canal                                                    |
| EXC-03  | Error interno del orquestador                         | Retorna `500` y registra en Elastic                                       |

---

## Tecnología a Usar

| Componente        | Tecnología          | Versión  | Nota                                             |
|-------------------|---------------------|----------|--------------------------------------------------|
| Lenguaje          | Java                | 21       |                                                  |
| Framework         | Spring Boot         | 3.2.6    |                                                  |
| Despliegue        | Docker / AKS        | —        | Mismo pod que HU-101 y HU-102 (`ms-consultas-oficinas`) |
| Logs              | Elastic             | —        |                                                  |

---

## Endpoints

| Método  | Ruta                    | Propósito                                     |
|---------|-------------------------|-----------------------------------------------|
| `POST`  | `/consultas/v1/tc`      | Consultar detalle de una tarjeta de crédito   |

---

## Modelo de Datos

El orquestador no persiste datos. Registra trazabilidad en el log de auditoría.

| Entidad (log)          | Campos                                                                                      |
|------------------------|---------------------------------------------------------------------------------------------|
| `TrazabilidadConsulta` | usuarioId, rol, oficina, banco, tipoDocumento, numeroDocumento, referenciaTarjeta, fechaHora, resultado |

---

## Dependencias

| HU / Componente      | Relación     | Descripción                                                            |
|----------------------|--------------|------------------------------------------------------------------------|
| HU-101-ORQ           | Relacionada  | Consulta general que provee la `referenciaTarjeta` al asesor          |
| HU-103-ADP-BDB       | Hijo         | Adaptador BdB para TC detallada                                       |
| HU-103-ADP-AVV       | Hijo         | Adaptador AVV para TC detallada                                       |
| HU-103-ADP-OCC       | Hijo         | Adaptador OCC para TC detallada                                       |
| HU-103-ADP-BPO       | Hijo         | Adaptador BPO para TC detallada                                       |
| HU-T02               | Prerrequisito condicional | Validación de huella — se invoca si parametrización lo exige |

---

## Seguridad

- **Autenticación:** Bearer Token JWT obligatorio.
- **Enmascaramiento:** Número de tarjeta siempre enmascarado en respuesta — obligatorio.
- **Validación de identidad:** Parametrizable.
- **Credenciales:** En variables de ambiente.

---

## Escenarios Gherkin

```gherkin
Feature: Orquestador — Consulta Detallada de Tarjeta de Crédito
  Como asesor autenticado
  Quiero consultar el detalle de una tarjeta de crédito
  Para orientar al cliente con información completa de su TC

  Background:
    Given el asesor está autenticado con JWT válido
    And el microservicio ms-consultas-oficinas está disponible

  Scenario: Consulta exitosa — número enmascarado en respuesta
    Given la parametrización no requiere validación de identidad
    And el banco "BDB" está disponible
    When el asesor envía banco "BDB", documento y referenciaTarjeta "************1234"
    Then el orquestador enruta al adaptador BdB
    And retorna el detalle con StatusCode 200
    And el número de tarjeta en la respuesta está enmascarado
    And registra la trazabilidad

  Scenario: Consulta exitosa — validación reutilizada de la interacción actual
    Given la parametrización requiere validación de identidad
    And el cliente ya fue validado durante la interacción actual por otra transacción
    When el asesor selecciona la tarjeta a consultar
    Then Everest reutiliza la validación existente y habilita el flujo
    And el asesor envía la solicitud al orquestador
    And el orquestador enruta al adaptador y retorna el detalle

  Scenario: Flujo bloqueado — validación de identidad requerida y pendiente
    Given la parametrización requiere validación de identidad
    And no existe validación previa del cliente en la interacción actual
    When el asesor intenta avanzar hacia la consulta de la tarjeta
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

  Scenario: Tarjeta no encontrada
    Given el banco "OCC" está disponible
    When el asesor envía una referenciaTarjeta que no existe en OCC
    Then el orquestador retorna 404

  Scenario: Campo obligatorio faltante
    Given el request no incluye el campo "referenciaTarjeta"
    When el asesor envía la solicitud
    Then el orquestador retorna 400 con detalle del campo faltante
```

---

## Notas Técnicas

- La `referenciaTarjeta` debe ser suficiente para identificar unívocamente la tarjeta en el banco destino. Coordinar con cada banco si se usa el número enmascarado como token de búsqueda o si se requiere un identificador interno.
- El enmascaramiento del número de tarjeta debe aplicarse en el adaptador antes de retornar al orquestador.

---

## Definition of Ready

- [ ] Definición de `referenciaTarjeta` acordada con los 4 bancos (¿número enmascarado o ID interno?)
- [ ] Modelo de respuesta normalizado de TC definido y acordado
- [ ] Mecanismo de parametrización de identidad validado (mismo que HU-101)
- [ ] Campos de trazabilidad definidos
- [ ] Al menos un adaptador listo para prueba
- [ ] HU-101-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación de story points asignada
- [ ] Aprobada por líder técnico y product owner

---

## Definition of Done

- [ ] Endpoint `POST /consultas/v1/tc` implementado en `ms-consultas-oficinas`
- [ ] Evaluación de parametrización de identidad implementada
- [ ] Enrutamiento por banco implementado
- [ ] Número de tarjeta enmascarado en respuesta — validado en pruebas
- [ ] Trazabilidad registrada por cada consulta
- [ ] Pruebas unitarias (cobertura ≥ 80%)
- [ ] Prueba de integración con al menos un adaptador en PT
- [ ] Aprobado por QA
- [ ] Aprobado por product owner
