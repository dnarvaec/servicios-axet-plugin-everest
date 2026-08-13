package serenityrest.stepdefinitions;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.is;

import io.cucumber.java.Before;
import io.cucumber.java.es.Cuando;
import io.cucumber.java.es.Dado;
import io.cucumber.java.es.Entonces;
import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.actors.OnStage;
import net.serenitybdd.screenplay.rest.interactions.Post;
import serenityrest.screenplay.questions.TheResponse;
import serenityrest.utils.ApiAssertions;
import serenityrest.utils.ApiEndpoints;
import serenityrest.utils.TestData;

/**
 * StepDefinitions — TX-01 Retiro de efectivo con OTP
 *
 * Invariantes de red corporativa NTT:
 *   - Setup común (RestAssured, actor, ability) vive en Hooks.java
 *   - PROHIBIDO Tasks.instrumented() en API tests
 */
public class RetiroStepDefinitions {

    private Actor actor;
    private int casoActual;

    @Before
    public void obtenerActor() {
        actor = OnStage.theActorInTheSpotlight();
    }

    // ── Dado ──────────────────────────────────────────────────────────────────

    @Dado("el actor est\u00e1 autorizado para operar en la API de retiros")
    public void elActorEstaAutorizadoParaRetiros() {
        // La ability CallAnApi ya fue configurada en Hooks
    }

    // ── Cuando ───────────────────────────────────────────────────────────────

    // Llamada REST directa — PROHIBIDO Tasks.instrumented() en API tests sin WebDriver
    @Cuando("realiza un retiro de efectivo con OTP del caso {int}")
    public void realizaRetiroConOtp(int caso) {
        casoActual = caso;
        actor.attemptsTo(
            Post.to(ApiEndpoints.Pagos.RETIRO)
                .with(requestSpec -> requestSpec
                    .headers(TestData.retiroHeaders(caso))
                    .body(TestData.retiroOtpPayload(caso)))
        );
    }

    // ── Entonces ─────────────────────────────────────────────────────────────
    // El resultado esperado (statusCode/severity/statusDesc) viene de datadriven.xlsx,
    // nunca como literal en el .feature — así cada caso puede tener su propio resultado.

    @Entonces("la transacci\u00f3n de retiro es exitosa")
    public void laTransaccionRetiroEsExitosa() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.retiroExpected(casoActual));
    }

    @Entonces("la severidad del retiro es la esperada")
    public void laSeveridadDelRetiroEsLaEsperada() {
        String severidadEsperada = TestData.retiroExpected(casoActual).get("severity");
        assertThat(
            "msgRsHdr.status.severity debe ser " + severidadEsperada,
            actor.asksFor(TheResponse.fieldAsString("msgRsHdr.status.severity")),
            equalTo(severidadEsperada)
        );
    }

    @Entonces("la descripci\u00f3n del retiro es la esperada")
    public void laDescripcionDelRetiroEsLaEsperada() {
        String descripcionEsperada = TestData.retiroExpected(casoActual).get("statusDesc");
        assertThat(
            "msgRsHdr.status.statusDesc debe ser " + descripcionEsperada,
            actor.asksFor(TheResponse.fieldAsString("msgRsHdr.status.statusDesc")),
            equalTo(descripcionEsperada)
        );
    }

    @Entonces("el campo endDt del retiro est\u00e1 presente")
    public void elCampoEndDtDelRetiroEstaPresente() {
        assertThat(
            "endDt debe estar presente en la respuesta",
            actor.asksFor(TheResponse.fieldIsNotNull("endDt")),
            is(true)
        );
    }
}
