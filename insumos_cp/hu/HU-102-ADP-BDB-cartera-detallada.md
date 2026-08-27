# HU-102-ADP-BDB: Adaptador Banco de Bogotá — Consulta Detallada de Cartera

## Metadatos

| Campo          | Valor                                                  |
|----------------|--------------------------------------------------------|
| ID             | HU-102-ADP-BDB                                         |
| Épica          | Épica 1 — Consultas P1                                 |
| Componente     | Adaptador BdB — Cartera Detallada                      |
| Microservicio  | `ms-consultas-oficinas` (mismo que HU-101 y HU-102-ORQ) |
| Sprint         | Por definir                                            |
| Prioridad      | Alta (P1)                                              |
| Estimación     | Por estimar                                            |
| Estado         | Pendiente                                              |
| HU Padre       | HU-102-ORQ                                             |
| Autor          | Por definir                                            |
| Fecha          | 2026-08-20                                             |

---

## Audiencias

| Rol / Audiencia       | Cómo interactúa                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------|
| Desarrollador Backend | Implementa el adaptador: invoca `retrieveLoanBalance` de BdB y mapea la respuesta normalizada |
| QA / Tester           | Valida la llamada REST a BdB, el mapeo de campos y el manejo de errores                      |
| Integrador BdB        | Provee acceso y soporte técnico al API REST `balances-management-v2`                         |

---

## Historia de Usuario

**Como** adaptador del canal Oficinas para Banco de Bogotá,  
**quiero** recibir del orquestador la solicitud de consulta detallada de cartera,  
**para** invocar el servicio `retrieveLoanBalance` de BdB, transformar la respuesta al modelo normalizado y retornarla al orquestador.

---

## Contexto de Negocio

BdB expone el detalle de saldos de cartera (créditos) a través del API REST `balances-management-v2`. La operación `retrieveLoanBalance` retorna información detallada de una obligación específica: saldo capital, intereses, mora, cuotas, tasa y fecha de próximo pago. Este adaptador se implementa dentro del microservicio `ms-consultas-oficinas`.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe `tipoDocumento`, `numeroDocumento` y `numeroObligacion` del orquestador.
- **CA-02:** El adaptador invoca `GET /V2/.../retrieveLoanBalance` con el número de obligación como parámetro.
- **CA-03:** El adaptador transforma la respuesta de BdB al modelo normalizado de cartera del canal Oficinas.
- **CA-04:** Si BdB retorna error de obligación no encontrada, el adaptador mapea el error al código estándar `404`.
- **CA-05:** Si BdB retorna error técnico (timeout, autenticación), el adaptador mapea al código estándar correspondiente y registra en Elastic.
- **CA-06:** El adaptador no realiza lógica de negocio — solo invoca, transforma y retorna.

---

## Inputs

### Recibidos del Orquestador

```json
{
  "tipoDocumento": "CC",
  "numeroDocumento": "12345678",
  "numeroObligacion": "987654321"
}
```

| Campo              | Tipo   | Descripción                              | Obligatorio |
|--------------------|--------|------------------------------------------|-------------|
| `tipoDocumento`    | String | Tipo de documento del cliente            | SI          |
| `numeroDocumento`  | String | Número de documento del cliente          | SI          |
| `numeroObligacion` | String | Número de la obligación a consultar      | SI          |

---

## Servicio de BdB Invocado

| # | API / Operación                                     | Tipo | Endpoint QA | Endpoint PROD |
|---|-----------------------------------------------------|------|-------------|---------------|
| 1 | `balances-management-v2` / `retrieveLoanBalance`    | REST | `https://api-balances-management.labdigitalbdbtvsqa.com` | `https://api-balances-management.labdigitalbdbtvs.com` |

**Método:** `GET`  
**Path:** `/V2/Enterprise/BalanceManagement/{acctId}/retrieveLoanBalance`  
Donde `{acctId}` = `numeroObligacion` enviado por el orquestador.

**Headers requeridos:**

