package serenityrest.stepdefinitions;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.is;

import io.cucumber.java.Before;
import io.cucumber.java.es.Cuando;
import io.cucumber.java.es.Entonces;
import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.actors.OnStage;
import net.serenitybdd.screenplay.rest.interactions.Post;
import serenityrest.screenplay.questions.TheResponse;
import serenityrest.utils.ApiAssertions;
import serenityrest.utils.ApiEndpoints;
import serenityrest.utils.DataDrivenExcelReader;

public class NuevasOficinasStepDefinitions {

    private Actor actor;
    private String sheetName;
    private int casoActual;

    @Before
    public void obtenerActor() {
        actor = OnStage.theActorInTheSpotlight();
    }

    @Cuando("ejecuta la operacion nueva {string} del banco {string} en el caso {int}")
    public void ejecutaOperacionNueva(String operacion, String banco, int caso) {
        ejecutaDesdeHoja(sheetNameFor(banco, operacion), caso);
    }

    @Cuando("ejecuta la consulta de cliente OCC del caso {int}")
    public void ejecutaConsultaClienteOcc(int caso) {
        ejecutaDesdeHoja("occ_consulta_cliente", caso);
    }

    @Cuando("ejecuta la consulta de productos OCC del caso {int}")
    public void ejecutaConsultaProductosOcc(int caso) {
        ejecutaDesdeHoja("occ_consulta_productos", caso);
    }

    @Cuando("ejecuta la consulta de CDT OCC del caso {int}")
    public void ejecutaConsultaCdtOcc(int caso) {
        ejecutaDesdeHoja("occ_consulta_cdt", caso);
    }

    @Cuando("ejecuta la consulta de cliente BPO del caso {int}")
    public void ejecutaConsultaClienteBpo(int caso) {
        ejecutaDesdeHoja("bpop_consulta_cliente", caso);
    }

    @Cuando("ejecuta la consulta de productos BPO del caso {int}")
    public void ejecutaConsultaProductosBpo(int caso) {
        ejecutaDesdeHoja("bpop_consulta_productos", caso);
    }

    @Cuando("ejecuta la consulta de cartera BPO del caso {int}")
    public void ejecutaConsultaCarteraBpo(int caso) {
        ejecutaDesdeHoja("bpop_consulta_cartera", caso);
    }

    @Cuando("ejecuta la consulta ORQ de TC del caso {int}")
    public void ejecutaConsultaOrqTc(int caso) {
        ejecutaDesdeHoja("orq_consulta_tc", caso);
    }

    @Cuando("ejecuta la consulta ORQ de CDT del caso {int}")
    public void ejecutaConsultaOrqCdt(int caso) {
        ejecutaDesdeHoja("orq_consulta_cdt", caso);
    }

    private void ejecutaDesdeHoja(String nuevaHoja, int caso) {
        sheetName = nuevaHoja;
        casoActual = caso;
        actor.attemptsTo(
            Post.to(endpointForSheet(sheetName))
                .with(requestSpec -> requestSpec
                    .headers(DataDrivenExcelReader.officeHeaders(sheetName, caso))
                    .body(DataDrivenExcelReader.officePayload(sheetName, caso)))
        );
    }

    @Entonces("la respuesta de la operacion nueva coincide con lo esperado")
    public void validaRespuestaEsperada() {
        ApiAssertions.assertTransaccionExitosa(
            actor,
            DataDrivenExcelReader.officeExpected(sheetName, casoActual)
        );
    }

    @Entonces("la respuesta de la operación nueva coincide con lo esperado")
    public void validaRespuestaEsperadaConAcento() {
        validaRespuestaEsperada();
    }

    @Entonces("la respuesta de la operacion nueva contiene el envelope")
    public void validaEnvelope() {
        assertThat(actor.asksFor(TheResponse.fieldIsNotNull("msgRsHdr.status")), is(true));
        assertThat(actor.asksFor(TheResponse.fieldIsNotNull("endDt")), is(true));
    }

