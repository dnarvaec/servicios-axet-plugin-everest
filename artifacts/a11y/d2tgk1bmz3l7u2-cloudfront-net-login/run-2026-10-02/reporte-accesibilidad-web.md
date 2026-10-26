# Reporte de accesibilidad web

## Configuracion

- Fecha: 2026-10-02.
- URL inicial: https://d2tgk1bmz3l7u2.cloudfront.net/login.
- URL final: https://d2tgk1bmz3l7u2.cloudfront.net/asesor.
- Runtime: Playwright MCP; escritorio (sesion final 1366x768).
- Alcance: los 91 casos cuyo Labels contiene accesibilidad; WCAG A/AA, no AAA ni movil.
- Excel leido y filtrado localmente. El navegador recibio solo el JSON filtrado y datos CC; no se subio el libro.

## Resumen

- FAIL: 4; PASS: 30; PARCIAL: 26; NO VERIFICADO: 31.
- Se ejecuto el recorrido web real; no fue dry-run ni una revision exclusiva de documentos.
- Los resultados se limitan al mock y al criterio observable de cada caso. No se declara conformidad WCAG completa.

## Recorrido ejecutado

- Login con usuario de prueba y seleccion de AV Villas, Bogota, Popular y Occidente.
- Consulta con CC 12345678, 23456789, 34567890 y 45678901 para cada banco; 16 combinaciones. Check de validar identidad y cambio visible a Identidad validada.
- Cuentas, creditos, tarjetas de credito, inversiones/CDT: pestañas y detalles, con pools alternativos para categorias sin productos.
- Edicion cliente y gates de identidad; Guardar invalido en AVV para comprobar mensajes correctivos.
- Bloqueo y desbloqueo TD simulados por UI en cuatro bancos; activacion TD en AVV y OCC. Se registraron estados posteriores, no solo formularios previos.
- Bloqueo TC simulado posterior en AVV y OCC; en BDB/BPO se intentaron tarjetas alternativas pero figuraban bloqueadas en el reintento.
- Consulta CC 00000000 por banco: mensaje de cliente no encontrado con orientacion para corregir o cambiar entidad.

## Moneda, fechas y datos vacios

- Los importes visibles como $ 3.700.000, $ 4.200.000 y $ 15.000.000 son legibles en contexto colombiano. El punto de miles no es un defecto.
- Las fechas visibles 22/10/2026, 27/09/2026, 02/10/2026 y vencimiento 05/2034 son legibles en sus contextos; meses como Junio 2018 tambien.
- Campos vacios y guiones del mock no se reportan como fallos de accesibilidad por ausencia de datos. Tampoco se inventan valores para aprobar criterios incompletos.
- Las diferencias entre un saldo resumen y el total de una lista son un asunto distinto del formato monetario: se describe el alcance no explicado, sin atribuir error de calculo al backend.

## Hallazgos

- **EV-10 (HU-101-ADP-AVV-CLIENTE):** AVV muestra el nombre, pero concatena documento y código 11001 sin rótulo de ciudad; el código no es autoexplicativo. Correo y Teléfono residencia sí tienen rótulos en edición. No se acredita asociación programática ni lectura asistiva. [captura](screenshots/continuacion-avv-cc-2-cuenta.png) [captura](screenshots/continuacion-avv-cc-3-cuenta.png) [captura](screenshots/continuacion-avv-cc-4-cuenta.png)
- **EV-121 (HU-101-ADP-BPO):** BPO CC-4: el resumen dice Saldo disponible $5.300.000, mientras la lista dice Total disponible $8.100.000 con dos cuentas ($5.300.000 y $2.800.000). Falta explicar el alcance de ambos totales; inconsistencia de claridad, no prueba de error del backend. [captura](screenshots/continuacion-bpo-cc-4-credito.png) [captura](screenshots/continuacion-bpo-cc-4-tc.png) [captura](screenshots/continuacion-bpo-cc-4-cdt.png)
- **EV-128 (HU-101-ADP-OCC-CLIENTE):** OCC: el encabezado concatena el documento con 10010 sin rótulo ni nombre de localidad; el código no explica su significado. Contacto rotulado en edición no subsana esa ambigüedad de datos personales. [captura](screenshots/continuacion-occ-cc1-cliente.png) [captura](screenshots/continuacion-occ-cc1-edicion.png)
- **EV-135 (HU-101-ADP-OCC):** OCC CC-4: Saldo disponible $2.100.000 en resumen frente a Total disponible $5.300.000 en la lista de dos cuentas ($2.100.000 y $3.200.000). Los textos no explican la diferencia de alcance; no se infiere fallo de cálculo bancario. [captura](screenshots/continuacion-occ-cc-4-credito.png) [captura](screenshots/continuacion-occ-cc-4-tc.png) [captura](screenshots/continuacion-occ-cc-4-cdt.png)

