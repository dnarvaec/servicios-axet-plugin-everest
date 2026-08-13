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
 * StepDefinitions — TX-04 Pago de obligaciones y TC Aval (Efectivo)
 *
 * Invariantes de red corporativa NTT:
 *   - Setup común (RestAssured, actor, ability) vive en Hooks.java
 *   - PROHIBIDO Tasks.instrumented() en API tests
 */
public class PagoObligacionStepDefinitions {

    private Actor actor;
    private int casoActual;

    @Before
    public void obtenerActor() {
        actor = OnStage.theActorInTheSpotlight();
    }

    // ── Dado ──────────────────────────────────────────────────────────────────

    @Dado("el actor est\u00e1 autorizado para operar en la API de pago de obligaciones")
    public void elActorEstaAutorizadoParaPagoObligaciones() {
        // La ability CallAnApi ya fue configurada en Hooks
    }

    // ── Cuando ───────────────────────────────────────────────────────────────

    // Llamada REST directa — PROHIBIDO Tasks.instrumented() en API tests sin WebDriver
    @Cuando("realiza el pago de la obligaci\u00f3n TC Aval del caso {int}")
    public void realizaElPagoDeLaObligacion(int caso) {
        casoActual = caso;
        actor.attemptsTo(
            Post.to(ApiEndpoints.Pagos.PAGO_OBLIGACIONES)
                .with(requestSpec -> requestSpec
                    .headers(TestData.pagoObligacionHeaders(caso))
                    .body(TestData.pagoObligacionPayload(caso)))
        );
    }

    // ── Entonces ─────────────────────────────────────────────────────────────
    // El resultado esperado (statusCode/severity/statusDesc) viene de datadriven.xlsx.

    @Entonces("la transacción de pago de obligación es exitosa")
    public void laTransaccionDePagoDeObligacionEsExitosa() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.pagoObligacionExpected(casoActual));
    }

    @Entonces("la severidad del pago de obligación es la esperada")
    public void laSeveridadDelPagoDeObligacionEsLaEsperada() {
        String severidadEsperada = TestData.pagoObligacionExpected(casoActual).get("severity");
        assertThat(
            "msgRsHdr.status.severity debe ser " + severidadEsperada,
            actor.asksFor(TheResponse.fieldAsString("msgRsHdr.status.severity")),
            equalTo(severidadEsperada)
        );
    }

    @Entonces("la descripción del pago de obligación es la esperada")
    public void laDescripcionDelPagoDeObligacionEsLaEsperada() {
        String descripcionEsperada = TestData.pagoObligacionExpected(casoActual).get("statusDesc");
        assertThat(
            "msgRsHdr.status.statusDesc debe ser " + descripcionEsperada,
            actor.asksFor(TheResponse.fieldAsString("msgRsHdr.status.statusDesc")),
            equalTo(descripcionEsperada)
        );
    }

    @Entonces("el campo endDt del pago de obligación está presente")
    public void elCampoEndDtDelPagoDeObligacionEstaPresente() {
        assertThat(
            "endDt debe estar presente en la respuesta",
            actor.asksFor(TheResponse.fieldIsNotNull("endDt")),
            is(true)
        );
    }
}
