# language: es
@tx03 @recaudo
Característica: TX-03 Recaudo de convenios en efectivo
  Como sistema ATM del Banco de Bogotá
  Quiero procesar pagos de convenios en dos pasos (consulta + pago)
  Para que los clientes puedan pagar facturas de servicios desde cajeros automáticos

  Antecedentes:
    Dado el actor está autorizado para operar en la API de recaudo

  @smoke @e2e @paso1
  Esquema del escenario: TX-03 Paso 1 - Consulta de factura de convenio exitosa
    Cuando consulta la factura del convenio TX-03 del caso <Caso>
    Entonces la consulta de factura es exitosa

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@recaudo
      | Caso |
      |1|

  @e2e @paso1 @validacion-datos
  Esquema del escenario: TX-03 Paso 1 - Consulta retorna nombre del convenio
    Cuando consulta la factura del convenio TX-03 del caso <Caso>
    Entonces la consulta de factura es exitosa
    Y la respuesta contiene el nombre del convenio

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@recaudo
      | Caso |
      |1|

  @e2e @paso1 @validacion-datos
  Esquema del escenario: TX-03 Paso 1 - Consulta retorna monto total y saldos
    Cuando consulta la factura del convenio TX-03 del caso <Caso>
    Entonces la consulta de factura es exitosa
    Y la respuesta contiene el monto total a pagar
    Y los saldos de la factura están presentes

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@recaudo
      | Caso |
      |1|

  @smoke @e2e @paso2
  Esquema del escenario: TX-03 Paso 2 - Pago de factura de convenio exitoso
    Cuando realiza el pago de la factura del convenio del caso <Caso>
    Entonces el pago de la factura es exitoso
    Y el campo endDt del recaudo está presente

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@recaudo
      | Caso |
      |1|

  @e2e @paso2 @validacion-estado
  Esquema del escenario: TX-03 Paso 2 - Pago de factura con severidad Info
    Cuando realiza el pago de la factura del convenio del caso <Caso>
    Entonces la severidad del recaudo es la esperada
    Y la descripción del recaudo es la esperada

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@recaudo
      | Caso |
      |1|

  @e2e @flujo-completo
  Esquema del escenario: TX-03 Flujo completo - Consulta y pago de convenio
    Cuando consulta la factura del convenio TX-03 del caso <Caso>
    Entonces la consulta de factura es exitosa
    Y la respuesta contiene el nombre del convenio
    Y la respuesta contiene el monto total a pagar
    Cuando realiza el pago de la factura del convenio del caso <Caso>
    Entonces el pago de la factura es exitoso
    Y la severidad del recaudo es la esperada
    Y la descripción del recaudo es la esperada
    Y el campo endDt del recaudo está presente

    Ejemplos:
      ##@externaldata@src/test/resources/datadriven/datadriven.xlsx@recaudo
      | Caso |
      |1|

