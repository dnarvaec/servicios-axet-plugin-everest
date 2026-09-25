# language: en
@oficinas @bpo
Feature: Oficinas - Servicios Banco Popular

  @ev-109-adaptador-bpo-consulta-cliente-flujo-principal-exitoso
  Scenario Outline: [HU-101-ADP-BPO-CLIENTE] Adaptador BPO — Consulta Cliente - flujo principal exitoso - codigo 200
    When ejecuta la consulta de cliente BPO del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_consulta_cliente
      | Caso |
      |1|

  @ev-110-adaptador-bpo-consulta-cliente-dato-obligatorio-ausente
  Scenario Outline: [HU-101-ADP-BPO-CLIENTE] Adaptador BPO — Consulta Cliente - dato obligatorio ausente - codigo 200
    When ejecuta la consulta de cliente BPO del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_consulta_cliente
      | Caso |
      |2|

  @ev-111-adaptador-bpo-consulta-cliente-operacion-no-soportada
  Scenario Outline: [HU-101-ADP-BPO-CLIENTE] Adaptador BPO — Consulta Cliente - operación no soportada - codigo 200
    When ejecuta la consulta de cliente BPO del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_consulta_cliente
      | Caso |
      |3|

  @ev-112-adaptador-bpo-consulta-cliente-cliente-o-producto-no-encontrado
  Scenario Outline: [HU-101-ADP-BPO-CLIENTE] Adaptador BPO — Consulta Cliente - cliente o producto no encontrado - codigo 206
    When ejecuta la consulta de cliente BPO del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_consulta_cliente
      | Caso |
      |4|

  @ev-113-adaptador-bpo-consulta-cliente-error-tecnico-del-banco
  Scenario Outline: [HU-101-ADP-BPO-CLIENTE] Adaptador BPO — Consulta Cliente - error técnico del banco - codigo 400
    When ejecuta la consulta de cliente BPO del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_consulta_cliente
      | Caso |
      |5|

  @ev-116-adaptador-bpo-consulta-productos-flujo-principal-exitoso
  Scenario Outline: [HU-101-ADP-BPO] Adaptador BPO — Consulta Productos - flujo principal exitoso - codigo 200
    When ejecuta la consulta de productos BPO del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_consulta_productos
      | Caso |
      |1|

  @ev-117-adaptador-bpo-consulta-productos-dato-obligatorio-ausente
  Scenario Outline: [HU-101-ADP-BPO] Adaptador BPO — Consulta Productos - dato obligatorio ausente - codigo 200
    When ejecuta la consulta de productos BPO del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_consulta_productos
      | Caso |
      |2|

  @ev-118-adaptador-bpo-consulta-productos-operacion-no-soportada
  Scenario Outline: [HU-101-ADP-BPO] Adaptador BPO — Consulta Productos - operación no soportada - codigo 200
    When ejecuta la consulta de productos BPO del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_consulta_productos
      | Caso |
      |3|

  @ev-119-adaptador-bpo-consulta-productos-cliente-o-producto-no-encontrado
  Scenario Outline: [HU-101-ADP-BPO] Adaptador BPO — Consulta Productos - cliente o producto no encontrado - codigo 206
    When ejecuta la consulta de productos BPO del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_consulta_productos
      | Caso |
      |4|

  @ev-120-adaptador-bpo-consulta-productos-error-tecnico-del-banco
  Scenario Outline: [HU-101-ADP-BPO] Adaptador BPO — Consulta Productos - error técnico del banco - codigo 400
    When ejecuta la consulta de productos BPO del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_consulta_productos
      | Caso |
      |5|

  @ev-137-adaptador-bpo-consulta-detallada-flujo-principal-exitoso
  Scenario Outline: [HU-102-ADP-BPO] Adaptador BPO — Consulta Detallada - flujo principal exitoso - codigo 200
    When ejecuta la consulta de cartera BPO del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_consulta_cartera
      | Caso |
      |1|

  @ev-138-adaptador-bpo-consulta-detallada-dato-obligatorio-ausente
  Scenario Outline: [HU-102-ADP-BPO] Adaptador BPO — Consulta Detallada - dato obligatorio ausente - codigo 200
    When ejecuta la consulta de cartera BPO del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_consulta_cartera
      | Caso |
      |2|

  @ev-139-adaptador-bpo-consulta-detallada-operacion-no-soportada
  Scenario Outline: [HU-102-ADP-BPO] Adaptador BPO — Consulta Detallada - operación no soportada - codigo 200
    When ejecuta la consulta de cartera BPO del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_consulta_cartera
      | Caso |
      |3|

  @ev-140-adaptador-bpo-consulta-detallada-cliente-o-producto-no-encontrado
  Scenario Outline: [HU-102-ADP-BPO] Adaptador BPO — Consulta Detallada - cliente o producto no encontrado - codigo 206
    When ejecuta la consulta de cartera BPO del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_consulta_cartera
      | Caso |
      |4|

  @ev-141-adaptador-bpo-consulta-detallada-error-tecnico-del-banco
  Scenario Outline: [HU-102-ADP-BPO] Adaptador BPO — Consulta Detallada - error técnico del banco - codigo 400
    When ejecuta la consulta de cartera BPO del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bpop_consulta_cartera
      | Caso |
      |5|