| Header           | Obligatorio | Descripción                       |
|------------------|-------------|-----------------------------------|
| `x-api-key`      | Sí          | API Key (variable de ambiente)    |
| `X-CustIdentType`| Sí          | Tipo de documento del cliente     |
| `X-CustIdentNum` | Sí          | Número de documento del cliente   |
| `X-RqUID`        | Sí          | UUID de la petición (mapear desde `X-Trace-Id`) |
| `X-Channel`      | Sí          | Canal (`OFI` para Oficinas)       |
| `X-Name`         | Sí          | Nombre de la aplicación (`ms-consultas-oficinas`) |
| `X-TerminalId`   | Sí          | ID del terminal                   |
| `X-CompanyId`    | Sí          | Código del banco BdB              |
| `X-NetworkOwner` | Sí          | Aplicación origen (máx. 10 chars) |
| `X-IPAddr`       | Sí          | IP origen del adaptador           |
| `X-Journey`      | Sí          | Identificador del journey         |

---

## Outputs

### Modelo normalizado de cartera

| Campo                | Tipo    | Descripción                                         |
|----------------------|---------|-----------------------------------------------------|
| `numeroObligacion`   | String  | Número de la obligación                             |
| `tipoCartera`        | String  | Tipo de cartera (LIBRE_DESTINO, HIPOTECARIA, VEHICULO, etc.) |
| `estado`             | String  | Estado de la obligación (AL_DIA, EN_MORA, CANCELADA)|
| `fechaDesembolso`    | Date    | Fecha de desembolso                                 |
| `plazoMeses`         | Integer | Plazo total en meses                                |
| `cuotasPagadas`      | Integer | Cuotas pagadas a la fecha                           |
| `cuotasPendientes`   | Integer | Cuotas pendientes                                   |
| `valorCuota`         | Decimal | Valor de la cuota mensual                           |
| `saldoCapital`       | Decimal | Saldo de capital vigente                            |
| `oficina`            | String  | Código de oficina de la obligación                  |
| `fechaVencimiento`   | Date    | Fecha de vencimiento del crédito                    |
| `saldoInteresesCorrientes` | Decimal | Saldo de intereses corrientes                |
| `saldoInteresesMora` | Decimal | Saldo de intereses de mora                          |
| `saldoMora`          | Decimal | Saldo total en mora (capital + intereses mora)      |
| `diasMora`           | Integer | Días de mora (0 si está al día)                     |
| `tasaEA`             | Decimal | Tasa efectiva anual                                 |
| `proximaFechaPago`   | Date    | Fecha del próximo pago                              |
| `valorProximoPago`   | Decimal | Valor del próximo pago                              |

> El modelo exacto está **pendiente de confirmar** con la respuesta real del API de BdB.

### Mapeo de errores BdB → estructura estándar

| Error BdB                          | HTTP BdB | Código Adaptador | StatusDesc                              |
|------------------------------------|----------|------------------|-----------------------------------------|
| Obligación no encontrada           | `404`    | `404`            | "Obligación no encontrada en BdB"       |
| Error de negocio BdB               | `409`    | `422`            | "Error de negocio en BdB"              |
| Timeout                            | `408`    | `504`            | "Timeout del servicio BdB"             |
| Sin autorización (API Key inválida)| `4xx`    | `502`            | "Error de autenticación con banco"     |
| Error interno BdB                  | `500`    | `502`            | "Error en el servicio del banco"       |

---

## Reglas de Negocio

1. **RN-01:** Las credenciales (API Key) y endpoints de BdB se configuran por variable de ambiente — nunca hardcodeadas.
2. **RN-02:** El adaptador no filtra ni modifica los datos de negocio retornados por BdB — solo mapea al modelo normalizado.
3. **RN-03:** El adaptador no realiza llamadas adicionales para completar datos faltantes — lo que retorna `retrieveLoanBalance` es el alcance.

---

## Caminos Alternativos y Excepciones

| ID      | Condición                              | Comportamiento esperado                              |
|---------|----------------------------------------|------------------------------------------------------|
| ALT-01  | Obligación no encontrada en BdB        | Retorna `404` al orquestador                         |
| ALT-02  | Cliente sin obligaciones activas       | Retorna código de negocio de BdB                     |
| EXC-01  | Timeout en llamada REST a BdB          | Retorna `504` al orquestador                         |
| EXC-02  | API Key inválida o expirada            | Retorna `502` y registra alerta en Elastic           |

---

## Tecnología a Usar

