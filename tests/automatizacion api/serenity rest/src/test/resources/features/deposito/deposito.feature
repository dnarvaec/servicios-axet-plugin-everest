# language: es
@tx02 @deposito
Característica: TX-02 Depósitos y consignaciones en efectivo
  Como sistema ATM del Banco de Bogotá
  Quiero procesar solicitudes de depósito y consignación en efectivo
  Para que los clientes puedan depositar dinero desde cajeros automáticos

  Antecedentes:
    Dado el actor está autorizado para operar en la API de depósitos

  @smoke @e2e
  Esquema del escenario: Depósito en efectivo - respuesta exitosa
    Cuando realiza un depósito en efectivo del caso <Caso>
    Entonces la transacción de depósito es exitosa
    Y el campo endDt del depósito está presente

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@deposito
      | Caso |
      |1|

  @e2e @validacion-estado
  Esquema del escenario: Depósito en efectivo - severidad Info confirmada
    Cuando realiza un depósito en efectivo del caso <Caso>
    Entonces la severidad del depósito es la esperada

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@deposito
      | Caso |
      |1|

  @e2e @validacion-mensaje
  Esquema del escenario: Depósito en efectivo - descripción transacción exitosa
    Cuando realiza un depósito en efectivo del caso <Caso>
    Entonces la descripción del depósito es la esperada

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@deposito
      | Caso |
      |1|

  @e2e @flujo-completo
  Esquema del escenario: Depósito en efectivo - validación completa de respuesta
    Cuando realiza un depósito en efectivo del caso <Caso>
    Entonces la transacción de depósito es exitosa
    Y la severidad del depósito es la esperada
    Y la descripción del depósito es la esperada
    Y el campo endDt del depósito está presente

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@deposito
      | Caso |
      |1|

