# HU-101-ADP-BPO: Adaptador Banco Popular — Consulta General de Cliente y Productos

## Metadatos

| Campo          | Valor                                                  |
|----------------|--------------------------------------------------------|
| ID             | HU-101-ADP-BPO                                         |
| Épica          | Épica 1 — Consultas P1                                 |
| Componente     | Adaptador BPO — Consulta General                       |
| Sprint         | Por definir                                            |
| Prioridad      | Alta (P1)                                              |
| Estimación     | Por estimar                                            |
| Estado         | Pendiente                                              |
| HU Padre       | HU-101 (Orquestador)                                   |
| Autor          | Por definir                                            |
| Fecha          | 2026-08-19                                             |

---

## Audiencias

| Rol / Audiencia       | Cómo interactúa                                                                                        |
|-----------------------|--------------------------------------------------------------------------------------------------------|
| Desarrollador Backend | Implementa el adaptador: realiza 2 llamadas SOAP a BPO (productos y cliente), consolida y transforma   |
| QA / Tester           | Valida las llamadas SOAP a BPO, el manejo de certificados, y el mapeo de campos                        |
| Integrador BPO        | Provee WSDLs, certificados TLS y whitelist IP en Datapower interno de BPO                              |

---

## Historia de Usuario

**Como** adaptador del canal Oficinas para Banco Popular,  
**quiero** recibir una solicitud de consulta general del orquestador,  
**para** invocar los servicios SOAP de BPO de consulta de productos (`BSCCC` / `getAccount`) y consulta de datos del cliente (`KK107` / `GetCustomerMDM`), consolidar ambas respuestas y retornar el resultado normalizado.

---

## Contexto de Negocio

BPO expone sus servicios a través del Datapower interno con autenticación por AAA Policy y whitelist de IPs. Los servicios relevantes para la consulta general son:
- `getAccount` (`AccountInquiryBySofia.wsdl`, código `BSCCC`): retorna el resumen de productos del cliente.
- `GetCustomerMDM` (`GetCustomerMDMBySofia.wsdl`, código `KK107`): retorna los datos básicos del cliente.

BPO requiere certificados específicos por ambiente: `datapower.servint.pruebas` en QA y `prd.dp.int.ssl.sofia.bpop` en PRD. El protocolo TLS soportado es 1.0/1.1/1.2 en QA y 1.2/1.3 en PRD. El frente actual de BPO es SOFIA.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe el payload de `obj_operacion` proveniente del orquestador.
- **CA-02:** El adaptador invoca el servicio `getAccount` (`BSCCC`) para obtener el resumen de productos del cliente.
- **CA-03:** El adaptador invoca el servicio `GetCustomerMDM` (`KK107`) para obtener nombre, documento y datos básicos del cliente.
- **CA-04:** El adaptador consolida ambas respuestas en un único objeto normalizado.
- **CA-05:** El adaptador transforma la respuesta consolidada al modelo de datos del canal Oficinas.
- **CA-06:** Si cualquiera de los servicios SOAP retorna un fault o error de negocio, el adaptador lo mapea a la estructura estándar y lo propaga al orquestador.
- **CA-07:** El adaptador gestiona los certificados TLS según el ambiente (QA vs PRD).
- **CA-08:** El adaptador no realiza lógica de negocio adicional — solo invoca, consolida y transforma.

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

## Servicios de BPO Invocados

### Llamada 1 — Consulta de Productos (`BSCCC`)

| Tipo | Código | WSDL | Endpoint QA | Endpoint PROD |
|------|--------|------|-------------|---------------|
| SOAP | BSCCC  | `AccountInquiryBySofia.wsdl` | `https://10.213.133.10:55544/sofia/inquiries` | `https://prd.dp.int.ssl.sofia.bpop:55544/sofia/inquiries` |

