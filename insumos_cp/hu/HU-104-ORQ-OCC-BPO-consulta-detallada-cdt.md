# HU-104-ORQ: Orquestador — Consulta Detallada de CDT

## Metadatos

| Campo            | Valor                                                        |
|------------------|--------------------------------------------------------------|
| ID               | HU-104-ORQ                                                   |
| ID Servicio      | SFA-008                                                      |
| Épica            | Épica 1 — Consultas P1                                       |
| Componente       | Orquestador — Consulta Detallada de CDT                      |
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

| Rol / Audiencia       | Cómo interactúa                                                                                             |
|-----------------------|-------------------------------------------------------------------------------------------------------------|
| Asesor bancario       | Desde la pantalla de detalle de CDT (luego de la consulta general), solicita la información completa del CDT |
| Desarrollador Backend | Implementa el endpoint en `ofic-consultas-orq` y la lógica de enrutamiento por `X-Destination-Bank`         |
| QA / Tester           | Valida enrutamiento, escenarios de error y respuesta normalizada                                            |

---

## Historia de Usuario

**Como** asesor bancario autenticado en el canal Oficinas,  
**quiero** consultar el detalle completo de un CDT del cliente en la entidad seleccionada,  
**para** obtener monto, tasa, fecha de vencimiento y condiciones del certificado para orientar al cliente.

---

## Contexto de Negocio

Nuevo endpoint dentro de `ofic-consultas-orq`. El flujo típico: el asesor realiza la consulta general (HU-101) y obtiene el inventario de CDTs; desde esa vista selecciona un CDT para ver su detalle.

La consulta es no monetaria y de solo lectura. La validación de identidad es parametrizable.

> **Nota BAVV:** Se debe confirmar si `getBalanceByProduct` (código CDA) cubre el detalle de CDT en AVV.

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
- **CA-07:** Enruta al ADP según el header `X-Destination-Bank` (`BBOG` → `ofic-consultas-adp-bbog`; `BAVV` → `ofic-consultas-adp-bavv`; `BOCC` → `ofic-consultas-adp-bocc`; `BPOP` → `ofic-consultas-adp-bpop`).
- **CA-09:** Retorna la respuesta normalizada del ADP sin modificar datos de negocio.
- **CA-10:** Registra trazabilidad: usuario, rol, fecha, hora, oficina, banco, cliente y número de producto.
- **CA-11:** Si el ADP retorna respuesta parcial con `bloquesFaltantes`, la propaga sin convertir en error.
- **CA-12:** El `user_id` se extrae siempre del JWT — nunca del body.
- **CA-13:** Prerequisito: debe existir una consulta general vigente (SFA-007 / HU-101) y un CDT seleccionado.
- **CA-14:** Si el valor del campo `operacion` no corresponde a ningún valor de `OperacionEnum`, el ORQ lanza una excepción en el boundary de deserialización y retorna `400 Bad Request` sin procesar la petición. Este es el primer nivel de validación — antes de cualquier enrutamiento o validación de banco.

---

## Inputs

### Request body

```json
{
  "operacion": "CONSULTA_DETALLADA_CDT",
  "obj_operacion": {
    "tipoDocumento": "CC",
    "numeroDocumento": "12345678",
    "acctId": "CDT-123456",
    "acctType": "CDA"
  }
}
```

| Campo          | Tipo   | Descripción                                                        | Obligatorio |
|----------------|--------|--------------------------------------------------------------------|-------------|
| `operacion`    | `OperacionEnum` | Identificador de la operación a ejecutar. Recibido como String en el boundary HTTP; convertido a `OperacionEnum` en el dominio. Ver definición completa en **HU-101-ORQ** | SI          |
| `obj_operacion`| Object | Payload de la consulta — campos funcionales de la operación        | SI          |

#### Campos de `obj_operacion` (documentación de referencia)

| Campo             | Tipo   | Descripción                                                                              |
|-------------------|--------|------------------------------------------------------------------------------------------|
| `tipoDocumento`   | String | Tipo de documento del cliente                                                            |
| `numeroDocumento` | String | Número de documento del cliente                                                          |
| `acctId`          | String | Número o referencia del CDT — se obtiene del `AcctId` retornado en la respuesta T1      |
| `acctType`        | String | Tipo de cuenta CDT: `CDA` (Banco de Occidente, BdB, AVV) o `CDT` (Banco Popular) |

