# HU-102-ORQ: Orquestador — Consulta Detallada de Cartera

## Metadatos

| Campo            | Valor                                                        |
|------------------|--------------------------------------------------------------|
| ID               | HU-102-ORQ                                                   |
| ID Servicio      | SFA-008                                                      |
| Épica            | Épica 1 — Consultas P1                                       |
| Componente       | Orquestador — Consulta Detallada de Cartera                  |
| Microservicio    | `ms-consultas-oficinas` (mismo que HU-101)                   |
| Sprint           | Por definir                                                  |
| Prioridad        | Alta (P1)                                                    |
| Estimación       | Por estimar                                                  |
| Estado           | Pendiente                                                    |
| Autor            | Por definir                                                  |
| Fecha            | 2026-08-20                                                   |
| Última revisión  | 2026-08-20                                                   |

---

## Audiencias

| Rol / Audiencia       | Cómo interactúa                                                                                            |
|-----------------------|------------------------------------------------------------------------------------------------------------|
| Asesor bancario       | Desde la pantalla de detalle de cartera (luego de la consulta general), solicita información completa de la obligación |
| Desarrollador Backend | Implementa el endpoint del orquestador y la lógica de enrutamiento hacia el adaptador del banco            |
| QA / Tester           | Valida el enrutamiento, la validación de campos, los escenarios de error y la respuesta normalizada        |
| Arquitecto            | Valida que el patrón orquestador-adaptador se aplique correctamente dentro de `ms-consultas-oficinas`      |

---

## Historia de Usuario

**Como** asesor bancario autenticado en el canal Oficinas,  
**quiero** consultar el detalle completo de una obligación de cartera del cliente en la entidad seleccionada,  
**para** obtener información de cuotas, saldo capital, saldo en mora, tasa y próximo pago que me permita orientar al cliente de forma precisa.

---

## Contexto de Negocio

Esta HU implementa un nuevo endpoint dentro del microservicio `ms-consultas-oficinas` (mismo desplegable que HU-101-ORQ). El flujo típico es: el asesor realiza primero la consulta general (HU-101) y obtiene el inventario de obligaciones del cliente; desde esa vista selecciona una obligación de cartera para ver el detalle.

La consulta detallada de cartera es no monetaria y de solo lectura. La validación de identidad es parametrizable: Everest consulta la configuración de la transacción para determinar si se requiere validación biométrica antes de enviar la consulta al banco.

> **Nota OCC:** El servicio de cartera detallada de Banco de Occidente presenta un gap técnico (no existe web service; el dato está en BI Publisher/ODS). El adaptador HU-102-ADP-OCC queda bloqueado hasta que OCC desarrolle o exponga el servicio. El orquestador debe retornar `503` con mensaje de banco no disponible cuando el banco enrutado es OCC.

---

## Criterios de Aceptación

- **CA-01:** El endpoint recibe el payload con `banco`, `tipoDocumento`, `numeroDocumento` y `numeroObligacion`. Todos son obligatorios.
- **CA-02:** El orquestador evalúa la primera condición: consulta la parametrización de la transacción para determinar si SFA-008 requiere validación de identidad. Si no la requiere, continúa directamente.
- **CA-03:** Si la parametrización exige validación, el orquestador evalúa la segunda condición: verifica si el cliente ya fue validado durante la interacción actual (por esta u otra transacción). Si existe validación previa, la reutiliza y continúa. Si no existe validación previa y el resultado de la nueva validación no es exitoso, retorna `403` con código `IDENTIDAD_NO_VALIDADA` y no envía la consulta al adaptador.
- **CA-04:** La validación de identidad se gestiona por interacción con el cliente, no por transacción. Una validación exitosa en la misma interacción se reutiliza para SFA-008 sin volver a solicitarla.
- **CA-05:** El orquestador enruta la petición al adaptador correspondiente según el campo `banco` (`BDB`, `AVV`, `OCC`, `BPO`).
- **CA-06:** Si el banco es `OCC`, el orquestador retorna `503` con mensaje `"Servicio no disponible para esta entidad"` hasta que el gap de OCC esté resuelto.
- **CA-07:** El orquestador retorna la respuesta normalizada del adaptador sin modificar los datos de negocio.
- **CA-08:** El orquestador registra la trazabilidad de la consulta: usuario, rol, fecha, hora, oficina, banco consultado, cliente consultado y obligación.
- **CA-09:** Si el adaptador retorna respuesta parcial con `bloquesFaltantes`, el orquestador la propaga al canal sin convertirla en error.
- **CA-10:** El `user_id` se extrae siempre del JWT — nunca del body.
- **CA-11:** Prerequisito: debe existir una consulta general vigente (SFA-007 / HU-101) y una obligación de cartera seleccionada.

