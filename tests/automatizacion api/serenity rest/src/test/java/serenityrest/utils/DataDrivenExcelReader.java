package serenityrest.utils;

import java.io.IOException;
import java.io.InputStream;
import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.DataFormatter;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.ss.usermodel.WorkbookFactory;

/**
 * Lee el workbook datadriven.xlsx y reconstruye, por caso, el payload, los
 * headers y el resultado esperado usados por las pruebas. Las columnas con
 * prefijo "header." y "expected." se extraen aparte del body de la petición.
 * La hoja recaudo comparte consulta_factura y pago_factura por prefijo de columna.
 */
public final class DataDrivenExcelReader {

    private static final Path WORKBOOK_PATH = Paths.get(
        "src", "test", "resources", "datadriven", "datadriven.xlsx"
    );
    private static final DataFormatter DATA_FORMATTER = new DataFormatter(Locale.US);
    private static final Pattern PATH_SEGMENT = Pattern.compile("([^\\[\\]]+)(?:\\[(\\d+)\\])?");
    private static final String HEADER_NODE = "header";
    private static final String EXPECTED_NODE = "expected";

    // Caches indexados por (RequestType, caso) — el número de caso es el selector maestro
    private static final Map<RequestType, Map<Integer, Map<String, Object>>> ALL_PAYLOADS;
    private static final Map<RequestType, Map<Integer, Map<String, String>>> ALL_HEADERS;
    private static final Map<RequestType, Map<Integer, Map<String, String>>> ALL_EXPECTED;

    static {
        LoadedWorkbook loaded = loadAllPayloads();
        ALL_PAYLOADS = loaded.payloads();
        ALL_HEADERS = loaded.headers();
        ALL_EXPECTED = loaded.expected();
    }

    private DataDrivenExcelReader() {}

    public static Map<String, Object> retiroPayload(int caso) {
        return payloadFor(RequestType.RETIRO, caso);
    }

    public static Map<String, String> retiroHeaders(int caso) {
        return headersFor(RequestType.RETIRO, caso);
    }

    public static Map<String, String> retiroExpected(int caso) {
        return expectedFor(RequestType.RETIRO, caso);
    }

    public static Map<String, Object> depositoPayload(int caso) {
        return payloadFor(RequestType.DEPOSITO, caso);
    }

    public static Map<String, String> depositoHeaders(int caso) {
        return headersFor(RequestType.DEPOSITO, caso);
    }

    public static Map<String, String> depositoExpected(int caso) {
        return expectedFor(RequestType.DEPOSITO, caso);
    }

    public static Map<String, Object> consultaFacturaPayload(int caso) {
        return payloadFor(RequestType.CONSULTA_FACTURA, caso);
    }

    public static Map<String, String> consultaFacturaHeaders(int caso) {
        return headersFor(RequestType.CONSULTA_FACTURA, caso);
    }

    public static Map<String, String> consultaFacturaExpected(int caso) {
        return expectedFor(RequestType.CONSULTA_FACTURA, caso);
    }

    public static Map<String, Object> pagoFacturaPayload(int caso) {
        return payloadFor(RequestType.PAGO_FACTURA, caso);
    }

    public static Map<String, String> pagoFacturaHeaders(int caso) {
        return headersFor(RequestType.PAGO_FACTURA, caso);
    }

    public static Map<String, String> pagoFacturaExpected(int caso) {
        return expectedFor(RequestType.PAGO_FACTURA, caso);
    }

    public static Map<String, Object> pagoObligacionPayload(int caso) {
        return payloadFor(RequestType.PAGO_OBLIGACIONES, caso);
    }

    public static Map<String, String> pagoObligacionHeaders(int caso) {
        return headersFor(RequestType.PAGO_OBLIGACIONES, caso);
    }

    public static Map<String, String> pagoObligacionExpected(int caso) {
        return expectedFor(RequestType.PAGO_OBLIGACIONES, caso);
    }