> **Nota:** El ORQ no valida los campos dentro de `obj_operacion`. Los campos `acctId` y `acctType` son pasados directamente al ADP sin transformación.

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
| `400`       | X-Destination-Bank ausente/inválido   | Header ausente o código de banco no reconocido|
| `403`       | Identidad no validada                 | Parametrización exige validación no completada|
| `404`       | CDT no encontrado                     | El banco no encontró el producto              |
| `502`       | Error en el servicio del banco        | El ADP retornó error                          |
| `504`       | Timeout del servicio del banco        | El ADP excedió tiempo de respuesta            |

---

## Reglas de Negocio

1. **RN-01:** `user_id` del JWT — nunca del body.
2. **RN-02:** Operación de solo lectura.
3. **RN-03:** La validación de identidad es parametrizable y se gestiona por interacción, no por transacción. Dos condiciones: (1) la configuración de SFA-008 debe exigir validación y (2) el cliente no debe haber sido validado durante la interacción actual por ninguna transacción. Solo si ambas condiciones se cumplen y la nueva validación falla, la consulta no se envía al banco.
4. **RN-04:** No transforma datos de negocio del ADP.
5. **RN-05:** Trazabilidad obligatoria.
6. **RN-06:** Credenciales en variables de ambiente.
7. **RN-07:** El enrutamiento al ADP se resuelve **exclusivamente** por el header `X-Destination-Bank`.
8. **RN-08:** El ORQ **no realiza validaciones funcionales** sobre los campos de `obj_operacion`. La validación corresponde al servicio del banco destino.
10. **RN-10:** El consumo del ORQ hacia los ADPs implementa **Circuit Breaker** (Resilience4j).
11. **RN-11: Propagación de headers al ADP** — El ORQ propaga al ADP todos los headers de contexto recibidos (`X-Origin-Bank`, `X-Destination-Bank`, `X-Trace-Id`, `Authorization`) sin transformación. No elimina headers que el ADP pueda necesitar para construir el consumo bancario.
12. **RN-12: Tipado de `operacion`** — El campo `operacion` usa el tipo `OperacionEnum`, definido localmente en este microservicio con los valores canónicos de **HU-101-ORQ** (_Enum de Operaciones_). El ORQ convierte el String HTTP a `OperacionEnum` en el boundary de entrada; si el valor no es válido, retorna `400` sin enrutar. Nunca comparar String literals contra valores de operación en código de producción.

---

## Caminos Alternativos y Excepciones

| ID      | Condición                                           | Comportamiento esperado                                               |
|---------|-----------------------------------------------------|-----------------------------------------------------------------------|
| ALT-00  | Valor de `operacion` no reconocido por `OperacionEnum` | Excepción en deserialización → retorna `400 Bad Request` con descripción del valor recibido. Ocurre antes de cualquier enrutamiento. |
| ALT-01  | `X-Destination-Bank` ausente o no registrado        | Retorna `400` con mensaje de banco no reconocido                      |
| ALT-02  | Identidad no validada                               | Retorna `403` con código `IDENTIDAD_NO_VALIDADA`                      |
| ALT-04  | CDT no encontrado                                   | Propaga `404` del ADP                                                 |
| ALT-05  | Respuesta parcial (bloquesFaltantes)                | Propaga sin convertir en error                                        |
| EXC-01  | Banco no disponible (503 del ADP)                   | Propaga `503`                                                         |
| EXC-02  | Timeout                                             | Propaga `504`                                                         |
| EXC-03  | Error interno orquestador                           | Retorna `500` y registra en Elastic                                   |

---

## Tecnología a Usar

| Componente     | Tecnología        | Versión | Nota                                                   |
|----------------|-------------------|---------|--------------------------------------------------------|
| Lenguaje       | Java              | 21      |                                                        |
| Framework      | Spring Boot       | 3.2.6   |                                                        |
| Circuit Breaker| Resilience4j      | —       | Implementado en todas las llamadas a ADPs              |
| Despliegue     | Docker / AKS      | —       | Mismo pod que HU-101/102/103 (`ofic-consultas-orq`)    |
| Logs           | Elastic           | —       |                                                        |