**Operación:** `getAccount`  
**Certificado QA:** `datapower.servint.pruebas`  
**Certificado PRD:** `prd.dp.int.ssl.sofia.bpop`  
**TLS QA:** 1.0 / 1.1 / 1.2  
**TLS PRD:** 1.2 / 1.3

### Llamada 2 — Consulta de Datos del Cliente (`KK107`)

| Tipo | Código | WSDL | Endpoint QA | Endpoint PROD |
|------|--------|------|-------------|---------------|
| SOAP | KK107  | `GetCustomerMDMBySofia.wsdl` | `https://qa.dp.int.ssl.sofia.bpop:55612/Inquiries/SSL/GetCustomerMDMBySofia` | `https://prd.dp.int.ssl.sofia.bpop:55612/Inquiries/SSL/GetCustomerMDMBySofia` |

**Operación:** `GetCustomerMDM`  
**Certificado:** El mismo que la Llamada 1 por ambiente.

---

## Outputs

### Datos a consolidar para la respuesta normalizada

**De la Llamada 1 — `getAccount` (productos):**

| Producto    | Campos a mapear                                                    |
|-------------|---------------------------------------------------------------------|
| Cuentas     | Tipo de cuenta, número, saldo, sobregiro (corriente)               |
| CDT         | Número de producto (incluido en `getAccount` — sin detalle)        |
| Carteras    | Tipo de cartera, número de obligación, saldo a pagar               |
| TC          | Número enmascarado, estado, franquicia, cupo disponible            |

**De la Llamada 2 — `GetCustomerMDM` (cliente):**
- Nombre completo
- Tipo y número de documento
- Segmento

### Mapeo de errores BPO → estructura estándar

| Error BPO                          | Código HTTP a retornar | StatusDesc                              |
|------------------------------------|------------------------|-----------------------------------------|
| SOAP Fault — cliente no encontrado | `206`                  | "Cliente no encontrado en BPO"          |
| SOAP Fault — sin productos         | `206`                  | "El cliente no tiene productos en BPO"  |
| Error de certificado TLS           | `502`                  | "Error de certificado TLS con BPO"      |
| IP no autorizada (whitelist)       | `502`                  | "IP no autorizada en Datapower BPO"     |
| Timeout del servicio SOAP          | `504`                  | "Timeout del servicio BPO"              |
| Error interno BPO                  | `502`                  | "Error en el servicio del banco"        |

---

## Reglas de Negocio

1. **RN-01:** Las credenciales, certificados y endpoints de BPO se configuran por variable de ambiente — nunca hardcodeados.
2. **RN-02:** El certificado TLS usado debe corresponder al ambiente activo (QA o PRD). El adaptador no puede usar el certificado de QA en PRD.
3. **RN-03:** Si ambas llamadas fallan, el adaptador retorna error total al orquestador.
4. **RN-04:** La IP desde la que se hacen las llamadas debe estar en la whitelist de BPO — coordinar con infraestructura antes de las pruebas.
5. **RN-05:** Los números de tarjeta de crédito se retornan **enmascarados** en la respuesta normalizada.
6. **RN-06:** Ante una respuesta parcial (cuando un bloque llega con error pero el otro es exitoso), el adaptador retorna la información disponible con el indicador de bloque faltante — no retorna error total.

---

## Caminos Alternativos y Excepciones

| ID      | Condición                                                   | Comportamiento esperado                                        |
|---------|-------------------------------------------------------------|----------------------------------------------------------------|
| ALT-01  | SOAP Fault en `getAccount` o `GetCustomerMDM`              | Mapear fault a estructura estándar y retornar al orquestador  |
| ALT-02  | Cliente sin productos en BPO                               | Retorna código de negocio de BPO                              |
| ALT-03  | Respuesta parcial — un bloque falla pero el otro tiene datos | Retorna lo obtenido con un campo `bloquesFaltantes` indicando qué no pudo consultarse — **no retorna error total** |
| EXC-01  | Timeout en cualquiera de las dos llamadas                  | Retorna `504` al orquestador                                   |
| EXC-02  | Error de certificado TLS (certificado vencido o incorrecto) | Retorna `502` y alerta en Elastic                             |
| EXC-03  | IP del pod AKS no está en la whitelist de BPO              | Retorna `502` con mensaje de IP no autorizada                 |

