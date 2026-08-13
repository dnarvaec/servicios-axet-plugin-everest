package serenityrest.screenplay.questions;

import net.serenitybdd.rest.SerenityRest;
import net.serenitybdd.screenplay.Question;

/**
 * TheResponse
 * ─────────────────────────────────────────────────────────────────────────────
 * Colección de Questions para extraer datos de la última respuesta HTTP.
 * Las aserciones SIEMPRE se hacen en los Step Definitions usando TheResponse.
 * NUNCA hacer aserciones dentro de los Tasks.
 *
 * Uso en Step Definitions:
 *   assertThat(theActor.asksFor(TheResponse.statusCode()), equalTo(200));
 *   assertThat(theActor.asksFor(TheResponse.field("data.id")), notNullValue());
 * ─────────────────────────────────────────────────────────────────────────────
 */
public final class TheResponse {

    private TheResponse() {}

    // ── Status code ───────────────────────────────────────────────────────────

    public static Question<Integer> statusCode() {
        return actor -> SerenityRest.lastResponse().statusCode();
    }

    // ── Body — path JSON ──────────────────────────────────────────────────────
    // Se valida el content-type ANTES de parsear: si el body no es JSON (p.ej. un 404/500
    // "text/plain" del gateway), se falla con un AssertionError legible en vez de dejar que
    // RestAssured lance IllegalStateException ("Cannot determine which path implementation...").

    public static <T> Question<T> field(String jsonPath) {
        return actor -> {
            assertJsonResponse(jsonPath);
            return SerenityRest.lastResponse().path(jsonPath);
        };
    }

    public static Question<String> fieldAsString(String jsonPath) {
        return actor -> {
            assertJsonResponse(jsonPath);
            return SerenityRest.lastResponse().path(jsonPath).toString();
        };
    }

    // ── Body completo como String ─────────────────────────────────────────────

    public static Question<String> body() {
        return actor -> SerenityRest.lastResponse().asString();
    }

    // ── Headers de respuesta ─────────────────────────────────────────────────

    public static Question<String> header(String headerName) {
        return actor -> SerenityRest.lastResponse().header(headerName);
    }

    // ── Tiempo de respuesta (ms) ──────────────────────────────────────────────

    public static Question<Long> responseTimeMs() {
        return actor -> SerenityRest.lastResponse().time();
    }

    // ── Validación de campo no nulo ───────────────────────────────────────────

    public static Question<Boolean> fieldIsNotNull(String jsonPath) {
        return actor -> {
            assertJsonResponse(jsonPath);
            return SerenityRest.lastResponse().path(jsonPath) != null;
        };
    }

    // ── Guarda interna ────────────────────────────────────────────────────────

    private static void assertJsonResponse(String jsonPath) {
        String contentType = SerenityRest.lastResponse().contentType();
        if (contentType == null || !contentType.toLowerCase().contains("json")) {
            throw new AssertionError(
                "No se puede leer el campo '" + jsonPath + "' del body: la respuesta no es JSON "
                    + "(status=" + SerenityRest.lastResponse().statusCode()
                    + ", content-type=" + contentType + ")"
            );
        }
    }
}
