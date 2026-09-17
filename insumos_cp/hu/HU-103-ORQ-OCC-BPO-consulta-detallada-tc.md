# HU-103-ORQ: Orquestador — Consulta Detallada de Tarjeta de Crédito

## Metadatos

| Campo            | Valor                                                        |
|------------------|--------------------------------------------------------------|
| ID               | HU-103-ORQ                                                   |
| ID Servicio      | SFA-008                                                      |
| Épica            | Épica 1 — Consultas P1                                       |
| Componente       | Orquestador — Consulta Detallada de TC                       |
| Microservicio    | `ofic-consultas-orq`                                         |
| Sprint           | Por definir                                                  |
| Prioridad        | Alta (P1)                                                    |
| Estimación       | Por estimar                                                  |
| Estado           | **Desarrollada**                                             |
| Autor            | Por definir                                                  |
| Fecha            | 2026-08-20                                                   |
| Última revisión  | 2026-09-03 — gestión de headers documentada; propagación ORQ→ADP explicitada; OperacionEnum documentado como contrato compartido (ofic-commons); operación no soportada: excepción + 400 documentada |

---

## Audiencias

| Rol / Audiencia       | Cómo interactúa                                                                                              |
|-----------------------|--------------------------------------------------------------------------------------------------------------|
| Asesor bancario       | Desde la pantalla de detalle de TC (luego de la consulta general), solicita información completa de la tarjeta |
| Desarrollador Backend | Implementa el endpoint del orquestador y la lógica de enrutamiento hacia el ADP del banco por `X-Destination-Bank` |
| QA / Tester           | Valida el enrutamiento, los escenarios de error y la respuesta normalizada                                   |

---

## Historia de Usuario

**Como** asesor bancario autenticado en el canal Oficinas,  
**quiero** consultar el detalle completo de una tarjeta de crédito del cliente en la entidad seleccionada,  
**para** obtener cupo disponible, saldo, fecha de corte, pago mínimo y movimientos que me permitan orientar al cliente con precisión.

---

## Contexto de Negocio

Este endpoint se implementa dentro del microservicio `ofic-consultas-orq`. El flujo típico es: el asesor realiza la consulta general (HU-101) y obtiene el inventario de tarjetas; desde esa vista selecciona una TC para ver el detalle completo.

La TC es un producto de **sensibilidad alta** (según SFA-007). El número de tarjeta se retorna siempre enmascarado. La validación de identidad es parametrizable al igual que en las demás consultas P1.

> **Nota BAVV:** Se debe confirmar con AVV si `getBalanceByProduct` (código CCA) retorna el nivel de detalle requerido o si existe otro servicio específico para TC detallada.

**Flujo de referencia:**

```text
Cliente/Frontend
      |
      | Headers: X-Origin-Bank, X-Destination-Bank
      | Body: { operacion: "...", obj_operacion: {...} }
      v
     ORQ (ofic-consultas-orq)
      |
      | operacion
      | X-Origin-Bank
      | X-Destination-Bank
      | obj_operacion
      v
     ADP (ofic-consultas-adp-[bbog|bavv|bocc|bpop])
      |
      | Transforma obj_operacion al contrato del banco
      v
Servicio/API del banco
      |
      | El banco realiza las validaciones funcionales
      v
     ADP → transforma respuesta → ORQ → respuesta al cliente
```

---

## Criterios de Aceptación

- **CA-01:** El endpoint recibe los headers requeridos y un body con `obj_operacion` conteniendo los datos funcionales (tipoDocumento, numeroDocumento, acctId, acctType).
- **CA-02:** El ORQ valida que el header `X-Destination-Bank` esté presente y sea un código de banco reconocido (`BBOG`, `BOCC`, `BPOP`, `BAVV`). Si está ausente o no es reconocido, retorna `400`.
- **CA-03:** El ORQ no realiza ninguna validación funcional sobre los campos de `obj_operacion`. La validación de los datos es responsabilidad del servicio del banco destino.
- **CA-04:** El orquestador evalúa la primera condición: consulta la parametrización de la transacción para determinar si SFA-008 requiere validación de identidad. Si no la requiere, continúa directamente.
- **CA-05:** Si la parametrización exige validación, el orquestador evalúa la segunda condición: verifica si el cliente ya fue validado durante la interacción actual (por esta u otra transacción). Si existe validación previa, la reutiliza y continúa. Si no existe validación previa y el resultado de la nueva validación no es exitoso, retorna `403` con código `IDENTIDAD_NO_VALIDADA`.
- **CA-06:** La validación de identidad se gestiona por interacción con el cliente, no por transacción.
- **CA-07:** El orquestador enruta al ADP correspondiente según el header `X-Destination-Bank` (`BBOG` → `ofic-consultas-adp-bbog`; `BAVV` → `ofic-consultas-adp-bavv`; `BOCC` → `ofic-consultas-adp-bocc`; `BPOP` → `ofic-consultas-adp-bpop`).
- **CA-08:** El número de tarjeta se retorna siempre enmascarado en la respuesta normalizada.
- **CA-09:** El orquestador retorna la respuesta normalizada del ADP sin modificar los datos de negocio.
- **CA-10:** Registra la trazabilidad: usuario, rol, fecha, hora, oficina, banco, cliente y referencia de tarjeta.
- **CA-11:** Si el ADP retorna respuesta parcial con `bloquesFaltantes`, el orquestador la propaga sin convertirla en error.
- **CA-12:** El `user_id` se extrae siempre del JWT — nunca del body.
- **CA-13:** Prerequisito: debe existir una consulta general vigente (SFA-007 / HU-101) y una tarjeta de crédito seleccionada.
- **CA-14:** Si el valor del campo `operacion` no corresponde a ningún valor de `OperacionEnum`, el ORQ lanza una excepción en el boundary de deserialización y retorna `400 Bad Request` sin procesar la petición. Este es el primer nivel de validación — antes de cualquier enrutamiento o validación de banco.