    // ── Oficinas AVV ──────────────────────────────────────────────────────────

    public static Map<String, Object> avvConsultaClientePayload(int caso) {
        return payloadFor(RequestType.AVV_CONSULTA_CLIENTE, caso);
    }

    public static Map<String, String> avvConsultaClienteHeaders(int caso) {
        return headersFor(RequestType.AVV_CONSULTA_CLIENTE, caso);
    }

    public static Map<String, String> avvConsultaClienteExpected(int caso) {
        return expectedFor(RequestType.AVV_CONSULTA_CLIENTE, caso);
    }

    public static Map<String, Object> avvConsultaProductosPayload(int caso) {
        return payloadFor(RequestType.AVV_CONSULTA_PRODUCTOS, caso);
    }

    public static Map<String, String> avvConsultaProductosHeaders(int caso) {
        return headersFor(RequestType.AVV_CONSULTA_PRODUCTOS, caso);
    }

    public static Map<String, String> avvConsultaProductosExpected(int caso) {
        return expectedFor(RequestType.AVV_CONSULTA_PRODUCTOS, caso);
    }

    public static Map<String, Object> avvCarteraDetalladaPayload(int caso) {
        return payloadFor(RequestType.AVV_CARTERA_DETALLADA, caso);
    }

    public static Map<String, String> avvCarteraDetalladaHeaders(int caso) {
        return headersFor(RequestType.AVV_CARTERA_DETALLADA, caso);
    }

    public static Map<String, String> avvCarteraDetalladaExpected(int caso) {
        return expectedFor(RequestType.AVV_CARTERA_DETALLADA, caso);
    }

    public static Map<String, Object> avvTcDetalladaPayload(int caso) {
        return payloadFor(RequestType.AVV_TC_DETALLADA, caso);
    }

    public static Map<String, String> avvTcDetalladaHeaders(int caso) {
        return headersFor(RequestType.AVV_TC_DETALLADA, caso);
    }

    public static Map<String, String> avvTcDetalladaExpected(int caso) {
        return expectedFor(RequestType.AVV_TC_DETALLADA, caso);
    }

    public static Map<String, Object> avvCdtDetalladoPayload(int caso) {
        return payloadFor(RequestType.AVV_CDT_DETALLADO, caso);
    }

    public static Map<String, String> avvCdtDetalladoHeaders(int caso) {
        return headersFor(RequestType.AVV_CDT_DETALLADO, caso);
    }

    public static Map<String, String> avvCdtDetalladoExpected(int caso) {
        return expectedFor(RequestType.AVV_CDT_DETALLADO, caso);
    }

    // ── Oficinas BDB ──────────────────────────────────────────────────────────

    public static Map<String, Object> bdbConsultaGeneralPayload(int caso) {
        return payloadFor(RequestType.BDB_CONSULTA_GENERAL, caso);
    }

    public static Map<String, String> bdbConsultaGeneralHeaders(int caso) {
        return headersFor(RequestType.BDB_CONSULTA_GENERAL, caso);
    }

    public static Map<String, String> bdbConsultaGeneralExpected(int caso) {
        return expectedFor(RequestType.BDB_CONSULTA_GENERAL, caso);
    }

    public static Map<String, Object> bdbCarteraDetalladaPayload(int caso) {
        return payloadFor(RequestType.BDB_CARTERA_DETALLADA, caso);
    }

    public static Map<String, String> bdbCarteraDetalladaHeaders(int caso) {
        return headersFor(RequestType.BDB_CARTERA_DETALLADA, caso);
    }

    public static Map<String, String> bdbCarteraDetalladaExpected(int caso) {
        return expectedFor(RequestType.BDB_CARTERA_DETALLADA, caso);
    }

    public static Map<String, Object> bdbTcDetalladaPayload(int caso) {
        return payloadFor(RequestType.BDB_TC_DETALLADA, caso);
    }

    public static Map<String, String> bdbTcDetalladaHeaders(int caso) {
        return headersFor(RequestType.BDB_TC_DETALLADA, caso);
    }

