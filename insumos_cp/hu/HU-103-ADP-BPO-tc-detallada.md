# HU-103-ADP-BPO: Adaptador Banco Popular — Consulta Detallada de Tarjeta de Crédito

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-103-ADP-BPO                                              |
| Épica          | Épica 1 — Consultas P1                                      |
| Componente     | Adaptador BPO — TC Detallada                                |
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

**Como** adaptador del canal Oficinas para Banco Popular,  
**quiero** recibir del orquestador la solicitud de consulta detallada de TC,  
**para** invocar `CreditCardInformationDetail` (código `FDCTC`) de BPO y retornar el detalle normalizado.

---

## Contexto de Negocio

BPO expone el detalle de tarjeta de crédito a través del servicio SOAP `CreditCardInformationDetail.wsdl` (código `FDCTC`). El servicio pasa por el Datapower interno de BPO con autenticación AAA Policy y whitelist IP. Los certificados TLS son los mismos que los demás servicios BPO por ambiente.

---

## Criterios de Aceptación

- **CA-01:** El adaptador recibe `tipoDocumento`, `numeroDocumento` y `referenciaTarjeta` del orquestador.
- **CA-02:** Invoca el servicio SOAP `CreditCardInformationDetail` (FDCTC) de BPO.
- **CA-03:** Transforma la respuesta al modelo normalizado con número enmascarado.
- **CA-04:** Si BPO retorna SOAP Fault de tarjeta no encontrada, mapea a `404`.
- **CA-05:** Si BPO retorna error técnico, mapea al código correspondiente y registra en Elastic.
- **CA-06:** El adaptador gestiona los certificados TLS según el ambiente.

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

## Servicios de BPO Disponibles

BPO expone dos servicios para consulta detallada de TC. Se debe confirmar cuál usar para el canal Oficinas:

### Opción A — CreditCardInformationDetail (SOFIA / Datapower interno) ← preferida

| Tipo | Código | WSDL | Endpoint QA | Endpoint PROD |
|------|--------|------|-------------|---------------|
| SOAP | FDCTC  | `CreditCardInformationDetail.wsdl` | `https://10.213.133.10:55544/inquiries/SSL/CreditCardInformationDetail` | `https://prd.dp.int.ssl.sofia.bpop:55544/inquiries/SSL/CreditCardInformationDetail` |

**Seguridad:** AAA Policy (Datapower) + Control por IP (whitelist) + TLS  
**Certificado QA:** `CN=datapower.servint.pruebas`  
**TLS QA:** 1.0 / 1.1 / 1.2

### Opción B — CreditCardInquiry (First Data / BUS ACE)

| Tipo | WSDL | Middleware | Endpoint QA | Endpoint PROD |
|------|------|------------|-------------|---------------|
| SOAP | `CreditCardInquiry.wsdl` | BUS ACE | `http://10.200.157.40:7801/inquiries/CreditCardInquiry` | `http://10.223.225.21:7801/inquiries/CreditCardInquiry` |

**Seguridad:** Firewall (permisos de FW) — sin TLS ni AAA

> **Pendiente de decisión:** confirmar con el equipo BPO cuál de los dos servicios usar para el canal Oficinas. La Opción A (SOFIA) es la ruta segura estándar.

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

> Modelo exacto **pendiente de confirmar** con la respuesta real del servicio BPO elegido.

### Mapeo de errores

| Error BPO                     | Código HTTP | StatusDesc                          |
|-------------------------------|-------------|-------------------------------------|
| SOAP Fault — no encontrada    | `404`        | "Tarjeta no encontrada en BPO"     |
| Error de certificado TLS      | `502`        | "Error de certificado TLS con BPO" |
| IP no autorizada              | `502`        | "IP no autorizada en Datapower BPO"|
| Timeout                       | `504`        | "Timeout del servicio BPO"         |
| Error interno BPO             | `502`        | "Error en el servicio del banco"   |

---

## Reglas de Negocio

1. **RN-01:** Credenciales, certificados y endpoints en variables de ambiente.
2. **RN-02:** Certificado TLS debe corresponder al ambiente activo.
3. **RN-03:** IP desde la que se hacen las llamadas debe estar en whitelist de BPO.
4. **RN-04:** Número de tarjeta siempre enmascarado.

---

## Caminos Alternativos

| ID      | Condición                        | Comportamiento                           |
|---------|----------------------------------|------------------------------------------|
| ALT-01  | Tarjeta no encontrada            | Retorna `404` al orquestador             |
| EXC-01  | Timeout                          | Retorna `504`                            |
| EXC-02  | Error de certificado TLS         | Retorna `502` y alerta en Elastic        |
| EXC-03  | IP no en whitelist               | Retorna `502` con mensaje IP no autorizada|

---

## Tecnología

| Componente   | Tecnología   | Versión |
|--------------|--------------|---------|
| Lenguaje     | Java         | 21      |
| Framework    | Spring Boot  | 3.2.6   |
| Cliente SOAP | JAX-WS / CXF | —       |
| TLS          | Keystore JKS | —       |
| Logs         | Elastic      | —       |

---

## Dependencias

| HU         | Relación |
|------------|----------|
| HU-103-ORQ | Padre    |

---

## Preguntas Abiertas

| # | Pregunta                                                                                  | Impacto                             |
|---|-------------------------------------------------------------------------------------------|-------------------------------------|
| 1 | ¿Cuál de los dos servicios usar para canal Oficinas: `CreditCardInformationDetail` (SOFIA) o `CreditCardInquiry` (First Data)? | Define implementación a realizar  |
| 2 | ¿`CreditCardInformationDetail` retorna cupos, fechas de corte, pago mínimo, tasa, mora?  | Afecta el modelo normalizado        |
| 3 | ¿El WSDL del servicio elegido está disponible para descarga?                             | Necesario para stubs Java           |
| 4 | ¿Los pods AKS tienen IP fija de salida para la whitelist de BPO?                         | Bloquea conectividad                |

---

## Escenarios Gherkin

```gherkin
Feature: Adaptador BPO — Consulta Detallada TC
  Background:
    Given el adaptador BPO está configurado con certificados válidos
    And la IP está en la whitelist de BPO

  Scenario: Consulta exitosa
    Given el adaptador recibe referenciaTarjeta "************1234"
    When invoca CreditCardInformationDetail (FDCTC) en BPO
    Then retorna el detalle con número enmascarado y StatusCode 200

  Scenario: Tarjeta no encontrada
    When BPO retorna SOAP Fault de tarjeta no encontrada
    Then el adaptador retorna 404 al orquestador

  Scenario: Error de certificado TLS
    When el handshake TLS falla
    Then retorna 502 con mensaje de error de certificado

  Scenario: Timeout
    When el servicio BPO no responde a tiempo
    Then retorna 504 al orquestador
```

---

## Definition of Ready

- [ ] WSDL `CreditCardInformationDetail.wsdl` obtenido del equipo BPO
- [ ] IPs de salida de pods AKS registradas en whitelist BPO
- [ ] Certificados TLS por ambiente en Keystore
- [ ] Conectividad de red desde AKS hacia Datapower BPO confirmada
- [ ] HU-103-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] WSDL obtenido y stubs Java generados
- [ ] Certificados TLS por ambiente cargados en Keystore
- [ ] Número de tarjeta enmascarado — validado en pruebas
- [ ] Mapeo de respuesta BPO → modelo normalizado implementado
- [ ] Pruebas unitarias (≥ 80%)
- [ ] Prueba de integración en PT
- [ ] Aprobado por QA
