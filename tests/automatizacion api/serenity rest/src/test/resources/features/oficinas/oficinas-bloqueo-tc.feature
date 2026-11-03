# language: en
@oficinas @actualizaciones @bloqueo_tc
Feature: Oficinas - Bloqueo de tarjeta de credito por banco

  @ev-256-como-analista-quiero-confirmar-el-bloqueo-exitoso-de-una-tarjeta-de-credito
  Scenario Outline: HU-202-ADP-BPO - Como analista quiero confirmar el bloqueo exitoso de una tarjeta de crédito - EV-256 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_bloqueo_tc
      | Caso |
      |1|

  @ev-257-como-analista-quiero-informar-una-tarjeta-no-encontrada
  Scenario Outline: HU-202-ADP-BPO - Como analista quiero informar una tarjeta no encontrada - EV-257 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_bloqueo_tc
      | Caso |
      |2|

  @ev-258-como-analista-quiero-informar-un-tiempo-de-espera-en-el-bloqueo
  Scenario Outline: HU-202-ADP-BPO - Como analista quiero informar un tiempo de espera en el bloqueo - EV-258 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_bloqueo_tc
      | Caso |
      |3|

  @ev-259-como-analista-quiero-rechazar-una-operacion-no-soportada
  Scenario Outline: HU-202-ADP-BPO - Como analista quiero rechazar una operación no soportada - EV-259 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_bloqueo_tc
      | Caso |
      |4|

  @ev-260-como-analista-quiero-confirmar-el-bloqueo-preventivo-de-una-tarjeta
  Scenario Outline: HU-202-ADP-BDB - Como analista quiero confirmar el bloqueo preventivo de una tarjeta - EV-260 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_bloqueo_tc
      | Caso |
      |1|

  @ev-261-como-analista-quiero-informar-el-rechazo-de-una-solicitud-de-bloqueo
  Scenario Outline: HU-202-ADP-BDB - Como analista quiero informar el rechazo de una solicitud de bloqueo - EV-261 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_bloqueo_tc
      | Caso |
      |2|

  @ev-262-como-analista-quiero-informar-tiempo-de-espera-del-banco @mock_gap
  Scenario Outline: HU-202-ADP-BDB - Como analista quiero informar tiempo de espera del banco - EV-262 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_bloqueo_tc
      | Caso |
      |3|

  @ev-263-como-analista-quiero-informar-un-conflicto-al-bloquear-la-tarjeta
  Scenario Outline: HU-202-ADP-BDB - Como analista quiero informar un conflicto al bloquear la tarjeta - EV-263 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_bloqueo_tc
      | Caso |
      |4|

  @ev-264-como-analista-quiero-informar-un-error-interno-del-banco
  Scenario Outline: HU-202-ADP-BDB - Como analista quiero informar un error interno del banco - EV-264 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_bloqueo_tc
      | Caso |
      |5|

  @ev-265-como-analista-quiero-informar-una-falla-de-conectividad @mock_gap
  Scenario Outline: HU-202-ADP-BDB - Como analista quiero informar una falla de conectividad - EV-265 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_bloqueo_tc
      | Caso |
      |6|

  @ev-266-como-analista-quiero-rechazar-una-operacion-no-soportada
  Scenario Outline: HU-202-ADP-BDB - Como analista quiero rechazar una operación no soportada - EV-266 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_bloqueo_tc
      | Caso |
      |7|

  @ev-267-como-analista-quiero-confirmar-el-bloqueo-definitivo-de-una-tarjeta
  Scenario Outline: HU-202-ADP-OCC - Como analista quiero confirmar el bloqueo definitivo de una tarjeta - EV-267 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_bloqueo_tc
      | Caso |
      |1|

  @ev-268-como-analista-quiero-informar-una-tarjeta-no-bloqueable
  Scenario Outline: HU-202-ADP-OCC - Como analista quiero informar una tarjeta no bloqueable - EV-268 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_bloqueo_tc
      | Caso |
      |2|

  @ev-269-como-analista-quiero-renovar-la-credencial-y-reintentar-el-bloqueo @mock_gap
  Scenario Outline: HU-202-ADP-OCC - Como analista quiero renovar la credencial y reintentar el bloqueo - EV-269 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_bloqueo_tc
      | Caso |
      |3|

  @ev-270-como-analista-quiero-informar-una-falla-al-obtener-la-credencial @mock_gap
  Scenario Outline: HU-202-ADP-OCC - Como analista quiero informar una falla al obtener la credencial - EV-270 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_bloqueo_tc
      | Caso |
      |4|

  @ev-271-como-analista-quiero-informar-una-falla-despues-del-reintento @mock_gap
  Scenario Outline: HU-202-ADP-OCC - Como analista quiero informar una falla después del reintento - EV-271 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_bloqueo_tc
      | Caso |
      |5|

  @ev-272-como-analista-quiero-informar-tiempo-de-espera-del-banco @mock_gap
  Scenario Outline: HU-202-ADP-OCC - Como analista quiero informar tiempo de espera del banco - EV-272 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_bloqueo_tc
      | Caso |
      |6|

  @ev-273-como-analista-quiero-informar-una-falla-de-conectividad @mock_gap
  Scenario Outline: HU-202-ADP-OCC - Como analista quiero informar una falla de conectividad - EV-273 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_bloqueo_tc
      | Caso |
      |7|

  @ev-274-como-analista-quiero-confirmar-el-bloqueo-exitoso-de-una-tarjeta
  Scenario Outline: HU-202-ADP-AVV - Como analista quiero confirmar el bloqueo exitoso de una tarjeta - EV-274 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BAVV" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_bloqueo_tc
      | Caso |
      |1|

  @ev-275-como-analista-quiero-informar-un-error-de-negocio-del-bloqueo
  Scenario Outline: HU-202-ADP-AVV - Como analista quiero informar un error de negocio del bloqueo - EV-275 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BAVV" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_bloqueo_tc
      | Caso |
      |2|

  @ev-276-como-analista-quiero-informar-un-error-interno-del-banco
  Scenario Outline: HU-202-ADP-AVV - Como analista quiero informar un error interno del banco - EV-276 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BAVV" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_bloqueo_tc
      | Caso |
      |3|

  @ev-277-como-analista-quiero-informar-un-tiempo-de-espera-en-el-bloqueo
  Scenario Outline: HU-202-ADP-AVV - Como analista quiero informar un tiempo de espera en el bloqueo - EV-277 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BAVV" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_bloqueo_tc
      | Caso |
      |4|

  @ev-278-como-analista-quiero-rechazar-una-operacion-no-soportada
  Scenario Outline: HU-202-ADP-AVV - Como analista quiero rechazar una operación no soportada - EV-278 - valida respuesta HTTP
    When ejecuta la operacion nueva "BLOQUEO_TC" del banco "BAVV" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_bloqueo_tc
      | Caso |
      |5|