    public static Map<String, String> bdbTcDetalladaExpected(int caso) {
        return expectedFor(RequestType.BDB_TC_DETALLADA, caso);
    }

    public static Map<String, Object> bdbCdtDetalladoPayload(int caso) {
        return payloadFor(RequestType.BDB_CDT_DETALLADO, caso);
    }

    public static Map<String, String> bdbCdtDetalladoHeaders(int caso) {
        return headersFor(RequestType.BDB_CDT_DETALLADO, caso);
    }

    public static Map<String, String> bdbCdtDetalladoExpected(int caso) {
        return expectedFor(RequestType.BDB_CDT_DETALLADO, caso);
    }

    public static Map<String, Object> officePayload(String sheetName, int caso) {
        return payloadFor(requestType(sheetName), caso);
    }

    public static Map<String, String> officeHeaders(String sheetName, int caso) {
        return headersFor(requestType(sheetName), caso);
    }

    public static Map<String, String> officeExpected(String sheetName, int caso) {
        return expectedFor(requestType(sheetName), caso);
    }

    private static RequestType requestType(String sheetName) {
        for (RequestType type : RequestType.values()) {
            if (type.sheetName.equals(sheetName)) {
                return type;
            }
        }
        throw new IllegalArgumentException("Hoja de Oficinas no soportada: " + sheetName);
    }

    private static Map<String, Object> payloadFor(RequestType requestType, int caso) {
        Map<String, Object> payload = lookup(ALL_PAYLOADS, requestType, caso);
        return deepCopyMap(payload);
    }

    private static Map<String, String> headersFor(RequestType requestType, int caso) {
        return new LinkedHashMap<>(lookup(ALL_HEADERS, requestType, caso));
    }

    private static Map<String, String> expectedFor(RequestType requestType, int caso) {
        return new LinkedHashMap<>(lookup(ALL_EXPECTED, requestType, caso));
    }

    private static <V> V lookup(Map<RequestType, Map<Integer, V>> source, RequestType requestType, int caso) {
        Map<Integer, V> byCase = source.get(requestType);
        if (byCase == null) {
            throw new IllegalStateException("No existe informaci\u00f3n configurada para " + requestType);
        }
        V value = byCase.get(caso);
        if (value == null) {
            throw new IllegalStateException(
                "No existe el caso " + caso + " para " + requestType + ". Casos disponibles: " + byCase.keySet()
            );
        }
        return value;
    }

    private static LoadedWorkbook loadAllPayloads() {
        EnumMap<RequestType, Map<Integer, Map<String, Object>>> payloads = new EnumMap<>(RequestType.class);
        EnumMap<RequestType, Map<Integer, Map<String, String>>> headers = new EnumMap<>(RequestType.class);
        EnumMap<RequestType, Map<Integer, Map<String, String>>> expected = new EnumMap<>(RequestType.class);

        try (InputStream inputStream = Files.newInputStream(WORKBOOK_PATH);
             Workbook workbook = WorkbookFactory.create(inputStream)) {
            for (RequestType requestType : RequestType.values()) {
                SheetData sheetData = readSheetData(workbook, requestType);
                payloads.put(requestType, sheetData.payloads());
                headers.put(requestType, sheetData.headers());
                expected.put(requestType, sheetData.expected());
            }
            return new LoadedWorkbook(payloads, headers, expected);
        } catch (IOException exception) {
            throw new IllegalStateException(
                "No fue posible leer el workbook datadriven: " + WORKBOOK_PATH.toAbsolutePath(),
                exception
            );
        }
    }

