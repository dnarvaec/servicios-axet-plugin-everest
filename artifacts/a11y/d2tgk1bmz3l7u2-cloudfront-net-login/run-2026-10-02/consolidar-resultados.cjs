const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

const root = __dirname;
const readJson = name => JSON.parse(fs.readFileSync(path.join(root, name), 'utf8'));
const audit = readJson('resultados-casos.json');
const sourceCases = readJson('casos-accesibilidad-filtrados.json').cases;
const transactions = readJson('post-transacciones.json');
const checks = readJson('validaciones-ui.json');
const results = new Map(audit.results.map(result => [result.caso, result]));

function relativeEvidence(filename) {
    const normalized = filename.replaceAll('\\', '/');
    const relative = normalized.includes('/run-2026-10-02/')
        ? normalized.split('/run-2026-10-02/')[1]
        : normalized;
    assert.ok(fs.existsSync(path.join(root, relative)), `Missing evidence: ${relative}`);
    return relative;
}

function approve(caseId, detail, record) {
    const result = results.get(caseId);
    assert.ok(result, `Unknown case: ${caseId}`);
    result.resultado = 'PASS';
    result.detalle = detail;
    result.intento = record.attempt;
    result.alcance = 'Resultado observado en la interfaz web del mock; no verifica el adaptador bancario ni certifica conformidad WCAG.';
    result.coberturaLimitada = false;
    result.evidencia.push({
        bank: record.bank,
        surface: record.operation,
        screenshot: relativeEvidence(record.screenshot),
        textFragments: [record.message || record.text],
        phase: 'postaction'
    });
}

const bankCases = {
    BDB: {block: 'EV-185', masked: 'EV-187', unlock: 'EV-307'},
    BPO: {block: 'EV-198', masked: 'EV-200'},
    OCC: {block: 'EV-210', masked: 'EV-212', unlock: 'EV-324', activation: 'EV-342', credit: 'EV-285'}
};
for (const record of transactions) {
    const mapping = bankCases[record.bank];
    if (!mapping || !/estado-posterior|confirmado-ui-mock/.test(record.result)) continue;
    if (record.operation === 'bloqueo-td') {
        assert.ok(record.text.includes('ha sido bloqueada'));
        approve(mapping.block, `${record.bank}: se confirmo el bloqueo SIMULADO por UI. Mensaje "Tarjeta ****8841 ha sido bloqueada", estado Bloqueada e instruccion para solicitar nueva tarjeta. No se sustituyo la confirmacion por una consulta de cliente.`, record);
        approve(mapping.masked, `${record.bank}: el panel posterior muestra tarjeta enmascarada, estado Bloqueada e historial "Bloqueada por user". Los datos son legibles y protegidos en la interfaz; no se evaluan logs bancarios.`, record);
    }
    if (record.operation === 'desbloqueo-td' && mapping.unlock) {
        assert.ok(record.text.includes('ha sido desbloqueada'));
        approve(mapping.unlock, `${record.bank}: la UI del mock confirma "Tarjeta ****2907 ha sido desbloqueada", muestra Activa e historial "Desbloqueada por user". Resultado posterior observado.`, record);
    }
    if (record.operation === 'activacion-td' && mapping.activation) {
        assert.ok(record.text.includes('3325') && record.text.includes('Activa'));
        approve(mapping.activation, `${record.bank}: se confirmo la activacion SIMULADA de la tarjeta enmascarada 3325. Cambio de Pendiente de Activacion a Activa; desaparece Activar tarjeta y aparece Bloquear. No se infiere respuesta SOAP ni NumeroTarjetaRealce del backend.`, record);
    }
    if (record.operation === 'bloqueo-tc' && mapping.credit) {
        assert.ok(record.text.includes('ha sido bloqueada'));
        approve(mapping.credit, `${record.bank}: se selecciono una TC activa y se confirmo el bloqueo SIMULADO. La UI muestra "Tarjeta ...5678 ha sido bloqueada" y estado Bloqueada.`, record);
    }
}

