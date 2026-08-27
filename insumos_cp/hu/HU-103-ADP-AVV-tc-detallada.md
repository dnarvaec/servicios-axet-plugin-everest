# HU-103-ADP-AVV: Adaptador AV Villas — Consulta Detallada de Tarjeta de Crédito

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-103-ADP-AVV                                              |
| Épica          | Épica 1 — Consultas P1                                      |
| Componente     | Adaptador AVV — TC Detallada                                |
| Microservicio  | `ms-consultas-oficinas`                                     |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P1)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | Pendiente — pendiente confirmar servicio con AVV            |
| HU Padre       | HU-103-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-20                                                  |

---

## Historia de Usuario

**Como** adaptador del canal Oficinas para AV Villas,  
**quiero** recibir del orquestador la solicitud de consulta detallada de TC,  
**para** invocar el servicio correspondiente de AVV y retornar el detalle normalizado.

---

## Contexto de Negocio

AVV no tiene documentación explícita para un servicio de TC detallada independiente. La hipótesis actual es que `getBalanceByProduct` (SOAP) con código de producto `CCA` pueda retornar el detalle de tarjeta de crédito, pero esto debe confirmarse con el equipo de AVV.

> **Pendiente de confirmación:** si `getBalanceByProduct` (CCA) es suficiente o si existe otro servicio específico para TC detallada en AVV.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe `tipoDocumento`, `numeroDocumento` y `referenciaTarjeta` del orquestador.
- **CA-02:** Invoca el servicio de TC detallada de AVV (a confirmar).
- **CA-03:** Transforma la respuesta al modelo normalizado con número enmascarado.
- **CA-04:** Si AVV retorna error de tarjeta no encontrada, mapea a `404`.
- **CA-05:** Si AVV retorna error técnico, mapea al código correspondiente y registra en Elastic.

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

## Servicio de AVV a Invocar (pendiente de confirmación)

| Tipo | Servicio / Operación | Endpoint QA | Endpoint PROD |
|------|----------------------|-------------|---------------|
| SOAP | `WSBA_Multiaplicacion_consultarSaldosIFX` / `getBalanceByProduct` (CCA — a confirmar) | No documentado — confirmar con AVV | `https://10.10.21.10:443/PFBA_Multiaplicacion31/sca/WSBA_Multiaplicacion_consultarSaldosIFX` |

---

## Outputs

### Modelo normalizado de TC

| Campo               | Tipo    | Descripción                                      |
|---------------------|---------|--------------------------------------------------|
| `referenciaTarjeta` | String  | Número enmascarado                               |
| `franquicia`        | String  | Franquicia                                       |
| `estado`            | String  | Estado de la tarjeta                             |
| `cupoAprobado`      | Decimal | Cupo total aprobado                              |
| `cupoDisponible`    | Decimal | Cupo disponible                                  |
| `saldoTotal`        | Decimal | Saldo total adeudado                             |
| `saldoDiferido`     | Decimal | Saldo diferido                                   |
| `cuotasDiferidas`   | Integer | Número de cuotas diferidas activas               |
| `tasaInteres`       | Decimal | Tasa de interés corriente EA                     |
| `saldoMora`         | Decimal | Saldo en mora (0 si está al día)                 |
| `diasMora`          | Integer | Días de mora                                     |
| `fechaCorte`        | Date    | Fecha de corte del período actual                |
| `fechaProximoPago`  | Date    | Fecha límite de pago                             |
| `pagoMinimo`        | Decimal | Pago mínimo requerido                            |
| `pagoTotal`         | Decimal | Pago total para quedar al día                    |

### Mapeo de errores

| Error AVV                       | Código HTTP | StatusDesc                          |
|---------------------------------|-------------|-------------------------------------|
| Tarjeta no encontrada           | `404`        | "Tarjeta no encontrada en AVV"     |
| Error de conectividad           | `502`        | "Error de conectividad con AVV"    |
| Timeout                         | `504`        | "Timeout del servicio AVV"         |
| Error interno                   | `502`        | "Error en el servicio del banco"   |

---

## Reglas de Negocio

1. **RN-01:** Credenciales en variables de ambiente.
2. **RN-02:** Número de tarjeta siempre enmascarado en la respuesta.
3. **RN-03:** El adaptador no modifica datos de negocio.

---

## Caminos Alternativos

| ID      | Condición                     | Comportamiento                     |
|---------|-------------------------------|------------------------------------|
| ALT-01  | Tarjeta no encontrada         | Retorna `404` al orquestador       |
| EXC-01  | Timeout                       | Retorna `504`                      |
| EXC-02  | Error TLS / conectividad      | Retorna `502` y registra en Elastic|

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

| # | Pregunta                                                                                          | Impacto                                           |
|---|---------------------------------------------------------------------------------------------------|---------------------------------------------------|
| 1 | ¿`getBalanceByProduct` con código CCA retorna el detalle completo de TC (cupos, fechas, saldo)?  | Define si es suficiente o se necesita otro servicio |
| 2 | ¿Existe un servicio específico de TC detallada en AVV distinto de `getBalanceByProduct`?         | Define el servicio a implementar                  |
| 3 | ¿Qué campo se usa para identificar la tarjeta en la búsqueda (número enmascarado o ID interno)?  | Define el campo `referenciaTarjeta`               |
| 4 | ¿Hay conectividad confirmada desde pods AKS hacia Datapowers de AVV?                             | Bloquea pruebas en PT                             |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador AVV — Consulta Detallada TC
  Background:
    Given el adaptador AVV está configurado con credenciales válidas
    And hay conectividad con los servicios de AVV

  Scenario: Consulta exitosa
    Given el adaptador recibe referenciaTarjeta "************1234"
    When invoca el servicio de TC detallada de AVV
    Then retorna el detalle con número enmascarado y StatusCode 200

  Scenario: Tarjeta no encontrada
    When AVV retorna error de tarjeta no encontrada
    Then el adaptador retorna 404 al orquestador

  Scenario: Timeout
    When el servicio AVV no responde a tiempo
    Then retorna 504 al orquestador
```

---

## Definition of Ready

- [ ] Confirmación de AVV sobre el servicio a usar para TC detallada
- [ ] Endpoint del servicio en QA confirmado
- [ ] Credenciales disponibles en PT
- [ ] Conectividad de red desde AKS hacia Datapower AVV confirmada
- [ ] HU-103-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Decisión sobre servicio documentada y aprobada
- [ ] Cliente SOAP/REST implementado
- [ ] Número de tarjeta enmascarado — validado en pruebas
- [ ] Mapeo de respuesta implementado
- [ ] Pruebas unitarias (≥ 80%)
- [ ] Prueba de integración en PT
- [ ] Aprobado por QA