    private static SheetData readSheetData(Workbook workbook, RequestType requestType) {
        Sheet sheet = workbook.getSheet(requestType.sheetName);
        if (sheet == null) {
            throw new IllegalStateException("No existe la hoja '" + requestType.sheetName + "' en datadriven.xlsx");
        }

        Map<Integer, String> headerColumns = headersOf(sheet.getRow(0));
        Integer casoCol = casoColumn(headerColumns);
        LinkedHashMap<Integer, Map<String, Object>> byCasePayload = new LinkedHashMap<>();
        LinkedHashMap<Integer, Map<String, String>> byCaseHeaders = new LinkedHashMap<>();
        LinkedHashMap<Integer, Map<String, String>> byCaseExpected = new LinkedHashMap<>();

        for (int rowIndex = 1; rowIndex <= sheet.getLastRowNum(); rowIndex++) {
            Row row = sheet.getRow(rowIndex);
            if (row == null) {
                continue;
            }

            // La hoja 'recaudo' trae consulta_factura y pago_factura en la misma fila,
            // separados por prefijo de columna (no por fila) — filtrado en flattenedValues.
            if (casoCol == null || cellText(row.getCell(casoCol)).isBlank()) {
                continue;
            }

            int caso;
            try {
                caso = (int) Double.parseDouble(cellText(row.getCell(casoCol)));
            } catch (NumberFormatException ignored) {
                continue;
            }

            Map<String, Object> flattened = flattenedValues(headerColumns, row, requestType);
            if (flattened.isEmpty()) {
                continue;
            }

            LinkedHashMap<String, Object> nested = new LinkedHashMap<>();
            for (Map.Entry<String, Object> entry : flattened.entrySet()) {
                putNestedValue(nested, entry.getKey(), entry.getValue());
            }

            byCaseHeaders.put(caso, toStringMap(nested.remove(HEADER_NODE)));
            byCaseExpected.put(caso, toStringMap(nested.remove(EXPECTED_NODE)));
            byCasePayload.put(caso, nested);
        }

        if (byCasePayload.isEmpty()) {
            throw new IllegalStateException(
                "No se encontraron filas con columna 'Caso' para " + requestType + " en la hoja '" + requestType.sheetName + "'"
            );
        }
        return new SheetData(byCasePayload, byCaseHeaders, byCaseExpected);
    }

    @SuppressWarnings("unchecked")
    private static Map<String, String> toStringMap(Object node) {
        LinkedHashMap<String, String> result = new LinkedHashMap<>();
        if (node instanceof Map<?, ?> mapNode) {
            for (Map.Entry<?, ?> entry : ((Map<String, Object>) mapNode).entrySet()) {
                result.put(String.valueOf(entry.getKey()), stringify(entry.getValue()));
            }
        }
        return result;
    }

    private static String stringify(Object value) {
        if (value == null) {
            return "";
        }
        if (value instanceof BigDecimal bigDecimal) {
            return bigDecimal.toPlainString();
        }
        return String.valueOf(value);
    }

    private record LoadedWorkbook(
        Map<RequestType, Map<Integer, Map<String, Object>>> payloads,
        Map<RequestType, Map<Integer, Map<String, String>>> headers,
        Map<RequestType, Map<Integer, Map<String, String>>> expected
    ) {}

    private record SheetData(
        Map<Integer, Map<String, Object>> payloads,
        Map<Integer, Map<String, String>> headers,
        Map<Integer, Map<String, String>> expected
    ) {}

    private static Map<Integer, String> headersOf(Row headerRow) {
        if (headerRow == null) {
            throw new IllegalStateException("El workbook datadriven.xlsx no tiene fila de encabezados");
        }

        LinkedHashMap<Integer, String> headers = new LinkedHashMap<>();
        for (int columnIndex = 0; columnIndex < headerRow.getLastCellNum(); columnIndex++) {
            String header = cellText(headerRow.getCell(columnIndex));
            if (!header.isBlank()) {
                headers.put(columnIndex, header);
            }
        }
        return headers;
    }

    private static Integer casoColumn(Map<Integer, String> headers) {
        for (Map.Entry<Integer, String> header : headers.entrySet()) {
            if ("caso".equalsIgnoreCase(header.getValue())) {
                return header.getKey();
            }
        }
        return null;
    }

