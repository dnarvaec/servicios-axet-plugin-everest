# HU-101-ADP-BDB: Adaptador Banco de Bogotá — Consulta General de Cliente y Productos

## Metadatos

| Campo          | Valor                                                  |
|----------------|--------------------------------------------------------|
| ID             | HU-101-ADP-BDB                                         |
| Épica          | Épica 1 — Consultas P1                                 |
| Componente     | Adaptador BdB — Consulta General                       |
| Sprint         | Por definir                                            |
| Prioridad      | Alta (P1)                                              |
| Estimación     | Por estimar                                            |
| Estado         | Pendiente                                              |
| HU Padre       | HU-101 (Orquestador)                                   |
| Autor          | Por definir                                            |
| Fecha          | 2026-08-19                                             |

---

## Audiencias

| Rol / Audiencia       | Cómo interactúa                                                                                      |
|-----------------------|------------------------------------------------------------------------------------------------------|
| Desarrollador Backend | Implementa el adaptador: orquesta las llamadas a los servicios de BdB y transforma la respuesta      |
| QA / Tester           | Valida que el adaptador llame correctamente a los servicios de BdB y mapee los campos esperados      |
| Integrador BdB        | Provee acceso y soporte técnico a los endpoints REST / SOAP del banco                                |

---

## Historia de Usuario

**Como** adaptador del canal Oficinas para Banco de Bogotá,  
**quiero** recibir una solicitud de consulta general del orquestador,  
**para** invocar los servicios correspondientes de BdB, consolidar los datos del cliente y sus productos, y retornar la respuesta normalizada.

---

## Contexto de Negocio

BdB expone dos canales para consulta de productos: SOAP (Bus interno, retorna productos + datos del cliente en una sola llamada) y REST (`customer-management-v3`, retorna solo productos sin datos del cliente). El adaptador debe orquestar las llamadas necesarias para completar el resumen esperado por el orquestador: **datos del cliente** + **resumen de productos**.

> **Decisión de implementación pendiente:** ¿Se usa el canal SOAP (una llamada, datos completos) o el canal REST (requiere llamada adicional para datos del cliente)? Esta decisión afecta la complejidad y el SLA del adaptador.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe el payload de `obj_operacion` proveniente del orquestador.
- **CA-02:** El adaptador invoca el/los servicio(s) de BdB necesarios para obtener datos del cliente y el resumen de productos.
- **CA-03:** Si se usa el canal SOAP (`getCustInfoUnivAccessInq`), el adaptador obtiene en una sola llamada: datos del cliente y listado de productos.
- **CA-04:** Si se usa el canal REST (`customer-management-v3`), el adaptador realiza una llamada para productos y una llamada adicional para datos del cliente, y consolida ambas respuestas.
- **CA-05:** El adaptador transforma la respuesta de BdB al modelo de datos normalizado del canal Oficinas (estructura pendiente de definición).
- **CA-06:** Si BdB retorna un error, el adaptador lo mapea a la estructura de error estándar del canal y lo propaga al orquestador.
- **CA-07:** El adaptador no realiza ninguna lógica de negocio adicional — solo invoca servicios, consolida y transforma la respuesta.

---

## Inputs

### Recibidos del Orquestador

El adaptador recibe el contenido de `obj_operacion`. Estructura mínima esperada:

```json
{
  "tipoDocumento": "CC",
  "numeroDocumento": "12345678"
}
```

| Campo              | Tipo   | Descripción                        | Obligatorio | Ejemplo    |
|--------------------|--------|------------------------------------|-------------|------------|
| `tipoDocumento`    | String | Tipo de documento del cliente      | SI          | `CC`, `CE`, `NIT` |
| `numeroDocumento`  | String | Número de documento del cliente    | SI          | `12345678` |

> **Nota:** La estructura exacta de `obj_operacion` está **pendiente de definición** con el equipo. Los campos aquí son los mínimos inferidos del servicio de BdB.

---

## Servicios de BdB Invocados

### Opción A — Canal SOAP (Bus)

| # | Servicio / Operación     | Tipo | Endpoint (referencial)     | Retorna                                   |
|---|--------------------------|------|----------------------------|-------------------------------------------|
| 1 | `getCustInfoUnivAccessInq` | SOAP | Bus interno BdB (DP)       | Datos del cliente + listado de productos  |

> El endpoint exacto del Bus está **pendiente de confirmación** con BdB (no documentado en los archivos actuales).

### Opción B — Canal REST (AWS)

| # | Servicio / API                    | Tipo | Endpoint QA                                          | Endpoint PROD                                         | Retorna           |
|---|-----------------------------------|------|------------------------------------------------------|-------------------------------------------------------|-------------------|
| 1 | `customer-management-v3` / `GET /V3/enterprise/customer/product` | REST | `https://api-clients.labdigitalbdbtvsqa.com/customer-management-v3-mngr` | `https://api-clients.labdigitalbdbtvs.com/customer-management-v3-mngr` | Listado de productos (sin datos del cliente) |
| 2 | Servicio de datos del cliente (a definir) | REST / SOAP | Por definir | Por definir | Nombre, documento, segmento |