const avvRecords = [
    {operation: 'bloqueo-td', file: 'final-avv-bloqueo-td.png', ids: ['EV-173', 'EV-175'], message: 'Tarjeta ****8841 ha sido bloqueada', detail: 'AVV: bloqueo SIMULADO confirmado por UI, tarjeta 8841 enmascarada, estado Bloqueada e historial Bloqueada por user. Confirmacion legible e instruccion para solicitar una nueva tarjeta.'},
    {operation: 'desbloqueo-td', file: 'final-avv-desbloqueo-td.png', ids: ['EV-298'], message: 'Tarjeta ****2907 ha sido desbloqueada', detail: 'AVV: despues de confirmar el desbloqueo SIMULADO, la UI muestra Tarjeta ****2907 ha sido desbloqueada, estado Activa e historial Desbloqueada por user.'},
    {operation: 'activacion-td', file: 'final-avv-activacion-td.png', ids: ['EV-333'], message: 'Tarjeta ****3325 ha sido activada', detail: 'AVV: despues de confirmar la activacion SIMULADA, la UI muestra Tarjeta ****3325 ha sido activada y estado Activa. No se infiere una respuesta del adaptador.'},
    {operation: 'bloqueo-tc', file: 'final-avv-bloqueo-tc.png', ids: ['EV-288'], message: 'Tarjeta ...5678 ha sido bloqueada', detail: 'AVV: bloqueo TC SIMULADO confirmado por UI, con mensaje ha sido bloqueada y estado Bloqueada. Se verifico visualmente en la captura posterior.'}
];
for (const record of avvRecords) {
    for (const caseId of record.ids) {
        approve(caseId, record.detail, {
            bank: 'AVV', operation: record.operation, message: record.message,
            screenshot: `screenshots/${record.file}`,
            attempt: 'UI normal del mock, check de identidad y confirmacion; captura posterior inspeccionada visualmente.'
        });
    }
}
for (const record of checks) {
    if (record.operation === 'consulta-cliente-error') {
        const caseId = {AVV: 'EV-11', BPO: 'EV-115', OCC: 'EV-129'}[record.bank];
        if (caseId) approve(caseId, `${record.bank}: CC 00000000 por UI produce "${record.text}". El mensaje identifica el problema y ofrece verificar datos o intentar otra entidad. Es error de consulta cliente, no de bloqueo ni actualizacion.`, record);
    }
    if (record.operation === 'validacion-form-correo-invalido') {
        approve('EV-221', `AVV: se pulso Guardar con correo invalido y campos requeridos vacios. La UI indica "${record.text}"; el formulario permanece abierto y el correo tiene aria-invalid=true. No se guardo una actualizacion valida. La asociacion programatica del mensaje no queda acreditada (aria-describedby ausente).`, record);
    }
}

assert.equal(results.size, 91);
assert.deepEqual([...results.keys()].sort(), sourceCases.map(item => item['Issue Key']).sort());
assert.ok(sourceCases.every(item => item.Labels.toLowerCase().includes('accesibilidad')));
audit.summary = [...results.values()].reduce((counts, result) => {
    counts[result.resultado] = (counts[result.resultado] || 0) + 1;
    return counts;
}, {});
audit.results = [...results.values()];
audit.status = 'completed-desktop-run-partial-criteria';
audit.postTransactions = transactions;
audit.additionalChecks = checks;
audit.avvPostTransactions = avvRecords;
audit.source.sourceFilesRead = true;
audit.source.sourceOfTruth = 'Extraccion local del Excel, registro Playwright MCP, capturas y mensajes posteriores de la UI del mock.';
audit.limitations = [
    'Solo interfaz web de escritorio; se observaron 1366x768 en la sesion final. No se realizaron pruebas de movil ni criterios AAA.',
    'Se consultaron cuatro bancos con las CC 12345678, 23456789, 34567890 y 45678901; los 16 gates alcanzaron Identidad validada. Es un check del mock, no autenticacion biometrica real.',
    'Las transacciones simuladas posteriores usan CC 12345678. Bloqueo/desbloqueo TD observado en los cuatro bancos; activacion TD en AVV/OCC; bloqueo TC posterior confirmado en AVV/OCC.',
    'En BDB/BPO se intento la primera y luego la segunda TC: ambas figuraban Bloqueada en el reintento. No se atribuye una nueva confirmacion a esos bancos. Puede haber estado compartido del mock; no se certifica aislamiento por entidad.',
    'Se provoco consulta de cliente inexistente con CC 00000000 en los cuatro bancos. No equivale a errores de bloqueo, desbloqueo, activacion, cartera, TC o CDT.',
    'Se pulso Guardar con correo invalido y requeridos vacios en AVV: mensajes correctivos observados; no actualizacion valida guardada. Los demas bancos conservan el alcance documentado en cada caso.',
    'No se fabricaron errores bancarios 400/422/502/504 ni se interceptaron APIs. Los criterios sin estado reproducible se mantienen NO VERIFICADO o PARCIAL con el intento y la causa.',
    'No se completo una auditoria automatica axe-core ni una prueba exhaustiva con lector de pantalla, teclado, contraste y zoom. Los PASS se limitan al criterio observable registrado y no certifican conformidad WCAG.',
    'Campos vacios y guiones de datos mock no se consideran defectos. Los campos no disponibles limitan la verificacion cuando el criterio exige su contenido.',
    'No se acredita exploracion de todos los controles auxiliares (Notificaciones, Centro de ayuda, ajustes de accesibilidad). La cobertura acreditada son las superficies y acciones documentadas.',
    'El Excel se leyo y filtro localmente; no se cargo al sitio ni se entrego completo al agente del navegador. No se modificaron fuente, automatizacion ni Excel.'
];

