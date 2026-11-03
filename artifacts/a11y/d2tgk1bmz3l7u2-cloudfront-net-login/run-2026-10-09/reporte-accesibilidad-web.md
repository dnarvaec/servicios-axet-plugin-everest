# Reporte de accesibilidad web: HU-302 y HU-303

## Metadatos

- Fecha: 2026-10-06.
- URL inicial: https://d2tgk1bmz3l7u2.cloudfront.net/login.
- URL final: https://d2tgk1bmz3l7u2.cloudfront.net/asesor.
- Runtime: Playwright MCP, Chromium; viewport escritorio 1366 x 768.
- Alcance: 12 casos etiquetados `accesibilidad` de HU-302/HU-303; web únicamente; criterios A/AA, sin AAA.
- Datos: extracción local de `casos de prueba/casos everest.xlsx`; referencia CC local `tests/Automatizacion api/serenity rest/src/test/resources/colecciones/mock-test-ref.html`. No se cargó el Excel al sitio.

## Resumen

- PASS: 6.
- FAIL: 0.
- NO VERIFICADO: 6.
- Casos cubiertos individualmente: EV-298, EV-299, EV-307, EV-308, EV-316, EV-317, EV-324, EV-325, EV-333, EV-334, EV-342 y EV-343.
- Resultado limitado a los estados visibles en el mock web; no constituye certificación WCAG global.

## Recorrido ejecutado

- Inicio de sesión con las credenciales proporcionadas, usadas sólo en el navegador y no persistidas.
- Selección de Banco de Bogotá, Banco Popular, Banco de Occidente y AV Villas.
- Consultas web con documento CC del Pool A (y Pool B para explorar alternativas BDB); se marcó «Verifica la identidad del cliente» en cada consulta ejecutada.
- Se inspeccionaron tarjetas débito; en las acciones que lo requerían se marcó «Confirmo que validé la identidad del cliente» y se confirmó la operación simulada.
- Desbloqueo confirmado para AVV, BDB, BPO y OCC. Activación confirmada para AVV y OCC.
- Se probaron los triggers CC `11111111` (desbloqueo) y `00000000` (activación) desde el formulario normal. La UI respondió «Cliente no encontrado» antes de llegar a las operaciones.
- Todas las mutaciones fueron interacciones de UI en el entorno mock autorizado; no se invocaron APIs directamente ni se alteró tráfico.

## Resultados por criterio

- EV-298, EV-307 y EV-324: PASS. La tarjeta pasó de «Bloqueada» por intentos fallidos a «Activa»; el historial muestra «Desbloqueada por user» y la UI presenta el final enmascarado `****2907`.
- EV-316: PASS. BPO identifica el estado como «Bloqueada» y «Bloqueo por intentos fallidos», y explica la acción «Desbloquear tarjeta y restablecer sus servicios».
- EV-333 y EV-342: PASS. La tarjeta `****3325` pasó de «Pendiente de Activación» a «Activa»; desapareció la acción «Activar tarjeta». El número permaneció enmascarado.
- EV-299, EV-308 y EV-334: NO VERIFICADO. Los triggers CC probados fueron detenidos por la búsqueda con «Cliente no encontrado»; no se observó el rechazo de desbloqueo/activación ni los mensajes HTTP 422/409 esperados.
- EV-317 y EV-325: NO VERIFICADO. El flujo normal con una tarjeta elegible concluyó en desbloqueo exitoso, no en el rechazo de negocio esperado; por ello no acredita el contenido de error.
- EV-343: NO VERIFICADO. La UI de OCC ejecutó la activación exitosa; el rechazo SOAP/RtaCod requerido no se puede seleccionar mediante un control visible.

Los resultados NO VERIFICADO reflejan la limitación concreta del flujo web observado. No se marcaron casos como N/A o blocked, ni se convirtieron los éxitos de operación en evidencia de errores.

## Moneda, fechas y datos vacíos

- Importes como `$ 3.350.000`, `$ 3.700.000` y `$ 10.100.000` se revisaron manualmente y son legibles en contexto colombiano; el punto como separador de miles no se reporta como defecto.
- Fechas como `10/08/2026` y vencimientos `05/2034` son legibles en su contexto.
- Los campos sin valor no se consideran defectos por sí mismos: corresponden al mock y no aportan evidencia de un problema de accesibilidad.

## Evidencia

- [Listado individual de casos](listado-resultados-casos.md).
- [Resultados estructurados](resultados-casos.json).
- Desbloqueo AVV: [antes](screenshots/avv-ev298-estado-td-bloqueada-pin.png), [después](screenshots/avv-ev298-desbloqueo-confirmado.png).
- Desbloqueo BDB: [estado de tarjetas](screenshots/bbog-cc-a-tarjetas-antes-de-desbloquear.png), [confirmación](screenshots/bbog-ev307-desbloqueo-confirmado.png).
- Estado previo BPO: [EV-316](screenshots/bpop-ev316-estado-pin-y-opciones.png); resultado del flujo de desbloqueo: [EV-317](screenshots/bpop-ev317-ui-responde-exito-no-error.png).
- Desbloqueo OCC: [antes](screenshots/occ-ev324-estado-td-bloqueada-pin.png), [después](screenshots/occ-ev324-desbloqueo-confirmado.png).
- Activación AVV: [EV-333](screenshots/avv-ev333-activacion-confirmada.png).
- Activación OCC: [EV-342](screenshots/occ-ev342-activacion-confirmada.png).
- Triggers no alcanzables desde búsqueda: [AVV, CC 11111111](screenshots/avv-negativo-cc11111111-cliente-no-encontrado.png), [AVV, CC 00000000](screenshots/avv-ev334-trigger-cc00000000-cliente-no-encontrado.png), [BDB, CC 11111111](screenshots/bbog-ev308-trigger-cc11111111-cliente-no-encontrado.png).
- [Selector bancario con BDB seleccionado](screenshots/bancos-seleccionables-bbog-activo.png).

## Limitaciones

- La UI no expuso controles para elegir los errores bancarios específicos (422/409/502/504) ni para suministrar RqUID, RtaCod u otros discriminadores internos. No se llamó a APIs ni se fabricaron respuestas.
- El trigger de documento `11111111` y el de `00000000` terminaron en la búsqueda de cliente inexistente; esos resultados no sustituyen una respuesta de error de desbloqueo o activación.
- El check «Identidad validada» es una confirmación funcional del mock, no una validación biométrica real.
- No se ejecutaron recorridos móviles ni una auditoría axe completa; el alcance es la ejecución de los 12 casos solicitados en escritorio.
- La delegación al agente no produjo un resumen utilizable; la ejecución y las verificaciones reportadas se completaron con Playwright MCP en esta sesión.

## Formato y datos

Se revisaron manualmente los formatos de moneda y fecha. Los resultados por caso mantienen el estado observado, con evidencia por banco; la lista se limita exactamente a las 12 filas filtradas localmente.