#### Headers requeridos para la API REST de BdB

> Los headers requeridos son variables y dependen de lo que solicite BdB. Se definirán en coordinación con el equipo de integración del banco.

---

## Outputs

### Datos a consolidar para la respuesta normalizada

El adaptador debe construir, a partir de la respuesta de BdB, el siguiente conjunto de datos:

**Datos del cliente:**
- Nombre completo
- Tipo y número de documento
- Segmento

**Cuentas de ahorro y corriente:**
- Tipo de cuenta
- Número de cuenta
- Saldo
- Sobregiro disponible (para cuentas corrientes)

**CDT:**
- Número de producto

**Carteras / Créditos:**
- Tipo de cartera
- Número de obligación
- Saldo a pagar

**Tarjetas de crédito:**
- Número enmascarado
- Estado
- Franquicia
- Cupo disponible

> El modelo de datos normalizado de salida está **pendiente de definición formal**. Los campos listados son los identificados en el documento de flujos .

### Estructura de respuesta

Ver estructura provisional en HU-101 (Orquestador). El adaptador llena los campos de `Status` y el objeto de datos con la información consolidada de BdB.

### Mapeo de errores BdB → estructura estándar

| Error BdB                          | Código HTTP a retornar | StatusDesc                              |
|------------------------------------|------------------------|-----------------------------------------|
| Cliente no encontrado              | `206`                  | "Cliente no encontrado en BdB"          |
| Sin productos                      | `206`                  | "El cliente no tiene productos en BdB"  |
| Error de autenticación con BdB     | `502`                  | "Error de autenticación con banco"      |
| Timeout del servicio BdB           | `504`                  | "Timeout del servicio BdB"              |
| Error interno del servicio BdB     | `502`                  | "Error en el servicio del banco"        |

---

## Reglas de Negocio

1. **RN-01:** El adaptador invoca los servicios de BdB usando las credenciales configuradas en variables de ambiente — nunca hardcodeadas.
2. **RN-02:** Si se usa la Opción B (REST), la consolidación de datos del cliente y productos es responsabilidad del adaptador; el orquestador recibe un único objeto ya consolidado.
3. **RN-03:** El adaptador no filtra ni modifica los datos retornados por BdB — solo los mapea al modelo normalizado.
4. **RN-04:** Los números de tarjeta de crédito se retornan **enmascarados** en la respuesta normalizada.
5. **RN-05:** Ante una respuesta parcial (cuando un bloque llega con error pero el otro es exitoso), el adaptador retorna la información disponible con el indicador de bloque faltante — no retorna error total.

---

## Caminos Alternativos y Excepciones

| ID      | Condición                                                | Comportamiento esperado                                          |
|---------|----------------------------------------------------------|------------------------------------------------------------------|
| ALT-01  | BdB retorna lista de productos vacía                    | Retorna respuesta con `data` vacío y StatusCode de negocio       |
| ALT-02  | Cliente no existe en BdB                                | Retorna código de negocio correspondiente de BdB                 |
| ALT-03  | Respuesta parcial — BdB devuelve datos del cliente pero falla en productos (o viceversa) | Retorna lo obtenido con un campo `bloquesFaltantes` indicando qué no pudo consultarse — **no retorna error total** |
| EXC-01  | Timeout en llamada REST/SOAP a BdB                      | Retorna `504` al orquestador                                     |
| EXC-02  | Error de certificado / TLS con el Bus                   | Retorna `502` y registra en Elastic                              |
| EXC-03  | API Key REST inválida o expirada                        | Retorna `502` y alerta en Elastic                                |

---

## Tecnología a Usar

| Componente        | Tecnología          | Versión  | Nota                                   |
|-------------------|---------------------|----------|----------------------------------------|
| Lenguaje          | Java                | 21       |                                        |
| Framework         | Spring Boot         | 3.2.6    |                                        |
| Cliente REST      | WebClient / RestTemplate | —   | Para el canal REST de BdB              |
| Cliente SOAP      | JAX-WS / CXF        | —        | Para el canal SOAP del Bus (si aplica) |
| Logs              | Elastic             | —        |                                        |

---

## Dependencias

### HUs relacionadas

| HU         | Relación      | Descripción                                          |
|------------|---------------|------------------------------------------------------|
| HU-101     | Padre         | Orquestador que invoca este adaptador                |

### Servicios externos (BdB)

| Servicio                    | Tipo | URL QA                                               | URL PRD                                              |
|-----------------------------|------|------------------------------------------------------|------------------------------------------------------|
| `getCustInfoUnivAccessInq`  | SOAP | Por definir (Bus interno)                            | Por definir (Bus interno)                            |
| `customer-management-v3`    | REST | `https://api-clients.labdigitalbdbtvsqa.com/customer-management-v3-mngr` | `https://api-clients.labdigitalbdbtvs.com/customer-management-v3-mngr` |