---

## Tecnología a Usar

| Componente   | Tecnología   | Versión | Nota                                                |
|--------------|--------------|---------|-----------------------------------------------------|
| Lenguaje     | Java         | 21      |                                                     |
| Framework    | Spring Boot  | 3.2.6   |                                                     |
| Cliente SOAP | JAX-WS / CXF | —       | Para `getAccount` y `GetCustomerMDM`                |
| TLS          | Keystore JKS | —       | Certificados por ambiente gestionados por Infra     |
| Logs         | Elastic      | —       |                                                     |

---

## Dependencias

### HUs relacionadas

| HU      | Relación | Descripción                          |
|---------|----------|--------------------------------------|
| HU-101  | Padre    | Orquestador que invoca este adaptador |

### Servicios externos (BPO)

| Servicio          | Código | WSDL                           | Endpoint QA                                    | Endpoint PRD                                          |
|-------------------|--------|--------------------------------|------------------------------------------------|-------------------------------------------------------|
| `getAccount`      | BSCCC  | `AccountInquiryBySofia.wsdl`  | `https://10.213.133.10:55544/sofia/inquiries`  | `https://prd.dp.int.ssl.sofia.bpop:55544/sofia/inquiries` |
| `GetCustomerMDM`  | KK107  | `GetCustomerMDMBySofia.wsdl`  | `https://qa.dp.int.ssl.sofia.bpop:55612/Inquiries/SSL/GetCustomerMDMBySofia` | `https://prd.dp.int.ssl.sofia.bpop:55612/Inquiries/SSL/GetCustomerMDMBySofia` |

---

## Seguridad

- **Autenticación BPO:** AAA Policy del Datapower — gestionada por certificado TLS de cliente.
- **Whitelist IP:** La IP/rango desde el que se invocan los servicios debe estar registrada en el Datapower de BPO. Los pods AKS usan IPs dinámicas — verificar si se usa NAT o IP fija de salida.
- **Certificados:** Deben cargarse en el Keystore del servicio según el ambiente. Gestión a cargo del equipo de infraestructura.

---

## Preguntas Abiertas

| # | Pregunta                                                                                        | Impacto                               |
|---|-------------------------------------------------------------------------------------------------|---------------------------------------|
| 1 | ¿Los pods AKS tienen IP fija de salida o se debe configurar NAT para la whitelist de BPO?      | Bloquea conectividad en todos los ambientes |
| 2 | ¿El servicio `getAccount` (`BSCCC`) retorna TC además de productos pasivos y activos?           | Afecta si se necesita llamada extra para TC |
| 3 | ¿`GetCustomerMDM` retorna el segmento del cliente?                                              | Afecta el modelo de datos             |
| 4 | ¿Los WSDLs `AccountInquiryBySofia.wsdl` y `GetCustomerMDMBySofia.wsdl` están disponibles para descarga? | Bloquea la generación de stubs Java |
| 5 | ¿El flujo de BPO en el documento (slides 9-10 sin validación de huella) corresponde efectivamente a BPO? | Confirma si este banco tiene variante de flujo distinta |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador BPO — Consulta General Cliente y Productos
  Como adaptador de Banco Popular
  Quiero invocar los servicios SOAP de BPO para obtener cliente y productos
  Para retornar la información consolidada al orquestador

  Background:
    Given el adaptador BPO está configurado con credenciales y certificados válidos
    And la IP del servicio está en la whitelist de BPO
    And hay conectividad con el Datapower de BPO

  Scenario: Consulta exitosa
    Given el adaptador recibe tipoDocumento "CC" y numeroDocumento "12345678"
    When invoca `getAccount` (BSCCC) - Llamada 1
    And invoca `GetCustomerMDM` (KK107) - Llamada 2
    Then consolida los datos del cliente y los productos
    And retorna la respuesta al orquestador con StatusCode 200

  Scenario: SOAP Fault en consulta de productos
    Given el servicio `getAccount` retorna un SOAP Fault
    When el adaptador procesa el fault
    Then retorna el error mapeado al orquestador sin intentar la Llamada 2

  Scenario: IP del servicio no está en whitelist de BPO
    Given la IP del pod AKS no está registrada en el Datapower de BPO
    When el adaptador intenta invocar cualquier servicio
    Then recibe un error de conexión rechazada
    And retorna 502 al orquestador con mensaje "IP no autorizada en Datapower BPO"
    And registra la alerta en Elastic

  Scenario: Certificado TLS vencido
    Given el certificado de ambiente está vencido
    When el adaptador establece la conexión TLS con BPO
    Then el handshake falla
    And retorna 502 al orquestador con mensaje "Error de certificado TLS con BPO"

  Scenario: Timeout en servicio BPO
    Given el servicio SOAP de BPO no responde en el tiempo configurado
    When el adaptador espera la respuesta
    Then retorna 504 al orquestador
    And registra el evento en Elastic