function evidenceLinks(result) {
    return [...new Set(result.evidencia.map(item => item.screenshot).filter(Boolean))]
        .filter(filename => fs.existsSync(path.join(root, filename)))
        .slice(-3).map(filename => `[captura](${filename})`).join(' ');
}
const counts = Object.entries(audit.summary).map(([name, count]) => `${name}: ${count}`).join('; ');
const rows = audit.results.map(result => `| ${result.caso} | ${result.hu} | ${result.resultado} | ${result.detalle.replaceAll('|', '/').replaceAll('\n', ' ')} ${evidenceLinks(result)} |`);
audit.listMarkdown = [
    '# Listado de resultados de accesibilidad web', '',
    '- Fecha: 2026-10-02.',
    '- Sitio: https://d2tgk1bmz3l7u2.cloudfront.net/login.',
    '- Entorno: mock web, escritorio; A/AA; sin movil.',
    `- Casos filtrados localmente: 91. ${counts}.`, '',
    'PASS indica cumplimiento del criterio observable en web. PARCIAL indica cobertura incompleta. NO VERIFICADO registra un estado no reproducido tras los intentos descritos; no es un defecto confirmado ni un PASS.', '',
    '| Caso | HU | Resultado | Detalle |', '|---|---|---|---|', ...rows, '',
    '## Alcance y limitaciones', '', ...audit.limitations.map(item => `- ${item}`), ''
].join('\n');
audit.reportMarkdown = [
    '# Reporte de accesibilidad web', '',
    '## Configuracion', '',
    '- Fecha: 2026-10-02.',
    '- URL inicial: https://d2tgk1bmz3l7u2.cloudfront.net/login.',
    '- URL final: https://d2tgk1bmz3l7u2.cloudfront.net/asesor.',
    '- Runtime: Playwright MCP; escritorio (sesion final 1366x768).',
    '- Alcance: los 91 casos cuyo Labels contiene accesibilidad; WCAG A/AA, no AAA ni movil.',
    '- Excel leido y filtrado localmente. El navegador recibio solo el JSON filtrado y datos CC; no se subio el libro.', '',
    '## Resumen', '', `- ${counts}.`,
    '- Se ejecuto el recorrido web real; no fue dry-run ni una revision exclusiva de documentos.',
    '- Los resultados se limitan al mock y al criterio observable de cada caso. No se declara conformidad WCAG completa.', '',
    '## Recorrido ejecutado', '',
    '- Login con usuario de prueba y seleccion de AV Villas, Bogota, Popular y Occidente.',
    '- Consulta con CC 12345678, 23456789, 34567890 y 45678901 para cada banco; 16 combinaciones. Check de validar identidad y cambio visible a Identidad validada.',
    '- Cuentas, creditos, tarjetas de credito, inversiones/CDT: pestañas y detalles, con pools alternativos para categorias sin productos.',
    '- Edicion cliente y gates de identidad; Guardar invalido en AVV para comprobar mensajes correctivos.',
    '- Bloqueo y desbloqueo TD simulados por UI en cuatro bancos; activacion TD en AVV y OCC. Se registraron estados posteriores, no solo formularios previos.',
    '- Bloqueo TC simulado posterior en AVV y OCC; en BDB/BPO se intentaron tarjetas alternativas pero figuraban bloqueadas en el reintento.',
    '- Consulta CC 00000000 por banco: mensaje de cliente no encontrado con orientacion para corregir o cambiar entidad.', '',
    '## Moneda, fechas y datos vacios', '',
    '- Los importes visibles como $ 3.700.000, $ 4.200.000 y $ 15.000.000 son legibles en contexto colombiano. El punto de miles no es un defecto.',
    '- Las fechas visibles 22/10/2026, 27/09/2026, 02/10/2026 y vencimiento 05/2034 son legibles en sus contextos; meses como Junio 2018 tambien.',
    '- Campos vacios y guiones del mock no se reportan como fallos de accesibilidad por ausencia de datos. Tampoco se inventan valores para aprobar criterios incompletos.',
    '- Las diferencias entre un saldo resumen y el total de una lista son un asunto distinto del formato monetario: se describe el alcance no explicado, sin atribuir error de calculo al backend.', '',
    '## Hallazgos', '',
    ...audit.results.filter(result => result.resultado === 'FAIL').map(result => `- **${result.caso} (${result.hu}):** ${result.detalle} ${evidenceLinks(result)}`), '',
    'Los FAIL anteriores son discrepancias frente a criterios de claridad del Excel, no incumplimientos WCAG confirmados automaticamente.',
    '- AVV: el correo invalido muestra aria-invalid=true, pero no se observo aria-describedby; la lectura asistiva del mensaje requiere comprobacion adicional.', '',
    '## Evidencia y resultados', '',
    '- [Listado completo de 91 casos](listado-resultados-casos.md).',
    '- [Resultados estructurados](resultados-casos.json).',
    '- [Registro del navegador](observaciones-navegador.json).',
    '- [Transacciones posteriores](post-transacciones.json).',
    '- [Validaciones UI](validaciones-ui.json).',
    '- [Lista filtrada localmente](casos-accesibilidad-filtrados.json).',
    '- [Confirmacion de desbloqueo AVV](screenshots/final-avv-desbloqueo-td.png).',
    '- [Confirmacion de activacion AVV](screenshots/final-avv-activacion-td.png).',
    '- [Confirmacion de bloqueo TC AVV](screenshots/final-avv-bloqueo-tc.png).',
    '- Las capturas finales de OCC/TC y errores de cliente estan en la raiz de esta ejecucion; las de detalles y operaciones TD estan bajo screenshots.', '',
    '## Limitaciones', '', ...audit.limitations.map(item => `- ${item}`), '',
    '## Contrato de reporte', '',
    'Se aplican los contratos de a11y-audit-foundation y a11y-report-normalization. Markdown UTF-8 normalizado, evidencia por banco y sin extrapolar errores de consulta a operaciones distintas.', ''
].join('\n');
audit.persistence = {status: 'normalized-utf8', reportFile: 'reporte-accesibilidad-web.md', listFile: 'listado-resultados-casos.md'};
audit.deliveryValidation = {caseIdsMatch: true, total: 91, excelUploaded: false, mobileTested: false, postactionEvidenceIncluded: true};
fs.writeFileSync(path.join(root, 'resultados-casos.json'), JSON.stringify(audit, null, 2) + '\n', 'utf8');
fs.writeFileSync(path.join(root, 'listado-resultados-casos.md'), audit.listMarkdown, 'utf8');
fs.writeFileSync(path.join(root, 'reporte-accesibilidad-web.md'), audit.reportMarkdown, 'utf8');
for (const name of ['listado-resultados-casos.md', 'reporte-accesibilidad-web.md']) {
    const markdown = fs.readFileSync(path.join(root, name), 'utf8');
    assert.ok(markdown.startsWith('# ') && markdown.includes('\n'));
    assert.ok(!markdown.includes('generic [ref=') && !markdown.includes('Pendiente de comprobacion UI'));
}
assert.equal(audit.listMarkdown.split('\n').filter(line => line.startsWith('| EV-')).length, 91);
console.log(JSON.stringify({total: 91, counts: audit.summary, evidenceFilesValidated: true, markdownNormalized: true}));