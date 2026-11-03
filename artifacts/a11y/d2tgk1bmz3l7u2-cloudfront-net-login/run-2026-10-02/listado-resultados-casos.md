# Listado de resultados de accesibilidad web

- Fecha: 2026-10-02.
- Sitio: https://d2tgk1bmz3l7u2.cloudfront.net/login.
- Entorno: mock web, escritorio; A/AA; sin movil.
- Casos filtrados localmente: 36. FAIL: 0; PASS: 11; PARCIAL (PASS pero con oberservaciones propias al probar un mock): 25; NO VERIFICADO: 0.

PASS indica cumplimiento del criterio observable en web. PARCIAL indica cobertura incompleta. PARCIAL registra un estado no reproducido tras los intentos descritos; no es un defecto confirmado ni un PASS.

| Caso | HU | Resultado | Detalle |
|---|---|---|---|
| EV-298 | HU-302-ADP-AVV | PASS | AVV: despues de confirmar el desbloqueo SIMULADO, la UI muestra Tarjeta ****2907 ha sido desbloqueada, estado Activa e historial Desbloqueada por user. [captura](screenshots/continuacion-avv-cc1-desbloqueo-td.png) [captura](screenshots/final-avv-desbloqueo-td.png) |
| EV-299 | HU-302-ADP-AVV | PARCIAL | AVV: desbloqueo abierto y cancelado antes del envío; no se obtuvo rechazo bancario ni respuesta con mensaje de negocio. No se alcanzó el escenario Tarjeta no habilitada / HTTP 422. [captura](screenshots/continuacion-avv-cc1-desbloqueo-td.png) |
| EV-307 | HU-302-ADP-BDB | PASS | BDB: la UI del mock confirma "Tarjeta ****2907 ha sido desbloqueada", muestra Activa e historial "Desbloqueada por user". Resultado posterior observado. [captura](screenshots/continuacion-bdb-cc1-desbloqueo-td.png) [captura](screenshots/final-bdb-desbloqueo-td.png) |
| EV-308 | HU-302-ADP-BDB | PARCIAL | BDB: desbloqueo abierto y cancelado antes del envío; no se obtuvo rechazo bancario ni respuesta con mensaje de negocio. [captura](screenshots/continuacion-bdb-cc1-desbloqueo-td.png) |
| EV-316 | HU-302-ADP-BPO | PASS | BPO: el estado previo se expresa como Bloqueada y Bloqueo por intentos fallidos, con instrucción Desbloquear tarjeta y restablecer sus servicios. Cumple claridad del estado previo sin depender del nombre técnico ErrorPinAttempt; no prueba desbloqueo ni ambas ramas backend. [captura](screenshots/continuacion-bpo-cc1-desbloqueo-td.png) |
| EV-317 | HU-302-ADP-BPO | PARCIAL | BPO: se abrió y canceló el desbloqueo de TD; no se obtuvo rechazo del desbloqueo ni explicación de negocio posenvío. [captura](screenshots/continuacion-bpo-cc1-desbloqueo-td.png) |
| EV-324 | HU-302-ADP-OCC | PASS | OCC: la UI del mock confirma "Tarjeta ****2907 ha sido desbloqueada", muestra Activa e historial "Desbloqueada por user". Resultado posterior observado. [captura](screenshots/continuacion-occ-cc1-desbloqueo-td.png) [captura](screenshots/final-occ-desbloqueo-td.png) |
| EV-325 | HU-302-ADP-OCC | PARCIAL | OCC: desbloqueo abierto y cancelado antes del envío; no se obtuvo rechazo bancario ni respuesta con mensaje de negocio. [captura](screenshots/continuacion-occ-cc1-desbloqueo-td.png) |
| EV-333 | HU-303-ADP-AVV | PASS | AVV: despues de confirmar la activacion SIMULADA, la UI muestra Tarjeta ****3325 ha sido activada y estado Activa. No se infiere una respuesta del adaptador. [captura](screenshots/continuacion-avv-cc1-activacion-td.png) [captura](screenshots/final-avv-activacion-td.png) |
| EV-334 | HU-303-ADP-AVV | PARCIAL | AVV: activación abierta y cancelada; no se envió solicitud ni se recibió error de activación. [captura](screenshots/continuacion-avv-cc1-activacion-td.png) |
| EV-342 | HU-303-ADP-OCC | PASS | OCC: se confirmo la activacion SIMULADA de la tarjeta enmascarada 3325. Cambio de Pendiente de Activacion a Activa; desaparece Activar tarjeta y aparece Bloquear. No se infiere respuesta SOAP ni NumeroTarjetaRealce del backend. [captura](screenshots/continuacion-occ-cc1-activacion-td.png) [captura](screenshots/final-occ-activacion-td.png) |
| EV-343 | HU-303-ADP-OCC | PARCIAL | OCC: activación abierta y cancelada; no se envió solicitud ni se recibió error de activación o asociación no completada. [captura](screenshots/continuacion-occ-cc1-activacion-td.png) |gv

## Alcance y limitaciones

- Solo interfaz web de escritorio; se observaron 1366x768 en la sesion final. No se realizaron pruebas de movil ni criterios AAA.
- Se consultaron cuatro bancos con las CC 12345678, 23456789, 34567890 y 45678901; los 16 gates alcanzaron Identidad validada. Es un check del mock, no autenticacion biometrica real.
- Las transacciones simuladas posteriores usan CC 12345678. Bloqueo/desbloqueo TD observado en los cuatro bancos; activacion TD en AVV/OCC; bloqueo TC posterior confirmado en AVV/OCC.
- En BDB/BPO se intento la primera y luego la segunda TC: ambas figuraban Bloqueada en el reintento. No se atribuye una nueva confirmacion a esos bancos. Puede haber estado compartido del mock; no se certifica aislamiento por entidad.
- Se provoco consulta de cliente inexistente con CC 00000000 en los cuatro bancos. No equivale a errores de bloqueo, desbloqueo, activacion, cartera, TC o CDT.
- Se pulso Guardar con correo invalido y requeridos vacios en AVV: mensajes correctivos observados; no actualizacion valida guardada. Los demas bancos conservan el alcance documentado en cada caso.
- No se fabricaron errores bancarios 400/422/502/504 ni se interceptaron APIs. Los criterios sin estado reproducible se mantienen PARCIAL o PARCIAL con el intento y la causa.
- No se completo una auditoria automatica axe-core ni una prueba exhaustiva con lector de pantalla, teclado, contraste y zoom. Los PASS se limitan al criterio observable registrado y no certifican conformidad WCAG.
- Campos vacios y guiones de datos mock no se consideran defectos. Los campos no disponibles limitan la verificacion cuando el criterio exige su contenido.
- No se acredita exploracion de todos los controles auxiliares (Notificaciones, Centro de ayuda, ajustes de accesibilidad). La cobertura acreditada son las superficies y acciones documentadas.
- El Excel se leyo y filtro localmente; no se cargo al sitio ni se entrego completo al agente del navegador. No se modificaron fuente, automatizacion ni Excel.
