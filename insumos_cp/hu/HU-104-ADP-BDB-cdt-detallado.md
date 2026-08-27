# HU-104-ADP-BDB: Adaptador Banco de Bogotá — Consulta Detallada de CDT

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-104-ADP-BDB                                              |
| Épica          | Épica 1 — Consultas P1                                      |
| Componente     | Adaptador BdB — CDT Detallado                               |
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

**Como** adaptador del canal Oficinas para Banco de Bogotá,  
**quiero** recibir del orquestador la solicitud de consulta detallada de CDT,  
**para** invocar `retrieveCertificateBalance` de BdB y retornar el detalle normalizado.

---

## Contexto de Negocio

BdB expone el detalle de CDT a través del API REST `balances-management-v2`, operación `retrieveCertificateBalance`. Es el mismo API que cartera y TC — el adaptador reutiliza la configuración de cliente HTTP del mismo microservicio.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe `tipoDocumento`, `numeroDocumento` y `numeroProducto` del orquestador.
- **CA-02:** Invoca `GET retrieveCertificateBalance` en `balances-management-v2`.
- **CA-03:** Transforma la respuesta al modelo normalizado de CDT.
- **CA-04:** Si BdB retorna error de CDT no encontrado, mapea a `404`.
- **CA-05:** Si BdB retorna error técnico, mapea al código correspondiente y registra en Elastic.

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

## Servicio de BdB Invocado

| API / Operación                                           | Tipo | Endpoint QA | Endpoint PROD |
|-----------------------------------------------------------|------|-------------|---------------|
| `balances-management-v2` / `retrieveCertificateBalance`   | REST | `https://api-balances-management.labdigitalbdbtvsqa.com` | `https://api-balances-management.labdigitalbdbtvs.com` |

**Método:** `GET`  
**Path:** `/V2/Enterprise/BalanceManagement/{acctId}/retrieveCertificateBalance`  
Donde `{acctId}` = `numeroProducto` (identificador del CDT en BdB — confirmar si es número interno o el mismo enviado por el asesor).

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

### Modelo normalizado de CDT

| Campo                    | Tipo    | Descripción                                      |
|--------------------------|---------|--------------------------------------------------|
| `numeroProducto`         | String  | Número o referencia del CDT                      |
| `monto`                  | Decimal | Monto del capital invertido                      |
| `tasaEA`                 | Decimal | Tasa efectiva anual                              |
| `fechaApertura`          | Date    | Fecha de apertura del CDT                        |
| `fechaVencimiento`       | Date    | Fecha de vencimiento                             |
| `plazoDias`              | Integer | Plazo en días                                    |
| `periodicidadIntereses`  | String  | Periodicidad de pago (AL_VENCIMIENTO, MENSUAL, etc.) |
| `interesesAcumulados`    | Decimal | Intereses acumulados a la fecha                  |
| `estado`                 | String  | Estado (VIGENTE, VENCIDO, CANCELADO)             |

### Mapeo de errores

| Error BdB            | HTTP BdB | Código Adaptador | StatusDesc                          |
|----------------------|----------|------------------|-------------------------------------|
| CDT no encontrado    | `404`    | `404`            | "CDT no encontrado en BdB"         |
| Error de negocio BdB | `409`    | `422`            | "Error de negocio en BdB"          |
| Timeout              | `408`    | `504`            | "Timeout del servicio BdB"         |
| API Key inválida     | `4xx`    | `502`            | "Error de autenticación con banco" |
| Error interno        | `500`    | `502`            | "Error en el servicio del banco"   |

---

## Reglas de Negocio

1. **RN-01:** Credenciales en variables de ambiente.
2. **RN-02:** No se modifican datos de negocio.

---

## Caminos Alternativos

| ID      | Condición              | Comportamiento                |
|---------|------------------------|-------------------------------|
| ALT-01  | CDT no encontrado      | Retorna `404`                 |
| EXC-01  | Timeout                | Retorna `504`                 |
| EXC-02  | API Key inválida       | Retorna `502`, alerta Elastic |

---

## Tecnología

| Componente   | Tecnología               | Versión |
|--------------|--------------------------|---------|
| Lenguaje     | Java                     | 21      |
| Framework    | Spring Boot              | 3.2.6   |
| Cliente REST | WebClient / RestTemplate | —       |
| Logs         | Elastic                  | —       |

---

## Dependencias

| HU         | Relación |
|------------|----------|
| HU-104-ORQ | Padre    |

---

## Preguntas Abiertas

| # | Pregunta                                                                    | Impacto                     |
|---|-----------------------------------------------------------------------------|-----------------------------|
| 1 | ¿`{acctId}` en la URL es el número de CDT del cliente o un ID interno de BdB? | Define cómo construir la URL |
| 2 | ¿Los valores exactos de `X-Channel`, `X-CompanyId` y `X-NetworkOwner` para canal Oficinas? | Necesario para cabeceras correctas |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador BdB — CDT Detallado
  Background:
    Given el adaptador BdB está configurado con API Key válida

  Scenario: Consulta exitosa
    Given el adaptador recibe numeroProducto "CDT-123456"
    When invoca retrieveCertificateBalance en BdB
    Then retorna el detalle del CDT con StatusCode 200

  Scenario: CDT no encontrado
    When BdB retorna error de CDT no encontrado
    Then el adaptador retorna 404

  Scenario: Timeout
    When el servicio BdB no responde a tiempo
    Then retorna 504 y registra en Elastic
```

---

## Definition of Ready

- [ ] Path de `retrieveCertificateBalance` confirmado con BdB
- [ ] API Key disponible en PT
- [ ] Modelo normalizado de CDT definido
- [ ] HU-104-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Cliente REST implementado
- [ ] Mapeo implementado
- [ ] Pruebas unitarias (≥ 80%)
- [ ] Prueba de integración en PT
- [ ] Aprobado por QA
