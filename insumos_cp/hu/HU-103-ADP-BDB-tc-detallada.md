# HU-103-ADP-BDB: Adaptador Banco de Bogotá — Consulta Detallada de Tarjeta de Crédito

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-103-ADP-BDB                                              |
| Épica          | Épica 1 — Consultas P1                                      |
| Componente     | Adaptador BdB — TC Detallada                                |
| Microservicio  | `ms-consultas-oficinas` (mismo que HU-101, HU-102, HU-103-ORQ) |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P1)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | Pendiente                                                   |
| HU Padre       | HU-103-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-20                                                  |

---

## Historia de Usuario

**Como** adaptador del canal Oficinas para Banco de Bogotá,  
**quiero** recibir del orquestador la solicitud de consulta detallada de TC,  
**para** invocar `retrieveCreditCardBalance` de BdB y retornar el detalle normalizado.

---

## Contexto de Negocio

BdB expone el detalle de saldos de tarjeta de crédito a través del mismo API REST `balances-management-v2` que cartera. La operación `retrieveCreditCardBalance` retorna cupos, saldos, fechas de corte y pago. El número de tarjeta se retorna siempre enmascarado.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe `tipoDocumento`, `numeroDocumento` y `referenciaTarjeta` del orquestador.
- **CA-02:** Invoca `GET retrieveCreditCardBalance` en `balances-management-v2` de BdB.
- **CA-03:** Transforma la respuesta al modelo normalizado de TC con número enmascarado.
- **CA-04:** Si BdB retorna error de tarjeta no encontrada, mapea a `404`.
- **CA-05:** Si BdB retorna error técnico, mapea al código correspondiente y registra en Elastic.

---

## Inputs

```json
{
  "tipoDocumento": "CC",
  "numeroDocumento": "12345678",
  "referenciaTarjeta": "************1234"
}
```

---

## Servicio de BdB Invocado

| API / Operación                                          | Tipo | Endpoint QA | Endpoint PROD |
|----------------------------------------------------------|------|-------------|---------------|
| `balances-management-v2` / `retrieveCreditCardBalance`   | REST | `https://api-balances-management.labdigitalbdbtvsqa.com` | `https://api-balances-management.labdigitalbdbtvs.com` |

**Método:** `GET`  
**Path:** `/V2/Enterprise/BalanceManagement/{acctId}/retrieveCreditCardBalance`  
Donde `{acctId}` = identificador de la tarjeta en BdB (confirmar si es el número enmascarado u otro ID interno).

**Headers requeridos:** (mismos que `balances-management-v2` — ver HU-102-ADP-BDB)

| Header           | Obligatorio | Descripción                       |
|------------------|-------------|-----------------------------------|
| `x-api-key`      | Sí          | API Key (variable de ambiente)    |
| `X-CustIdentType`| Sí          | Tipo de documento del cliente     |
| `X-CustIdentNum` | Sí          | Número de documento del cliente   |
| `X-RqUID`        | Sí          | UUID de la petición               |
| `X-Channel`      | Sí          | Canal (`OFI`)                     |
| `X-Name`         | Sí          | `ms-consultas-oficinas`           |
| `X-TerminalId`   | Sí          | ID del terminal                   |
| `X-CompanyId`    | Sí          | Código banco BdB                  |
| `X-NetworkOwner` | Sí          | Aplicación origen (máx. 10 chars) |
| `X-IPAddr`       | Sí          | IP origen                         |
| `X-Journey`      | Sí          | Identificador del journey         |

---

## Outputs

### Modelo normalizado de TC

