# Listado de resultados: HU-302 y HU-303

- Fecha: 2026-10-06.
- Sitio: https://d2tgk1bmz3l7u2.cloudfront.net/login.
- Entorno: mock web, escritorio 1366 x 768; A/AA; sin móvil.
- Casos extraídos localmente: 12. PASS: 6; FAIL: 0; NO VERIFICADO: 6.

| Caso | HU | Resultado | Detalle |
|---|---|---|---|
| EV-298 | HU-302-ADP-AVV | PASS | AVV, CC Pool A: tras el gate de identidad, desbloqueo confirmado. Tarjeta `****2907` en estado Activa; historial «Desbloqueada por user». [antes](screenshots/avv-ev298-estado-td-bloqueada-pin.png) [después](screenshots/avv-ev298-desbloqueo-confirmado.png) |
| EV-299 | HU-302-ADP-AVV | NO VERIFICADO | Se intentó el trigger CC `11111111` por búsqueda normal; la UI respondió «Cliente no encontrado» antes del flujo de desbloqueo. No se observó mensaje de negocio 422. [captura](screenshots/avv-negativo-cc11111111-cliente-no-encontrado.png) |
| EV-307 | HU-302-ADP-BDB | PASS | BDB, CC Pool A: desbloqueo confirmado después de validar identidad. Estado Activa, historial «Desbloqueada por user» y confirmación «Tarjeta ****2907 ha sido desbloqueada». [captura](screenshots/bbog-ev307-desbloqueo-confirmado.png) |
| EV-308 | HU-302-ADP-BDB | NO VERIFICADO | Se intentó CC `11111111` por UI y la búsqueda terminó en «Cliente no encontrado»; el panel normal sólo habilita desbloqueo para una tarjeta elegible. No se observó el rechazo 409. [trigger](screenshots/bbog-ev308-trigger-cc11111111-cliente-no-encontrado.png) [estados BDB](screenshots/bbog-cc-pool-b-estados-de-tarjeta.png) |
| EV-316 | HU-302-ADP-BPO | PASS | BPO, CC Pool A: el estado previo se expone como «Bloqueada» y «Bloqueo por intentos fallidos»; la acción se describe como «Desbloquear tarjeta y restablecer sus servicios», sin depender de `ErrorPinAttempt`. [captura](screenshots/bpop-ev316-estado-pin-y-opciones.png) |
| EV-317 | HU-302-ADP-BPO | NO VERIFICADO | Se recorrió el desbloqueo visible, se confirmó identidad y la UI devolvió éxito («Tarjeta ****2907 ha sido desbloqueada»), no un rechazo con mensaje de negocio. El trigger SOAP no es seleccionable por controles visibles. [captura](screenshots/bpop-ev317-ui-responde-exito-no-error.png) |
| EV-324 | HU-302-ADP-OCC | PASS | OCC, CC Pool A: desbloqueo confirmado. Estado Activa, historial «Desbloqueada por user» y confirmación «Tarjeta ****2907 ha sido desbloqueada». [antes](screenshots/occ-ev324-estado-td-bloqueada-pin.png) [después](screenshots/occ-ev324-desbloqueo-confirmado.png) |
| EV-325 | HU-302-ADP-OCC | NO VERIFICADO | El desbloqueo visible para la tarjeta elegible terminó exitosamente; la UI no presentó el rechazo/RtaDesc HTTP 422 requerido por el caso. [resultado observado](screenshots/occ-ev324-desbloqueo-confirmado.png) |
| EV-333 | HU-303-ADP-AVV | PASS | AVV, CC Pool A: la tarjeta `****3325` pasó de Pendiente de Activación a Activa después del gate de identidad; el número permaneció enmascarado. [captura](screenshots/avv-ev333-activacion-confirmada.png) |
| EV-334 | HU-303-ADP-AVV | NO VERIFICADO | Se intentó el trigger CC `00000000` por búsqueda normal; la UI respondió «Cliente no encontrado» antes de activar. No se alcanzaron los estados de error 422/502/504. [captura](screenshots/avv-ev334-trigger-cc00000000-cliente-no-encontrado.png) |
| EV-342 | HU-303-ADP-OCC | PASS | OCC, CC Pool A: la tarjeta `****3325` pasó de Pendiente de Activación a Activa tras confirmar identidad; permaneció enmascarada y dejó de ofrecer «Activar tarjeta». [captura](screenshots/occ-ev342-activacion-confirmada.png) |
| EV-343 | HU-303-ADP-OCC | NO VERIFICADO | El recorrido visible de activación OCC terminó en éxito; no se mostró RtaCod de rechazo ni mensaje de asociación incompleta. El trigger SOAP no está expuesto por la UI. [resultado observado](screenshots/occ-ev342-activacion-confirmada.png) |

Los estados NO VERIFICADO reflejan que no se alcanzó el error específico del caso después de intentar la ruta web normal y los triggers CC documentados. No equivalen a N/A o blocked ni confirman un defecto. Los campos vacíos del mock no se consideraron fallos; moneda y fechas visibles se revisaron manualmente y son legibles.