| Componente    | Tecnología              | Versión | Nota                                       |
|---------------|-------------------------|---------|--------------------------------------------|
| Lenguaje      | Java                    | 21      |                                            |
| Framework     | Spring Boot             | 3.2.6   |                                            |
| Cliente REST  | WebClient / RestTemplate| —       | Para `balances-management-v2`              |
| Logs          | Elastic                 | —       |                                            |

---

## Dependencias

| HU / Componente     | Relación | Descripción                                     |
|---------------------|----------|-------------------------------------------------|
| HU-102-ORQ          | Padre    | Orquestador que invoca este adaptador           |

### Servicios externos (BdB)

| Servicio                  | Tipo | URL QA                                                    | URL PRD                                               |
|---------------------------|------|-----------------------------------------------------------|-------------------------------------------------------|
| `balances-management-v2`  | REST | `https://api-balances-management.labdigitalbdbtvsqa.com`  | `https://api-balances-management.labdigitalbdbtvs.com` |

---

## Seguridad

- **Credenciales:** API Key en variables de ambiente. Nunca en código.
- **TLS:** HTTPS obligatorio en todos los ambientes.

---

## Preguntas Abiertas

| # | Pregunta                                                                                  | Impacto                          |
|---|-------------------------------------------------------------------------------------------|----------------------------------|
| 1 | ¿El API retorna el tipo de cartera (`tipoCartera`) directamente o hay que inferirlo?     | Afecta el modelo normalizado     |
| 2 | ¿`{acctId}` en la URL es el `numeroObligacion` o un identificador interno de BdB?        | Define cómo construir la URL     |
| 3 | ¿El acceso habilitado para `customer-management-v3` cubre también `balances-management-v2`? | Bloquea pruebas si no está habilitado |
| 4 | ¿Los valores exactos de `X-Channel`, `X-CompanyId` y `X-NetworkOwner` para canal Oficinas? | Necesario para cabeceras correctas |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador BdB — Consulta Detallada de Cartera
  Como adaptador de Banco de Bogotá
  Quiero invocar retrieveLoanBalance para obtener el detalle de la obligación
  Para retornar la información normalizada al orquestador

  Background:
    Given el adaptador BdB está configurado con API Key válida
    And el servicio balances-management-v2 está disponible

  Scenario: Consulta exitosa de cartera
    Given el adaptador recibe tipoDocumento "CC", numeroDocumento "12345678" y numeroObligacion "987654321"
    When invoca GET retrieveLoanBalance en BdB
    Then obtiene el detalle de la obligación
    And retorna la respuesta normalizada al orquestador con StatusCode 200

  Scenario: Obligación no encontrada
    Given el adaptador recibe un numeroObligacion que no existe en BdB
    When invoca retrieveLoanBalance
    Then BdB retorna error de no encontrado
    And el adaptador retorna 404 al orquestador

  Scenario: Timeout del servicio
    Given el servicio de BdB no responde en el tiempo configurado
    When el adaptador espera la respuesta
    Then retorna 504 al orquestador
    And registra el evento en Elastic
```

---

## Notas Técnicas

- El API `balances-management-v2` de BdB también expone `retrieveCreditCardBalance` y `retrieveCertificateBalance` — ver HU-103-ADP-BDB y HU-104-ADP-BDB para esas operaciones en el mismo servicio.
- Los headers `X-RqUID`, `X-Channel`, `X-CompanyId` deben coordinarse con el equipo de BdB; el `X-RqUID` puede mapearse desde el `X-Trace-Id` del orquestador.

---

## Definition of Ready

- [ ] Path exacto de `retrieveLoanBalance` confirmado con BdB
- [ ] Headers requeridos para el API documentados y confirmados
- [ ] API Key disponible en PT
- [ ] Conectividad de red desde pods AKS hacia `api-balances-management.labdigitalbdbtvsqa.com` confirmada
- [ ] Modelo de respuesta normalizado definido y acordado
- [ ] HU-102-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación de story points asignada
- [ ] Aprobada por líder técnico y product owner

---

## Definition of Done

- [ ] Cliente REST hacia `balances-management-v2` implementado
- [ ] Mapeo de respuesta BdB → modelo normalizado implementado
- [ ] Manejo de errores y timeouts implementado
- [ ] Pruebas unitarias del mapeo (cobertura ≥ 80%)
- [ ] Prueba de integración contra BdB en PT
- [ ] Aprobado por QA
