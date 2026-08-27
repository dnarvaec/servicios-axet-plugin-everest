# HU-104-ADP-BPO: Adaptador Banco Popular — Consulta Detallada de CDT

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-104-ADP-BPO                                              |
| Épica          | Épica 1 — Consultas P1                                      |
| Componente     | Adaptador BPO — CDT Detallado                               |
| Microservicio  | `ms-consultas-oficinas`                                     |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P1)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | **BLOQUEADA — gap técnico en BPO**                          |
| HU Padre       | HU-104-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-20                                                  |

---

> ## ⚠ HU BLOQUEADA — GAP TÉCNICO
>
> BPO no cuenta con documentación de servicio web para la consulta detallada de CDT. No se encontró información técnica en `InformacionTecnicaEverest_v3.md` ni en ninguna otra fuente relevada.
>
> **Acciones requeridas:**
> - El equipo de BPO debe confirmar si existe un servicio web para CDT detallado.
> - De no existir, BPO debe desarrollar o exponer el servicio.
> - Esta HU no puede entrar a sprint hasta que el servicio esté disponible y documentado.
>
> Mientras el gap esté activo, el orquestador (HU-104-ORQ) retorna `503` cuando el banco seleccionado es BPO para esta operación.

---

## Audiencias

| Rol / Audiencia       | Cómo interactúa                                                    |
|-----------------------|--------------------------------------------------------------------|
| Desarrollador Backend | Implementará el adaptador una vez que BPO confirme el servicio    |
| Integrador BPO        | Responsable de confirmar o desarrollar el servicio web de CDT     |

---

## Historia de Usuario

**Como** adaptador del canal Oficinas para Banco Popular,  
**quiero** recibir del orquestador la solicitud de consulta detallada de CDT,  
**para** invocar el servicio web de BPO, transformar la respuesta al modelo normalizado y retornarla al orquestador.

> **Nota:** Implementación pendiente hasta que BPO confirme o desarrolle el servicio.

---

## Criterios de Aceptación *(pendientes de implementación)*

- **CA-01:** Recibe `tipoDocumento`, `numeroDocumento` y `numeroProducto` del orquestador.
- **CA-02:** Invoca el servicio CDT de BPO (a definir).
- **CA-03:** Transforma la respuesta al modelo normalizado.
- **CA-04:** Si BPO retorna error de CDT no encontrado, mapea a `404`.
- **CA-05:** Si BPO retorna error técnico, mapea y registra en Elastic.
- **CA-06:** El adaptador gestiona los certificados TLS por ambiente.

---

## Inputs *(pendiente — estructura a confirmar)*

```json
{
  "tipoDocumento": "CC",
  "numeroDocumento": "12345678",
  "numeroProducto": "CDT-123456"
}
```

---

## Servicio de BPO a Invocar

| Tipo | Servicio | Estado |
|------|----------|--------|
| Por definir | Por confirmar con BPO | **Sin documentación** |

---

## Reglas de Negocio

1. **RN-01:** Credenciales, certificados y endpoints en variables de ambiente.
2. **RN-02:** Certificado TLS debe corresponder al ambiente activo.
3. **RN-03:** IP desde la que se hacen las llamadas debe estar en whitelist de BPO.

---

## Dependencias

| HU         | Relación   | Descripción                                              |
|------------|------------|----------------------------------------------------------|
| HU-104-ORQ | Padre      | Orquestador — retorna 503 para BPO mientras gap activo  |

---

## Preguntas Abiertas

| # | Pregunta                                                             | Impacto                      |
|---|----------------------------------------------------------------------|------------------------------|
| 1 | ¿BPO cuenta con un servicio web para CDT detallado?                 | Desbloquea toda la HU        |
| 2 | De existir, ¿cuál es el WSDL, código y endpoint?                    | Define el adaptador          |
| 3 | ¿Cuál es la hoja de ruta de BPO para resolver este gap?             | Afecta planificación         |

---

## Definition of Ready

- [ ] **BPO ha confirmado o desarrollado el servicio web de CDT detallado** ← bloqueante principal
- [ ] WSDL / contrato del servicio obtenido
- [ ] Endpoint QA y PRD confirmados con BPO
- [ ] IPs de AKS en whitelist de BPO
- [ ] Certificados TLS por ambiente disponibles
- [ ] Conectividad de red desde AKS hacia Datapower BPO confirmada
- [ ] Estimación asignada y aprobada

## Definition of Done

- [ ] Servicio BPO disponible y documentado
- [ ] Adaptador implementado con cliente HTTP/SOAP
- [ ] Certificados TLS cargados en Keystore
- [ ] Mapeo de respuesta implementado
- [ ] Pruebas unitarias (≥ 80%)
- [ ] Prueba de integración en PT
- [ ] Aprobado por QA