```

---

## Notas Técnicas

- BPO es el banco con más restricciones de conectividad: AAA Policy + whitelist IP + certificados por ambiente. La coordinación con el equipo de BPO e infraestructura debe iniciarse en paralelo al desarrollo.
- Los WSDLs `AccountInquiryBySofia.wsdl` y `GetCustomerMDMBySofia.wsdl` deben solicitarse al equipo de BPO para generar los stubs Java con JAX-WS/CXF.
- En QA, el endpoint de `getAccount` usa IP pública (`10.213.133.10`) pero el de `GetCustomerMDM` usa hostname DNS (`qa.dp.int.ssl.sofia.bpop`). Verificar resolución DNS en los pods AKS.
- El frente actual de BPO es SOFIA — los servicios pueden tener restricciones pensadas para ese frente. Verificar si hay limitaciones al usarlos desde un canal nuevo.

---

## Definition of Ready

> La HU puede entrar a sprint solo cuando **todos** los ítems están cumplidos.

- [ ] WSDLs `AccountInquiryBySofia.wsdl` y `GetCustomerMDMBySofia.wsdl` obtenidos del equipo BPO
- [ ] IPs de salida de los pods AKS identificadas y registradas en la whitelist de BPO
- [ ] Certificados TLS por ambiente (`datapower.servint.pruebas` para QA, `prd.dp.int.ssl.sofia.bpop` para PRD) obtenidos y cargados en Keystore
- [ ] Conectividad de red desde pods AKS hacia Datapower BPO confirmada en PT
- [ ] Confirmado si `getAccount` (BSCCC) incluye TC en su respuesta o requiere llamada adicional
- [ ] Confirmado si `GetCustomerMDM` (KK107) retorna el segmento del cliente
- [ ] Estructura de `obj_operacion` definida y acordada
- [ ] Modelo de respuesta normalizada definido y acordado con el orquestador
- [ ] HU-101 (Orquestador) en estado "En desarrollo" o "Completada"
- [ ] Estimación de story points asignada por el equipo
- [ ] Aprobada por líder técnico y product owner

---

## Definition of Done

- [ ] WSDLs de BPO obtenidos y stubs Java generados
- [ ] Certificados TLS por ambiente cargados en Keystore
- [ ] IPs de los pods AKS registradas en whitelist de BPO
- [ ] Implementación de las dos llamadas SOAP
- [ ] Consolidación y mapeo al modelo normalizado
- [ ] Pruebas unitarias (cobertura ≥ 80%)
- [ ] Prueba de integración contra BPO en PT
- [ ] Aprobado por QA
