package serenityrest.stepdefinitions;

import io.cucumber.java.After;
import io.cucumber.java.Before;
import io.restassured.RestAssured;
import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.actors.Cast;
import net.serenitybdd.screenplay.actors.OnStage;
import net.serenitybdd.screenplay.rest.abilities.CallAnApi;
import serenityrest.utils.ApiEndpoints;

/**
 * Hooks compartidos por las 4 *StepDefinitions (evita repetir @Before/@After
 * idénticos en cada clase — Cucumber los ejecuta una sola vez por escenario
 * sin importar en qué clase del glue path estén declarados).
 */
public class Hooks {

    // order = 0 garantiza que este @Before corra ANTES que el de cada
    // *StepDefinitions (que usan el valor por defecto) — sin esto, Cucumber
    // no garantiza el orden entre @Before de distintas clases del glue path.
    @Before(order = 0)
    public void configurarEscenario() {
        // Obligatorio en red NTT/corporativa — proxy MITM con certificado propio
        RestAssured.useRelaxedHTTPSValidation();
        OnStage.setTheStage(Cast.ofStandardActors());
        Actor actor = OnStage.theActorCalled("API Tester");
        actor.whoCan(CallAnApi.at(ApiEndpoints.API_BASE_URL));
    }

    @After
    public void cerrarEscenario() {
        OnStage.drawTheCurtain();
    }
}
