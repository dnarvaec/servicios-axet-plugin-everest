# HU-103-ADP-OCC: Adaptador Banco de Occidente — Consulta Detallada de Tarjeta de Crédito

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-103-ADP-OCC                                              |
| Épica          | Épica 1 — Consultas P1                                      |
| Componente     | Adaptador OCC — TC Detallada                                |
| Microservicio  | `ms-consultas-oficinas`                                     |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P1)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | Pendiente                                                   |
| HU Padre       | HU-103-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-20                                                  |

---

## Historia de Usuario

**Como** adaptador del canal Oficinas para Banco de Occidente,  
**quiero** recibir del orquestador la solicitud de consulta detallada de TC,  
**para** invocar `ConsultaSaldoTarjetaCreditoPort` / `consultarSaldoConsolidado` de OCC y retornar el detalle normalizado.

---

## Contexto de Negocio

OCC expone el detalle de tarjeta de crédito a través del servicio SOAP `ConsultaSaldoTarjetaCreditoPort` / `consultarSaldoConsolidado`. El servicio pasa por el middleware BOCC-ACE12. A diferencia de cartera (donde OCC tiene un gap), para TC sí existe un servicio documentado.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe `tipoDocumento`, `numeroDocumento` y `referenciaTarjeta` del orquestador.
- **CA-02:** Invoca `consultarSaldoConsolidado` de `ConsultaSaldoTarjetaCreditoPort` en OCC.
- **CA-03:** Transforma la respuesta al modelo normalizado con número enmascarado.
- **CA-04:** Si OCC retorna SOAP Fault de tarjeta no encontrada, mapea a `404`.
- **CA-05:** Si OCC retorna error técnico, mapea al código correspondiente y registra en Elastic.

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

## Servicio de OCC Invocado

| Tipo | Servicio / Puerto / Operación | Middleware | Endpoint |
|------|-------------------------------|------------|----------|
| SOAP | `ConsultaSaldoTarjetaCreditoService` / `ConsultaSaldoTarjetaCreditoPort` / `consultarSaldoConsolidado` | BOCC-ACE12 (Datapower Interno) | Por confirmar con OCC |

> El WSDL y el endpoint exacto deben solicitarse al equipo de OCC.

---

## Outputs

### Modelo normalizado de TC

| Campo               | Tipo    | Descripción                              |
|---------------------|---------|------------------------------------------|
| `referenciaTarjeta` | String  | Número enmascarado                       |
| `franquicia`        | String  | Franquicia                               |
| `estado`            | String  | Estado de la tarjeta                     |
| `cupoAprobado`      | Decimal | Cupo total aprobado                      |
| `cupoDisponible`    | Decimal | Cupo disponible                          |
| `saldoTotal`        | Decimal | Saldo total adeudado                     |
| `saldoDiferido`     | Decimal | Saldo diferido                           |
| `cuotasDiferidas`   | Integer | Número de cuotas diferidas activas       |
| `tasaInteres`       | Decimal | Tasa de interés corriente EA             |
| `saldoMora`         | Decimal | Saldo en mora (0 si está al día)         |
| `diasMora`          | Integer | Días de mora                             |
| `fechaCorte`        | Date    | Fecha de corte del período actual        |
| `fechaProximoPago`  | Date    | Fecha límite de pago                     |
| `pagoMinimo`        | Decimal | Pago mínimo requerido                    |
| `pagoTotal`         | Decimal | Pago total para quedar al día            |

### Mapeo de errores

| Error OCC                   | Código HTTP | StatusDesc                         |
|-----------------------------|-------------|-----------------------------------|
| SOAP Fault — no encontrada  | `404`        | "Tarjeta no encontrada en OCC"   |
| Error conectividad BOCC     | `502`        | "Error de conectividad con OCC"  |
| Timeout SOAP                | `504`        | "Timeout del servicio OCC"       |
| Error interno OCC           | `502`        | "Error en el servicio del banco" |

---

## Reglas de Negocio

1. **RN-01:** Credenciales en variables de ambiente.
2. **RN-02:** Número de tarjeta siempre enmascarado.
3. **RN-03:** No se modifica la lógica de negocio — solo se mapea.

---

## Caminos Alternativos

| ID      | Condición                   | Comportamiento                     |
|---------|-----------------------------|------------------------------------|
| ALT-01  | Tarjeta no encontrada       | Retorna `404`                      |
| EXC-01  | Timeout                     | Retorna `504`                      |
| EXC-02  | Error TLS / BOCC-ACE12      | Retorna `502` y registra en Elastic|

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
| HU-103-ORQ | Padre    |

---

## Preguntas Abiertas

| # | Pregunta                                                                                        | Impacto                          |
|---|-------------------------------------------------------------------------------------------------|----------------------------------|
| 1 | ¿Cuál es el endpoint de `ConsultaSaldoTarjetaCreditoPort` en QA y PRD?                        | Bloquea implementación           |
| 2 | ¿El WSDL está disponible para descarga?                                                        | Necesario para stubs Java        |
| 3 | ¿`consultarSaldoConsolidado` retorna el nivel de detalle completo (cupos, fechas, pagos)?      | Afecta el modelo normalizado     |
| 4 | ¿Hay conectividad de red desde pods AKS hacia BOCC-ACE12?                                      | Bloquea pruebas en PT            |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador OCC — Consulta Detallada TC
  Background:
    Given el adaptador OCC está configurado con credenciales válidas
    And hay conectividad con los servicios SOAP de OCC (BOCC-ACE12)

  Scenario: Consulta exitosa
    Given el adaptador recibe referenciaTarjeta "************1234"
    When invoca consultarSaldoConsolidado en OCC
    Then retorna el detalle con número enmascarado y StatusCode 200

  Scenario: SOAP Fault — tarjeta no encontrada
    When OCC retorna SOAP Fault de tarjeta no encontrada
    Then el adaptador retorna 404 al orquestador

  Scenario: Timeout
    When el servicio OCC no responde a tiempo
    Then retorna 504 al orquestador
```

---

## Definition of Ready

- [ ] WSDL de `ConsultaSaldoTarjetaCreditoPort` obtenido y procesable
- [ ] Endpoint QA y PRD confirmados con OCC
- [ ] Conectividad de red desde AKS hacia BOCC-ACE12 confirmada
- [ ] Credenciales de OCC disponibles en PT
- [ ] HU-103-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] WSDL obtenido y stubs Java generados
- [ ] Número de tarjeta enmascarado — validado en pruebas
- [ ] Mapeo de respuesta OCC → modelo normalizado implementado
- [ ] Pruebas unitarias (≥ 80%)
- [ ] Prueba de integración en PT
- [ ] Aprobado por QA
