# HU-104-ADP-OCC: Adaptador Banco de Occidente — Consulta Detallada de CDT

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-104-ADP-OCC                                              |
| Épica          | Épica 1 — Consultas P1                                      |
| Componente     | Adaptador OCC — CDT Detallado                               |
| Microservicio  | `ms-consultas-oficinas`                                     |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P1)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | Pendiente                                                   |
| HU Padre       | HU-104-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-20                                                  |

---

## Historia de Usuario

**Como** adaptador del canal Oficinas para Banco de Occidente,  
**quiero** recibir del orquestador la solicitud de consulta detallada de CDT,  
**para** invocar `ConsultaCDTPort` / `ConsultarCDT` de OCC y retornar el detalle normalizado.

---

## Contexto de Negocio

OCC expone la consulta de CDT a través del servicio SOAP `ConsultaCDTPort` / `ConsultarCDT`, accesible a través del middleware BOCC-ACE12. A diferencia de cartera (donde OCC tiene un gap), para CDT sí existe documentación de servicio.

---

## Criterios de Aceptación

- **CA-01:** Recibe `tipoDocumento`, `numeroDocumento` y `numeroProducto` del orquestador.
- **CA-02:** Invoca `ConsultarCDT` de `ConsultaCDTPort` en OCC.
- **CA-03:** Transforma la respuesta al modelo normalizado.
- **CA-04:** Si OCC retorna SOAP Fault de CDT no encontrado, mapea a `404`.
- **CA-05:** Si OCC retorna error técnico, mapea y registra en Elastic.

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

## Servicio de OCC Invocado

| Tipo | Servicio / Puerto / Operación | Middleware | Endpoint |
|------|-------------------------------|------------|----------|
| SOAP | `ConsultaCDTPort` / `ConsultarCDT` | BOCC-ACE12 | Por confirmar con OCC (Datapower Interno) |

> El WSDL y endpoint exactos deben solicitarse al equipo de OCC.

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
| `interesesAcumulados`   | Decimal | Intereses acumulados                         |
| `estado`                | String  | Estado (VIGENTE, VENCIDO, CANCELADO)         |

### Mapeo de errores

| Error OCC                  | Código HTTP | StatusDesc                          |
|----------------------------|-------------|-------------------------------------|
| SOAP Fault — no encontrado | `404`        | "CDT no encontrado en OCC"         |
| Error conectividad BOCC    | `502`        | "Error de conectividad con OCC"    |
| Timeout SOAP               | `504`        | "Timeout del servicio OCC"         |
| Error interno OCC          | `502`        | "Error en el servicio del banco"   |

---

## Reglas de Negocio

1. **RN-01:** Credenciales en variables de ambiente.
2. **RN-02:** No se modifica la lógica de negocio.

---

## Caminos Alternativos

| ID      | Condición              | Comportamiento                     |
|---------|------------------------|------------------------------------|
| ALT-01  | CDT no encontrado      | Retorna `404`                      |
| EXC-01  | Timeout                | Retorna `504`                      |
| EXC-02  | Error TLS / BOCC-ACE12 | Retorna `502`, registra en Elastic |

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

| # | Pregunta                                                              | Impacto                      |
|---|-----------------------------------------------------------------------|------------------------------|
| 1 | ¿Cuál es el endpoint de `ConsultaCDTPort` en QA y PRD?               | Bloquea implementación       |
| 2 | ¿El WSDL está disponible para descarga?                              | Necesario para stubs Java    |
| 3 | ¿`ConsultarCDT` retorna tasa, fechas y periodicidad de intereses?    | Afecta el modelo normalizado |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador OCC — CDT Detallado
  Background:
    Given el adaptador OCC está configurado con credenciales válidas
    And hay conectividad con BOCC-ACE12

  Scenario: Consulta exitosa
    Given el adaptador recibe numeroProducto "CDT-123456"
    When invoca ConsultarCDT en OCC
    Then retorna el detalle con StatusCode 200

  Scenario: CDT no encontrado
    When OCC retorna SOAP Fault de CDT no encontrado
    Then el adaptador retorna 404

  Scenario: Timeout
    When el servicio OCC no responde a tiempo
    Then retorna 504
```

---

## Definition of Ready

- [ ] WSDL de `ConsultaCDTPort` obtenido y procesable
- [ ] Endpoint QA y PRD confirmados con OCC
- [ ] Conectividad desde AKS hacia BOCC-ACE12 confirmada
- [ ] Credenciales de OCC disponibles en PT
- [ ] HU-104-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] WSDL obtenido y stubs Java generados
- [ ] Mapeo de respuesta OCC → modelo normalizado implementado
- [ ] Pruebas unitarias (≥ 80%)
- [ ] Prueba de integración en PT
- [ ] Aprobado por QA
