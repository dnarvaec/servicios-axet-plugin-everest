# language: es
@oficinas @avv
Característica: Oficinas — Consultas ADP AV Villas
  Como sistema Oficinas de Grupo Aval
  Quiero consultar cliente, productos, cartera, TC y CDT del banco AV Villas
  Para que el asesor de oficina vea la información consolidada del cliente

  # NOTA — validado en vivo con mvn verify (2026-09-15): el orquestador real
  # (https://d299ks4asy14z3.cloudfront.net/api/v1/everst/ofi/avv/adp/consulta)
  # responde HTTP 200 con msgRsHdr.status.statusCode=200 para estas operaciones.
  # Ver /memories/repo/oficinas-consulta-notes.md para el historial de la
  # exploración (una prueba anterior con curl.exe el mismo día había devuelto
  # 400 "operacion no reconocida"; el backend quedó disponible más tarde).

  Antecedentes:
    Dado el actor está autorizado para operar en la API de Oficinas AVV

  @smoke @e2e @consulta-cliente
  Esquema del escenario: Oficinas AVV - Consulta de cliente exitosa
    Cuando consulta el cliente en AVV del caso <Caso>
    Entonces la consulta de cliente en AVV es exitosa
    Y el envelope de respuesta de Oficinas AVV está presente

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_cliente
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @e2e @consulta-productos
  Esquema del escenario: Oficinas AVV - Consulta de productos exitosa
    Cuando consulta los productos en AVV del caso <Caso>
    Entonces la consulta de productos en AVV es exitosa
    Y el envelope de respuesta de Oficinas AVV está presente

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_productos
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @e2e @cartera-detallada
  Esquema del escenario: Oficinas AVV - Consulta de cartera detallada exitosa
    Cuando consulta la cartera detallada en AVV del caso <Caso>
    Entonces la consulta de cartera detallada en AVV es exitosa
    Y el envelope de respuesta de Oficinas AVV está presente

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cartera_detallada
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @e2e @tc-detallada
  Esquema del escenario: Oficinas AVV - Consulta de TC detallada exitosa
    Cuando consulta la tarjeta de crédito detallada en AVV del caso <Caso>
    Entonces la consulta de tarjeta de crédito detallada en AVV es exitosa
    Y el envelope de respuesta de Oficinas AVV está presente

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_tc_detallada
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @e2e @cdt-detallado
  Esquema del escenario: Oficinas AVV - Consulta de CDT detallado exitosa
    Cuando consulta el CDT detallado en AVV del caso <Caso>
    Entonces la consulta de CDT detallado en AVV es exitosa
    Y el envelope de respuesta de Oficinas AVV está presente

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cdt_detallado
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @negative @funcional @consulta-cliente
  Esquema del escenario: Oficinas AVV - Consulta de cliente con respuesta de fallo
    Cuando consulta el cliente en AVV del caso <Caso>
    Entonces la respuesta de consulta de cliente en AVV coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_cliente
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @negative @funcional @consulta-productos
  Esquema del escenario: Oficinas AVV - Consulta de productos con respuesta de fallo
    Cuando consulta los productos en AVV del caso <Caso>
    Entonces la respuesta de consulta de productos en AVV coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_productos
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @negative @funcional @cartera-detallada
  Esquema del escenario: Oficinas AVV - Consulta de cartera con respuesta de fallo
    Cuando consulta la cartera detallada en AVV del caso <Caso>
    Entonces la respuesta de cartera detallada en AVV coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cartera_detallada
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @negative @funcional @tc-detallada
  Esquema del escenario: Oficinas AVV - Consulta de TC con respuesta de fallo
    Cuando consulta la tarjeta de crédito detallada en AVV del caso <Caso>
    Entonces la respuesta de tarjeta de crédito detallada en AVV coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_tc_detallada
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @negative @funcional @cdt-detallado
  Esquema del escenario: Oficinas AVV - Consulta de CDT con respuesta de fallo
    Cuando consulta el CDT detallado en AVV del caso <Caso>
    Entonces la respuesta de CDT detallado en AVV coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cdt_detallado
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @functional @consulta-cliente
  Esquema del escenario: Oficinas AVV - Consulta de cliente en estados funcionales especiales
    Cuando consulta el cliente en AVV del caso <Caso>
    Entonces la respuesta de consulta de cliente en AVV coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_cliente
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @functional @consulta-productos
  Esquema del escenario: Oficinas AVV - Consulta de productos en estados funcionales especiales
    Cuando consulta los productos en AVV del caso <Caso>
    Entonces la respuesta de consulta de productos en AVV coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_consulta_productos
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @functional @cartera-detallada
  Esquema del escenario: Oficinas AVV - Cartera en estados funcionales especiales
    Cuando consulta la cartera detallada en AVV del caso <Caso>
    Entonces la respuesta de cartera detallada en AVV coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cartera_detallada
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @functional @tc-detallada
  Esquema del escenario: Oficinas AVV - TC en estados funcionales especiales
    Cuando consulta la tarjeta de crédito detallada en AVV del caso <Caso>
    Entonces la respuesta de tarjeta de crédito detallada en AVV coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_tc_detallada
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @functional @cdt-detallado
  Esquema del escenario: Oficinas AVV - CDT en estados funcionales especiales
    Cuando consulta el CDT detallado en AVV del caso <Caso>
    Entonces la respuesta de CDT detallado en AVV coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@avv_cdt_detallado
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

