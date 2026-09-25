package serenityrest.stepdefinitions;

import static org.hamcrest.MatcherAssert.assertThat;
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
 * StepDefinitions — Oficinas ADP BDB (Consulta General, Cartera Detallada,
 * TC Detallada, CDT Detallado)
 *
 * NOTA — validado en vivo con mvn verify (2026-09-15): el orquestador real
 * responde HTTP 200 con msgRsHdr.status.statusCode=200 para estas operaciones.
 * Ver /memories/repo/oficinas-consulta-notes.md para el historial completo.
 *
 * Invariantes de red corporativa NTT:
 *   - Setup común (RestAssured, actor, ability) vive en Hooks.java
 *   - PROHIBIDO Tasks.instrumented() en API tests
 */
public class OficinasBdbStepDefinitions {

    private Actor actor;
    private int casoActual;

    @Before
    public void obtenerActor() {
        actor = OnStage.theActorInTheSpotlight();
    }

    // ── Dado ──────────────────────────────────────────────────────────────────

    @Dado("el actor est\u00e1 autorizado para operar en la API de Oficinas BDB")
    public void elActorEstaAutorizadoParaOficinasBdb() {
        // La ability CallAnApi ya fue configurada en Hooks
    }

    // ── Cuando ───────────────────────────────────────────────────────────────
    // Llamada REST directa — PROHIBIDO Tasks.instrumented() en API tests sin WebDriver

    @Cuando("consulta general de cliente y productos en BDB del caso {int}")
    public void consultaGeneralDeClienteYProductosEnBdb(int caso) {
        casoActual = caso;
        actor.attemptsTo(
            Post.to(ApiEndpoints.Oficinas.CONSULTA_BDB)
                .with(requestSpec -> requestSpec
                    .headers(TestData.bdbConsultaGeneralHeaders(caso))
                    .body(TestData.bdbConsultaGeneralPayload(caso)))
        );
    }

    @Cuando("consulta la cartera detallada en BDB del caso {int}")
    public void consultaLaCarteraDetalladaEnBdb(int caso) {
        casoActual = caso;
        actor.attemptsTo(
            Post.to(ApiEndpoints.Oficinas.CONSULTA_BDB)
                .with(requestSpec -> requestSpec
                    .headers(TestData.bdbCarteraDetalladaHeaders(caso))
                    .body(TestData.bdbCarteraDetalladaPayload(caso)))
        );
    }

    @Cuando("consulta la tarjeta de credito detallada en BDB del caso {int}")
    public void consultaLaTarjetaDeCreditoDetalladaEnBdb(int caso) {
        casoActual = caso;
        actor.attemptsTo(
            Post.to(ApiEndpoints.Oficinas.CONSULTA_BDB)
                .with(requestSpec -> requestSpec
                    .headers(TestData.bdbTcDetalladaHeaders(caso))
                    .body(TestData.bdbTcDetalladaPayload(caso)))
        );
    }

    @Cuando("consulta el CDT detallado en BDB del caso {int}")
    public void consultaElCdtDetalladoEnBdb(int caso) {
        casoActual = caso;
        actor.attemptsTo(
            Post.to(ApiEndpoints.Oficinas.CONSULTA_BDB)
                .with(requestSpec -> requestSpec
                    .headers(TestData.bdbCdtDetalladoHeaders(caso))
                    .body(TestData.bdbCdtDetalladoPayload(caso)))
        );
    }

    // ── Entonces ─────────────────────────────────────────────────────────────
    // El resultado esperado (httpStatusCode/statusCode) viene de datadriven.xlsx.

    @Entonces("la consulta general en BDB es exitosa")
    public void laConsultaGeneralEnBdbEsExitosa() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.bdbConsultaGeneralExpected(casoActual));
    }

    @Entonces("la consulta de cartera detallada en BDB es exitosa")
    public void laConsultaDeCarteraDetalladaEnBdbEsExitosa() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.bdbCarteraDetalladaExpected(casoActual));
    }

    @Entonces("la consulta de tarjeta de credito detallada en BDB es exitosa")
    public void laConsultaDeTarjetaDeCreditoDetalladaEnBdbEsExitosa() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.bdbTcDetalladaExpected(casoActual));
    }

    @Entonces("la consulta de CDT detallado en BDB es exitosa")
    public void laConsultaDeCdtDetalladoEnBdbEsExitosa() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.bdbCdtDetalladoExpected(casoActual));
    }

    @Entonces("la respuesta de consulta general en BDB coincide con el error esperado")
    public void laRespuestaDeConsultaGeneralEnBdbCoincideConElErrorEsperado() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.bdbConsultaGeneralExpected(casoActual));
    }

    @Entonces("la respuesta de cartera detallada en BDB coincide con el error esperado")
    public void laRespuestaDeCarteraDetalladaEnBdbCoincideConElErrorEsperado() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.bdbCarteraDetalladaExpected(casoActual));
    }

    @Entonces("la respuesta de tarjeta de credito detallada en BDB coincide con el error esperado")
    public void laRespuestaDeTarjetaDeCreditoDetalladaEnBdbCoincideConElErrorEsperado() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.bdbTcDetalladaExpected(casoActual));
    }

    @Entonces("la respuesta de CDT detallado en BDB coincide con el error esperado")
    public void laRespuestaDeCdtDetalladoEnBdbCoincideConElErrorEsperado() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.bdbCdtDetalladoExpected(casoActual));
    }

    @Entonces("el envelope de respuesta de Oficinas BDB esta presente")
    public void elEnvelopeDeRespuestaDeOficinasBdbEstaPresente() {
        assertThat(
            "msgRsHdr.status debe estar presente",
            actor.asksFor(TheResponse.fieldIsNotNull("msgRsHdr.status")),
            is(true)
        );
        assertThat(
            "endDt debe estar presente en la respuesta",
            actor.asksFor(TheResponse.fieldIsNotNull("endDt")),
            is(true)
        );
    }
}
