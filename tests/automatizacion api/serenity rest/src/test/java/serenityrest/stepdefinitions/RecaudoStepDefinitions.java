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
 * StepDefinitions — TX-03 Recaudo de convenios (Efectivo)
 * Flujo de dos pasos: consulta de factura (paso 1) → pago de factura (paso 2)
 *
 * Invariantes de red corporativa NTT:
 *   - Setup común (RestAssured, actor, ability) vive en Hooks.java
 *   - PROHIBIDO Tasks.instrumented() en API tests
 */
public class RecaudoStepDefinitions {

    private Actor actor;
    private int casoActual;

    @Before
    public void obtenerActor() {
        actor = OnStage.theActorInTheSpotlight();
    }

    // ── Dado ──────────────────────────────────────────────────────────────────

    @Dado("el actor est\u00e1 autorizado para operar en la API de recaudo")
    public void elActorEstaAutorizadoParaRecaudo() {
        // La ability CallAnApi ya fue configurada en Hooks
    }

    // ── Cuando — Paso 1: Consulta ─────────────────────────────────────────────
    // Llamada REST directa — PROHIBIDO Tasks.instrumented() en API tests sin WebDriver

    @Cuando("consulta la factura del convenio TX-03 del caso {int}")
    public void consultaLaFacturaDelConvenio(int caso) {
        casoActual = caso;
        actor.attemptsTo(
            Post.to(ApiEndpoints.Consultas.CONSULTA_FACTURA)
                .with(requestSpec -> requestSpec
                    .headers(TestData.consultaFacturaHeaders(caso))
                    .body(TestData.consultaFacturaPayload(caso)))
        );
    }

    // ── Cuando — Paso 2: Pago ─────────────────────────────────────────────────

    @Cuando("realiza el pago de la factura del convenio del caso {int}")
    public void realizaElPagoDeLaFactura(int caso) {
        casoActual = caso;
        actor.attemptsTo(
            Post.to(ApiEndpoints.Pagos.PAGO_FACTURA)
                .with(requestSpec -> requestSpec
                    .headers(TestData.pagoFacturaHeaders(caso))
                    .body(TestData.pagoFacturaPayload(caso)))
        );
    }

    // ── Entonces — Validaciones de Consulta (Paso 1) ─────────────────────────
    // El resultado esperado viene de datadriven.xlsx (hoja recaudo, prefijo consulta_factura/pago_factura).

    @Entonces("la consulta de factura es exitosa")
    public void laConsultaDeFacturaEsExitosa() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.consultaFacturaExpected(casoActual));
    }

    @Entonces("la respuesta contiene el nombre del convenio")
    public void laRespuestaContieneElNombreDelConvenio() {
        assertThat(
            "data.Agreement.Name debe estar presente",
            actor.asksFor(TheResponse.fieldIsNotNull("data.Agreement.Name")),
            is(true)
        );
    }

    @Entonces("la respuesta contiene el monto total a pagar")
    public void laRespuestaContieneElMontoTotalAPagar() {
        assertThat(
            "data.TotalCurAmt.Amt debe estar presente",
            actor.asksFor(TheResponse.fieldIsNotNull("data.TotalCurAmt.Amt")),
            is(true)
        );
    }

    @Entonces("los saldos de la factura est\u00e1n presentes")
    public void losSaldosDeLaFacturaEstanPresentes() {
        assertThat(
            "data.AcctBal debe estar presente",
            actor.asksFor(TheResponse.fieldIsNotNull("data.AcctBal")),
            is(true)
        );
    }

    // ── Entonces — Validaciones de Pago (Paso 2) ─────────────────────────────

    @Entonces("el pago de la factura es exitoso")
    public void elPagoDeLaFacturaEsExitoso() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.pagoFacturaExpected(casoActual));
    }

    @Entonces("la severidad del recaudo es la esperada")
    public void laSeveridadDelRecaudoEsLaEsperada() {
        String severidadEsperada = TestData.pagoFacturaExpected(casoActual).get("severity");
        assertThat(
            "msgRsHdr.status.severity debe ser " + severidadEsperada,
            actor.asksFor(TheResponse.fieldAsString("msgRsHdr.status.severity")),
            equalTo(severidadEsperada)
        );
    }

    @Entonces("la descripci\u00f3n del recaudo es la esperada")
    public void laDescripcionDelRecaudoEsLaEsperada() {
        String descripcionEsperada = TestData.pagoFacturaExpected(casoActual).get("statusDesc");
        assertThat(
            "msgRsHdr.status.statusDesc debe ser " + descripcionEsperada,
            actor.asksFor(TheResponse.fieldAsString("msgRsHdr.status.statusDesc")),
            equalTo(descripcionEsperada)
        );
    }

    @Entonces("el campo endDt del recaudo est\u00e1 presente")
    public void elCampoEndDtDelRecaudoEstaPresente() {
        assertThat(
            "endDt debe estar presente en la respuesta",
            actor.asksFor(TheResponse.fieldIsNotNull("endDt")),
            is(true)
        );
    }
}
