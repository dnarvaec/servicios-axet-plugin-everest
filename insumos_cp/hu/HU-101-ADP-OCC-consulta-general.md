# HU-101-ADP-OCC: Adaptador Banco de Occidente — Consulta General de Cliente y Productos

## Metadatos

| Campo          | Valor                                                  |
|----------------|--------------------------------------------------------|
| ID             | HU-101-ADP-OCC                                         |
| Épica          | Épica 1 — Consultas P1                                 |
| Componente     | Adaptador OCC — Consulta General                       |
| Sprint         | Por definir                                            |
| Prioridad      | Alta (P1)                                              |
| Estimación     | Por estimar                                            |
| Estado         | Pendiente                                              |
| HU Padre       | HU-101 (Orquestador)                                   |
| Autor          | Por definir                                            |
| Fecha          | 2026-08-19                                             |

---

## Audiencias

| Rol / Audiencia       | Cómo interactúa                                                                                           |
|-----------------------|-----------------------------------------------------------------------------------------------------------|
| Desarrollador Backend | Implementa el adaptador: realiza 2 llamadas SOAP a OCC (productos y cliente), consolida y transforma      |
| QA / Tester           | Valida las llamadas SOAP a OCC, el manejo del WSDL y el mapeo de campos                                  |
| Integrador OCC        | Provee WSDLs, credenciales y acceso al Datapower interno BOCC-ACE12                                      |

---

## Historia de Usuario

**Como** adaptador del canal Oficinas para Banco de Occidente,  
**quiero** recibir una solicitud de consulta general del orquestador,  
**para** invocar los servicios SOAP de OCC de consulta de productos y consulta de cliente, consolidar ambas respuestas y retornar el resultado normalizado.

---

## Contexto de Negocio

OCC expone los servicios a través de su middleware BOCC-ACE12 (conectado a MDM, SAM, Flexcube y AS400). Los servicios de consulta de productos (`ESB_ACE12_ConsultaDeProductos`) y consulta de cliente (`ConsultaClientePort`) son SOAP separados. El sub-proceso interno de productos pasa por ESB `355011 consultarSaldo` y `FCUBSAccService QueryAccBal` de Flexcube.

> **Nota de alcance:** La consulta general para OCC incluye productos pasivos, activos y TC. La cartera detallada es un servicio aparte (HU-103) y actualmente tiene un gap técnico (no existe web service; ver preguntas abiertas).

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe el payload de `obj_operacion` proveniente del orquestador.
- **CA-02:** El adaptador invoca `ESB_ACE12_ConsultaDeProductos` / `consultaDeProductos` para obtener el listado de productos del cliente.
- **CA-03:** El adaptador invoca `ConsultaClientePort` / `consultarDatosBasicos` para obtener nombre, documento y datos básicos del cliente.
- **CA-04:** El adaptador consolida ambas respuestas en un único objeto normalizado.
- **CA-05:** El adaptador transforma la respuesta consolidada al modelo de datos del canal Oficinas.
- **CA-06:** Si cualquiera de los servicios SOAP retorna un fault o error de negocio, el adaptador lo mapea a la estructura estándar y lo propaga al orquestador.
- **CA-07:** El adaptador no realiza lógica de negocio adicional — solo invoca, consolida y transforma.

---

## Inputs

### Recibidos del Orquestador

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

> La estructura exacta de `obj_operacion` está **pendiente de definición**.

---

## Servicios de OCC Invocados

### Llamada 1 — Consulta de Productos

| Tipo | Servicio / Puerto / Operación | Middleware | Endpoint |
|------|-------------------------------|------------|----------|
| SOAP | `ESB_ACE12_ConsultaDeProductos` / `ConsultaDeProductosPort` / `consultaDeProductos` | BOCC-ACE12 → MDM, SAM, Flexcube, AS400 | Por confirmar con OCC (Datapower Interno) |

Sub-proceso interno: ESB `355011 consultarSaldo` → `FCUBSAccService QueryAccBal`

> **Nota:** El WSDL de `ESB_ACE12_ConsultaDeProductos` (512 KB) está disponible pero excede los límites de lectura. El endpoint exacto debe solicitarse al equipo de OCC.