| Campo               | Tipo    | Descripción                                      |
|---------------------|---------|--------------------------------------------------|
| `referenciaTarjeta` | String  | Número enmascarado (e.g. `************1234`)     |
| `franquicia`        | String  | Franquicia (VISA, MASTERCARD, AMEX)              |
| `estado`            | String  | Estado (ACTIVA, BLOQUEADA, CANCELADA)            |
| `cupoAprobado`      | Decimal | Cupo total aprobado                              |
| `cupoDisponible`    | Decimal | Cupo disponible                                  |
| `saldoTotal`        | Decimal | Saldo total adeudado                             |
| `saldoDiferido`     | Decimal | Saldo en diferido                                |
| `cuotasDiferidas`   | Integer | Número de cuotas diferidas activas               |
| `tasaInteres`       | Decimal | Tasa de interés corriente EA                     |
| `saldoMora`         | Decimal | Saldo en mora (0 si está al día)                 |
| `diasMora`          | Integer | Días de mora (0 si está al día)                  |
| `fechaCorte`        | Date    | Fecha de corte del período actual                |
| `fechaProximoPago`  | Date    | Fecha límite de pago                             |
| `pagoMinimo`        | Decimal | Pago mínimo requerido                            |
| `pagoTotal`         | Decimal | Pago total para quedar al día                    |

### Mapeo de errores

| Error BdB               | HTTP BdB | Código Adaptador | StatusDesc                        |
|-------------------------|----------|------------------|-----------------------------------|
| Tarjeta no encontrada   | `404`    | `404`            | "Tarjeta no encontrada en BdB"   |
| Error de negocio BdB    | `409`    | `422`            | "Error de negocio en BdB"        |
| Timeout                 | `408`    | `504`            | "Timeout del servicio BdB"        |
| API Key inválida        | `4xx`    | `502`            | "Error de autenticación con banco"|
| Error interno BdB       | `500`    | `502`            | "Error en el servicio del banco"  |

---

## Reglas de Negocio

1. **RN-01:** Credenciales en variables de ambiente.
2. **RN-02:** El número de tarjeta se retorna siempre enmascarado.
3. **RN-03:** El adaptador no modifica datos de negocio — solo mapea.

---

## Caminos Alternativos

| ID      | Condición                        | Comportamiento                         |
|---------|----------------------------------|----------------------------------------|
| ALT-01  | Tarjeta no encontrada            | Retorna `404` al orquestador           |
| EXC-01  | Timeout                          | Retorna `504`                          |
| EXC-02  | API Key inválida                 | Retorna `502` y alerta en Elastic      |

---

## Tecnología

| Componente   | Tecnología              | Versión |
|--------------|-------------------------|---------|
| Lenguaje     | Java                    | 21      |
| Framework    | Spring Boot             | 3.2.6   |
| Cliente REST | WebClient / RestTemplate| —       |
| Logs         | Elastic                 | —       |

---

## Dependencias

| HU         | Relación | Descripción                         |
|------------|----------|-------------------------------------|
| HU-103-ORQ | Padre    | Orquestador que invoca el adaptador |

---

## Preguntas Abiertas

| # | Pregunta                                                                          | Impacto                        |
|---|-----------------------------------------------------------------------------------|--------------------------------|
| 1 | ¿Cuál es el path exacto de `retrieveCreditCardBalance`?                          | Define URL del endpoint        |
| 2 | ¿La referencia de búsqueda es el número enmascarado o un ID interno?             | Define campo de búsqueda       |
| 3 | ¿Los headers son los mismos que para `balances-management-v2` en cartera?        | Reutilización de configuración |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador BdB — Consulta Detallada TC
  Background:
    Given el adaptador BdB está configurado con API Key válida

  Scenario: Consulta exitosa
    Given el adaptador recibe referenciaTarjeta "************1234"
    When invoca retrieveCreditCardBalance en BdB
    Then retorna el detalle con número enmascarado y StatusCode 200

  Scenario: Tarjeta no encontrada
    When BdB retorna error de tarjeta no encontrada
    Then el adaptador retorna 404 al orquestador

  Scenario: Timeout
    When el servicio BdB no responde a tiempo
    Then retorna 504 al orquestador y registra en Elastic
```

---

## Definition of Ready

- [ ] Path de `retrieveCreditCardBalance` confirmado con BdB
- [ ] Mecanismo de búsqueda por referencia definido
- [ ] API Key disponible en PT
- [ ] HU-103-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Cliente REST implementado
- [ ] Número de tarjeta enmascarado — validado en pruebas
- [ ] Mapeo de respuesta implementado
- [ ] Pruebas unitarias (≥ 80%)
- [ ] Prueba de integración en PT
- [ ] Aprobado por QA
