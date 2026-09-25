# language: en
@oficinas @orq
Feature: Oficinas - Consultas ORQ

  @ev-151-orquestador-consulta-detallada-de-tc-flujo-principal-exitoso
  Scenario Outline: [HU-103-ORQ] Orquestador — Consulta Detallada de TC - flujo principal exitoso - codigo 200
    When ejecuta la consulta ORQ de TC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@orq_consulta_tc
      | Caso |
      |1|

  @ev-152-orquestador-consulta-detallada-de-tc-dato-obligatorio-ausente
  Scenario Outline: [HU-103-ORQ] Orquestador — Consulta Detallada de TC - dato obligatorio ausente - codigo 200
    When ejecuta la consulta ORQ de TC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@orq_consulta_tc
      | Caso |
      |2|

  @ev-153-orquestador-consulta-detallada-de-tc-operacion-no-soportada
  Scenario Outline: [HU-103-ORQ] Orquestador — Consulta Detallada de TC - operación no soportada - codigo 200
    When ejecuta la consulta ORQ de TC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@orq_consulta_tc
      | Caso |
      |3|

  @ev-154-orquestador-consulta-detallada-de-tc-cliente-o-producto-no-encontrado
  Scenario Outline: [HU-103-ORQ] Orquestador — Consulta Detallada de TC - cliente o producto no encontrado - codigo 206
    When ejecuta la consulta ORQ de TC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@orq_consulta_tc
      | Caso |
      |4|

  @ev-155-orquestador-consulta-detallada-de-tc-error-tecnico-del-banco
  Scenario Outline: [HU-103-ORQ] Orquestador — Consulta Detallada de TC - error técnico del banco - codigo 400
    When ejecuta la consulta ORQ de TC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@orq_consulta_tc
      | Caso |
      |5|

  @ev-158-orquestador-consulta-detallada-de-cdt-flujo-principal-exitoso
  Scenario Outline: [HU-104-ORQ] Orquestador — Consulta Detallada de CDT - flujo principal exitoso - codigo 200
    When ejecuta la consulta ORQ de CDT del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@orq_consulta_cdt
      | Caso |
      |1|

  @ev-159-orquestador-consulta-detallada-de-cdt-dato-obligatorio-ausente
  Scenario Outline: [HU-104-ORQ] Orquestador — Consulta Detallada de CDT - dato obligatorio ausente - codigo 200
    When ejecuta la consulta ORQ de CDT del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@orq_consulta_cdt
      | Caso |
      |2|

  @ev-160-orquestador-consulta-detallada-de-cdt-operacion-no-soportada
  Scenario Outline: [HU-104-ORQ] Orquestador — Consulta Detallada de CDT - operación no soportada - codigo 200
    When ejecuta la consulta ORQ de CDT del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@orq_consulta_cdt
      | Caso |
      |3|

  @ev-161-orquestador-consulta-detallada-de-cdt-cliente-o-producto-no-encontrado
  Scenario Outline: [HU-104-ORQ] Orquestador — Consulta Detallada de CDT - cliente o producto no encontrado - codigo 206
    When ejecuta la consulta ORQ de CDT del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@orq_consulta_cdt
      | Caso |
      |4|

  @ev-162-orquestador-consulta-detallada-de-cdt-error-tecnico-del-banco
  Scenario Outline: [HU-104-ORQ] Orquestador — Consulta Detallada de CDT - error técnico del banco - codigo 400
    When ejecuta la consulta ORQ de CDT del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@orq_consulta_cdt
      | Caso |
      |5|
