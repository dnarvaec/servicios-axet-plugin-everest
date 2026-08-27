# HU-102-ADP-OCC: Adaptador Banco de Occidente — Consulta Detallada de Cartera

## Metadatos

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| ID             | HU-102-ADP-OCC                                              |
| Épica          | Épica 1 — Consultas P1                                      |
| Componente     | Adaptador OCC — Cartera Detallada                           |
| Microservicio  | `ms-consultas-oficinas` (mismo que HU-101 y HU-102-ORQ)    |
| Sprint         | Por definir                                                 |
| Prioridad      | Alta (P1)                                                   |
| Estimación     | Por estimar                                                 |
| Estado         | **BLOQUEADA — gap técnico en OCC**                          |
| HU Padre       | HU-102-ORQ                                                  |
| Autor          | Por definir                                                 |
| Fecha          | 2026-08-20                                                  |

---

> ## ⚠ HU BLOQUEADA — GAP TÉCNICO
>
> OCC no cuenta actualmente con un web service para la consulta detallada de cartera. Los datos de cartera están disponibles únicamente a través de **BI Publisher / ODS**, sin exposición como servicio web consumible.
>
> **Acciones requeridas:**
> - OCC debe desarrollar o exponer un nuevo web service para cartera detallada.
> - El equipo de OCC debe evaluar `ConsultaDetPrestamoACSOAP` como posible solución alternativa (pendiente de validación).
> - Esta HU no puede entrar a sprint hasta que el servicio esté disponible y documentado.
>
> Mientras el gap esté activo, el orquestador (HU-102-ORQ) retorna `503` con mensaje `"Servicio no disponible para esta entidad"` cuando el banco seleccionado es OCC.

---

## Audiencias

| Rol / Audiencia       | Cómo interactúa                                                                        |
|-----------------------|----------------------------------------------------------------------------------------|
| Desarrollador Backend | Implementará el adaptador una vez que OCC exponga el servicio web                     |
| QA / Tester           | Validará la integración una vez el servicio esté disponible                           |
| Integrador OCC        | Responsable de desarrollar o exponer el web service de cartera detallada              |

---

## Historia de Usuario

**Como** adaptador del canal Oficinas para Banco de Occidente,  
**quiero** recibir del orquestador la solicitud de consulta detallada de cartera,  
**para** invocar el servicio web de OCC, transformar la respuesta al modelo normalizado y retornarla al orquestador.

> **Nota:** Esta funcionalidad está pendiente de implementación hasta que OCC desarrolle el servicio web correspondiente.

---

## Contexto de Negocio

OCC gestiona la información de cartera en BI Publisher / ODS. Actualmente no existe un web service que exponga el detalle de una obligación de cartera de forma sincrónica. El equipo de OCC debe desarrollar un nuevo servicio (posiblemente a través del middleware BOCC-ACE12) o validar si `ConsultaDetPrestamoACSOAP` cubre el caso de uso requerido.

---

## Criterios de Aceptación

*(Aplican una vez resuelto el gap — el servicio OCC esté disponible)*

- **CA-01:** El adaptador recibe `tipoDocumento`, `numeroDocumento` y `numeroObligacion` del orquestador.
- **CA-02:** El adaptador invoca el servicio SOAP de OCC para cartera detallada.
- **CA-03:** El adaptador transforma la respuesta de OCC al modelo normalizado.
- **CA-04:** Si OCC retorna error de obligación no encontrada, el adaptador mapea al código estándar `404`.
- **CA-05:** Si OCC retorna error técnico, el adaptador mapea al código correspondiente y registra en Elastic.
- **CA-06:** El adaptador no realiza lógica de negocio — solo invoca, transforma y retorna.

---

## Inputs

### Recibidos del Orquestador (pendiente de implementación)

```json
{
  "tipoDocumento": "CC",
  "numeroDocumento": "12345678",
  "numeroObligacion": "987654321"
}
```

---

## Servicio de OCC a Invocar (pendiente de definición)

| Tipo | Servicio / Operación                    | Middleware    | Estado          |
|------|-----------------------------------------|---------------|-----------------|
| SOAP | `ConsultaDetPrestamoACSOAP` (a validar) | BOCC-ACE12    | Por confirmar   |
| SOAP | Nuevo servicio a desarrollar por OCC   | BOCC-ACE12    | Pendiente OCC   |

> El endpoint, WSDL y operación exactos quedan **pendientes** hasta que OCC confirme qué servicio se expone.

---

## Reglas de Negocio

1. **RN-01:** Las credenciales y endpoints de OCC se configuran por variable de ambiente.
2. **RN-02:** El adaptador no modifica datos de negocio — solo mapea al modelo normalizado.

---

## Caminos Alternativos y Excepciones

| ID      | Condición                              | Comportamiento esperado                    |
|---------|----------------------------------------|--------------------------------------------|
| ALT-01  | Obligación no encontrada en OCC        | Retorna `404` al orquestador               |
| EXC-01  | Timeout en llamada SOAP a OCC          | Retorna `504` al orquestador               |
| EXC-02  | Error de certificado / conectividad    | Retorna `502` y registra en Elastic        |

---

## Dependencias

| HU / Componente | Relación   | Descripción                                           |
|-----------------|------------|-------------------------------------------------------|
| HU-102-ORQ      | Padre      | Orquestador — retorna 503 para OCC mientras gap activo |

---

## Preguntas Abiertas

| # | Pregunta                                                                               | Impacto                                    |
|---|----------------------------------------------------------------------------------------|--------------------------------------------|
| 1 | ¿`ConsultaDetPrestamoACSOAP` cubre el caso de uso de cartera detallada?               | Define si se reutiliza o se desarrolla nuevo |
| 2 | ¿OCC puede exponer un nuevo web service a través de BOCC-ACE12 para esta consulta?    | Desbloquea toda la HU                      |
| 3 | ¿Cuál es la hoja de ruta de OCC para resolver este gap y en qué fecha?                | Afecta la planificación del sprint         |
| 4 | ¿La información de cartera en BI Publisher / ODS puede exponerse a través de una API? | Posible alternativa temporal               |

---

## Definition of Ready

- [ ] **OCC ha desarrollado o expuesto el servicio web de cartera detallada** ← bloqueante principal
- [ ] WSDL del servicio OCC obtenido y procesable
- [ ] Endpoint QA y PRD confirmados con OCC
- [ ] Conectividad de red desde pods AKS hacia BOCC-ACE12 confirmada
- [ ] Credenciales y certificados de OCC disponibles
- [ ] Modelo de respuesta normalizado definido y acordado
- [ ] HU-102-ORQ en estado "En desarrollo" o "Completada"
- [ ] Estimación de story points asignada
- [ ] Aprobada por líder técnico y product owner

---

## Definition of Done

- [ ] Servicio web OCC disponible y documentado
- [ ] WSDL obtenido y stubs Java generados
- [ ] Conectividad de red con BOCC-ACE12 confirmada en PT
- [ ] Adaptador SOAP implementado
- [ ] Mapeo de respuesta OCC → modelo normalizado implementado
- [ ] Pruebas unitarias (cobertura ≥ 80%)
- [ ] Prueba de integración contra OCC en PT
- [ ] Aprobado por QA
