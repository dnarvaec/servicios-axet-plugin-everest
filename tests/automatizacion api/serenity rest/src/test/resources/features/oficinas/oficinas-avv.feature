# language: en
@oficinas @avv
Feature: Oficinas - Consultas ADP AV Villas

  @ev-1-como-analista-de-pruebas-quiero-consultar-los-datos-personales-y-de-contacto-de-un-cliente-existente-para-conf
  Scenario Outline: [HU-101-ADP-AVV-CLIENTE] Como analista de pruebas quiero consultar los datos personales y de contacto de un cliente existente para confirmar la recepción exitosa y normalizada de su información - codigo 200
    When consulta el cliente en AVV del caso <Caso>
    Then la consulta de cliente en AVV es exitosa

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_cliente
      | Caso |
      |1|

  @ev-2-como-analista-de-pruebas-quiero-consultar-los-datos-de-un-cliente-no-registrado-para-confirmar-que-el-sistema-
  Scenario Outline: [HU-101-ADP-AVV-CLIENTE] Como analista de pruebas quiero consultar los datos de un cliente no registrado para confirmar que el sistema responde con la notificación de cliente no encontrado - codigo 206
    When consulta el cliente en AVV del caso <Caso>
    Then la respuesta de consulta de cliente en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_cliente
      | Caso |
      |2|

  @ev-3-como-analista-de-pruebas-quiero-intentar-una-consulta-enviando-una-operacion-no-soportada-para-confirmar-que-e
  Scenario Outline: [HU-101-ADP-AVV-CLIENTE] Como analista de pruebas quiero intentar una consulta enviando una operación no soportada para confirmar que el sistema rechaza la solicitud defensivamente - codigo 400
    When consulta el cliente en AVV del caso <Caso>
    Then la respuesta de consulta de cliente en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_cliente
      | Caso |
      |3|

  @ev-4-como-analista-de-pruebas-quiero-consultar-los-datos-del-cliente-omitiendo-el-numero-de-documento-para-confirma
  Scenario Outline: [HU-101-ADP-AVV-CLIENTE] Como analista de pruebas quiero consultar los datos del cliente omitiendo el número de documento para confirmar la validación y respuesta de error correspondiente - codigo 400
    When consulta el cliente en AVV del caso <Caso>
    Then la respuesta de consulta de cliente en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_cliente
      | Caso |
      |4|

  @ev-5-como-analista-de-pruebas-quiero-consultar-los-datos-del-cliente-con-un-tipo-de-documento-no-admitido-para-conf
  Scenario Outline: [HU-101-ADP-AVV-CLIENTE] Como analista de pruebas quiero consultar los datos del cliente con un tipo de documento no admitido para confirmar el rechazo de la solicitud - codigo 200
    When consulta el cliente en AVV del caso <Caso>
    Then la consulta de cliente en AVV es exitosa

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_cliente
      | Caso |
      |5|

  @ev-6-como-analista-de-pruebas-quiero-consultar-un-cliente-con-nombres-y-direcciones-extensos-para-confirmar-la-corr
  Scenario Outline: [HU-101-ADP-AVV-CLIENTE] Como analista de pruebas quiero consultar un cliente con nombres y direcciones extensos para confirmar la correcta integridad y completitud de la respuesta - codigo 502
    When consulta el cliente en AVV del caso <Caso>
    Then la respuesta de consulta de cliente en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_cliente
      | Caso |
      |6|

  @ev-7-como-analista-de-pruebas-quiero-simular-una-falla-o-indisponibilidad-en-el-servicio-bancario-para-confirmar-el
  Scenario Outline: [HU-101-ADP-AVV-CLIENTE] Como analista de pruebas quiero simular una falla o indisponibilidad en el servicio bancario para confirmar el manejo de error y trazabilidad - codigo 504
    When consulta el cliente en AVV del caso <Caso>
    Then la respuesta de consulta de cliente en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_cliente
      | Caso |
      |7|

  @ev-13-como-analista-de-pruebas-quiero-consultar-el-portafolio-de-productos-de-un-cliente-activo-para-confirmar-la-re
  Scenario Outline: [HU-101-ADP-AVV] Como analista de pruebas quiero consultar el portafolio de productos de un cliente activo para confirmar la recepción consolidada de cuentas, CDT, carteras y tarjetas - codigo 200
    When consulta los productos en AVV del caso <Caso>
    Then la consulta de productos en AVV es exitosa

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_productos
      | Caso |
      |1|

  @ev-14-como-analista-de-pruebas-quiero-consultar-los-productos-de-un-cliente-que-no-tiene-productos-activos-para-conf
  Scenario Outline: [HU-101-ADP-AVV] Como analista de pruebas quiero consultar los productos de un cliente que no tiene productos activos para confirmar la respuesta de cliente sin productos - codigo 206
    When consulta los productos en AVV del caso <Caso>
    Then la respuesta de consulta de productos en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_productos
      | Caso |
      |2|

  @ev-15-como-analista-de-pruebas-quiero-consultar-productos-de-un-cliente-no-registrado-para-confirmar-la-notificacion
  Scenario Outline: [HU-101-ADP-AVV] Como analista de pruebas quiero consultar productos de un cliente no registrado para confirmar la notificación de cliente no encontrado - codigo 400
    When consulta los productos en AVV del caso <Caso>
    Then la respuesta de consulta de productos en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_productos
      | Caso |
      |3|

  @ev-16-como-analista-de-pruebas-quiero-solicitar-la-consulta-de-productos-con-una-operacion-no-soportada-para-confirm
  Scenario Outline: [HU-101-ADP-AVV] Como analista de pruebas quiero solicitar la consulta de productos con una operación no soportada para confirmar el rechazo de la petición - codigo 400
    When consulta los productos en AVV del caso <Caso>
    Then la respuesta de consulta de productos en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_productos
      | Caso |
      |4|

  @ev-17-como-analista-de-pruebas-quiero-consultar-productos-omitiendo-los-datos-de-identificacion-para-confirmar-la-va
  Scenario Outline: [HU-101-ADP-AVV] Como analista de pruebas quiero consultar productos omitiendo los datos de identificación para confirmar la validación del sistema - codigo 206
    When consulta los productos en AVV del caso <Caso>
    Then la respuesta de consulta de productos en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_productos
      | Caso |
      |5|

  @ev-18-como-analista-de-pruebas-quiero-verificar-la-consulta-de-productos-para-un-cliente-con-mas-de-10-productos-par
  Scenario Outline: [HU-101-ADP-AVV] Como analista de pruebas quiero verificar la consulta de productos para un cliente con más de 10 productos para confirmar la completitud del listado - codigo 200
    When consulta los productos en AVV del caso <Caso>
    Then la consulta de productos en AVV es exitosa

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_productos
      | Caso |
      |6|

  @ev-19-como-analista-de-pruebas-quiero-simular-un-error-tecnico-o-timeout-en-el-servicio-soap-bancario-para-confirmar
  Scenario Outline: [HU-101-ADP-AVV] Como analista de pruebas quiero simular un error técnico o timeout en el servicio SOAP bancario para confirmar el manejo de error y Circuit Breaker - codigo 502
    When consulta los productos en AVV del caso <Caso>
    Then la respuesta de consulta de productos en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_productos
      | Caso |
      |7|

  @ev-37-como-analista-de-pruebas-quiero-consultar-el-detalle-de-una-obligacion-de-cartera-activa-para-confirmar-la-obt
  Scenario Outline: [HU-102-ADP-AVV] Como analista de pruebas quiero consultar el detalle de una obligación de cartera activa para confirmar la obtención de sus saldos y estado - codigo 200
    When consulta la cartera detallada en AVV del caso <Caso>
    Then la consulta de cartera detallada en AVV es exitosa

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cartera_detallada
      | Caso |
      |1|

  @ev-38-como-analista-de-pruebas-quiero-consultar-una-obligacion-que-no-existe-para-confirmar-la-respuesta-de-error-o-
  Scenario Outline: [HU-102-ADP-AVV] Como analista de pruebas quiero consultar una obligación que no existe para confirmar la respuesta de error o no encontrada - codigo 206
    When consulta la cartera detallada en AVV del caso <Caso>
    Then la respuesta de cartera detallada en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cartera_detallada
      | Caso |
      |2|

  @ev-39-como-analista-de-pruebas-quiero-solicitar-la-consulta-de-cartera-omitiendo-el-numero-de-obligacion-para-confir
  Scenario Outline: [HU-102-ADP-AVV] Como analista de pruebas quiero solicitar la consulta de cartera omitiendo el número de obligación para confirmar el rechazo de la solicitud - codigo 400
    When consulta la cartera detallada en AVV del caso <Caso>
    Then la respuesta de cartera detallada en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cartera_detallada
      | Caso |
      |3|

  @ev-40-como-analista-de-pruebas-quiero-intentar-la-consulta-de-cartera-con-una-operacion-no-soportada-para-confirmar-
  Scenario Outline: [HU-102-ADP-AVV] Como analista de pruebas quiero intentar la consulta de cartera con una operación no soportada para confirmar el rechazo 400 - codigo 400
    When consulta la cartera detallada en AVV del caso <Caso>
    Then la respuesta de cartera detallada en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cartera_detallada
      | Caso |
      |4|

  @ev-41-como-analista-de-pruebas-quiero-consultar-una-obligacion-con-caracteres-no-numericos-para-confirmar-la-validac
  Scenario Outline: [HU-102-ADP-AVV] Como analista de pruebas quiero consultar una obligación con caracteres no numéricos para confirmar la validación del identificador - codigo 200
    When consulta la cartera detallada en AVV del caso <Caso>
    Then la consulta de cartera detallada en AVV es exitosa

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cartera_detallada
      | Caso |
      |5|

  @ev-42-como-analista-de-pruebas-quiero-consultar-una-obligacion-en-estado-especial-de-mora-o-castigada-para-confirmar
  Scenario Outline: [HU-102-ADP-AVV] Como analista de pruebas quiero consultar una obligación en estado especial de mora o castigada para confirmar el detalle del estado de deuda - codigo 502
    When consulta la cartera detallada en AVV del caso <Caso>
    Then la respuesta de cartera detallada en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cartera_detallada
      | Caso |
      |6|

  @ev-43-como-analista-de-pruebas-quiero-simular-un-error-soap-fault-o-timeout-en-el-backend-de-av-villas-para-confirma
  Scenario Outline: [HU-102-ADP-AVV] Como analista de pruebas quiero simular un error SOAP fault o timeout en el backend de AV Villas para confirmar la propagación del error y auditoría - codigo 504
    When consulta la cartera detallada en AVV del caso <Caso>
    Then la respuesta de cartera detallada en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cartera_detallada
      | Caso |
      |7|

  @ev-61-como-analista-de-pruebas-quiero-consultar-el-detalle-de-una-tarjeta-de-credito-activa-para-confirmar-la-obtenc
  Scenario Outline: [HU-103-ADP-AVV] Como analista de pruebas quiero consultar el detalle de una tarjeta de crédito activa para confirmar la obtención de cupos, saldos y estado - codigo 200
    When consulta la tarjeta de credito detallada en AVV del caso <Caso>
    Then la consulta de tarjeta de credito detallada en AVV es exitosa

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_tc_detallada
      | Caso |
      |1|

  @ev-62-como-analista-de-pruebas-quiero-consultar-una-tarjeta-de-credito-inexistente-para-confirmar-el-retorno-de-erro
  Scenario Outline: [HU-103-ADP-AVV] Como analista de pruebas quiero consultar una tarjeta de crédito inexistente para confirmar el retorno de error 404 - codigo 404
    When consulta la tarjeta de credito detallada en AVV del caso <Caso>
    Then la respuesta de tarjeta de credito detallada en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_tc_detallada
      | Caso |
      |2|

  @ev-63-como-analista-de-pruebas-quiero-solicitar-la-consulta-de-tc-omitiendo-la-referencia-de-tarjeta-para-confirmar-
  Scenario Outline: [HU-103-ADP-AVV] Como analista de pruebas quiero solicitar la consulta de TC omitiendo la referencia de tarjeta para confirmar el rechazo de la solicitud - codigo 400
    When consulta la tarjeta de credito detallada en AVV del caso <Caso>
    Then la respuesta de tarjeta de credito detallada en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_tc_detallada
      | Caso |
      |3|

  @ev-64-como-analista-de-pruebas-quiero-consultar-una-tarjeta-con-operacion-no-soportada-para-confirmar-el-rechazo-def
  Scenario Outline: [HU-103-ADP-AVV] Como analista de pruebas quiero consultar una tarjeta con operación no soportada para confirmar el rechazo defensivo 400 - codigo 400
    When consulta la tarjeta de credito detallada en AVV del caso <Caso>
    Then la respuesta de tarjeta de credito detallada en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_tc_detallada
      | Caso |
      |4|

  @ev-65-como-analista-de-pruebas-quiero-consultar-una-tarjeta-con-referencia-en-formato-o-longitud-incorrecta-para-con
  Scenario Outline: [HU-103-ADP-AVV] Como analista de pruebas quiero consultar una tarjeta con referencia en formato o longitud incorrecta para confirmar la validación - codigo 200
    When consulta la tarjeta de credito detallada en AVV del caso <Caso>
    Then la consulta de tarjeta de credito detallada en AVV es exitosa

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_tc_detallada
      | Caso |
      |5|

  @ev-66-como-analista-de-pruebas-quiero-consultar-una-tarjeta-bloqueada-o-cancelada-para-confirmar-la-correcta-entrega
  Scenario Outline: [HU-103-ADP-AVV] Como analista de pruebas quiero consultar una tarjeta bloqueada o cancelada para confirmar la correcta entrega de su estado y saldos - codigo 502
    When consulta la tarjeta de credito detallada en AVV del caso <Caso>
    Then la respuesta de tarjeta de credito detallada en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_tc_detallada
      | Caso |
      |6|

  @ev-67-como-analista-de-pruebas-quiero-simular-un-error-tecnico-en-el-servicio-soap-de-tc-para-confirmar-el-manejo-de
  Scenario Outline: [HU-103-ADP-AVV] Como analista de pruebas quiero simular un error técnico en el servicio SOAP de TC para confirmar el manejo de error y Circuit Breaker - codigo 504
    When consulta la tarjeta de credito detallada en AVV del caso <Caso>
    Then la respuesta de tarjeta de credito detallada en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_tc_detallada
      | Caso |
      |7|

  @ev-85-como-analista-de-pruebas-quiero-consultar-el-detalle-de-un-cdt-activo-para-confirmar-la-obtencion-de-su-monto-
  Scenario Outline: [HU-104-ADP-AVV] Como analista de pruebas quiero consultar el detalle de un CDT activo para confirmar la obtención de su monto, tasa EA, fechas y periodicidad - codigo 200
    When consulta el CDT detallado en AVV del caso <Caso>
    Then la consulta de CDT detallado en AVV es exitosa

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cdt_detallado
      | Caso |
      |1|

  @ev-86-como-analista-de-pruebas-quiero-consultar-un-cdt-no-registrado-en-av-villas-para-confirmar-la-respuesta-de-err
  Scenario Outline: [HU-104-ADP-AVV] Como analista de pruebas quiero consultar un CDT no registrado en AV Villas para confirmar la respuesta de error 404 - codigo 404
    When consulta el CDT detallado en AVV del caso <Caso>
    Then la respuesta de CDT detallado en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cdt_detallado
      | Caso |
      |2|

  @ev-87-como-analista-de-pruebas-quiero-solicitar-la-consulta-de-cdt-omitiendo-el-numero-de-producto-para-confirmar-el
  Scenario Outline: [HU-104-ADP-AVV] Como analista de pruebas quiero solicitar la consulta de CDT omitiendo el número de producto para confirmar el rechazo de la petición - codigo 400
    When consulta el CDT detallado en AVV del caso <Caso>
    Then la respuesta de CDT detallado en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cdt_detallado
      | Caso |
      |3|

  @ev-88-como-analista-de-pruebas-quiero-intentar-la-consulta-de-cdt-con-una-operacion-no-soportada-para-confirmar-el-r
  Scenario Outline: [HU-104-ADP-AVV] Como analista de pruebas quiero intentar la consulta de CDT con una operación no soportada para confirmar el rechazo defensivo 400 - codigo 400
    When consulta el CDT detallado en AVV del caso <Caso>
    Then la respuesta de CDT detallado en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cdt_detallado
      | Caso |
      |4|

  @ev-89-como-analista-de-pruebas-quiero-consultar-un-cdt-con-plazo-en-dias-limite-o-especial-para-confirmar-el-calculo
  Scenario Outline: [HU-104-ADP-AVV] Como analista de pruebas quiero consultar un CDT con plazo en días límite o especial para confirmar el cálculo correcto de fechas - codigo 200
    When consulta el CDT detallado en AVV del caso <Caso>
    Then la consulta de CDT detallado en AVV es exitosa

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cdt_detallado
      | Caso |
      |5|

  @ev-90-como-analista-de-pruebas-quiero-consultar-un-cdt-ya-vencido-para-confirmar-la-informacion-de-estado-de-vencimi
  Scenario Outline: [HU-104-ADP-AVV] Como analista de pruebas quiero consultar un CDT ya vencido para confirmar la información de estado de vencimiento - codigo 502
    When consulta el CDT detallado en AVV del caso <Caso>
    Then la respuesta de CDT detallado en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cdt_detallado
      | Caso |
      |6|

  @ev-91-como-analista-de-pruebas-quiero-simular-un-error-tecnico-en-el-backend-de-cdt-para-confirmar-el-codigo-de-erro
  Scenario Outline: [HU-104-ADP-AVV] Como analista de pruebas quiero simular un error técnico en el backend de CDT para confirmar el código de error y Circuit Breaker - codigo 504
    When consulta el CDT detallado en AVV del caso <Caso>
    Then la respuesta de CDT detallado en AVV coincide con el error esperado

    Examples:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cdt_detallado
      | Caso |
      |7|
