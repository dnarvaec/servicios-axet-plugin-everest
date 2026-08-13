# language: es
@tx01 @retiro
Característica: TX-01 Retiro de efectivo con OTP
  Como sistema ATM del Banco de Bogotá
  Quiero procesar solicitudes de retiro de efectivo con OTP
  Para que los clientes puedan retirar dinero de forma segura desde cajeros automáticos

  Antecedentes:
    Dado el actor está autorizado para operar en la API de retiros

  @smoke @e2e
  Esquema del escenario: Retiro de efectivo con OTP - respuesta exitosa
    Cuando realiza un retiro de efectivo con OTP del caso <Caso>
    Entonces la transacción de retiro es exitosa
    Y el campo endDt del retiro está presente

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@retiro
      | Caso |
      |1|

  @e2e @validacion-estado
  Esquema del escenario: Retiro de efectivo - severidad Info confirmada
    Cuando realiza un retiro de efectivo con OTP del caso <Caso>
    Entonces la severidad del retiro es la esperada

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@retiro
      | Caso |
      |1|

  @e2e @validacion-mensaje
  Esquema del escenario: Retiro de efectivo - descripción transacción exitosa
    Cuando realiza un retiro de efectivo con OTP del caso <Caso>
    Entonces la descripción del retiro es la esperada

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@retiro
      | Caso |
      |1|

  @e2e @flujo-completo
  Esquema del escenario: Retiro de efectivo - validación completa de respuesta
    Cuando realiza un retiro de efectivo con OTP del caso <Caso>
    Entonces la transacción de retiro es exitosa
    Y la severidad del retiro es la esperada
    Y la descripción del retiro es la esperada
    Y el campo endDt del retiro está presente

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@retiro
      | Caso |
      |1|

