# language: en
@oficinas @local
Feature: Oficinas - Desbloqueo TD por PIN errado y activacion de plastico

  @hu302 @funcional @bavv @caso-01
  Scenario Outline: HU-302-ADP-AVV - Desbloqueo TD PIN - caso 1 - HTTP 200
    When ejecuta la operacion nueva "DESBLOQUEO_TD_PIN" del banco "BAVV" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_desbloqueo_td_pin
      | Caso |
      |1|

  @hu302 @funcional @bavv @caso-02
  Scenario Outline: HU-302-ADP-AVV - Desbloqueo TD PIN - caso 2 - HTTP 404
    When ejecuta la operacion nueva "DESBLOQUEO_TD_PIN" del banco "BAVV" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_desbloqueo_td_pin
      | Caso |
      |2|

  @hu302 @funcional @bavv @caso-03
  Scenario Outline: HU-302-ADP-AVV - Desbloqueo TD PIN - caso 3 - HTTP 409
    When ejecuta la operacion nueva "DESBLOQUEO_TD_PIN" del banco "BAVV" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_desbloqueo_td_pin
      | Caso |
      |3|

  @hu302 @funcional @bavv @caso-04
  Scenario Outline: HU-302-ADP-AVV - Desbloqueo TD PIN - caso 4 - HTTP 400
    When ejecuta la operacion nueva "DESBLOQUEO_TD_PIN" del banco "BAVV" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_desbloqueo_td_pin
      | Caso |
      |4|

  @hu302 @funcional @bbog @caso-01
  Scenario Outline: HU-302-ADP-BDB - Desbloqueo TD PIN - caso 1 - HTTP 200
    When ejecuta la operacion nueva "DESBLOQUEO_TD_PIN" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_desbloqueo_td_pin
      | Caso |
      |1|

  @hu302 @funcional @bbog @caso-02
  Scenario Outline: HU-302-ADP-BDB - Desbloqueo TD PIN - caso 2 - HTTP 404
    When ejecuta la operacion nueva "DESBLOQUEO_TD_PIN" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_desbloqueo_td_pin
      | Caso |
      |2|

  @hu302 @funcional @bbog @caso-03
  Scenario Outline: HU-302-ADP-BDB - Desbloqueo TD PIN - caso 3 - HTTP 409
    When ejecuta la operacion nueva "DESBLOQUEO_TD_PIN" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_desbloqueo_td_pin
      | Caso |
      |3|

  @hu302 @funcional @bbog @caso-04
  Scenario Outline: HU-302-ADP-BDB - Desbloqueo TD PIN - caso 4 - HTTP 400
    When ejecuta la operacion nueva "DESBLOQUEO_TD_PIN" del banco "BBOG" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_desbloqueo_td_pin
      | Caso |
      |4|

  @hu302 @funcional @bpop @caso-01
  Scenario Outline: HU-302-ADP-BPO - Desbloqueo TD PIN - caso 1 - HTTP 200
    When ejecuta la operacion nueva "DESBLOQUEO_TD_PIN" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_desbloqueo_td_pin
      | Caso |
      |1|

  @hu302 @funcional @bpop @caso-02
  Scenario Outline: HU-302-ADP-BPO - Desbloqueo TD PIN - caso 2 - HTTP 404
    When ejecuta la operacion nueva "DESBLOQUEO_TD_PIN" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_desbloqueo_td_pin
      | Caso |
      |2|

  @hu302 @funcional @bpop @caso-03
  Scenario Outline: HU-302-ADP-BPO - Desbloqueo TD PIN - caso 3 - HTTP 409
    When ejecuta la operacion nueva "DESBLOQUEO_TD_PIN" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_desbloqueo_td_pin
      | Caso |
      |3|

  @hu302 @funcional @bpop @caso-04
  Scenario Outline: HU-302-ADP-BPO - Desbloqueo TD PIN - caso 4 - HTTP 400
    When ejecuta la operacion nueva "DESBLOQUEO_TD_PIN" del banco "BPOP" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_desbloqueo_td_pin
      | Caso |
      |4|

  @hu302 @funcional @bocc @caso-01
  Scenario Outline: HU-302-ADP-OCC - Desbloqueo TD PIN - caso 1 - HTTP 200
    When ejecuta la operacion nueva "DESBLOQUEO_TD_PIN" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_desbloqueo_td_pin
      | Caso |
      |1|

  @hu302 @funcional @bocc @caso-02
  Scenario Outline: HU-302-ADP-OCC - Desbloqueo TD PIN - caso 2 - HTTP 404
    When ejecuta la operacion nueva "DESBLOQUEO_TD_PIN" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_desbloqueo_td_pin
      | Caso |
      |2|

  @hu302 @funcional @bocc @caso-03
  Scenario Outline: HU-302-ADP-OCC - Desbloqueo TD PIN - caso 3 - HTTP 409
    When ejecuta la operacion nueva "DESBLOQUEO_TD_PIN" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_desbloqueo_td_pin
      | Caso |
      |3|

  @hu302 @funcional @bocc @caso-04
  Scenario Outline: HU-302-ADP-OCC - Desbloqueo TD PIN - caso 4 - HTTP 400
    When ejecuta la operacion nueva "DESBLOQUEO_TD_PIN" del banco "BOCC" en el caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_desbloqueo_td_pin
      | Caso |
      |4|

  #@hu303 @funcional @bavv @caso-01
  #Scenario Outline: HU-303-ADP-AVV - Activacion plastico TD - caso 1 - HTTP 200
    #When ejecuta la operacion nueva "ACTIVACION_PLASTICO_TD" del banco "BAVV" en el caso <Caso>
    #Then la respuesta de la operacion nueva coincide con lo esperado

    #Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_activacion_plastico_td
      #| Caso |
      #|1|

  #@hu303 @funcional @bavv @caso-02
  #Scenario Outline: HU-303-ADP-AVV - Activacion plastico TD - caso 2 - HTTP 404
    #When ejecuta la operacion nueva "ACTIVACION_PLASTICO_TD" del banco "BAVV" en el caso <Caso>
    #Then la respuesta de la operacion nueva coincide con lo esperado

    #Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_activacion_plastico_td
      #| Caso |
      #|2|

  #@hu303 @funcional @bavv @caso-03
  #Scenario Outline: HU-303-ADP-AVV - Activacion plastico TD - caso 3 - HTTP 400
    #When ejecuta la operacion nueva "ACTIVACION_PLASTICO_TD" del banco "BAVV" en el caso <Caso>
    #Then la respuesta de la operacion nueva coincide con lo esperado

    #Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_activacion_plastico_td
      #| Caso |
      #|3|

  #@hu303 @funcional @bavv @caso-04
  #Scenario Outline: HU-303-ADP-AVV - Activacion plastico TD - caso 4 - HTTP 502
    #When ejecuta la operacion nueva "ACTIVACION_PLASTICO_TD" del banco "BAVV" en el caso <Caso>
    #Then la respuesta de la operacion nueva coincide con lo esperado

    #Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_activacion_plastico_td
      #| Caso |
      #|4|

  #@hu303 @funcional @bavv @caso-05
  #Scenario Outline: HU-303-ADP-AVV - Activacion plastico TD - caso 5 - HTTP 400
    #When ejecuta la operacion nueva "ACTIVACION_PLASTICO_TD" del banco "BAVV" en el caso <Caso>
    #Then la respuesta de la operacion nueva coincide con lo esperado

    #Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_activacion_plastico_td
      #| Caso |
      #|5|

  #@hu303 @funcional @bocc @caso-01
  #Scenario Outline: HU-303-ADP-OCC - Activacion plastico TD - caso 1 - HTTP 200
    #When ejecuta la operacion nueva "ACTIVACION_PLASTICO_TD" del banco "BOCC" en el caso <Caso>
    #Then la respuesta de la operacion nueva coincide con lo esperado

    #Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_activacion_plastico_td
      #| Caso |
      #|1|

  #@hu303 @funcional @bocc @caso-02
  #Scenario Outline: HU-303-ADP-OCC - Activacion plastico TD - caso 2 - HTTP 404
    #When ejecuta la operacion nueva "ACTIVACION_PLASTICO_TD" del banco "BOCC" en el caso <Caso>
    #Then la respuesta de la operacion nueva coincide con lo esperado

    #Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_activacion_plastico_td
      #| Caso |
      #|2|

  #@hu303 @funcional @bocc @caso-03
  #Scenario Outline: HU-303-ADP-OCC - Activacion plastico TD - caso 3 - HTTP 400
    #When ejecuta la operacion nueva "ACTIVACION_PLASTICO_TD" del banco "BOCC" en el caso <Caso>
    #Then la respuesta de la operacion nueva coincide con lo esperado

    #Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_activacion_plastico_td
      #| Caso |
      #|3|