---

## Inputs

### Request body

```json
{
  "banco": "BDB",
  "tipoDocumento": "CC",
  "numeroDocumento": "12345678",
  "numeroObligacion": "987654321"
}
```

| Campo              | Tipo   | Descripción                               | Obligatorio | Ejemplo      |
|--------------------|--------|-------------------------------------------|-------------|--------------|
| `banco`            | String | Código del banco destino                  | SI          | `BDB`, `AVV`, `OCC`, `BPO` |
| `tipoDocumento`    | String | Tipo de documento del cliente             | SI          | `CC`, `CE`, `NIT` |
| `numeroDocumento`  | String | Número de documento del cliente           | SI          | `12345678`   |
| `numeroObligacion` | String | Número de la obligación a consultar       | SI          | `987654321`  |

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
    "numeroObligacion": "987654321",
    "tipoCartera": "LIBRE_DESTINO",
    "estado": "AL_DIA",
    "oficina": "0123",
    "fechaDesembolso": "2023-03-15",
    "fechaVencimiento": "2028-03-15",
    "plazoMeses": 60,
    "cuotasPagadas": 29,
    "cuotasPendientes": 31,
    "valorCuota": 450000.00,
    "saldoCapital": 12500000.00,
    "saldoInteresesCorrientes": 320000.00,
    "saldoInteresesMora": 0.00,
    "saldoMora": 0.00,
    "diasMora": 0,
    "tasaEA": 18.5,
    "proximaFechaPago": "2026-09-15",
    "valorProximoPago": 450000.00
  }
}
```

### Respuesta parcial (200 con bloquesFaltantes)

```json
{
  "statusCode": "206",
  "statusDesc": "Respuesta parcial",
  "data": { ... },
  "bloquesFaltantes": ["detalleAmortizacion"]
}
```

### Errores

| Código HTTP | statusDesc                            | Condición                                      |
|-------------|---------------------------------------|------------------------------------------------|
| `400`       | Campos obligatorios faltantes         | Falta banco / tipoDocumento / numeroDocumento / numeroObligacion |
| `403`       | Identidad no validada                 | Parametrización exige validación y no fue completada |
| `404`       | Obligación no encontrada              | El banco no encontró la obligación             |
| `503`       | Servicio no disponible para OCC       | Gap técnico OCC — sin web service              |
| `502`       | Error en el servicio del banco        | El adaptador retornó error                     |
| `504`       | Timeout del servicio del banco        | El adaptador excedió el tiempo de respuesta    |

---

## Reglas de Negocio

1. **RN-01:** El `user_id` se extrae siempre del JWT — nunca del cuerpo de la petición.
2. **RN-02:** La operación es de solo lectura — no modifica datos del cliente ni de la obligación.
3. **RN-03:** La validación de identidad es parametrizable y se gestiona por interacción, no por transacción. Dos condiciones: (1) la configuración de SFA-008 debe exigir validación y (2) el cliente no debe haber sido validado durante la interacción actual por ninguna transacción. Solo si ambas condiciones se cumplen y la nueva validación falla, la consulta no se envía al banco.
4. **RN-04:** El orquestador no transforma los datos de negocio de la respuesta del adaptador — solo normaliza la estructura de envoltura (`statusCode`, `statusDesc`, `data`).
5. **RN-05:** Trazabilidad obligatoria: registrar usuario, rol, fecha, hora, oficina, banco consultado, cliente y número de obligación.
6. **RN-06:** Las credenciales siempre en variables de ambiente.
7. **RN-07:** El banco `OCC` retorna `503` hasta que el gap de cartera quede resuelto.

---

## Caminos Alternativos y Excepciones

| ID      | Condición                                                        | Comportamiento esperado                                                  |
|---------|------------------------------------------------------------------|--------------------------------------------------------------------------|
| ALT-01  | Campo obligatorio faltante en el request                        | Retorna `400` con detalle del campo faltante                             |
| ALT-02  | Banco enviado no está en la lista válida                        | Retorna `400` con mensaje de banco no soportado                          |
| ALT-03  | Banco = OCC (gap técnico activo)                                | Retorna `503` con mensaje `"Servicio no disponible para esta entidad"`   |
| ALT-04  | Identidad no validada (parametrización lo exige)                | Retorna `403` con código `IDENTIDAD_NO_VALIDADA`                         |
| ALT-05  | Obligación no encontrada en el banco                            | Propaga el `404` del adaptador al canal                                  |
| ALT-06  | Respuesta parcial del adaptador (bloquesFaltantes)              | Propaga la respuesta parcial con el indicador — no convierte en error    |
| EXC-01  | Banco no disponible (adaptador retorna 503)                     | Propaga `503` al canal                                                   |
| EXC-02  | Timeout en el adaptador                                         | Propaga `504` al canal                                                   |
| EXC-03  | Error interno del orquestador                                   | Retorna `500` y registra en Elastic                                      |

---

## Tecnología a Usar

| Componente        | Tecnología          | Versión  | Nota                                             |
|-------------------|---------------------|----------|--------------------------------------------------|
| Lenguaje          | Java                | 21       |                                                  |
| Framework         | Spring Boot         | 3.2.6    |                                                  |
| Despliegue        | Docker / AKS        | —        | Mismo pod que HU-101 (`ms-consultas-oficinas`)   |
| Mensajería        | Azure Service Bus   | 2.4.0    | Para trazabilidad asíncrona si aplica            |
| Logs              | Elastic             | —        |                                                  |

---

## Endpoints

| Método  | Ruta                               | Propósito                                        |
|---------|------------------------------------|--------------------------------------------------|
| `POST`  | `/consultas/v1/cartera`            | Consultar detalle de una obligación de cartera   |

> El path exacto está pendiente de confirmación con el equipo de arquitectura. Se define dentro de `ms-consultas-oficinas`.

---

## Modelo de Datos

El orquestador no persiste datos. Registra trazabilidad en el log de auditoría del microservicio.

| Entidad (log)       | Campos                                                                                   |
|---------------------|------------------------------------------------------------------------------------------|
| `TrazabilidadConsulta` | usuarioId, rol, oficina, banco, tipoDocumento, numeroDocumento, numeroObligacion, fechaHora, resultado |

---

## Dependencias

| HU / Componente      | Relación     | Descripción                                                       |
|----------------------|--------------|-------------------------------------------------------------------|
| HU-101-ORQ           | Relacionada  | Consulta general que provee el `numeroObligacion` al asesor       |
| HU-102-ADP-BDB       | Hijo         | Adaptador BdB para cartera detallada                              |
| HU-102-ADP-AVV       | Hijo         | Adaptador AVV para cartera detallada                              |
| HU-102-ADP-OCC       | Hijo (GAP)   | Adaptador OCC — bloqueado por gap técnico                         |
| HU-102-ADP-BPO       | Hijo         | Adaptador BPO para cartera detallada                              |
| HU-T02               | Prerrequisito condicional | Validación de huella — se invoca si parametrización lo exige |

---

## Seguridad

- **Autenticación:** Bearer Token JWT obligatorio. El `user_id` siempre proviene del token, nunca del body.
- **Validación de identidad:** Parametrizable por transacción — el orquestador evalúa la configuración antes de enrutar.
- **Credenciales:** Siempre en variables de ambiente.
- **Enmascaramiento:** No aplica en este endpoint (la cartera no tiene campos con enmascaramiento requerido; los números de documento se reciben del asesor autenticado).

---

## Consideraciones No Funcionales

| Atributo           | Valor / Descripción                                              |
|--------------------|------------------------------------------------------------------|
| Tiempo de respuesta| < 5 s extremo a extremo (incluyendo llamada al banco)           |
| Disponibilidad     | En línea — no procesamiento por lotes                           |
| Trazabilidad       | Log inmutable por cada consulta                                 |
| Escalabilidad      | El microservicio escala horizontalmente en AKS                  |

---

## Escenarios Gherkin

```gherkin
Feature: Orquestador — Consulta Detallada de Cartera
  Como asesor autenticado
  Quiero consultar el detalle de una obligación de cartera
  Para orientar al cliente con información precisa de su crédito

  Background:
    Given el asesor está autenticado con JWT válido
    And el microservicio ms-consultas-oficinas está disponible

  Scenario: Consulta exitosa sin validación de identidad requerida
    Given la parametrización de la transacción no requiere validación de identidad
    And el banco "BDB" está disponible
    When el asesor envía banco "BDB", tipoDocumento "CC", numeroDocumento "12345678", numeroObligacion "987654321"
    Then el orquestador enruta al adaptador BdB
    And retorna el detalle de la obligación con StatusCode 200
    And registra la trazabilidad de la consulta

  Scenario: Flujo bloqueado — validación de identidad requerida y pendiente
    Given la parametrización de la transacción requiere validación de identidad
    And no existe validación previa del cliente en la interacción actual
    When el asesor intenta avanzar hacia la consulta de cartera
    Then Everest habilita el mecanismo de validación de identidad (lector de huellas)
    And el flujo queda bloqueado — el asesor no puede continuar sin completar la validación
    And no se envía ninguna solicitud al banco

  Scenario: Flujo bloqueado — validación biométrica fallida
    Given la parametrización de la transacción requiere validación de identidad
    And no existe validación previa del cliente en la interacción actual
    And el asesor ejecutó la validación biométrica sin éxito
    When el asesor intenta continuar
    Then el flujo permanece bloqueado
    And no se envía ninguna solicitud al banco

  Scenario: Consulta exitosa — validación reutilizada de la interacción actual
    Given la parametrización requiere validación de identidad
    And el cliente ya fue validado durante la interacción actual por otra transacción
    When el asesor selecciona la obligación de cartera a consultar
    Then Everest reutiliza la validación existente y habilita el flujo
    And el asesor envía la solicitud al orquestador
    And el orquestador enruta al adaptador correspondiente y retorna el detalle

  Scenario: Consulta exitosa — validación biométrica completada en esta transacción
    Given la parametrización requiere validación de identidad
    And no existe validación previa del cliente en la interacción actual
    And el asesor completa la validación biométrica exitosamente
    When el flujo se desbloquea y el asesor envía la solicitud
    Then el orquestador enruta al adaptador correspondiente
    And retorna el detalle con StatusCode 200

  Scenario: Banco OCC — gap técnico activo
    Given el banco seleccionado es "OCC"
    When el asesor envía la solicitud de consulta de cartera
    Then el orquestador retorna 503 con mensaje "Servicio no disponible para esta entidad"
    And no intenta llamar al adaptador OCC

  Scenario: Obligación no encontrada
    Given el banco "BDB" está disponible
    When el asesor envía un numeroObligacion que no existe en BdB
    Then el orquestador retorna 404 con mensaje de obligación no encontrada

  Scenario: Campo obligatorio faltante
    Given el request no incluye el campo "numeroObligacion"
    When el asesor envía la solicitud
    Then el orquestador retorna 400 con detalle del campo faltante

  Scenario: Banco no disponible
    Given el banco "BDB" no está disponible
    When el asesor envía la solicitud de consulta de cartera
    Then el orquestador retorna 503 con mensaje de banco no disponible