### Llamada 2 — Consulta de Datos del Cliente

| Tipo | Servicio / Puerto / Operación | Middleware | Endpoint |
|------|-------------------------------|------------|----------|
| SOAP | `ConsultaClientePort` / `consultarDatosBasicos` | BOCC-ACE12 | Por confirmar con OCC (Datapower Interno) |

---

## Outputs

### Datos a consolidar para la respuesta normalizada

**De la Llamada 1 (productos):**

| Producto    | Campos a mapear                                                    |
|-------------|---------------------------------------------------------------------|
| Cuentas     | Tipo de cuenta, número, saldo, sobregiro (corriente)               |
| CDT         | Número de producto                                                  |
| Carteras    | Tipo de cartera, número de obligación, saldo a pagar               |
| TC          | Número enmascarado, estado, franquicia, cupo disponible            |

**De la Llamada 2 (cliente):**
- Nombre completo
- Tipo y número de documento
- Segmento

### Mapeo de errores OCC → estructura estándar

| Error OCC                          | Código HTTP a retornar | StatusDesc                              |
|------------------------------------|------------------------|-----------------------------------------|
| SOAP Fault — cliente no encontrado | `206`                  | "Cliente no encontrado en OCC"          |
| SOAP Fault — sin productos         | `206`                  | "El cliente no tiene productos en OCC"  |
| Error de conectividad BOCC-ACE12   | `502`                  | "Error de conectividad con OCC"         |
| Timeout del servicio SOAP          | `504`                  | "Timeout del servicio OCC"              |
| Error interno OCC                  | `502`                  | "Error en el servicio del banco"        |

---

## Reglas de Negocio

1. **RN-01:** Las credenciales y endpoints de OCC se configuran por variable de ambiente — nunca hardcodeadas.
2. **RN-02:** Si ambas llamadas fallan, el adaptador retorna error total al orquestador.
3. **RN-03:** El adaptador consolida ambas respuestas antes de retornar al orquestador.
4. **RN-04:** Los números de tarjeta de crédito se retornan **enmascarados** en la respuesta normalizada.
5. **RN-05:** Ante una respuesta parcial (cuando un bloque llega con error pero el otro es exitoso), el adaptador retorna la información disponible con el indicador de bloque faltante — no retorna error total.

---

## Caminos Alternativos y Excepciones

| ID      | Condición                                                  | Comportamiento esperado                                        |
|---------|------------------------------------------------------------|----------------------------------------------------------------|
| ALT-01  | SOAP Fault en Llamada 1 o Llamada 2                        | Mapear fault a estructura estándar y retornar al orquestador  |
| ALT-02  | Cliente sin productos en OCC                               | Retorna código de negocio de OCC                              |
| ALT-03  | Respuesta parcial — un bloque falla pero el otro tiene datos | Retorna lo obtenido con un campo `bloquesFaltantes` indicando qué no pudo consultarse — **no retorna error total** |
| EXC-01  | Timeout en cualquiera de las dos llamadas                  | Retorna `504` al orquestador                                   |
| EXC-02  | Error de certificado TLS con Datapower BOCC-ACE12          | Retorna `502` y registra en Elastic                           |

---

## Tecnología a Usar

| Componente   | Tecnología    | Versión | Nota                                               |
|--------------|---------------|---------|----------------------------------------------------|
| Lenguaje     | Java          | 21      |                                                    |
| Framework    | Spring Boot   | 3.2.6   |                                                    |
| Cliente SOAP | JAX-WS / CXF  | —       | Para `ESB_ACE12_ConsultaDeProductos` y `ConsultaClientePort` |
| Logs         | Elastic       | —       |                                                    |

---

## Dependencias

### HUs relacionadas

| HU      | Relación | Descripción                          |
|---------|----------|--------------------------------------|
| HU-101  | Padre    | Orquestador que invoca este adaptador |

### Servicios externos (OCC)

| Servicio                          | Tipo | Endpoint QA          | Endpoint PRD         |
|-----------------------------------|------|----------------------|----------------------|
| `ESB_ACE12_ConsultaDeProductos`   | SOAP | Por definir con OCC  | Por definir con OCC  |
| `ConsultaClientePort`             | SOAP | Por definir con OCC  | Por definir con OCC  |