    private static String sheetNameFor(String banco, String operacion) {
        String prefix = prefixFor(banco);
        if ("BLOQUEO_TD_DEFINITIVO".equals(operacion)) return prefix + "bloqueo_td";
        if ("BLOQUEO_TC".equals(operacion)) return prefix + "bloqueo_tc";
        if ("ACTUALIZACION_DATOS".equals(operacion)) return prefix + "actualizacion_datos";
        if ("CONSULTA_CLIENTE".equals(operacion)) return prefix + "consulta_cliente";
        if ("CONSULTA_PRODUCTOS".equals(operacion)) return prefix + "consulta_productos";
        if ("CONSULTA_DETALLADA_CDT".equals(operacion)) return prefix + "consulta_cdt";
        if ("CONSULTA_DETALLADA_CARTERA".equals(operacion)) return prefix + "consulta_cartera";
        throw new IllegalArgumentException("Operación nueva no soportada: " + operacion);
    }

    private static String prefixFor(String banco) {
        if ("BAVV".equals(banco)) return "avv_";
        if ("BBOG".equals(banco)) return "bdb_";
        if ("BOCC".equals(banco)) return "occ_";
        if ("BPOP".equals(banco)) return "bpop_";
        throw new IllegalArgumentException("Banco no soportado: " + banco);
    }

    private static String endpointForSheet(String sheetName) {
        if (sheetName.endsWith("_bloqueo_td")) return bloqueoTdEndpointForSheet(sheetName);
        if (sheetName.endsWith("_bloqueo_tc")) return bloqueoTcEndpointForSheet(sheetName);
        if (sheetName.endsWith("_actualizacion_datos")) return actualizacionDatosEndpointForSheet(sheetName);
        if (sheetName.startsWith("avv_")) return ApiEndpoints.Oficinas.CONSULTA_AVV;
        if (sheetName.startsWith("bdb_")) return ApiEndpoints.Oficinas.CONSULTA_BDB;
        if (sheetName.startsWith("occ_") || sheetName.startsWith("orq_")) return ApiEndpoints.Oficinas.CONSULTA_OCC;
        if (sheetName.startsWith("bpop_")) return ApiEndpoints.Oficinas.CONSULTA_BPOP;
        throw new IllegalArgumentException("No hay endpoint configurado para hoja: " + sheetName);
    }

    private static String bloqueoTdEndpointForSheet(String sheetName) {
        if (sheetName.startsWith("avv_")) return ApiEndpoints.Oficinas.BLOQUEO_TD_AVV;
        if (sheetName.startsWith("bdb_")) return ApiEndpoints.Oficinas.BLOQUEO_TD_BDB;
        if (sheetName.startsWith("occ_")) return ApiEndpoints.Oficinas.BLOQUEO_TD_OCC;
        if (sheetName.startsWith("bpop_")) return ApiEndpoints.Oficinas.BLOQUEO_TD_BPOP;
        throw new IllegalArgumentException("No hay endpoint de bloqueo TD configurado para hoja: " + sheetName);
    }

    private static String bloqueoTcEndpointForSheet(String sheetName) {
        if (sheetName.startsWith("avv_")) return ApiEndpoints.Oficinas.BLOQUEO_TC_AVV;
        if (sheetName.startsWith("bdb_")) return ApiEndpoints.Oficinas.BLOQUEO_TC_BDB;
        if (sheetName.startsWith("occ_")) return ApiEndpoints.Oficinas.BLOQUEO_TC_OCC;
        if (sheetName.startsWith("bpop_")) return ApiEndpoints.Oficinas.BLOQUEO_TC_BPOP;
        throw new IllegalArgumentException("No hay endpoint de bloqueo TC configurado para hoja: " + sheetName);
    }

    private static String actualizacionDatosEndpointForSheet(String sheetName) {
        if (sheetName.startsWith("avv_")) return ApiEndpoints.Oficinas.ACTUALIZACION_DATOS_AVV;
        if (sheetName.startsWith("bdb_")) return ApiEndpoints.Oficinas.ACTUALIZACION_DATOS_BDB;
        if (sheetName.startsWith("occ_")) return ApiEndpoints.Oficinas.ACTUALIZACION_DATOS_OCC;
        if (sheetName.startsWith("bpop_")) return ApiEndpoints.Oficinas.ACTUALIZACION_DATOS_BPOP;
        throw new IllegalArgumentException("No hay endpoint de actualización de datos configurado para hoja: " + sheetName);
    }
}