---

## Seguridad

- **Credenciales hacia BdB:** API Key (REST) y/o usuario/contraseña (SOAP) almacenadas en variables de ambiente o gestor de secretos. Nunca en código.
- **TLS:** Las llamadas al Bus de BdB utilizan TLS. Certificados gestionados por el equipo de infraestructura.

---

## Preguntas Abiertas

| # | Pregunta                                                                                     | Impacto                          |
|---|----------------------------------------------------------------------------------------------|----------------------------------|
| 1 | ¿Se usa el canal SOAP o REST para la consulta de productos?                                  | Define si se necesita 1 o 2 llamadas |
| 2 | Si se usa REST, ¿qué servicio provee datos del cliente (nombre, segmento)?                  | Bloquea el diseño del adaptador  |
| 3 | ¿Cuál es el endpoint del Bus para `getCustInfoUnivAccessInq` en QA y PRD?                   | Necesario para implementar       |
| 4 | ¿El `customer-management-v3` REST ya tiene acceso habilitado para el canal Oficinas?        | Bloquea pruebas en PT            |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador BdB — Consulta General Cliente y Productos
  Como adaptador de Banco de Bogotá
  Quiero invocar los servicios de BdB para obtener cliente y productos
  Para retornar la información consolidada al orquestador

  Background:
    Given el adaptador BdB está configurado con credenciales válidas
    And los servicios de BdB están disponibles

  Scenario: Consulta exitosa con datos de cliente y productos
    Given el adaptador recibe tipoIdentificacion "CC" y numeroIdentificacion "12345678"
    When invoca el/los servicio(s) de BdB
    Then obtiene los datos del cliente (nombre, documento, segmento)
    And obtiene el listado de productos (cuentas, CDT, carteras, TC)
    And retorna la respuesta consolidada al orquestador con StatusCode 200

  Scenario: Cliente no encontrado en BdB
    Given el adaptador recibe un número de documento que no existe en BdB
    When invoca el/los servicio(s) de BdB
    Then BdB retorna respuesta de cliente no encontrado
    And el adaptador mapea la respuesta al código de error estándar

  Scenario: Timeout del servicio BdB
    Given el servicio de BdB no responde en el tiempo configurado
    When el adaptador espera la respuesta
    Then retorna un error de timeout (504) al orquestador
    And registra el evento en Elastic

  Scenario: Credenciales de API inválidas
    Given la API Key de BdB está vencida o es inválida
    When el adaptador intenta invocar el servicio REST
    Then recibe un error de autenticación
    And retorna 502 al orquestador con mensaje "Error de autenticación con banco"
```

---

## Notas Técnicas

- El canal REST (`customer-management-v3`) de BdB es el más moderno y su endpoint es público (AWS). Si se decide usar, es la opción preferida por disponibilidad y menor acoplamiento al middleware del banco.
- El canal SOAP (`getCustInfoUnivAccessInq`) tiene la ventaja de devolver datos del cliente + productos en una sola llamada, reduciendo la latencia.
- Los headers `X-RqUID`, `X-Channel`, `X-CompanyId` para el REST deben poblarse con valores del contexto de la petición (`X-Trace-Id` del orquestador puede mapearse a `X-RqUID`).

---

## Definition of Ready

> La HU puede entrar a sprint solo cuando **todos** los ítems están cumplidos.

- [ ] Decisión tomada sobre canal de comunicación (SOAP Bus vs REST AWS) y documentada
- [ ] Endpoint de QA del canal elegido confirmado y accesible desde PT
- [ ] Credenciales disponibles en PT (API Key REST o usuario/contraseña SOAP según canal)
- [ ] Si se usa REST: servicio de datos del cliente identificado (BdB no lo incluye en `customer-management-v3`)
- [ ] Conectividad de red desde pods AKS hacia BdB confirmada en PT
- [ ] Estructura de `obj_operacion` (campos del request) definida y acordada
- [ ] Modelo de respuesta normalizada definido y acordado con el orquestador
- [ ] HU-101 (Orquestador) en estado "En desarrollo" o "Completada"
- [ ] Estimación de story points asignada por el equipo
- [ ] Aprobada por líder técnico y product owner

---

## Definition of Done

- [ ] Canal de comunicación con BdB definido (SOAP o REST) y documentado
- [ ] Implementación del cliente HTTP/SOAP hacia BdB
- [ ] Mapeo de respuesta BdB → modelo normalizado implementado
- [ ] Manejo de errores y timeouts
- [ ] Pruebas unitarias del mapeo (cobertura ≥ 80%)
- [ ] Prueba de integración contra BdB en ambiente PT
- [ ] Aprobado por QA