---

## Endpoints

| Método | Ruta                                  | Propósito                          |
|--------|---------------------------------------|------------------------------------|
| `POST` | `/api/v1/everst/ofi/orq/cdt-detallado`| Consultar detalle de un CDT        |

---

## Modelo de Datos

| Entidad (log)          | Campos                                                                                    |
|------------------------|-------------------------------------------------------------------------------------------|
| `TrazabilidadConsulta` | usuarioId, rol, oficina, banco, tipoDocumento, numeroDocumento, acctId, acctType, fechaHora, resultado |

---

## Dependencias

| HU / Componente      | Relación     | Descripción                                                              |
|----------------------|--------------|--------------------------------------------------------------------------|
| HU-101-ORQ           | Relacionada  | Consulta general que provee el `numeroProducto` al asesor                |
| HU-104-ADP-BBOG      | Hijo         | Adaptador `ofic-consultas-adp-bbog` — BdB para CDT detallado            |
| HU-104-ADP-BAVV      | Hijo         | Adaptador `ofic-consultas-adp-bavv` — AVV para CDT detallado            |
| HU-104-ADP-BOCC      | Hijo         | Adaptador `ofic-consultas-adp-bocc` — OCC para CDT detallado            |
| HU-102-ADP-BPOP      | Hijo         | Adaptador `ofic-consultas-adp-bpop` — BPO para CDT detallado |

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
    And el microservicio ofic-consultas-orq está disponible

  Scenario: Consulta exitosa sin validación de identidad
    Given la parametrización no requiere validación de identidad
    And el header X-Destination-Bank es "BBOG" y el banco está disponible
    When el asesor envía la solicitud con obj_operacion conteniendo documento y numeroProducto
    Then el orquestador enruta al ADP ofic-consultas-adp-bbog
    And retorna el detalle con StatusCode 200
    And registra la trazabilidad

  Scenario: Consulta exitosa — validación reutilizada de la interacción actual
    Given la parametrización requiere validación de identidad
    And el cliente ya fue validado durante la interacción actual por otra transacción
    When el asesor selecciona el CDT a consultar
    Then Everest reutiliza la validación existente y habilita el flujo
    And el asesor envía la solicitud al orquestador
    And el orquestador enruta al ADP correspondiente y retorna el detalle

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

  Scenario: CDT no encontrado
    Given el header X-Destination-Bank es "BOCC" y el banco está disponible
    When el asesor envía un numeroProducto que no existe
    Then el orquestador retorna 404

  Scenario: X-Destination-Bank ausente
    Given el request no incluye el header "X-Destination-Bank"
    When el asesor envía la solicitud
    Then retorna 400 con mensaje descriptivo
```

---

## Notas Técnicas

- Este endpoint se implementa en `ofic-consultas-orq`. No se requiere nuevo microservicio.
- BPOP soporta CDT vía `getBalanceByProduct` con `acctType=CDT`. Implementado en `HU-102-ADP-BPOP`.
- El **Circuit Breaker** (Resilience4j) debe configurarse en cada llamada del ORQ hacia los ADPs.

---

## Definition of Ready


- [ ] Modelo de respuesta normalizado de CDT definido y acordado
- [ ] Mecanismo de parametrización de identidad validado
- [ ] Campos de trazabilidad definidos
- [ ] Al menos un ADP listo para prueba (BBOG, BOCC o BPOP)
- [ ] HU-101-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Endpoint `POST /api/v1/everst/ofi/orq/cdt-detallado` implementado
- [ ] Validación de headers `X-Origin-Bank` y `X-Destination-Bank` implementada
- [ ] Evaluación de parametrización de identidad implementada
- [ ] Enrutamiento por `X-Destination-Bank` implementado (BBOG, BAVV, BOCC, BPOP)
- [ ] Trazabilidad implementada
- [ ] Circuit Breaker (Resilience4j) configurado en llamadas a ADPs
- [ ] Pruebas unitarias (≥ 80%)
- [ ] Prueba de integración con al menos un ADP en PT
- [ ] Aprobado por QA y product owner