```

---

## Notas Técnicas

- Este endpoint se implementa en el microservicio `ms-consultas-oficinas`, mismo desplegable y mismo repositorio que HU-101-ORQ. No se requiere un nuevo microservicio.
- El `numeroObligacion` es el identificador obtenido de la respuesta de HU-101 (consulta general). El orquestador no valida su existencia — la delega al adaptador del banco.
- El gap de OCC (cartera sin web service) debe ser resuelto por el equipo de OCC. Hasta que esté resuelto, el orquestador retorna 503 para ese banco en esta operación.

---

## Definition of Ready

> La HU puede entrar a sprint solo cuando **todos** los ítems están cumplidos.

- [ ] Modelo de respuesta normalizado de cartera definido y acordado con el equipo funcional
- [ ] Mecanismo de parametrización de identidad definido (mismo que HU-101 o variante)
- [ ] Campos de trazabilidad definidos y acordados
- [ ] Comportamiento del gap OCC documentado y aprobado (retornar 503)
- [ ] Al menos un adaptador listo para prueba (HU-102-ADP-BDB o HU-102-ADP-BPO)
- [ ] HU-101-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación de story points asignada por el equipo
- [ ] Aprobada por líder técnico y product owner

---

## Definition of Done

- [ ] Endpoint `POST /consultas/v1/cartera` implementado en `ms-consultas-oficinas`
- [ ] Evaluación de parametrización de identidad implementada
- [ ] Enrutamiento por banco implementado (BDB, AVV, OCC=503, BPO)
- [ ] Respuesta parcial propagada sin conversión a error
- [ ] Trazabilidad registrada por cada consulta
- [ ] `user_id` extraído del JWT — validado en pruebas
- [ ] Pruebas unitarias del orquestador (cobertura ≥ 80%)
- [ ] Prueba de integración con al menos un adaptador en PT
- [ ] Aprobado por QA
- [ ] Aprobado por product owner
