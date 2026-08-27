# HU-104-ADP-AVV: Adaptador AV Villas — Consulta Detallada de CDT

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-104-ADP-AVV                                              |
| Épica          | Épica 1 — Consultas P1                                      |
| Componente     | Adaptador AVV — CDT Detallado                               |
| Microservicio  | `ms-consultas-oficinas`                                     |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P1)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | Pendiente — pendiente confirmar servicio con AVV            |
| HU Padre       | HU-104-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-20                                                  |

---

## Historia de Usuario

**Como** adaptador del canal Oficinas para AV Villas,  
**quiero** recibir del orquestador la solicitud de consulta detallada de CDT,  
**para** invocar el servicio correspondiente de AVV y retornar el detalle normalizado.

---

## Contexto de Negocio

AVV no tiene documentación explícita para un servicio de CDT detallado independiente. La hipótesis actual es que `getBalanceByProduct` (SOAP) con código de producto `CDA` pueda retornar el detalle del CDT. Esto debe confirmarse con el equipo de AVV.

> **Pendiente de confirmación:** si `getBalanceByProduct` (CDA) es suficiente o si existe un servicio específico para CDT detallado en AVV.

---

## Criterios de Aceptación

- **CA-01:** Recibe `tipoDocumento`, `numeroDocumento` y `numeroProducto` del orquestador.
- **CA-02:** Invoca el servicio CDT detallado de AVV (a confirmar).
- **CA-03:** Transforma la respuesta al modelo normalizado.
- **CA-04:** Si AVV retorna error de CDT no encontrado, mapea a `404`.
- **CA-05:** Si AVV retorna error técnico, mapea y registra en Elastic.

---

## Inputs

```json
{
  "tipoDocumento": "CC",
  "numeroDocumento": "12345678",
  "numeroProducto": "CDT-123456"
}
```

---

## Servicio de AVV a Invocar (pendiente de confirmación)

| Tipo | Servicio / Operación | Endpoint QA | Endpoint PROD |
|------|----------------------|-------------|---------------|
| SOAP | `WSBA_Multiaplicacion_consultarSaldosIFX` / `getBalanceByProduct` (CDA — a confirmar) | `https://10.10.9.200:443/PFBA_Multiaplicacion31/sca/WSBA_Multiaplicacion_consultarSaldosIFX` | `https://10.10.21.10:443/PFBA_Multiaplicacion31/sca/WSBA_Multiaplicacion_consultarSaldosIFX` |

---

## Outputs

### Modelo normalizado de CDT

| Campo                   | Tipo    | Descripción                                  |
|-------------------------|---------|----------------------------------------------|
| `numeroProducto`        | String  | Número del CDT                               |
| `monto`                 | Decimal | Monto capital                                |
| `tasaEA`                | Decimal | Tasa efectiva anual                          |
| `fechaApertura`         | Date    | Fecha de apertura                            |
| `fechaVencimiento`      | Date    | Fecha de vencimiento                         |
| `plazoDias`             | Integer | Plazo en días                                |
| `periodicidadIntereses` | String  | Periodicidad de pago                         |
| `interesesAcumulados`   | Decimal | Intereses acumulados a la fecha              |
| `estado`                | String  | Estado (VIGENTE, VENCIDO, CANCELADO)         |

### Mapeo de errores

| Error AVV                | Código HTTP | StatusDesc                         |
|--------------------------|-------------|-----------------------------------|
| CDT no encontrado        | `404`        | "CDT no encontrado en AVV"       |
| Error de conectividad    | `502`        | "Error de conectividad con AVV"  |
| Timeout                  | `504`        | "Timeout del servicio AVV"       |
| Error interno            | `502`        | "Error en el servicio del banco" |

---

## Reglas de Negocio

1. **RN-01:** Credenciales en variables de ambiente.
2. **RN-02:** No se modifica la lógica de negocio.

---

## Caminos Alternativos

| ID      | Condición             | Comportamiento                     |
|---------|-----------------------|------------------------------------|
| ALT-01  | CDT no encontrado     | Retorna `404`                      |
| EXC-01  | Timeout               | Retorna `504`                      |
| EXC-02  | Error TLS/conectividad| Retorna `502`, registra en Elastic |

---

## Tecnología

| Componente   | Tecnología   | Versión |
|--------------|--------------|---------|
| Lenguaje     | Java         | 21      |
| Framework    | Spring Boot  | 3.2.6   |
| Cliente SOAP | JAX-WS / CXF | —       |
| Logs         | Elastic      | —       |

---

## Dependencias

| HU         | Relación |
|------------|----------|
| HU-104-ORQ | Padre    |

---

## Preguntas Abiertas

| # | Pregunta                                                                                       | Impacto                                      |
|---|------------------------------------------------------------------------------------------------|----------------------------------------------|
| 1 | ¿`getBalanceByProduct` con código CDA retorna el detalle completo del CDT (tasa, fechas, monto)?| Define si es suficiente o se necesita otro  |
| 2 | ¿Existe servicio específico para CDT detallado en AVV distinto de `getBalanceByProduct`?      | Define el servicio a implementar             |
| 3 | ¿Hay conectividad de red confirmada desde pods AKS hacia Datapowers de AVV?                   | Bloquea pruebas en PT                        |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador AVV — CDT Detallado
  Background:
    Given el adaptador AVV está configurado con credenciales válidas
    And hay conectividad con los servicios de AVV

  Scenario: Consulta exitosa
    Given el adaptador recibe numeroProducto "CDT-123456"
    When invoca el servicio CDT detallado de AVV
    Then retorna el detalle con StatusCode 200

  Scenario: CDT no encontrado
    When AVV retorna error de CDT no encontrado
    Then el adaptador retorna 404

  Scenario: Timeout
    When el servicio AVV no responde a tiempo
    Then retorna 504
```

---

## Definition of Ready

- [ ] Confirmación de AVV sobre el servicio CDT detallado
- [ ] Endpoint en QA confirmado
- [ ] Credenciales disponibles en PT
- [ ] Conectividad desde AKS hacia Datapower AVV confirmada
- [ ] HU-104-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Decisión sobre servicio documentada
- [ ] Cliente SOAP/REST implementado
- [ ] Mapeo de respuesta implementado
- [ ] Pruebas unitarias (≥ 80%)
- [ ] Prueba de integración en PT
- [ ] Aprobado por QA
