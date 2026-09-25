# language: en
@oficinas @occ
Feature: Oficinas - Servicios Banco de Occidente

  @ev-123-adaptador-occ-consulta-cliente-flujo-principal-exitoso
  Scenario Outline: [HU-101-ADP-OCC-CLIENTE] Adaptador OCC — Consulta Cliente - flujo principal exitoso - codigo 200
    When ejecuta la consulta de cliente OCC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_consulta_cliente
      | Caso |
      |1|

  @ev-124-adaptador-occ-consulta-cliente-dato-obligatorio-ausente
  Scenario Outline: [HU-101-ADP-OCC-CLIENTE] Adaptador OCC — Consulta Cliente - dato obligatorio ausente - codigo 200
    When ejecuta la consulta de cliente OCC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_consulta_cliente
      | Caso |
      |2|

  @ev-125-adaptador-occ-consulta-cliente-operacion-no-soportada
  Scenario Outline: [HU-101-ADP-OCC-CLIENTE] Adaptador OCC — Consulta Cliente - operación no soportada - codigo 200
    When ejecuta la consulta de cliente OCC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_consulta_cliente
      | Caso |
      |3|

  @ev-126-adaptador-occ-consulta-cliente-cliente-o-producto-no-encontrado
  Scenario Outline: [HU-101-ADP-OCC-CLIENTE] Adaptador OCC — Consulta Cliente - cliente o producto no encontrado - codigo 206
    When ejecuta la consulta de cliente OCC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_consulta_cliente
      | Caso |
      |4|

  @ev-127-adaptador-occ-consulta-cliente-error-tecnico-del-banco
  Scenario Outline: [HU-101-ADP-OCC-CLIENTE] Adaptador OCC — Consulta Cliente - error técnico del banco - codigo 400
    When ejecuta la consulta de cliente OCC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_consulta_cliente
      | Caso |
      |5|

  @ev-130-adaptador-occ-consulta-productos-flujo-principal-exitoso
  Scenario Outline: [HU-101-ADP-OCC] Adaptador OCC — Consulta Productos - flujo principal exitoso - codigo 200
    When ejecuta la consulta de productos OCC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_consulta_productos
      | Caso |
      |1|

  @ev-131-adaptador-occ-consulta-productos-dato-obligatorio-ausente
  Scenario Outline: [HU-101-ADP-OCC] Adaptador OCC — Consulta Productos - dato obligatorio ausente - codigo 200
    When ejecuta la consulta de productos OCC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_consulta_productos
      | Caso |
      |2|

  @ev-132-adaptador-occ-consulta-productos-operacion-no-soportada
  Scenario Outline: [HU-101-ADP-OCC] Adaptador OCC — Consulta Productos - operación no soportada - codigo 200
    When ejecuta la consulta de productos OCC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_consulta_productos
      | Caso |
      |3|

  @ev-133-adaptador-occ-consulta-productos-cliente-o-producto-no-encontrado
  Scenario Outline: [HU-101-ADP-OCC] Adaptador OCC — Consulta Productos - cliente o producto no encontrado - codigo 206
    When ejecuta la consulta de productos OCC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_consulta_productos
      | Caso |
      |4|

  @ev-134-adaptador-occ-consulta-productos-error-tecnico-del-banco
  Scenario Outline: [HU-101-ADP-OCC] Adaptador OCC — Consulta Productos - error técnico del banco - codigo 400
    When ejecuta la consulta de productos OCC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_consulta_productos
      | Caso |
      |5|

  @ev-144-adaptador-occ-consulta-detallada-flujo-principal-exitoso
  Scenario Outline: [HU-102-ADP-OCC] Adaptador OCC — Consulta Detallada - flujo principal exitoso - codigo 200
    When ejecuta la consulta de CDT OCC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_consulta_cdt
      | Caso |
      |1|

  @ev-145-adaptador-occ-consulta-detallada-dato-obligatorio-ausente
  Scenario Outline: [HU-102-ADP-OCC] Adaptador OCC — Consulta Detallada - dato obligatorio ausente - codigo 200
    When ejecuta la consulta de CDT OCC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_consulta_cdt
      | Caso |
      |2|

  @ev-146-adaptador-occ-consulta-detallada-operacion-no-soportada
  Scenario Outline: [HU-102-ADP-OCC] Adaptador OCC — Consulta Detallada - operación no soportada - codigo 200
    When ejecuta la consulta de CDT OCC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_consulta_cdt
      | Caso |
      |3|

  @ev-147-adaptador-occ-consulta-detallada-cliente-o-producto-no-encontrado
  Scenario Outline: [HU-102-ADP-OCC] Adaptador OCC — Consulta Detallada - cliente o producto no encontrado - codigo 206
    When ejecuta la consulta de CDT OCC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_consulta_cdt
      | Caso |
      |4|

  @ev-148-adaptador-occ-consulta-detallada-error-tecnico-del-banco
  Scenario Outline: [HU-102-ADP-OCC] Adaptador OCC — Consulta Detallada - error técnico del banco - codigo 400
    When ejecuta la consulta de CDT OCC del caso <Caso>
    Then la respuesta de la operacion nueva coincide con lo esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@occ_consulta_cdt
      | Caso |
      |5|
