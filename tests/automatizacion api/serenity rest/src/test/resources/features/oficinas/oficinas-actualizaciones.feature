# language: en
@oficinas @actualizaciones
Feature: Oficinas - Bloqueo TD y actualizacion de datos

  @ev-169-como-analista-de-pruebas-quiero-ejecutar-el-bloqueo-definitivo-de-tarjeta-debito-exitosamente-para-confirmar-que-el-bloq
  Scenario Outline: HU-201-ADP-AVV - Como analista de pruebas quiero ejecutar el bloqueo definitivo de tarjeta debito exitosamente para confirmar que el bloqueo definitivo se confirma y se retorna el resultado normalizado al orquestador - EV-169 - codigo 200 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BAVV" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_bloqueo_td
      | Caso |
      |1|

  @ev-170-como-analista-de-pruebas-quiero-rechazar-una-operacion-no-soportada-para-confirmar-que-se-retorna-codigo-400-al-orquesta
  Scenario Outline: HU-201-ADP-AVV - Como analista de pruebas quiero rechazar una operacion no soportada para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro - EV-170 - codigo 400 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BAVV" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_bloqueo_td
      | Caso |
      |2|

  @ev-176-como-analista-de-pruebas-quiero-ejecutar-el-bloqueo-definitivo-de-tarjeta-debito-exitosamente-para-confirmar-que-la-tarj
  Scenario Outline: HU-201-ADP-BDB - Como analista de pruebas quiero ejecutar el bloqueo definitivo de tarjeta debito exitosamente para confirmar que la tarjeta queda con bloqueo definitivo y la respuesta se normaliza hacia el orquestador - EV-176 - codigo 200 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_bloqueo_td
      | Caso |
      |1|

  @ev-177-como-analista-de-pruebas-quiero-confirmar-la-respuesta-cuando-la-tarjeta-no-existe-para-confirmar-que-se-retorna-codigo-
  Scenario Outline: HU-201-ADP-BDB - Como analista de pruebas quiero confirmar la respuesta cuando la tarjeta no existe para confirmar que se retorna codigo 404 al orquestador con mensaje funcional claro - EV-177 - codigo 404 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_bloqueo_td
      | Caso |
      |2|

  @ev-178-como-analista-de-pruebas-quiero-confirmar-la-respuesta-cuando-la-tarjeta-ya-esta-bloqueada-para-confirmar-que-se-retorna
  Scenario Outline: HU-201-ADP-BDB - Como analista de pruebas quiero confirmar la respuesta cuando la tarjeta ya esta bloqueada para confirmar que se retorna codigo 409 al orquestador con mensaje funcional claro - EV-178 - codigo 409 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_bloqueo_td
      | Caso |
      |3|

  @ev-179-como-analista-de-pruebas-quiero-confirmar-el-mapeo-de-error-de-negocio-para-confirmar-que-se-retorna-codigo-422-al-orque
  Scenario Outline: HU-201-ADP-BDB - Como analista de pruebas quiero confirmar el mapeo de error de negocio para confirmar que se retorna codigo 422 al orquestador con mensaje funcional claro - EV-179 - codigo 422 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_bloqueo_td
      | Caso |
      |4|

  @ev-180-como-analista-de-pruebas-quiero-rechazar-una-operacion-no-soportada-para-confirmar-que-se-retorna-codigo-400-al-orquesta
  Scenario Outline: HU-201-ADP-BDB - Como analista de pruebas quiero rechazar una operacion no soportada para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro - EV-180 - codigo 400 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_bloqueo_td
      | Caso |
      |5|

  @ev-181-como-analista-de-pruebas-quiero-manejar-credenciales-o-acceso-de-integracion-invalido-para-confirmar-que-se-retorna-codi
  Scenario Outline: HU-201-ADP-BDB - Como analista de pruebas quiero manejar credenciales o acceso de integracion invalido para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro - EV-181 - codigo 502 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_bloqueo_td
      | Caso |
      |6|

  @ev-182-como-analista-de-pruebas-quiero-manejar-un-timeout-del-banco-para-confirmar-que-se-retorna-codigo-504-al-orquestador-con
  Scenario Outline: HU-201-ADP-BDB - Como analista de pruebas quiero manejar un timeout del banco para confirmar que se retorna codigo 504 al orquestador con mensaje funcional claro - EV-182 - codigo 504 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_bloqueo_td
      | Caso |
      |7|

  @ev-188-como-analista-de-pruebas-quiero-ejecutar-el-bloqueo-definitivo-de-tarjeta-debito-exitosamente-para-confirmar-que-los-pre
  Scenario Outline: HU-201-ADP-BPO - Como analista de pruebas quiero ejecutar el bloqueo definitivo de tarjeta debito exitosamente para confirmar que los prerequisitos de identidad y consulta de tarjeta se cumplen, el bloqueo se confirma y la respuesta se normaliza - EV-188 - codigo 200 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_bloqueo_td
      | Caso |
      |1|

  @ev-189-como-analista-de-pruebas-quiero-ejecutar-el-bloqueo-con-las-causales-documentadas-para-confirmar-que-el-banco-confirma-e
  Scenario Outline: HU-201-ADP-BPO - Como analista de pruebas quiero ejecutar el bloqueo con las causales documentadas para confirmar que el banco confirma el bloqueo para cada causal documentada en la coleccion - EV-189 - codigo 200 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_bloqueo_td
      | Caso |
      |2|

  @ev-190-como-analista-de-pruebas-quiero-confirmar-la-respuesta-cuando-la-tarjeta-no-existe-para-confirmar-que-se-retorna-codigo-
  Scenario Outline: HU-201-ADP-BPO - Como analista de pruebas quiero confirmar la respuesta cuando la tarjeta no existe para confirmar que se retorna codigo 404 al orquestador con mensaje funcional claro - EV-190 - codigo 404 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_bloqueo_td
      | Caso |
      |3|

  @ev-191-como-analista-de-pruebas-quiero-confirmar-el-mapeo-de-error-de-negocio-para-confirmar-que-se-retorna-codigo-422-al-orque
  Scenario Outline: HU-201-ADP-BPO - Como analista de pruebas quiero confirmar el mapeo de error de negocio para confirmar que se retorna codigo 422 al orquestador con mensaje funcional claro - EV-191 - codigo 422 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_bloqueo_td
      | Caso |
      |4|

  @ev-192-como-analista-de-pruebas-quiero-rechazar-una-operacion-no-soportada-para-confirmar-que-se-retorna-codigo-400-al-orquesta
  Scenario Outline: HU-201-ADP-BPO - Como analista de pruebas quiero rechazar una operacion no soportada para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro - EV-192 - codigo 400 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_bloqueo_td
      | Caso |
      |5|

  @ev-193-como-analista-de-pruebas-quiero-manejar-una-ip-no-autorizada-por-el-banco-para-confirmar-que-se-retorna-codigo-502-al-or
  Scenario Outline: HU-201-ADP-BPO - Como analista de pruebas quiero manejar una IP no autorizada por el banco para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro - EV-193 - codigo 502 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_bloqueo_td
      | Caso |
      |6|

  @ev-194-como-analista-de-pruebas-quiero-manejar-un-error-de-certificado-o-seguridad-para-confirmar-que-se-retorna-codigo-502-al-
  Scenario Outline: HU-201-ADP-BPO - Como analista de pruebas quiero manejar un error de certificado o seguridad para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro - EV-194 - codigo 502 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_bloqueo_td
      | Caso |
      |7|

  @ev-195-como-analista-de-pruebas-quiero-manejar-un-timeout-del-banco-para-confirmar-que-se-retorna-codigo-504-al-orquestador-con
  Scenario Outline: HU-201-ADP-BPO - Como analista de pruebas quiero manejar un timeout del banco para confirmar que se retorna codigo 504 al orquestador con mensaje funcional claro - EV-195 - codigo 504 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_bloqueo_td
      | Caso |
      |8|

  @ev-201-como-analista-de-pruebas-quiero-ejecutar-el-bloqueo-definitivo-de-tarjeta-debito-exitosamente-para-confirmar-que-el-banc
  Scenario Outline: HU-201-ADP-OCC - Como analista de pruebas quiero ejecutar el bloqueo definitivo de tarjeta debito exitosamente para confirmar que el banco confirma la cancelacion definitiva y la respuesta se normaliza con estado bloqueada - EV-201 - codigo 200 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_bloqueo_td
      | Caso |
      |1|

  @ev-202-como-analista-de-pruebas-quiero-ejecutar-el-bloqueo-con-las-causales-documentadas-para-confirmar-que-el-banco-confirma-e
  Scenario Outline: HU-201-ADP-OCC - Como analista de pruebas quiero ejecutar el bloqueo con las causales documentadas para confirmar que el banco confirma el bloqueo para cada causal documentada en la coleccion - EV-202 - codigo 200 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_bloqueo_td
      | Caso |
      |2|

  @ev-203-como-analista-de-pruebas-quiero-confirmar-la-respuesta-cuando-la-tarjeta-no-existe-para-confirmar-que-se-retorna-codigo-
  Scenario Outline: HU-201-ADP-OCC - Como analista de pruebas quiero confirmar la respuesta cuando la tarjeta no existe para confirmar que se retorna codigo 404 al orquestador con mensaje funcional claro - EV-203 - codigo 404 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_bloqueo_td
      | Caso |
      |3|

  @ev-204-como-analista-de-pruebas-quiero-confirmar-la-respuesta-cuando-el-estado-no-permite-bloqueo-para-confirmar-que-se-retorna
  Scenario Outline: HU-201-ADP-OCC - Como analista de pruebas quiero confirmar la respuesta cuando el estado no permite bloqueo para confirmar que se retorna codigo 422 al orquestador con mensaje funcional claro - EV-204 - codigo 422 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_bloqueo_td
      | Caso |
      |4|

  @ev-205-como-analista-de-pruebas-quiero-rechazar-una-operacion-no-soportada-para-confirmar-que-se-retorna-codigo-400-al-orquesta
  Scenario Outline: HU-201-ADP-OCC - Como analista de pruebas quiero rechazar una operacion no soportada para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro - EV-205 - codigo 400 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_bloqueo_td
      | Caso |
      |5|

  @ev-206-como-analista-de-pruebas-quiero-manejar-una-falla-de-comunicacion-con-el-banco-para-confirmar-que-se-retorna-codigo-502-
  Scenario Outline: HU-201-ADP-OCC - Como analista de pruebas quiero manejar una falla de comunicacion con el banco para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro - EV-206 - codigo 502 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_bloqueo_td
      | Caso |
      |6|

  @ev-207-como-analista-de-pruebas-quiero-manejar-un-timeout-del-banco-para-confirmar-que-se-retorna-codigo-504-al-orquestador-con
  Scenario Outline: HU-201-ADP-OCC - Como analista de pruebas quiero manejar un timeout del banco para confirmar que se retorna codigo 504 al orquestador con mensaje funcional claro - EV-207 - codigo 504 - valida respuesta
    When ejecuta la operacion nueva "BLOQUEO_TD_DEFINITIVO" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_bloqueo_td
      | Caso |
      |7|

  @ev-213-como-analista-de-pruebas-quiero-ejecutar-la-actualizacion-de-datos-del-cliente-exitosamente-para-confirmar-que-la-actual
  Scenario Outline: HU-203-ADP-AVV - Como analista de pruebas quiero ejecutar la actualizacion de datos del cliente exitosamente para confirmar que la actualizacion se confirma con codigo exitoso y mensaje normalizado - EV-213 - codigo 200 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BAVV" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_actualizacion_datos
      | Caso |
      |1|

  @ev-214-como-analista-de-pruebas-quiero-confirmar-el-mapeo-de-error-de-negocio-para-confirmar-que-se-retorna-codigo-422-al-orque
  Scenario Outline: HU-203-ADP-AVV - Como analista de pruebas quiero confirmar el mapeo de error de negocio para confirmar que se retorna codigo 422 al orquestador con mensaje funcional claro - EV-214 - codigo 422 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BAVV" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_actualizacion_datos
      | Caso |
      |2|

  @ev-215-como-analista-de-pruebas-quiero-rechazar-una-operacion-no-soportada-para-confirmar-que-se-retorna-codigo-400-al-orquesta
  Scenario Outline: HU-203-ADP-AVV - Como analista de pruebas quiero rechazar una operacion no soportada para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro - EV-215 - codigo 400 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BAVV" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_actualizacion_datos
      | Caso |
      |3|

  @ev-216-como-analista-de-pruebas-quiero-manejar-una-falla-de-comunicacion-con-el-banco-para-confirmar-que-se-retorna-codigo-502-
  Scenario Outline: HU-203-ADP-AVV - Como analista de pruebas quiero manejar una falla de comunicacion con el banco para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro - EV-216 - codigo 502 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BAVV" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_actualizacion_datos
      | Caso |
      |4|

  @ev-217-como-analista-de-pruebas-quiero-manejar-un-timeout-del-banco-para-confirmar-que-se-retorna-codigo-504-al-orquestador-con
  Scenario Outline: HU-203-ADP-AVV - Como analista de pruebas quiero manejar un timeout del banco para confirmar que se retorna codigo 504 al orquestador con mensaje funcional claro - EV-217 - codigo 504 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BAVV" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_actualizacion_datos
      | Caso |
      |5|

  @ev-223-como-analista-de-pruebas-quiero-ejecutar-la-actualizacion-de-datos-del-cliente-exitosamente-para-confirmar-que-la-actual
  Scenario Outline: HU-203-ADP-BDB - Como analista de pruebas quiero ejecutar la actualizacion de datos del cliente exitosamente para confirmar que la actualizacion se confirma como exitosa y se retorna mensaje normalizado - EV-223 - codigo 200 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_actualizacion_datos
      | Caso |
      |1|

  @ev-224-como-analista-de-pruebas-quiero-confirmar-el-rechazo-por-datos-invalidos-para-confirmar-que-se-retorna-codigo-400-al-orq
  Scenario Outline: HU-203-ADP-BDB - Como analista de pruebas quiero confirmar el rechazo por datos invalidos para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro - EV-224 - codigo 400 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_actualizacion_datos
      | Caso |
      |2|

  @ev-225-como-analista-de-pruebas-quiero-confirmar-el-rechazo-por-cliente-no-encontrado-para-confirmar-que-se-retorna-codigo-400-
  Scenario Outline: HU-203-ADP-BDB - Como analista de pruebas quiero confirmar el rechazo por cliente no encontrado para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro - EV-225 - codigo 400 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_actualizacion_datos
      | Caso |
      |3|

  @ev-226-como-analista-de-pruebas-quiero-manejar-credenciales-o-acceso-de-integracion-invalido-para-confirmar-que-se-retorna-codi
  Scenario Outline: HU-203-ADP-BDB - Como analista de pruebas quiero manejar credenciales o acceso de integracion invalido para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro - EV-226 - codigo 502 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_actualizacion_datos
      | Caso |
      |4|

  @ev-227-como-analista-de-pruebas-quiero-rechazar-una-operacion-no-soportada-para-confirmar-que-se-retorna-codigo-400-al-orquesta
  Scenario Outline: HU-203-ADP-BDB - Como analista de pruebas quiero rechazar una operacion no soportada para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro - EV-227 - codigo 400 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_actualizacion_datos
      | Caso |
      |5|

  @ev-228-como-analista-de-pruebas-quiero-manejar-un-timeout-del-banco-para-confirmar-que-se-retorna-codigo-504-al-orquestador-con
  Scenario Outline: HU-203-ADP-BDB - Como analista de pruebas quiero manejar un timeout del banco para confirmar que se retorna codigo 504 al orquestador con mensaje funcional claro - EV-228 - codigo 504 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_actualizacion_datos
      | Caso |
      |6|

  @ev-234-como-analista-de-pruebas-quiero-ejecutar-la-actualizacion-de-datos-del-cliente-exitosamente-para-confirmar-que-la-actual
  Scenario Outline: HU-203-ADP-BPO - Como analista de pruebas quiero ejecutar la actualizacion de datos del cliente exitosamente para confirmar que la actualizacion se confirma en el MDM y se retorna resultado normalizado - EV-234 - codigo 200 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_actualizacion_datos
      | Caso |
      |1|

  @ev-235-como-analista-de-pruebas-quiero-confirmar-el-rechazo-por-datos-invalidos-para-confirmar-que-se-retorna-codigo-400-al-orq
  Scenario Outline: HU-203-ADP-BPO - Como analista de pruebas quiero confirmar el rechazo por datos invalidos para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro - EV-235 - codigo 400 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_actualizacion_datos
      | Caso |
      |2|

  @ev-236-como-analista-de-pruebas-quiero-confirmar-el-rechazo-por-cliente-no-encontrado-para-confirmar-que-se-retorna-codigo-400-
  Scenario Outline: HU-203-ADP-BPO - Como analista de pruebas quiero confirmar el rechazo por cliente no encontrado para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro - EV-236 - codigo 400 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_actualizacion_datos
      | Caso |
      |3|

  @ev-237-como-analista-de-pruebas-quiero-rechazar-una-operacion-no-soportada-para-confirmar-que-se-retorna-codigo-400-al-orquesta
  Scenario Outline: HU-203-ADP-BPO - Como analista de pruebas quiero rechazar una operacion no soportada para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro - EV-237 - codigo 400 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_actualizacion_datos
      | Caso |
      |4|

  @ev-238-como-analista-de-pruebas-quiero-manejar-un-error-interno-del-banco-para-confirmar-que-se-retorna-codigo-502-al-orquestad
  Scenario Outline: HU-203-ADP-BPO - Como analista de pruebas quiero manejar un error interno del banco para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro - EV-238 - codigo 502 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_actualizacion_datos
      | Caso |
      |5|

  @ev-239-como-analista-de-pruebas-quiero-manejar-un-timeout-del-banco-para-confirmar-que-se-retorna-codigo-504-al-orquestador-con
  Scenario Outline: HU-203-ADP-BPO - Como analista de pruebas quiero manejar un timeout del banco para confirmar que se retorna codigo 504 al orquestador con mensaje funcional claro - EV-239 - codigo 504 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_actualizacion_datos
      | Caso |
      |6|

  @ev-245-como-analista-de-pruebas-quiero-ejecutar-la-actualizacion-de-datos-del-cliente-exitosamente-para-confirmar-que-el-banco-
  Scenario Outline: HU-203-ADP-OCC - Como analista de pruebas quiero ejecutar la actualizacion de datos del cliente exitosamente para confirmar que el banco confirma la actualizacion y el adaptador retorna respuesta exitosa normalizada - EV-245 - codigo 200 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_actualizacion_datos
      | Caso |
      |1|

  @ev-246-como-analista-de-pruebas-quiero-confirmar-el-rechazo-por-datos-invalidos-para-confirmar-que-se-retorna-codigo-400-al-orq
  Scenario Outline: HU-203-ADP-OCC - Como analista de pruebas quiero confirmar el rechazo por datos invalidos para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro - EV-246 - codigo 400 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_actualizacion_datos
      | Caso |
      |2|

  @ev-247-como-analista-de-pruebas-quiero-manejar-error-al-obtener-token-de-integracion-para-confirmar-que-se-retorna-codigo-502-a
  Scenario Outline: HU-203-ADP-OCC - Como analista de pruebas quiero manejar error al obtener token de integracion para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro - EV-247 - codigo 502 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_actualizacion_datos
      | Caso |
      |3|

  @ev-248-como-analista-de-pruebas-quiero-manejar-token-invalido-despues-del-reintento-para-confirmar-que-se-retorna-codigo-502-al
  Scenario Outline: HU-203-ADP-OCC - Como analista de pruebas quiero manejar token invalido despues del reintento para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro - EV-248 - codigo 502 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_actualizacion_datos
      | Caso |
      |4|

  @ev-249-como-analista-de-pruebas-quiero-rechazar-una-operacion-no-soportada-para-confirmar-que-se-retorna-codigo-400-al-orquesta
  Scenario Outline: HU-203-ADP-OCC - Como analista de pruebas quiero rechazar una operacion no soportada para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro - EV-249 - codigo 400 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_actualizacion_datos
      | Caso |
      |5|

  @ev-250-como-analista-de-pruebas-quiero-manejar-un-timeout-del-banco-para-confirmar-que-se-retorna-codigo-504-al-orquestador-con
  Scenario Outline: HU-203-ADP-OCC - Como analista de pruebas quiero manejar un timeout del banco para confirmar que se retorna codigo 504 al orquestador con mensaje funcional claro - EV-250 - codigo 504 - valida respuesta
    When ejecuta la operacion nueva "ACTUALIZACION_DATOS" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_actualizacion_datos
      | Caso |
      |6|