    private static Map<String, Object> flattenedValues(
        Map<Integer, String> headers,
        Row row,
        RequestType requestType
    ) {
        LinkedHashMap<String, Object> flattened = new LinkedHashMap<>();

        for (Map.Entry<Integer, String> entry : headers.entrySet()) {
            String header = entry.getValue();
            if ("tipo_request".equalsIgnoreCase(header) || "caso".equalsIgnoreCase(header)) {
                continue;
            }

            if (requestType.rowSelector != null) {
                String requiredPrefix = requestType.rowSelector + ".";
                if (!header.startsWith(requiredPrefix)) {
                    continue;
                }
                header = header.substring(requiredPrefix.length());
            }

            String cellValue = cellText(row.getCell(entry.getKey()));
            if (cellValue.isBlank()) {
                continue;
            }
            flattened.put(header, parseValue(cellValue));
        }

        return flattened;
    }

    private static String cellText(Cell cell) {
        if (cell == null) {
            return "";
        }
        return DATA_FORMATTER.formatCellValue(cell).trim();
    }

    private static Object parseValue(String rawValue) {
        if (rawValue.matches("-?\\d+\\.\\d+")) {
            return new BigDecimal(rawValue);
        }

        if (rawValue.matches("-?\\d+")) {
            if (hasLeadingZeros(rawValue)) {
                return rawValue;
            }
            try {
                return Long.parseLong(rawValue);
            } catch (NumberFormatException ignored) {
                return rawValue;
            }
        }

        return rawValue;
    }

    private static boolean hasLeadingZeros(String value) {
        if (value.startsWith("-")) {
            return value.length() > 2 && value.charAt(1) == '0';
        }
        return value.length() > 1 && value.charAt(0) == '0';
    }

