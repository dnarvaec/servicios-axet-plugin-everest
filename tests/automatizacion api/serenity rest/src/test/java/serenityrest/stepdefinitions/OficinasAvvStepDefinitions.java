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
 * StepDefinitions — Oficinas ADP AVV (Consulta Cliente, Productos, Cartera
 * Detallada, TC Detallada, CDT Detallado)
 *
 * NOTA — validado en vivo con mvn verify (2026-09-15): el orquestador real
 * responde HTTP 200 con msgRsHdr.status.statusCode=200 para estas operaciones.
 * Ver /memories/repo/oficinas-consulta-notes.md para el historial completo.
 *
 * Invariantes de red corporativa NTT:
 *   - Setup común (RestAssured, actor, ability) vive en Hooks.java
 *   - PROHIBIDO Tasks.instrumented() en API tests
 */
public class OficinasAvvStepDefinitions {

    private Actor actor;
    private int casoActual;

    @Before
    public void obtenerActor() {
        actor = OnStage.theActorInTheSpotlight();
    }

    // ── Dado ──────────────────────────────────────────────────────────────────

    @Dado("el actor est\u00e1 autorizado para operar en la API de Oficinas AVV")
    public void elActorEstaAutorizadoParaOficinasAvv() {
        // La ability CallAnApi ya fue configurada en Hooks
    }

    // ── Cuando ───────────────────────────────────────────────────────────────
    // Llamada REST directa — PROHIBIDO Tasks.instrumented() en API tests sin WebDriver

    @Cuando("consulta el cliente en AVV del caso {int}")
    public void consultaElClienteEnAvv(int caso) {
        casoActual = caso;
        actor.attemptsTo(
            Post.to(ApiEndpoints.Oficinas.CONSULTA_AVV)
                .with(requestSpec -> requestSpec
                    .headers(TestData.avvConsultaClienteHeaders(caso))
                    .body(TestData.avvConsultaClientePayload(caso)))
        );
    }

    @Cuando("consulta los productos en AVV del caso {int}")
    public void consultaLosProductosEnAvv(int caso) {
        casoActual = caso;
        actor.attemptsTo(
            Post.to(ApiEndpoints.Oficinas.CONSULTA_AVV)
                .with(requestSpec -> requestSpec
                    .headers(TestData.avvConsultaProductosHeaders(caso))
                    .body(TestData.avvConsultaProductosPayload(caso)))
        );
    }

    @Cuando("consulta la cartera detallada en AVV del caso {int}")
    public void consultaLaCarteraDetalladaEnAvv(int caso) {
        casoActual = caso;
        actor.attemptsTo(
            Post.to(ApiEndpoints.Oficinas.CONSULTA_AVV)
                .with(requestSpec -> requestSpec
                    .headers(TestData.avvCarteraDetalladaHeaders(caso))
                    .body(TestData.avvCarteraDetalladaPayload(caso)))
        );
    }

    @Cuando("consulta la tarjeta de credito detallada en AVV del caso {int}")
    public void consultaLaTarjetaDeCreditoDetalladaEnAvv(int caso) {
        casoActual = caso;
        actor.attemptsTo(
            Post.to(ApiEndpoints.Oficinas.CONSULTA_AVV)
                .with(requestSpec -> requestSpec
                    .headers(TestData.avvTcDetalladaHeaders(caso))
                    .body(TestData.avvTcDetalladaPayload(caso)))
        );
    }

    @Cuando("consulta el CDT detallado en AVV del caso {int}")
    public void consultaElCdtDetalladoEnAvv(int caso) {
        casoActual = caso;
        actor.attemptsTo(
            Post.to(ApiEndpoints.Oficinas.CONSULTA_AVV)
                .with(requestSpec -> requestSpec
                    .headers(TestData.avvCdtDetalladoHeaders(caso))
                    .body(TestData.avvCdtDetalladoPayload(caso)))
        );
    }

    // ── Entonces ─────────────────────────────────────────────────────────────
    // El resultado esperado (httpStatusCode/statusCode) viene de datadriven.xlsx.

    @Entonces("la consulta de cliente en AVV es exitosa")
    public void laConsultaDeClienteEnAvvEsExitosa() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.avvConsultaClienteExpected(casoActual));
    }

    @Entonces("la consulta de productos en AVV es exitosa")
    public void laConsultaDeProductosEnAvvEsExitosa() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.avvConsultaProductosExpected(casoActual));
    }

    @Entonces("la consulta de cartera detallada en AVV es exitosa")
    public void laConsultaDeCarteraDetalladaEnAvvEsExitosa() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.avvCarteraDetalladaExpected(casoActual));
    }

    @Entonces("la consulta de tarjeta de credito detallada en AVV es exitosa")
    public void laConsultaDeTarjetaDeCreditoDetalladaEnAvvEsExitosa() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.avvTcDetalladaExpected(casoActual));
    }

    @Entonces("la consulta de CDT detallado en AVV es exitosa")
    public void laConsultaDeCdtDetalladoEnAvvEsExitosa() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.avvCdtDetalladoExpected(casoActual));
    }

    @Entonces("la respuesta de consulta de cliente en AVV coincide con el error esperado")
    public void laRespuestaDeConsultaDeClienteEnAvvCoincideConElErrorEsperado() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.avvConsultaClienteExpected(casoActual));
    }

    @Entonces("la respuesta de consulta de productos en AVV coincide con el error esperado")
    public void laRespuestaDeConsultaDeProductosEnAvvCoincideConElErrorEsperado() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.avvConsultaProductosExpected(casoActual));
    }

    @Entonces("la respuesta de cartera detallada en AVV coincide con el error esperado")
    public void laRespuestaDeCarteraDetalladaEnAvvCoincideConElErrorEsperado() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.avvCarteraDetalladaExpected(casoActual));
    }

    @Entonces("la respuesta de tarjeta de credito detallada en AVV coincide con el error esperado")
    public void laRespuestaDeTarjetaDeCreditoDetalladaEnAvvCoincideConElErrorEsperado() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.avvTcDetalladaExpected(casoActual));
    }

    @Entonces("la respuesta de CDT detallado en AVV coincide con el error esperado")
    public void laRespuestaDeCdtDetalladoEnAvvCoincideConElErrorEsperado() {
        ApiAssertions.assertTransaccionExitosa(actor, TestData.avvCdtDetalladoExpected(casoActual));
    }

    @Entonces("el envelope de respuesta de Oficinas AVV est\u00e1 presente")
    public void elEnvelopeDeRespuestaDeOficinasAvvEstaPresente() {
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