---

## Inputs

### Request body

```json
{
  "operacion": "CONSULTA_DETALLADA_TC",
  "obj_operacion": {
    "tipoDocumento": "CC",
    "numeroDocumento": "12345678",
    "acctId": "4575001234567890",
    "acctType": "CCA"
  }
}
```

| Campo          | Tipo   | Descripción                                                        | Obligatorio |
|----------------|--------|--------------------------------------------------------------------|-------------|
| `operacion`    | `OperacionEnum` | Identificador de la operación a ejecutar. Recibido como String en el boundary HTTP; convertido a `OperacionEnum` en el dominio. Ver definición completa en **HU-101-ORQ** | SI          |
| `obj_operacion`| Object | Payload de la consulta — campos funcionales de la operación        | SI          |

#### Campos de `obj_operacion` (documentación de referencia)

| Campo             | Tipo   | Descripción                                                                          |
|-------------------|--------|--------------------------------------------------------------------------------------|
| `tipoDocumento`   | String | Tipo de documento del cliente                                                        |
| `numeroDocumento` | String | Número de documento del cliente                                                      |
| `acctId`          | String | Número de la tarjeta de crédito — se obtiene del `AcctId` retornado en la respuesta T1 |
| `acctType`        | String | Tipo de cuenta — siempre `CCA` para tarjetas de crédito                              |

> **Nota:** El ORQ no valida los campos dentro de `obj_operacion`. Los campos `acctId` y `acctType` son pasados directamente al ADP sin transformación. El `acctId` es el número de tarjeta obtenido de la respuesta T1.

### Headers

| Header | Descripción | Obligatorio |
|--------|-------------|-------------|
| `Authorization` | Bearer JWT del asesor autenticado | SI |
| `X-Trace-Id` | ID de traza para correlación de logs | SI |
| `X-Origin-Bank` | Código del banco de origen de la operación (`BBOG`, `BOCC`, `BPOP`, `BAVV`) | SI |
| `X-Destination-Bank` | Código del banco destino — determina el ADP a invocar (`BBOG`, `BOCC`, `BPOP`, `BAVV`) | SI |

### Gestión de headers

#### Nivel 1 — Headers recibidos por el ORQ

Los headers de entrada están documentados en la sección **Headers** de esta HU (tabla anterior).

#### Nivel 2 — Headers propagados ORQ → ADP

El ORQ propaga al ADP **todos** los headers de contexto recibidos, sin modificar ni eliminar ninguno. El ADP es responsable de seleccionar y construir los headers que el servicio bancario requiere para cada combinación `operacion + X-Destination-Bank`.

| Header propagado | Propagado al ADP |
|------------------|-----------------|
| `Authorization` | SI |
| `X-Trace-Id` | SI |
| `X-Origin-Bank` | SI |
| `X-Destination-Bank` | SI |

> **Principio arquitectónico:** El ORQ actúa como propagador del contexto. NO determina qué headers requiere el banco destino ni los transforma. El ADP aplica la selección y transformación de headers según el contrato técnico del servicio bancario.

#### Nivel 3 — Headers ADP → Banco

Responsabilidad del ADP, no del ORQ. Ver HUs hijas (ADP) para el detalle de headers enviados al banco por cada combinación `operacion + banco destino + servicio`.

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
| `400`       | X-Destination-Bank ausente/inválido   | Header ausente o código de banco no reconocido |
| `403`       | Identidad no validada                 | Parametrización exige validación no completada |
| `404`       | Tarjeta no encontrada                 | El banco no encontró la referencia de tarjeta  |
| `502`       | Error en el servicio del banco        | El ADP retornó error                           |
| `504`       | Timeout del servicio del banco        | El ADP excedió tiempo de respuesta             |

