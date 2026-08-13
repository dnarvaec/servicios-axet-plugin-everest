# language: es
@tx04 @pago-obligaciones
Característica: TX-04 Pago de obligaciones y TC Aval en efectivo
  Como sistema ATM del Banco de Bogotá
  Quiero procesar pagos de obligaciones y Tarjeta de Crédito Aval
  Para que los clientes puedan pagar sus obligaciones financieras desde cajeros automáticos

  Antecedentes:
    Dado el actor está autorizado para operar en la API de pago de obligaciones

  @smoke @e2e
  Esquema del escenario: TX-04 Pago de obligación TC Aval - respuesta exitosa
    Cuando realiza el pago de la obligación TC Aval del caso <Caso>
    Entonces la transacción de pago de obligación es exitosa
    Y el campo endDt del pago de obligación está presente

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@pago_obligaciones
      | Caso |
      |1|

  @e2e @validacion-estado
  Esquema del escenario: TX-04 Pago de obligación TC Aval - severidad Info confirmada
    Cuando realiza el pago de la obligación TC Aval del caso <Caso>
    Entonces la severidad del pago de obligación es la esperada

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@pago_obligaciones
      | Caso |
      |1|

  @e2e @validacion-mensaje
  Esquema del escenario: TX-04 Pago de obligación TC Aval - descripción transacción exitosa
    Cuando realiza el pago de la obligación TC Aval del caso <Caso>
    Entonces la descripción del pago de obligación es la esperada

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@pago_obligaciones
      | Caso |
      |1|

  @e2e @flujo-completo
  Esquema del escenario: TX-04 Pago de obligación TC Aval - validación completa de respuesta
    Cuando realiza el pago de la obligación TC Aval del caso <Caso>
    Entonces la transacción de pago de obligación es exitosa
    Y la severidad del pago de obligación es la esperada
    Y la descripción del pago de obligación es la esperada
    Y el campo endDt del pago de obligación está presente

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@pago_obligaciones
      | Caso |
      |1|

