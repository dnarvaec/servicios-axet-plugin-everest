package serenityrest.utils;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;

import java.util.Map;

import net.serenitybdd.screenplay.Actor;
import serenityrest.screenplay.questions.TheResponse;

/**
 * Aserciones compartidas por las 4 TX — evita repetir la validación del HTTP status
 * en cada StepDefinitions.
 */
public final class ApiAssertions {

    private ApiAssertions() {}

    public static void assertHttpStatusCode(Actor actor, Map<String, String> esperado) {
        assertThat(
            "HTTP status code debe ser " + esperado.get("httpStatusCode"),
            actor.asksFor(TheResponse.statusCode()),
            equalTo(Integer.parseInt(esperado.get("httpStatusCode")))
        );
    }

    public static void assertTransaccionExitosa(Actor actor, Map<String, String> esperado) {
        assertHttpStatusCode(actor, esperado);
    }
}