---

## Reglas de Negocio

1. **RN-01:** El `user_id` se extrae siempre del JWT — nunca del body.
3. **RN-03:** La validación de identidad es parametrizable y se gestiona por interacción, no por transacción. Dos condiciones: (1) la configuración de SFA-008 debe exigir validación y (2) el cliente no debe haber sido validado durante la interacción actual por ninguna transacción. Solo si ambas condiciones se cumplen y la nueva validación falla, la consulta no se envía al banco.
4. **RN-04:** El orquestador no transforma datos de negocio — solo normaliza la envoltura de respuesta.
5. **RN-05:** Trazabilidad obligatoria: usuario, rol, fecha, hora, oficina, banco, cliente y referencia de tarjeta.
6. **RN-06:** Credenciales siempre en variables de ambiente.
7. **RN-07:** El enrutamiento al ADP se resuelve **exclusivamente** por el header `X-Destination-Bank`.
8. **RN-08:** El ORQ **no realiza validaciones funcionales** sobre los campos de `obj_operacion`. La validación corresponde al servicio del banco destino.
9. **RN-09:** El consumo del ORQ hacia los ADPs implementa **Circuit Breaker** (Resilience4j).
10. **RN-10: Propagación de headers al ADP** — El ORQ propaga al ADP todos los headers de contexto recibidos (`X-Origin-Bank`, `X-Destination-Bank`, `X-Trace-Id`, `Authorization`) sin transformación. No elimina headers que el ADP pueda necesitar para construir el consumo bancario.
11. **RN-11: Tipado de `operacion`** — El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en este microservicio con los valores canónicos de **HU-101-ORQ** (_Enum de Operaciones_). El ORQ convierte el String HTTP a `OperacionEnum` en el boundary de entrada; si el valor no es válido, retorna `400` sin enrutar. Nunca comparar String literals contra valores de operación en código de producción.

---

## Caminos Alternativos y Excepciones

| ID      | Condición                                              | Comportamiento esperado                                                   |
|---------|--------------------------------------------------------|---------------------------------------------------------------------------|
| ALT-00  | Valor de `operacion` no reconocido por `OperacionEnum` | Excepción en deserialización → retorna `400 Bad Request` con descripción del valor recibido. Ocurre antes de cualquier enrutamiento. |
| ALT-01  | `X-Destination-Bank` ausente o no registrado en catálogo | Retorna `400` con mensaje de banco no reconocido                        |
| ALT-02  | Identidad no validada (parametrización lo exige)       | Retorna `403` con código `IDENTIDAD_NO_VALIDADA`                          |
| ALT-03  | Tarjeta no encontrada en el banco                     | Propaga el `404` del ADP al canal                                         |
| ALT-04  | Respuesta parcial del ADP (bloquesFaltantes)          | Propaga la respuesta parcial — no convierte en error                      |
| EXC-01  | Banco no disponible (ADP retorna 503)                 | Propaga `503` al canal                                                    |
| EXC-02  | Timeout en el ADP                                     | Propaga `504` al canal                                                    |
| EXC-03  | Error interno del orquestador                         | Retorna `500` y registra en Elastic                                       |

---

## Tecnología a Usar

| Componente        | Tecnología          | Versión  | Nota                                               |
|-------------------|---------------------|----------|----------------------------------------------------|
| Lenguaje          | Java                | 21       |                                                    |
| Framework         | Spring Boot         | 3.2.6    |                                                    |
| Circuit Breaker   | Resilience4j        | —        | Implementado en todas las llamadas a ADPs          |
| Despliegue        | Docker / AKS        | —        | Mismo pod que HU-101 y HU-102 (`ofic-consultas-orq`) |
| Logs              | Elastic             | —        |                                                    |


---

## Endpoints

| Método  | Ruta                                   | Propósito                                     |
|---------|----------------------------------------|-----------------------------------------------|
| `POST`  | `/api/v1/everst/ofi/orq/tc-detallada`  | Consultar detalle de una tarjeta de crédito   |

---

## Modelo de Datos

El orquestador no persiste datos. Registra trazabilidad en el log de auditoría.

| Entidad (log)          | Campos                                                                                      |
|------------------------|---------------------------------------------------------------------------------------------|
| `TrazabilidadConsulta` | usuarioId, rol, oficina, banco, tipoDocumento, numeroDocumento, acctId, acctType, fechaHora, resultado |

---

## Dependencias

