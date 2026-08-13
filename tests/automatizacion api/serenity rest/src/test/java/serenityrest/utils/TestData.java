package serenityrest.utils;

import java.util.Map;

/**
 * TestData — Everest / Grupo Aval
 * Fachada delgada sobre DataDrivenExcelReader: headers, payloads y resultados
 * esperados viven SIEMPRE en datadriven.xlsx, nunca hardcodeados aquí.
 *
 * TX-01  retiro                      POST /api/v1/pagos/retiro
 * TX-02  deposito                    POST /api/v1/pagos/deposito
 * TX-03  consultaFactura/pagoFactura POST /everest/orq/.../consulta y POST /api/v1/pagos/pago-factura
 * TX-04  pagoObligacion              POST /api/v1/pagos/pago-obligaciones
 */
public final class TestData {

    private TestData() {}

    // =========================================================================
    // TX-01 — Retiro de efectivo (OTP)
    // =========================================================================

    public static Map<String, String> retiroHeaders(int caso) {
        return DataDrivenExcelReader.retiroHeaders(caso);
    }

    public static Map<String, Object> retiroOtpPayload(int caso) {
        return DataDrivenExcelReader.retiroPayload(caso);
    }

    public static Map<String, String> retiroExpected(int caso) {
        return DataDrivenExcelReader.retiroExpected(caso);
    }

    // =========================================================================
    // TX-02 — Depósitos y consignaciones (Efectivo)
    // =========================================================================

    public static Map<String, String> depositoHeaders(int caso) {
        return DataDrivenExcelReader.depositoHeaders(caso);
    }

    public static Map<String, Object> depositoPayload(int caso) {
        return DataDrivenExcelReader.depositoPayload(caso);
    }

    public static Map<String, String> depositoExpected(int caso) {
        return DataDrivenExcelReader.depositoExpected(caso);
    }

    // =========================================================================
    // TX-03 Paso 1 — Consulta factura (orquestador Everest)
    // Ejecutar SIEMPRE antes de pagoFacturaPayload() en el flujo TX-03.
    // =========================================================================

    public static Map<String, String> consultaFacturaHeaders(int caso) {
        return DataDrivenExcelReader.consultaFacturaHeaders(caso);
    }

    public static Map<String, Object> consultaFacturaPayload(int caso) {
        return DataDrivenExcelReader.consultaFacturaPayload(caso);
    }

    public static Map<String, String> consultaFacturaExpected(int caso) {
        return DataDrivenExcelReader.consultaFacturaExpected(caso);
    }

    // =========================================================================
    // TX-03 Paso 2 — Recaudo de convenios / pago de factura (Efectivo)
    // =========================================================================

    public static Map<String, String> pagoFacturaHeaders(int caso) {
        return DataDrivenExcelReader.pagoFacturaHeaders(caso);
    }

    public static Map<String, Object> pagoFacturaPayload(int caso) {
        return DataDrivenExcelReader.pagoFacturaPayload(caso);
    }

    public static Map<String, String> pagoFacturaExpected(int caso) {
        return DataDrivenExcelReader.pagoFacturaExpected(caso);
    }

    // =========================================================================
    // TX-04 — Pago de obligaciones y Tarjeta de Crédito Aval (Efectivo)
    // =========================================================================

    public static Map<String, String> pagoObligacionHeaders(int caso) {
        return DataDrivenExcelReader.pagoObligacionHeaders(caso);
    }

    public static Map<String, Object> pagoObligacionPayload(int caso) {
        return DataDrivenExcelReader.pagoObligacionPayload(caso);
    }

    public static Map<String, String> pagoObligacionExpected(int caso) {
        return DataDrivenExcelReader.pagoObligacionExpected(caso);
    }

    // ── Utilidad: nombre único para datos de prueba ───────────────────────────

    public static String uniqueName(String prefix) {
        return prefix + "-" + System.currentTimeMillis();
    }
}
