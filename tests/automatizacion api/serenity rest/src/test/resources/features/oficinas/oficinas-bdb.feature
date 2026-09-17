# language: es
@oficinas @bdb
Característica: Oficinas — Consultas ADP Banco de Bogotá
  Como sistema Oficinas de Grupo Aval
  Quiero consultar datos generales, cartera, TC y CDT del Banco de Bogotá
  Para que el asesor de oficina vea la información consolidada del cliente

  # NOTA — validado en vivo con mvn verify (2026-09-15): el orquestador real
  # (https://d299ks4asy14z3.cloudfront.net/api/v1/everst/ofi/bog/adp/consulta)
  # responde HTTP 200 con msgRsHdr.status.statusCode=200 para estas operaciones.
  # Ver /memories/repo/oficinas-consulta-notes.md para el historial de la
  # exploración (una prueba anterior con curl.exe el mismo día había devuelto
  # 400 "operacion no reconocida"; el backend quedó disponible más tarde).

  Antecedentes:
    Dado el actor está autorizado para operar en la API de Oficinas BDB

  @smoke @e2e @consulta-general
  Esquema del escenario: Oficinas BDB - Consulta general de cliente y productos exitosa
    Cuando consulta general de cliente y productos en BDB del caso <Caso>
    Entonces la consulta general en BDB es exitosa
    Y el envelope de respuesta de Oficinas BDB está presente

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_consulta_general
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @e2e @cartera-detallada
  Esquema del escenario: Oficinas BDB - Consulta de cartera detallada exitosa
    Cuando consulta la cartera detallada en BDB del caso <Caso>
    Entonces la consulta de cartera detallada en BDB es exitosa
    Y el envelope de respuesta de Oficinas BDB está presente

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cartera_detallada
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @e2e @tc-detallada
  Esquema del escenario: Oficinas BDB - Consulta de TC detallada exitosa
    Cuando consulta la tarjeta de crédito detallada en BDB del caso <Caso>
    Entonces la consulta de tarjeta de crédito detallada en BDB es exitosa
    Y el envelope de respuesta de Oficinas BDB está presente

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_tc_detallada
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @e2e @cdt-detallado
  Esquema del escenario: Oficinas BDB - Consulta de CDT detallado exitosa
    Cuando consulta el CDT detallado en BDB del caso <Caso>
    Entonces la consulta de CDT detallado en BDB es exitosa
    Y el envelope de respuesta de Oficinas BDB está presente

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cdt_detallado
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @negative @funcional @consulta-general
  Esquema del escenario: Oficinas BDB - Consulta general con respuesta de fallo
    Cuando consulta general de cliente y productos en BDB del caso <Caso>
    Entonces la respuesta de consulta general en BDB coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_consulta_general
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @negative @funcional @cartera-detallada
  Esquema del escenario: Oficinas BDB - Consulta de cartera con respuesta de fallo
    Cuando consulta la cartera detallada en BDB del caso <Caso>
    Entonces la respuesta de cartera detallada en BDB coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cartera_detallada
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @negative @funcional @tc-detallada
  Esquema del escenario: Oficinas BDB - Consulta de TC con respuesta de fallo
    Cuando consulta la tarjeta de crédito detallada en BDB del caso <Caso>
    Entonces la respuesta de tarjeta de crédito detallada en BDB coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_tc_detallada
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @negative @funcional @cdt-detallado
  Esquema del escenario: Oficinas BDB - Consulta de CDT con respuesta de fallo
    Cuando consulta el CDT detallado en BDB del caso <Caso>
    Entonces la respuesta de CDT detallado en BDB coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cdt_detallado
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @functional @consulta-general
  Esquema del escenario: Oficinas BDB - Consulta general en estados funcionales especiales
    Cuando consulta general de cliente y productos en BDB del caso <Caso>
    Entonces la respuesta de consulta general en BDB coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_consulta_general
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @functional @cartera-detallada
  Esquema del escenario: Oficinas BDB - Cartera en estados funcionales especiales
    Cuando consulta la cartera detallada en BDB del caso <Caso>
    Entonces la respuesta de cartera detallada en BDB coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cartera_detallada
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @functional @tc-detallada
  Esquema del escenario: Oficinas BDB - TC en estados funcionales especiales
    Cuando consulta la tarjeta de crédito detallada en BDB del caso <Caso>
    Entonces la respuesta de tarjeta de crédito detallada en BDB coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_tc_detallada
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

  @functional @cdt-detallado
  Esquema del escenario: Oficinas BDB - CDT en estados funcionales especiales
    Cuando consulta el CDT detallado en BDB del caso <Caso>
    Entonces la respuesta de CDT detallado en BDB coincide con el error esperado

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@bdb_cdt_detallado
      | Caso |
      |1|
      |2|
      |3|
      |4|
      |5|
      |6|
      |7|

