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
 * StepDefinitions — TX-02 Dep\u00f3sitos y consignaciones (Efectivo)
 *
 * Invariantes de red corporativa NTT:
 *   - Setup común (RestAssured, actor, ability) vive en Hooks.java
 *   - PROHIBIDO Tasks.instrumented() en API tests
 */
public class DepositoStepDefinitions {

    private Actor actor;
    private int casoActual;

    @Before
    public void obtenerActor() {
        actor = OnStage.theActorInTheSpotlight();
    }

    // ── Dado ──────────────────────────────────────────────────────────────────

    @Dado("el actor est\u00e1 autorizado para operar en la API de dep\u00f3sitos")
    public void elActorEstaAutorizadoParaDepositos() {
        // La ability CallAnApi ya fue configurada en Hooks
    }

    // ── Cuando ───────────────────────────────────────────────────────────────

    // Llamada REST directa — PROHIBIDO Tasks.instrumented() en API tests sin WebDriver
    @Cuando("realiza un dep\u00f3sito en efectivo del caso {int}")
    public void realizaDepositoEnEfectivo(int caso) {
        casoActual = caso;
        actor.attemptsTo(
            Post.to(ApiEndpoints.Pagos.DEPOSITO)
                .with(requestSpec -> requestSpec
                    .headers(TestData.depositoHeaders(caso))
                    .body(TestData.depositoPayload(caso)))
        );
    }

    // ── Entonces ─────────────────────────────────────────────────────────────
    // El resultado esperado (statusCode/severity/statusDesc) viene de datadriven.xlsx.

    @Entonces("la transacci\u00f3n de dep\u00f3sito es exitosa")
    public void laTransaccionDepositoEsExitosa() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.depositoExpected(casoActual));
    }

    @Entonces("la severidad del dep\u00f3sito es la esperada")
    public void laSeveridadDelDepositoEsLaEsperada() {
        String severidadEsperada = TestData.depositoExpected(casoActual).get("severity");
        assertThat(
            "msgRsHdr.status.severity debe ser " + severidadEsperada,
            actor.asksFor(TheResponse.fieldAsString("msgRsHdr.status.severity")),
            equalTo(severidadEsperada)
        );
    }

    @Entonces("la descripci\u00f3n del dep\u00f3sito es la esperada")
    public void laDescripcionDelDepositoEsLaEsperada() {
        String descripcionEsperada = TestData.depositoExpected(casoActual).get("statusDesc");
        assertThat(
            "msgRsHdr.status.statusDesc debe ser " + descripcionEsperada,
            actor.asksFor(TheResponse.fieldAsString("msgRsHdr.status.statusDesc")),
            equalTo(descripcionEsperada)
        );
    }

    @Entonces("el campo endDt del dep\u00f3sito est\u00e1 presente")
    public void elCampoEndDtDelDepositoEstaPresente() {
        assertThat(
            "endDt debe estar presente en la respuesta",
            actor.asksFor(TheResponse.fieldIsNotNull("endDt")),
            is(true)
        );
    }
}
