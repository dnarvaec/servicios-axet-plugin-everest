package serenityrest.utils;

/**
 * ApiEndpoints
 * ─────────────────────────────────────────────────────────────────────────────
 * Fuente de verdad única para URLs base y paths de endpoints.
 * NUNCA hardcodear URLs en Tasks, Interactions ni Step Definitions.
 *
 * PROYECTO : Everest — Automatización API Grupo Aval
 * HOST     : ver API_BASE_URL más abajo (única fuente; no duplicar el valor en comentarios)
 *
 * Transacciones cubiertas:
 *   TX-01  Retiro de efectivo (OTP)               X-RqUID: 001001
 *   TX-02  Depósitos y consignaciones (Efectivo)   X-RqUID: 002001
 *   TX-03  Recaudo de convenios (Efectivo)          X-RqUID: 003001
 *   TX-04  Pago de obligaciones y TC Aval (Efect.) X-RqUID: 004001
 *
 * Flujo TX-03 (dos pasos):
 *   1º Consultas.CONSULTA_FACTURA  (orquestador)
 *   2º Pagos.PAGO_FACTURA
 *
 * Flujo TX-04 (un paso directo):
 *   Pagos.PAGO_OBLIGACIONES
 * ─────────────────────────────────────────────────────────────────────────────
 */
public final class ApiEndpoints {

    private ApiEndpoints() {}

    // ── URL base — host compartido de todos los endpoints Everest/Aval ────────
    public static final String API_BASE_URL = "https://d2q3sea1wnkwiy.cloudfront.net";

    // ── Pagos — endpoints bajo /api/v1/pagos/ ─────────────────────────────────
    /**
     * Agrupa los paths del módulo de pagos (TX-01, TX-02, TX-03 paso 2, TX-04 directo).
     * Los paths son relativos a API_BASE_URL.
     */
    public static final class Pagos {
        /** TX-01 — Retiro de efectivo con OTP.
         *  POST {API_BASE_URL}/api/v1/pagos/retiro
         *  X-RqUID incremental: 001001 */
        public static final String RETIRO        = "/api/v1/pagos/retiro";

        /** TX-02 — Depósitos y consignaciones (Efectivo).
         *  POST {API_BASE_URL}/api/v1/pagos/deposito
         *  X-RqUID incremental: 002001 */
        public static final String DEPOSITO      = "/api/v1/pagos/deposito";


        /** TX-03 paso 2 / TX-04 paso 2 — Pago de factura / convenios / TC Aval.
         *  POST {API_BASE_URL}/api/v1/pagos/pago-factura
         *  X-RqUID incremental: 003001 (recaudo) | 004001 (pago oblig.) */
        public static final String PAGO_FACTURA  = "/api/v1/pagos/pago-factura";

        /** TX-03 paso 2 — Pago de factura / convenios (Efectivo).
         *  POST {API_BASE_URL}/api/v1/pagos/pago-factura
         *  X-RqUID incremental: 003001 (recaudo) */
        

        /** TX-04 — Pago de obligaciones y TC Aval (Efectivo).
         *  POST {API_BASE_URL}/api/v1/pagos/pago-obligaciones
         *  X-RqUID incremental: 004001 */
        public static final String PAGO_OBLIGACIONES = "/api/v1/pagos/pago-obligaciones";
        
    }

    // ── Consultas — endpoint orquestador bajo /everest/orq/consultas/ ─────────
    /**
     * Agrupa los paths del módulo de consultas (TX-03 paso 1 únicamente).
     * Los paths son relativos a API_BASE_URL.
     * TX-04 NO usa este endpoint — es un endpoint directo: Pagos.PAGO_OBLIGACIONES.
     */
    public static final class Consultas {

        /** TX-03 paso 1 / TX-04 paso 1 — Consulta de factura (orquestador Everest).
         *  POST {API_BASE_URL}/everest/orq/consultas/api/v1/consulta
         *  Se ejecuta SIEMPRE antes de los Pagos.PAGO_FACTURA. */


        public static final String CONSULTA_FACTURA = "/everest/orq/consultas/api/v1/consulta";
    }

    // ── Oficinas — orquestador de consultas ADP AVV / BDB ──────────────────────
    /**
     * Host distinto al de Pagos/Consultas (arriba). Confirmado en vivo (2026-09-15):
     * responde HTTP 200 para las 9 operaciones de este módulo — ver
     * /memories/repo/oficinas-consulta-notes.md.
     */
    public static final class Oficinas {

        /** Host propio de Oficinas — distinto de API_BASE_URL. La ability del actor
         *  se reconfigura a este host solo para escenarios @oficinas (ver Hooks.java);
         *  por eso los paths de abajo son relativos, no URLs absolutas. */
        public static final String BASE_URL = "https://d299ks4asy14z3.cloudfront.net";

        /** POST — Orquestador ADP AVV (CONSULTA_CLIENTE, CONSULTA_PRODUCTOS,
         *  CONSULTA_DETALLADA_CARTERA, CONSULTA_DETALLADA_TC, CONSULTA_DETALLADA_CDT). */
        public static final String CONSULTA_AVV = "/api/v1/everst/ofi/avv/adp/consulta";

        /** POST — Orquestador ADP BDB (CONSULTA_GENERAL, CONSULTA_DETALLADA_CARTERA,
         *  CONSULTA_DETALLADA_TC, CONSULTA_DETALLADA_CDT). */
        public static final String CONSULTA_BDB = "/api/v1/everst/ofi/bog/adp/consulta";
    }

    // ── Auth — paths de autenticación (si aplica en futuros sprints) ──────────
    public static final class Auth {
        /** POST — Login, devuelve token de sesión */
        public static final String LOGIN    = "/login";
        /** POST — Registro de nuevo usuario */
        public static final String REGISTER = "/register";
        /** POST — Renovar token */
        public static final String REFRESH  = "/refresh";
    }
}