    private static void putNestedValue(Map<String, Object> root, String path, Object value) {
        String[] segments = path.split("\\.");
        Object current = root;

        for (int index = 0; index < segments.length; index++) {
            Matcher matcher = PATH_SEGMENT.matcher(segments[index]);
            if (!matcher.matches()) {
                throw new IllegalStateException("Path inválido en datadriven.xlsx: " + path);
            }

            String name = matcher.group(1);
            String listIndex = matcher.group(2);
            boolean lastSegment = index == segments.length - 1;

            if (listIndex == null) {
                Map<String, Object> currentMap = asMap(current);
                if (lastSegment) {
                    currentMap.put(name, value);
                } else {
                    Object next = currentMap.get(name);
                    if (!(next instanceof Map)) {
                        next = new LinkedHashMap<String, Object>();
                        currentMap.put(name, next);
                    }
                    current = next;
                }
                continue;
            }

            Map<String, Object> currentMap = asMap(current);
            List<Object> list = asList(currentMap.get(name));
            currentMap.put(name, list);

            int position = Integer.parseInt(listIndex);
            ensureSize(list, position + 1);

            if (lastSegment) {
                list.set(position, value);
            } else {
                Object next = list.get(position);
                if (!(next instanceof Map)) {
                    next = new LinkedHashMap<String, Object>();
                    list.set(position, next);
                }
                current = next;
            }
        }
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> asMap(Object value) {
        if (value instanceof Map<?, ?> mapValue) {
            return (Map<String, Object>) mapValue;
        }
        return new LinkedHashMap<>();
    }

    @SuppressWarnings("unchecked")
    private static List<Object> asList(Object value) {
        if (value instanceof List<?> listValue) {
            return (List<Object>) listValue;
        }
        return new ArrayList<>();
    }

    private static void ensureSize(List<Object> list, int size) {
        while (list.size() < size) {
            list.add(null);
        }
    }

    private static Map<String, Object> childMap(Map<String, Object> parent, String key) {
        Object child = parent.get(key);
        if (!(child instanceof Map<?, ?> childMap)) {
            throw new IllegalStateException("No existe el nodo esperado '" + key + "' en payload datadriven");
        }
        @SuppressWarnings("unchecked")
        Map<String, Object> result = (Map<String, Object>) childMap;
        return result;
    }

    private static Map<String, Object> deepCopyMap(Map<String, Object> source) {
        LinkedHashMap<String, Object> copy = new LinkedHashMap<>();
        for (Map.Entry<String, Object> entry : source.entrySet()) {
            copy.put(entry.getKey(), deepCopy(entry.getValue()));
        }
        return copy;
    }

    private static Object deepCopy(Object value) {
        if (value instanceof Map<?, ?> mapValue) {
            LinkedHashMap<String, Object> copy = new LinkedHashMap<>();
            for (Map.Entry<?, ?> entry : mapValue.entrySet()) {
                copy.put(String.valueOf(entry.getKey()), deepCopy(entry.getValue()));
            }
            return copy;
        }

        if (value instanceof List<?> listValue) {
            List<Object> copy = new ArrayList<>();
            for (Object item : listValue) {
                copy.add(deepCopy(item));
            }
            return copy;
        }

        return value;
    }

    private enum RequestType {
        RETIRO("retiro", null),
        DEPOSITO("deposito", null),
        CONSULTA_FACTURA("recaudo", "consulta_factura"),
        PAGO_FACTURA("recaudo", "pago_factura"),
        PAGO_OBLIGACIONES("pago_obligaciones", null),
        AVV_CONSULTA_CLIENTE("avv_consulta_cliente", null),
        AVV_CONSULTA_PRODUCTOS("avv_consulta_productos", null),
        AVV_CARTERA_DETALLADA("avv_cartera_detallada", null),
        AVV_TC_DETALLADA("avv_tc_detallada", null),
        AVV_CDT_DETALLADO("avv_cdt_detallado", null),
        BDB_CONSULTA_GENERAL("bdb_consulta_general", null),
        BDB_CARTERA_DETALLADA("bdb_cartera_detallada", null),
        BDB_TC_DETALLADA("bdb_tc_detallada", null),
        BDB_CDT_DETALLADO("bdb_cdt_detallado", null),
        AVV_BLOQUEO_TD("avv_bloqueo_td", null),
        BDB_BLOQUEO_TD("bdb_bloqueo_td", null),
        OCC_BLOQUEO_TD("occ_bloqueo_td", null),
        BPOP_BLOQUEO_TD("bpop_bloqueo_td", null),
        AVV_BLOQUEO_TC("avv_bloqueo_tc", null),
        BDB_BLOQUEO_TC("bdb_bloqueo_tc", null),
        OCC_BLOQUEO_TC("occ_bloqueo_tc", null),
        BPOP_BLOQUEO_TC("bpop_bloqueo_tc", null),
        AVV_ACTUALIZACION_DATOS("avv_actualizacion_datos", null),
        BDB_ACTUALIZACION_DATOS("bdb_actualizacion_datos", null),
        OCC_ACTUALIZACION_DATOS("occ_actualizacion_datos", null),
        BPOP_ACTUALIZACION_DATOS("bpop_actualizacion_datos", null),
        OCC_CONSULTA_CLIENTE("occ_consulta_cliente", null),
        OCC_CONSULTA_PRODUCTOS("occ_consulta_productos", null),
        OCC_CONSULTA_CDT("occ_consulta_cdt", null),
        BPOP_CONSULTA_CLIENTE("bpop_consulta_cliente", null),
        BPOP_CONSULTA_PRODUCTOS("bpop_consulta_productos", null),
        BPOP_CONSULTA_CARTERA("bpop_consulta_cartera", null),
        ORQ_CONSULTA_TC("orq_consulta_tc", null),
        ORQ_CONSULTA_CDT("orq_consulta_cdt", null);

        private final String sheetName;
        private final String rowSelector;

        RequestType(String sheetName, String rowSelector) {
            this.sheetName = sheetName;
            this.rowSelector = rowSelector;
        }
    }
}