| HU / Componente      | Relación     | Descripción                                                                |
|----------------------|--------------|----------------------------------------------------------------------------|
| HU-101-ORQ           | Relacionada  | Consulta general que provee la `referenciaTarjeta` al asesor              |
| HU-103-ADP-BBOG      | Hijo         | Adaptador `ofic-consultas-adp-bbog` — BdB para TC detallada               |
| HU-103-ADP-BAVV      | Hijo         | Adaptador `ofic-consultas-adp-bavv` — AVV para TC detallada               |
| HU-103-ADP-BOCC      | Hijo         | Adaptador `ofic-consultas-adp-bocc` — OCC para TC detallada               |
| HU-103-ADP-BPOP      | Hijo         | Adaptador `ofic-consultas-adp-bpop` — BPO para TC detallada               |
| HU-T02               | Prerrequisito condicional | Validación de huella — se invoca si parametrización lo exige  |

---

## Seguridad

- **Autenticación:** Bearer Token JWT obligatorio.
- **Validación de identidad:** Parametrizable.
- **Credenciales:** En variables de ambiente.
- **Masking en logs:** Los números de tarjeta NUNCA se registran en texto plano en logs. En Elastic, los números de tarjeta deben aparecer ofuscados (últimos 4 dígitos visibles: `*******5678`). El payload funcional que viaja entre ORQ, ADP y banco circula con el valor completo.

---

## Escenarios Gherkin

```gherkin
Feature: Orquestador — Consulta Detallada de Tarjeta de Crédito
  Como asesor autenticado
  Quiero consultar el detalle de una tarjeta de crédito
  Para orientar al cliente con información completa de su TC

  Background:
    Given el asesor está autenticado con JWT válido
    And el microservicio ofic-consultas-orq está disponible

  Scenario: Consulta exitosa — número enmascarado en respuesta
    Given la parametrización no requiere validación de identidad
    And el header X-Destination-Bank es "BBOG" y el banco está disponible
    When el asesor envía la solicitud con obj_operacion conteniendo documento y referenciaTarjeta
    Then el orquestador enruta al ADP ofic-consultas-adp-bbog
    And retorna el detalle con StatusCode 200
    And el número de tarjeta en la respuesta está enmascarado
    And registra la trazabilidad

  Scenario: Consulta exitosa — validación reutilizada de la interacción actual
    Given la parametrización requiere validación de identidad
    And el cliente ya fue validado durante la interacción actual por otra transacción
    When el asesor selecciona la tarjeta a consultar
    Then Everest reutiliza la validación existente y habilita el flujo
    And el asesor envía la solicitud al orquestador
    And el orquestador enruta al ADP y retorna el detalle

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
    Given el header X-Destination-Bank es "BOCC" y el banco está disponible
    When el asesor envía una referenciaTarjeta que no existe en OCC
    Then el orquestador retorna 404

  Scenario: X-Destination-Bank ausente
    Given el request no incluye el header "X-Destination-Bank"
    When el asesor envía la solicitud
    Then el orquestador retorna 400 con mensaje descriptivo

  Scenario: Enrutar solicitud al ADP de Banco Popular
    Given el header X-Destination-Bank es "BPOP"
    When el asesor envía la solicitud
    Then el orquestador enruta al ADP ofic-consultas-adp-bpop
    And retorna la respuesta del ADP sin modificarla
```

---

## Notas Técnicas

- El campo `acctId` corresponde al número de tarjeta obtenido de la respuesta T1 (`AcctId` en el payload de cada banco). El campo `acctType` es siempre `CCA` para tarjetas de crédito.
- El enmascaramiento del número de tarjeta debe aplicarse en el ADP antes de retornar al orquestador.
- El **Circuit Breaker** (Resilience4j) debe configurarse en cada llamada del ORQ hacia los ADPs.

---

## Definition of Ready


- [ ] Definición de `referenciaTarjeta` acordada con los 4 bancos (¿número enmascarado o ID interno?)
- [ ] Modelo de respuesta normalizado de TC definido y acordado
- [ ] Mecanismo de parametrización de identidad validado (mismo que HU-101)
- [ ] Campos de trazabilidad definidos
- [ ] Al menos un ADP listo para prueba
- [ ] HU-101-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación de story points asignada
- [ ] Aprobada por líder técnico y product owner

---

## Definition of Done

- [ ] Endpoint `POST /api/v1/everst/ofi/orq/tc-detallada` implementado en `ofic-consultas-orq`
- [ ] Validación de headers `X-Origin-Bank` y `X-Destination-Bank` implementada
- [ ] Evaluación de parametrización de identidad implementada
- [ ] Enrutamiento por `X-Destination-Bank` implementado
- [ ] Número de tarjeta enmascarado en respuesta — validado en pruebas
- [ ] Trazabilidad registrada por cada consulta
- [ ] Circuit Breaker (Resilience4j) configurado en llamadas a ADPs
- [ ] Pruebas unitarias (cobertura ≥ 80%)
- [ ] Prueba de integración con al menos un ADP en PT
- [ ] Aprobado por QA
- [ ] Aprobado por product owner
