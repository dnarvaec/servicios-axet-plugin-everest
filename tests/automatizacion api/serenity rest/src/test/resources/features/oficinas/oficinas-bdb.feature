# language: en
@oficinas @bdb
Feature: Oficinas - Consultas ADP Banco de Bogota

  @ev-25-como-analista-de-pruebas-quiero-consultar-de-forma-unificada-los-datos-del-cliente-y-sus-productos-en-banco-de
  Scenario Outline: [HU-101-ADP-BDB] Como analista de pruebas quiero consultar de forma unificada los datos del cliente y sus productos en Banco de Bogotá para confirmar la consolidación completa en una sola respuesta - codigo 200
    When consulta general de cliente y productos en BDB del caso <Caso>
    Then la consulta general en BDB es exitosa

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_consulta_general
      | Caso |
      |1|

  @ev-26-como-analista-de-pruebas-quiero-consultar-un-cliente-que-no-tiene-productos-registrados-en-banco-de-bogota-par
  Scenario Outline: [HU-101-ADP-BDB] Como analista de pruebas quiero consultar un cliente que no tiene productos registrados en Banco de Bogotá para confirmar la respuesta controlada - codigo 206
    When consulta general de cliente y productos en BDB del caso <Caso>
    Then la respuesta de consulta general en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_consulta_general
      | Caso |
      |2|

  @ev-27-como-analista-de-pruebas-quiero-consultar-un-cliente-inexistente-en-banco-de-bogota-para-confirmar-el-mensaje-
  Scenario Outline: [HU-101-ADP-BDB] Como analista de pruebas quiero consultar un cliente inexistente en Banco de Bogotá para confirmar el mensaje de cliente no encontrado - codigo 400
    When consulta general de cliente y productos en BDB del caso <Caso>
    Then la respuesta de consulta general en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_consulta_general
      | Caso |
      |3|

  @ev-28-como-analista-de-pruebas-quiero-validar-la-respuesta-parcial-cuando-un-bloque-de-informacion-presenta-novedad-
  Scenario Outline: [HU-101-ADP-BDB] Como analista de pruebas quiero validar la respuesta parcial cuando un bloque de información presenta novedad para confirmar que la información disponible no se pierde - codigo 400
    When consulta general de cliente y productos en BDB del caso <Caso>
    Then la respuesta de consulta general en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_consulta_general
      | Caso |
      |4|

  @ev-29-como-analista-de-pruebas-quiero-enviar-una-solicitud-con-operacion-no-soportada-para-confirmar-el-rechazo-cont
  Scenario Outline: [HU-101-ADP-BDB] Como analista de pruebas quiero enviar una solicitud con operación no soportada para confirmar el rechazo controlado de la petición - codigo 206
    When consulta general de cliente y productos en BDB del caso <Caso>
    Then la respuesta de consulta general en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_consulta_general
      | Caso |
      |5|

  @ev-30-como-analista-de-pruebas-quiero-consultar-omitiendo-los-headers-de-identificacion-bancaria-para-confirmar-la-v
  Scenario Outline: [HU-101-ADP-BDB] Como analista de pruebas quiero consultar omitiendo los headers de identificación bancaria para confirmar la validación del sistema - codigo 200
    When consulta general de cliente y productos en BDB del caso <Caso>
    Then la consulta general en BDB es exitosa

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_consulta_general
      | Caso |
      |6|

  @ev-31-como-analista-de-pruebas-quiero-simular-timeout-o-falla-de-autenticacion-con-el-servicio-rest-de-banco-de-bogo
  Scenario Outline: [HU-101-ADP-BDB] Como analista de pruebas quiero simular timeout o falla de autenticación con el servicio REST de Banco de Bogotá para confirmar el código de error y auditoría - codigo 502
    When consulta general de cliente y productos en BDB del caso <Caso>
    Then la respuesta de consulta general en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_consulta_general
      | Caso |
      |7|

  @ev-49-como-analista-de-pruebas-quiero-consultar-el-detalle-de-un-credito-activo-en-banco-de-bogota-para-confirmar-la
  Scenario Outline: [HU-102-ADP-BDB] Como analista de pruebas quiero consultar el detalle de un crédito activo en Banco de Bogotá para confirmar la recepción directa de saldos, cuota mínima y fechas - codigo 200
    When consulta la cartera detallada en BDB del caso <Caso>
    Then la consulta de cartera detallada en BDB es exitosa

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cartera_detallada
      | Caso |
      |1|

  @ev-50-como-analista-de-pruebas-quiero-consultar-una-obligacion-inexistente-en-banco-de-bogota-para-confirmar-la-prop
  Scenario Outline: [HU-102-ADP-BDB] Como analista de pruebas quiero consultar una obligación inexistente en Banco de Bogotá para confirmar la propagación del código 404 - codigo 404
    When consulta la cartera detallada en BDB del caso <Caso>
    Then la respuesta de cartera detallada en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cartera_detallada
      | Caso |
      |2|

  @ev-51-como-analista-de-pruebas-quiero-simular-un-error-de-negocio-en-la-consulta-de-cartera-para-confirmar-su-mapeo-
  Scenario Outline: [HU-102-ADP-BDB] Como analista de pruebas quiero simular un error de negocio en la consulta de cartera para confirmar su mapeo al código 422 - codigo 400
    When consulta la cartera detallada en BDB del caso <Caso>
    Then la respuesta de cartera detallada en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cartera_detallada
      | Caso |
      |3|

  @ev-52-como-analista-de-pruebas-quiero-solicitar-la-consulta-de-cartera-con-una-operacion-no-soportada-para-confirmar
  Scenario Outline: [HU-102-ADP-BDB] Como analista de pruebas quiero solicitar la consulta de cartera con una operación no soportada para confirmar el rechazo 400 - codigo 400
    When consulta la cartera detallada en BDB del caso <Caso>
    Then la respuesta de cartera detallada en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cartera_detallada
      | Caso |
      |4|

  @ev-53-como-analista-de-pruebas-quiero-consultar-omitiendo-el-numero-de-obligacion-para-confirmar-la-validacion-del-d
  Scenario Outline: [HU-102-ADP-BDB] Como analista de pruebas quiero consultar omitiendo el número de obligación para confirmar la validación del dato requerido - codigo 422
    When consulta la cartera detallada en BDB del caso <Caso>
    Then la respuesta de cartera detallada en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cartera_detallada
      | Caso |
      |5|

  @ev-54-como-analista-de-pruebas-quiero-consultar-un-credito-cancelado-para-confirmar-que-se-entrega-el-estado-final-y
  Scenario Outline: [HU-102-ADP-BDB] Como analista de pruebas quiero consultar un crédito cancelado para confirmar que se entrega el estado final y saldo en cero - codigo 504
    When consulta la cartera detallada en BDB del caso <Caso>
    Then la respuesta de cartera detallada en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cartera_detallada
      | Caso |
      |6|

  @ev-55-como-analista-de-pruebas-quiero-simular-un-timeout-sockettimeoutexception-en-el-servicio-de-balances-de-bdb-pa
  Scenario Outline: [HU-102-ADP-BDB] Como analista de pruebas quiero simular un timeout (SocketTimeoutException) en el servicio de balances de BdB para confirmar el retorno de 504 - codigo 200
    When consulta la cartera detallada en BDB del caso <Caso>
    Then la consulta de cartera detallada en BDB es exitosa

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cartera_detallada
      | Caso |
      |7|

  @ev-73-como-analista-de-pruebas-quiero-consultar-el-detalle-de-una-tarjeta-de-credito-activa-en-banco-de-bogota-para-
  Scenario Outline: [HU-103-ADP-BDB] Como analista de pruebas quiero consultar el detalle de una tarjeta de crédito activa en Banco de Bogotá para confirmar la recepción de cupos, saldos y cuotas diferidas - codigo 200
    When consulta la tarjeta de credito detallada en BDB del caso <Caso>
    Then la consulta de tarjeta de credito detallada en BDB es exitosa

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_tc_detallada
      | Caso |
      |1|

  @ev-74-como-analista-de-pruebas-quiero-consultar-una-tarjeta-de-credito-no-registrada-en-banco-de-bogota-para-confirm
  Scenario Outline: [HU-103-ADP-BDB] Como analista de pruebas quiero consultar una tarjeta de crédito no registrada en Banco de Bogotá para confirmar el retorno de código 404 - codigo 404
    When consulta la tarjeta de credito detallada en BDB del caso <Caso>
    Then la respuesta de tarjeta de credito detallada en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_tc_detallada
      | Caso |
      |2|

  @ev-75-como-analista-de-pruebas-quiero-consultar-omitiendo-la-referencia-de-la-tarjeta-de-credito-para-confirmar-el-r
  Scenario Outline: [HU-103-ADP-BDB] Como analista de pruebas quiero consultar omitiendo la referencia de la tarjeta de crédito para confirmar el rechazo de la solicitud - codigo 400
    When consulta la tarjeta de credito detallada en BDB del caso <Caso>
    Then la respuesta de tarjeta de credito detallada en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_tc_detallada
      | Caso |
      |3|

  @ev-76-como-analista-de-pruebas-quiero-enviar-una-solicitud-de-tc-con-operacion-no-soportada-para-confirmar-el-rechaz
  Scenario Outline: [HU-103-ADP-BDB] Como analista de pruebas quiero enviar una solicitud de TC con operación no soportada para confirmar el rechazo con código 400 - codigo 400
    When consulta la tarjeta de credito detallada en BDB del caso <Caso>
    Then la respuesta de tarjeta de credito detallada en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_tc_detallada
      | Caso |
      |4|

  @ev-77-como-analista-de-pruebas-quiero-consultar-una-tarjeta-con-compras-diferidas-a-multiples-cuotas-para-confirmar-
  Scenario Outline: [HU-103-ADP-BDB] Como analista de pruebas quiero consultar una tarjeta con compras diferidas a múltiples cuotas para confirmar la entrega del número de cuotas activas - codigo 200
    When consulta la tarjeta de credito detallada en BDB del caso <Caso>
    Then la consulta de tarjeta de credito detallada en BDB es exitosa

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_tc_detallada
      | Caso |
      |5|

  @ev-78-como-analista-de-pruebas-quiero-consultar-una-tarjeta-cancelada-para-confirmar-la-entrega-de-estado-cancelada-
  Scenario Outline: [HU-103-ADP-BDB] Como analista de pruebas quiero consultar una tarjeta cancelada para confirmar la entrega de estado CANCELADA y saldos en cero - codigo 422
    When consulta la tarjeta de credito detallada en BDB del caso <Caso>
    Then la respuesta de tarjeta de credito detallada en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_tc_detallada
      | Caso |
      |6|

  @ev-79-como-analista-de-pruebas-quiero-simular-un-error-tecnico-o-timeout-en-balances-management-v2-para-confirmar-el
  Scenario Outline: [HU-103-ADP-BDB] Como analista de pruebas quiero simular un error técnico o timeout en balances-management-v2 para confirmar el retorno de 502/504 y auditoría - codigo 502
    When consulta la tarjeta de credito detallada en BDB del caso <Caso>
    Then la respuesta de tarjeta de credito detallada en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_tc_detallada
      | Caso |
      |7|

  @ev-97-como-analista-de-pruebas-quiero-consultar-el-detalle-de-un-cdt-activo-en-banco-de-bogota-para-confirmar-la-rec
  Scenario Outline: [HU-104-ADP-BDB] Como analista de pruebas quiero consultar el detalle de un CDT activo en Banco de Bogotá para confirmar la recepción de monto, tasa EA, fechas e intereses acumulados - codigo 200
    When consulta el CDT detallado en BDB del caso <Caso>
    Then la consulta de CDT detallado en BDB es exitosa

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cdt_detallado
      | Caso |
      |1|

  @ev-98-como-analista-de-pruebas-quiero-consultar-un-cdt-no-registrado-en-banco-de-bogota-para-confirmar-el-retorno-de
  Scenario Outline: [HU-104-ADP-BDB] Como analista de pruebas quiero consultar un CDT no registrado en Banco de Bogotá para confirmar el retorno de código 404 - codigo 404
    When consulta el CDT detallado en BDB del caso <Caso>
    Then la respuesta de CDT detallado en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cdt_detallado
      | Caso |
      |2|

  @ev-99-como-analista-de-pruebas-quiero-solicitar-la-consulta-de-cdt-omitiendo-el-identificador-de-producto-para-confi
  Scenario Outline: [HU-104-ADP-BDB] Como analista de pruebas quiero solicitar la consulta de CDT omitiendo el identificador de producto para confirmar el rechazo de la solicitud - codigo 400
    When consulta el CDT detallado en BDB del caso <Caso>
    Then la respuesta de CDT detallado en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cdt_detallado
      | Caso |
      |3|

  @ev-100-como-analista-de-pruebas-quiero-enviar-una-solicitud-de-cdt-con-operacion-no-soportada-para-confirmar-el-recha
  Scenario Outline: [HU-104-ADP-BDB] Como analista de pruebas quiero enviar una solicitud de CDT con operación no soportada para confirmar el rechazo con código 400 - codigo 400
    When consulta el CDT detallado en BDB del caso <Caso>
    Then la respuesta de CDT detallado en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cdt_detallado
      | Caso |
      |4|

  @ev-101-como-analista-de-pruebas-quiero-consultar-un-cdt-con-intereses-acumulados-liquidados-a-la-fecha-para-confirmar
  Scenario Outline: [HU-104-ADP-BDB] Como analista de pruebas quiero consultar un CDT con intereses acumulados liquidados a la fecha para confirmar la consistencia del monto de rendimiento - codigo 422
    When consulta el CDT detallado en BDB del caso <Caso>
    Then la respuesta de CDT detallado en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cdt_detallado
      | Caso |
      |5|

  @ev-102-como-analista-de-pruebas-quiero-consultar-un-cdt-con-periodicidad-de-pago-mensual-para-confirmar-la-entrega-de
  Scenario Outline: [HU-104-ADP-BDB] Como analista de pruebas quiero consultar un CDT con periodicidad de pago mensual para confirmar la entrega de la periodicidad pactada - codigo 504
    When consulta el CDT detallado en BDB del caso <Caso>
    Then la respuesta de CDT detallado en BDB coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cdt_detallado
      | Caso |
      |6|

  @ev-103-como-analista-de-pruebas-quiero-simular-un-error-tecnico-o-timeout-en-balances-management-v2-para-confirmar-el
  Scenario Outline: [HU-104-ADP-BDB] Como analista de pruebas quiero simular un error técnico o timeout en balances-management-v2 para confirmar el retorno de 502/504 y auditoría - codigo 200
    When consulta el CDT detallado en BDB del caso <Caso>
    Then la consulta de CDT detallado en BDB es exitosa
    And el envelope de respuesta de Oficinas BDB esta presente

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cdt_detallado
      | Caso |
      |7|