---

## Preguntas Abiertas

| # | Pregunta                                                                               | Impacto                               |
|---|----------------------------------------------------------------------------------------|---------------------------------------|
| 1 | ¿Cuáles son los endpoints exactos en QA y PRD para los dos servicios SOAP de OCC?     | Bloquea implementación y pruebas      |
| 2 | ¿Hay conectividad de red desde los ambientes del canal Oficinas hacia BOCC-ACE12?     | Bloquea pruebas en PT                 |
| 3 | ¿El WSDL de `ESB_ACE12_ConsultaDeProductos` retorna TC o solo productos pasivos/activos? | Afecta si se necesita llamada extra |
| 4 | ¿El servicio `ConsultaClientePort` retorna el segmento del cliente?                   | Afecta el modelo de datos             |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador OCC — Consulta General Cliente y Productos
  Como adaptador de Banco de Occidente
  Quiero invocar los servicios SOAP de OCC para obtener cliente y productos
  Para retornar la información consolidada al orquestador

  Background:
    Given el adaptador OCC está configurado con credenciales válidas
    And hay conectividad con los servicios SOAP de OCC (BOCC-ACE12)

  Scenario: Consulta exitosa
    Given el adaptador recibe tipoDocumento "CC" y numeroDocumento "12345678"
    When invoca `consultaDeProductos` (Llamada 1)
    And invoca `consultarDatosBasicos` (Llamada 2)
    Then consolida los datos del cliente y los productos
    And retorna la respuesta al orquestador con StatusCode 200

  Scenario: SOAP Fault en consulta de productos
    Given el servicio `ESB_ACE12_ConsultaDeProductos` retorna un SOAP Fault
    When el adaptador procesa el fault
    Then retorna el error mapeado al orquestador sin intentar la Llamada 2

  Scenario: Timeout en servicio OCC
    Given el servicio SOAP de OCC no responde en el tiempo configurado
    When el adaptador espera la respuesta
    Then retorna 504 al orquestador
    And registra el evento en Elastic
```

---

## Notas Técnicas

- Todos los servicios de OCC son SOAP y pasan por el Datapower interno BOCC-ACE12. Se requiere gestionar certificados y whitelist IP.
- El WSDL de `ESB_ACE12_ConsultaDeProductos` (512 KB) debe ser procesado para generar los stubs Java — coordinar con el equipo de OCC para obtener la versión procesable.
- El front actual de OCC es Siebel — el comportamiento de los servicios puede haber sido diseñado para Siebel; verificar si hay restricciones de uso desde otros canales.

---

## Definition of Ready

> La HU puede entrar a sprint solo cuando **todos** los ítems están cumplidos.

- [ ] WSDLs de `ESB_ACE12_ConsultaDeProductos` y `ConsultaClientePort` obtenidos y procesables
- [ ] Endpoints QA y PRD de los servicios SOAP de OCC confirmados
- [ ] Conectividad de red desde pods AKS hacia Datapower BOCC-ACE12 confirmada en PT
- [ ] Credenciales y certificados de OCC disponibles en PT
- [ ] Confirmado si `consultaDeProductos` retorna TC o requiere llamada adicional
- [ ] Confirmado si `consultarDatosBasicos` retorna el segmento del cliente
- [ ] Estructura de `obj_operacion` definida y acordada
- [ ] Modelo de respuesta normalizada definido y acordado con el orquestador
- [ ] HU-101 (Orquestador) en estado "En desarrollo" o "Completada"
- [ ] Estimación de story points asignada por el equipo
- [ ] Aprobada por líder técnico y product owner

---

## Definition of Done

- [ ] WSDLs de OCC obtenidos y stubs Java generados
- [ ] Conectividad de red con BOCC-ACE12 confirmada en PT
- [ ] Implementación de las dos llamadas SOAP
- [ ] Consolidación y mapeo al modelo normalizado
- [ ] Pruebas unitarias (cobertura ≥ 80%)
- [ ] Prueba de integración contra OCC en PT
- [ ] Aprobado por QA