Los FAIL anteriores son discrepancias frente a criterios de claridad del Excel, no incumplimientos WCAG confirmados automaticamente.
- AVV: el correo invalido muestra aria-invalid=true, pero no se observo aria-describedby; la lectura asistiva del mensaje requiere comprobacion adicional.

## Evidencia y resultados

- [Listado completo de 91 casos](listado-resultados-casos.md).
- [Resultados estructurados](resultados-casos.json).
- [Registro del navegador](observaciones-navegador.json).
- [Transacciones posteriores](post-transacciones.json).
- [Validaciones UI](validaciones-ui.json).
- [Lista filtrada localmente](casos-accesibilidad-filtrados.json).
- [Confirmacion de desbloqueo AVV](screenshots/final-avv-desbloqueo-td.png).
- [Confirmacion de activacion AVV](screenshots/final-avv-activacion-td.png).
- [Confirmacion de bloqueo TC AVV](screenshots/final-avv-bloqueo-tc.png).
- Las capturas finales de OCC/TC y errores de cliente estan en la raiz de esta ejecucion; las de detalles y operaciones TD estan bajo screenshots.

## Limitaciones

- Solo interfaz web de escritorio; se observaron 1366x768 en la sesion final. No se realizaron pruebas de movil ni criterios AAA.
- Se consultaron cuatro bancos con las CC 12345678, 23456789, 34567890 y 45678901; los 16 gates alcanzaron Identidad validada. Es un check del mock, no autenticacion biometrica real.
- Las transacciones simuladas posteriores usan CC 12345678. Bloqueo/desbloqueo TD observado en los cuatro bancos; activacion TD en AVV/OCC; bloqueo TC posterior confirmado en AVV/OCC.
- En BDB/BPO se intento la primera y luego la segunda TC: ambas figuraban Bloqueada en el reintento. No se atribuye una nueva confirmacion a esos bancos. Puede haber estado compartido del mock; no se certifica aislamiento por entidad.
- Se provoco consulta de cliente inexistente con CC 00000000 en los cuatro bancos. No equivale a errores de bloqueo, desbloqueo, activacion, cartera, TC o CDT.
- Se pulso Guardar con correo invalido y requeridos vacios en AVV: mensajes correctivos observados; no actualizacion valida guardada. Los demas bancos conservan el alcance documentado en cada caso.
- No se fabricaron errores bancarios 400/422/502/504 ni se interceptaron APIs. Los criterios sin estado reproducible se mantienen NO VERIFICADO o PARCIAL con el intento y la causa.
- No se completo una auditoria automatica axe-core ni una prueba exhaustiva con lector de pantalla, teclado, contraste y zoom. Los PASS se limitan al criterio observable registrado y no certifican conformidad WCAG.
- Campos vacios y guiones de datos mock no se consideran defectos. Los campos no disponibles limitan la verificacion cuando el criterio exige su contenido.
- No se acredita exploracion de todos los controles auxiliares (Notificaciones, Centro de ayuda, ajustes de accesibilidad). La cobertura acreditada son las superficies y acciones documentadas.
- El Excel se leyo y filtro localmente; no se cargo al sitio ni se entrego completo al agente del navegador. No se modificaron fuente, automatizacion ni Excel.

## Contrato de reporte

Se aplican los contratos de a11y-audit-foundation y a11y-report-normalization. Markdown UTF-8 normalizado, evidencia por banco y sin extrapolar errores de consulta a operaciones distintas.
