# Casos de accesibilidad extraidos

Total: 67

## Datos de prueba

| Pool | Tipo | Documento | Nombre | Productos |
|---|---|---|---|---|
| POOL A | CC | 12345678 | JUAN CARLOS RODRIGUEZ GOMEZ | SDA |
| POOL B | CC | 23456789 | MARIA FERNANDA LOPEZ VARGAS | SDA + CCA |
| POOL C | CC | 34567890 | PEDRO ANDRES MARTINEZ DIAZ | LOC + CDA |
| POOL D | CC | 45678901 | ANA LUCIA HERRERA MUNOZ | SDA + LOC + CCA |
| POOL E | NIT | 900123456 | EMPRESA COMERCIAL SAS | DDA |
| POOL F | RC | 55667788 | CARLOS ANTONIO JIMENEZ RUIZ | SDA |
| POOL G | TI | 1020304050 | SOFIA VALENTINA TORRES PEREZ | SDA |
| POOL H | PS | PA567890 | JOHN SMITH FOREIGN | SDA |
| POOL I | CE | 66778899 | MICHAEL ALEJANDRO BROWN | SDA |
| POOL J | CD | 44556677 | PIERRE DUPONT DIPLOMATICO | SDA |

## Casos

### EV-10 - HU-101-ADP-AVV-CLIENTE
**Summary:** [HU-101-ADP-AVV-CLIENTE] Como analista de pruebas quiero verificar que la información de identificación y contacto del cliente sea clara, estructurada y comprensible para consumo humano
**Expected:** Los datos están etiquetados de forma explícita, sin abreviaturas ambiguas y facilitando su lectura por asesores y herramientas de accesibilidad.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-11 - HU-101-ADP-AVV-CLIENTE
**Summary:** [HU-101-ADP-AVV-CLIENTE] Como analista de pruebas quiero verificar que los mensajes de estado y error de consulta de cliente sean legibles y orientativos
**Expected:** Los mensajes proporcionan descripciones funcionales claras y accionables para el usuario final.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-12 - HU-101-ADP-AVV-CLIENTE
**Summary:** [HU-101-ADP-AVV-CLIENTE] Como analista de pruebas quiero verificar la consistencia en el formato de números telefónicos y correos para su correcta interpretación
**Expected:** La información es uniforme, legible y no presenta concatenaciones confusas.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-22 - HU-101-ADP-AVV
**Summary:** [HU-101-ADP-AVV] Como analista de pruebas quiero verificar que la agrupación por tipo de producto (cuentas, CDT, carteras, tarjetas) sea clara y organizada
**Expected:** Cada categoría de producto está claramente delimitada y categorizada, permitiendo navegación y lectura sin confusiones.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-23 - HU-101-ADP-AVV
**Summary:** [HU-101-ADP-AVV] Como analista de pruebas quiero verificar la claridad en el rotulado de saldos, sobregiros y cupos disponibles
**Expected:** Los campos diferencian con total claridad entre saldo total, saldo disponible, sobregiro y deuda.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-24 - HU-101-ADP-AVV
**Summary:** [HU-101-ADP-AVV] Como analista de pruebas quiero verificar la legibilidad y coherencia en los mensajes informativos cuando no existen productos
**Expected:** El mensaje informa claramente la ausencia de productos sin causar confusión ni alarmas técnicas.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-34 - HU-101-ADP-BDB
**Summary:** [HU-101-ADP-BDB] Como analista de pruebas quiero verificar la estructura y jerarquía en la visualización unificada de cliente y productos
**Expected:** La información está jerárquicamente estructurada, facilitando la comprensión y navegación del asesor.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-35 - HU-101-ADP-BDB
**Summary:** [HU-101-ADP-BDB] Como analista de pruebas quiero verificar que las advertencias de respuestas parciales sean claras y autoexplicativas
**Expected:** El mensaje describe claramente la sección afectada sin causar confusión sobre los datos sí entregados.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-36 - HU-101-ADP-BDB
**Summary:** [HU-101-ADP-BDB] Como analista de pruebas quiero verificar el formato y rotulado uniforme de números de cuentas, carteras y saldos monetarios
**Expected:** Los datos numéricos y financieros son inequívocos, legibles y fácilmente interpretables.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-46 - HU-102-ADP-AVV
**Summary:** [HU-102-ADP-AVV] Como analista de pruebas quiero verificar que el desglose de saldos de capital, intereses y mora sea claro e intuitivo
**Expected:** Los conceptos de capital, intereses corrientes e intereses de mora están nítidamente identificados.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-47 - HU-102-ADP-AVV
**Summary:** [HU-102-ADP-AVV] Como analista de pruebas quiero verificar que las fechas de vencimiento y próximo pago tengan un formato comprensible y estándar
**Expected:** Las fechas siguen un formato estándar y legible para los usuarios y sistemas asistivos.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-48 - HU-102-ADP-AVV
**Summary:** [HU-102-ADP-AVV] Como analista de pruebas quiero verificar la claridad de los mensajes de error cuando la obligación no existe
**Expected:** El mensaje indica con claridad que la obligación consultada no fue localizada.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-58 - HU-102-ADP-BDB
**Summary:** [HU-102-ADP-BDB] Como analista de pruebas quiero verificar la claridad en el rotulado de montos de cuota mínima, saldos corrientes y plazos
**Expected:** Los campos permiten distinguir con total claridad el valor a pagar de la deuda total y los plazos restantes.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-59 - HU-102-ADP-BDB
**Summary:** [HU-102-ADP-BDB] Como analista de pruebas quiero verificar que las descripciones de estados de cuenta y tasas de interés sean transparentes
**Expected:** La información es autoexplicativa y fácilmente interpretable por cualquier usuario.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-60 - HU-102-ADP-BDB
**Summary:** [HU-102-ADP-BDB] Como analista de pruebas quiero verificar la legibilidad y mensaje accionable ante errores 404 o 422 en cartera
**Expected:** Los mensajes explican claramente si el crédito no existe o si presenta una condición particular de negocio.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-70 - HU-103-ADP-AVV
**Summary:** [HU-103-ADP-AVV] Como analista de pruebas quiero verificar la visualización clara y diferenciada de cupo aprobado, disponible y saldo adeudado
**Expected:** Cada concepto monetario está etiquetado con precisión sin posibilidad de confusión sobre los fondos disponibles.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-71 - HU-103-ADP-AVV
**Summary:** [HU-103-ADP-AVV] Como analista de pruebas quiero verificar el formato claro y comprensible de franquicia y estado de la tarjeta
**Expected:** Los valores son comprensibles y no presentan códigos numéricos opacos.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-72 - HU-103-ADP-AVV
**Summary:** [HU-103-ADP-AVV] Como analista de pruebas quiero verificar la claridad del mensaje ante tarjeta no encontrada
**Expected:** El mensaje indica con claridad que la tarjeta consultada no fue localizada.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-82 - HU-103-ADP-BDB
**Summary:** [HU-103-ADP-BDB] Como analista de pruebas quiero verificar el desglose claro y legible de cupos aprobados, cupo disponible y saldos diferidos
**Expected:** Cada concepto financiero es fácilmente comprensible y legible sin ambigüedades.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-83 - HU-103-ADP-BDB
**Summary:** [HU-103-ADP-BDB] Como analista de pruebas quiero verificar la claridad en la exposición del número de cuotas diferidas y franquicia
**Expected:** La información es autoexplicativa y comprensible.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-84 - HU-103-ADP-BDB
**Summary:** [HU-103-ADP-BDB] Como analista de pruebas quiero verificar la claridad del mensaje de error cuando la tarjeta no existe en Banco de Bogotá
**Expected:** El mensaje indica con claridad que la tarjeta consultada no existe en el banco.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-94 - HU-104-ADP-AVV
**Summary:** [HU-104-ADP-AVV] Como analista de pruebas quiero verificar la claridad en la presentación de tasa EA, plazo en días y monto del CDT
**Expected:** Los conceptos de rentabilidad, capital y tiempo están claramente expuestos sin ambigüedad.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-95 - HU-104-ADP-AVV
**Summary:** [HU-104-ADP-AVV] Como analista de pruebas quiero verificar que las fechas de apertura y vencimiento tengan un formato estándar y comprensible
**Expected:** Las fechas siguen una estructura cronológica clara y legible.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-96 - HU-104-ADP-AVV
**Summary:** [HU-104-ADP-AVV] Como analista de pruebas quiero verificar la claridad del mensaje de error ante CDT no encontrado
**Expected:** El mensaje informa claramente la no existencia del CDT consultado.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-106 - HU-104-ADP-BDB
**Summary:** [HU-104-ADP-BDB] Como analista de pruebas quiero verificar la comprensión inmediata en la presentación de capital, intereses acumulados y tasa EA
**Expected:** La información es nítida y permite distinguir con total claridad entre el capital inicial y los intereses ganados.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-107 - HU-104-ADP-BDB
**Summary:** [HU-104-ADP-BDB] Como analista de pruebas quiero verificar la visualización accesible de plazos en días, periodicidad y fechas
**Expected:** Los datos temporales se entienden de forma directa sin requerir conocimientos técnicos.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-108 - HU-104-ADP-BDB
**Summary:** [HU-104-ADP-BDB] Como analista de pruebas quiero verificar la claridad del mensaje de error cuando el CDT no existe en Banco de Bogotá
**Expected:** El mensaje informa claramente que el certificado consultado no fue encontrado en la entidad.
**Labels:** everest,accesibilidad,oficinas,consultas

### EV-114 - HU-101-ADP-BPO-CLIENTE
**Summary:** [HU-101-ADP-BPO-CLIENTE] Adaptador BPO — Consulta Cliente - claridad de datos
**Expected:** La información es clara, consistente y comprensible para el consumo humano.
**Labels:** everest,accesibilidad,oficinas

### EV-115 - HU-101-ADP-BPO-CLIENTE
**Summary:** [HU-101-ADP-BPO-CLIENTE] Adaptador BPO — Consulta Cliente - claridad de mensajes
**Expected:** Los mensajes son legibles, consistentes y orientan al usuario sin ambigüedad.
**Labels:** everest,accesibilidad,oficinas

### EV-121 - HU-101-ADP-BPO
**Summary:** [HU-101-ADP-BPO] Adaptador BPO — Consulta Productos - claridad de datos
**Expected:** La información es clara, consistente y comprensible para el consumo humano.
**Labels:** everest,accesibilidad,oficinas

### EV-122 - HU-101-ADP-BPO
**Summary:** [HU-101-ADP-BPO] Adaptador BPO — Consulta Productos - claridad de mensajes
**Expected:** Los mensajes son legibles, consistentes y orientan al usuario sin ambigüedad.
**Labels:** everest,accesibilidad,oficinas

### EV-128 - HU-101-ADP-OCC-CLIENTE
**Summary:** [HU-101-ADP-OCC-CLIENTE] Adaptador OCC — Consulta Cliente - claridad de datos
**Expected:** La información es clara, consistente y comprensible para el consumo humano.
**Labels:** everest,accesibilidad,oficinas

### EV-129 - HU-101-ADP-OCC-CLIENTE
**Summary:** [HU-101-ADP-OCC-CLIENTE] Adaptador OCC — Consulta Cliente - claridad de mensajes
**Expected:** Los mensajes son legibles, consistentes y orientan al usuario sin ambigüedad.
**Labels:** everest,accesibilidad,oficinas

### EV-135 - HU-101-ADP-OCC
**Summary:** [HU-101-ADP-OCC] Adaptador OCC — Consulta Productos - claridad de datos
**Expected:** La información es clara, consistente y comprensible para el consumo humano.
**Labels:** everest,accesibilidad,oficinas

### EV-136 - HU-101-ADP-OCC
**Summary:** [HU-101-ADP-OCC] Adaptador OCC — Consulta Productos - claridad de mensajes
**Expected:** Los mensajes son legibles, consistentes y orientan al usuario sin ambigüedad.
**Labels:** everest,accesibilidad,oficinas

### EV-142 - HU-102-ADP-BPO
**Summary:** [HU-102-ADP-BPO] Adaptador BPO — Consulta Detallada - claridad de datos
**Expected:** La información es clara, consistente y comprensible para el consumo humano.
**Labels:** everest,accesibilidad,oficinas

### EV-143 - HU-102-ADP-BPO
**Summary:** [HU-102-ADP-BPO] Adaptador BPO — Consulta Detallada - claridad de mensajes
**Expected:** Los mensajes son legibles, consistentes y orientan al usuario sin ambigüedad.
**Labels:** everest,accesibilidad,oficinas

### EV-149 - HU-102-ADP-OCC
**Summary:** [HU-102-ADP-OCC] Adaptador OCC — Consulta Detallada - claridad de datos
**Expected:** La información es clara, consistente y comprensible para el consumo humano.
**Labels:** everest,accesibilidad,oficinas

### EV-150 - HU-102-ADP-OCC
**Summary:** [HU-102-ADP-OCC] Adaptador OCC — Consulta Detallada - claridad de mensajes
**Expected:** Los mensajes son legibles, consistentes y orientan al usuario sin ambigüedad.
**Labels:** everest,accesibilidad,oficinas

### EV-156 - HU-103-ORQ
**Summary:** [HU-103-ORQ] Orquestador — Consulta Detallada de TC - claridad de datos
**Expected:** La información es clara, consistente y comprensible para el consumo humano.
**Labels:** everest,accesibilidad,oficinas

### EV-157 - HU-103-ORQ
**Summary:** [HU-103-ORQ] Orquestador — Consulta Detallada de TC - claridad de mensajes
**Expected:** Los mensajes son legibles, consistentes y orientan al usuario sin ambigüedad.
**Labels:** everest,accesibilidad,oficinas

### EV-163 - HU-104-ORQ
**Summary:** [HU-104-ORQ] Orquestador — Consulta Detallada de CDT - claridad de datos
**Expected:** La información es clara, consistente y comprensible para el consumo humano.
**Labels:** everest,accesibilidad,oficinas

### EV-164 - HU-104-ORQ
**Summary:** [HU-104-ORQ] Orquestador — Consulta Detallada de CDT - claridad de mensajes
**Expected:** Los mensajes son legibles, consistentes y orientan al usuario sin ambigüedad.
**Labels:** everest,accesibilidad,oficinas

### EV-181 - HU-201-ADP-AVV
**Summary:** [HU-201-ADP-AVV] Como analista de pruebas quiero revisar la claridad del mensaje de bloqueo exitoso para confirmar que la confirmacion del bloqueo sea comprensible y no ambigua
**Expected:** La confirmacion del bloqueo sea comprensible y no ambigua.
**Labels:** everest,accesibilidad,oficinas,hu-201-adp-avv

### EV-182 - HU-201-ADP-AVV
**Summary:** [HU-201-ADP-AVV] Como analista de pruebas quiero revisar la claridad de los mensajes de error de bloqueo para confirmar que el usuario entienda si la tarjeta no existe, ya esta bloqueada o el banco no responde
**Expected:** El usuario entienda si la tarjeta no existe, ya esta bloqueada o el banco no responde.
**Labels:** everest,accesibilidad,oficinas,hu-201-adp-avv

### EV-183 - HU-201-ADP-AVV
**Summary:** [HU-201-ADP-AVV] Como analista de pruebas quiero revisar la legibilidad de tarjeta causal y estado para confirmar que los datos sensibles se presenten de forma protegida y entendible
**Expected:** Los datos sensibles se presenten de forma protegida y entendible.
**Labels:** everest,accesibilidad,oficinas,hu-201-adp-avv

### EV-199 - HU-201-ADP-BDB
**Summary:** [HU-201-ADP-BDB] Como analista de pruebas quiero revisar la claridad del mensaje de bloqueo exitoso para confirmar que la confirmacion del bloqueo sea comprensible y no ambigua
**Expected:** La confirmacion del bloqueo sea comprensible y no ambigua.
**Labels:** everest,accesibilidad,oficinas,hu-201-adp-bdb

### EV-200 - HU-201-ADP-BDB
**Summary:** [HU-201-ADP-BDB] Como analista de pruebas quiero revisar la claridad de los mensajes de error de bloqueo para confirmar que el usuario entienda si la tarjeta no existe, ya esta bloqueada o el banco no responde
**Expected:** El usuario entienda si la tarjeta no existe, ya esta bloqueada o el banco no responde.
**Labels:** everest,accesibilidad,oficinas,hu-201-adp-bdb

### EV-201 - HU-201-ADP-BDB
**Summary:** [HU-201-ADP-BDB] Como analista de pruebas quiero revisar la legibilidad de tarjeta causal y estado para confirmar que los datos sensibles se presenten de forma protegida y entendible
**Expected:** Los datos sensibles se presenten de forma protegida y entendible.
**Labels:** everest,accesibilidad,oficinas,hu-201-adp-bdb

### EV-219 - HU-201-ADP-BPO
**Summary:** [HU-201-ADP-BPO] Como analista de pruebas quiero revisar la claridad del mensaje de bloqueo exitoso para confirmar que la confirmacion del bloqueo sea comprensible y no ambigua
**Expected:** La confirmacion del bloqueo sea comprensible y no ambigua.
**Labels:** everest,accesibilidad,oficinas,hu-201-adp-bpo

### EV-220 - HU-201-ADP-BPO
**Summary:** [HU-201-ADP-BPO] Como analista de pruebas quiero revisar la claridad de los mensajes de error de bloqueo para confirmar que el usuario entienda si la tarjeta no existe, ya esta bloqueada o el banco no responde
**Expected:** El usuario entienda si la tarjeta no existe, ya esta bloqueada o el banco no responde.
**Labels:** everest,accesibilidad,oficinas,hu-201-adp-bpo

### EV-221 - HU-201-ADP-BPO
**Summary:** [HU-201-ADP-BPO] Como analista de pruebas quiero revisar la legibilidad de tarjeta causal y estado para confirmar que los datos sensibles se presenten de forma protegida y entendible
**Expected:** Los datos sensibles se presenten de forma protegida y entendible.
**Labels:** everest,accesibilidad,oficinas,hu-201-adp-bpo

### EV-236 - HU-201-ADP-OCC
**Summary:** [HU-201-ADP-OCC] Como analista de pruebas quiero revisar la claridad del mensaje de bloqueo exitoso para confirmar que la confirmacion del bloqueo sea comprensible y no ambigua
**Expected:** La confirmacion del bloqueo sea comprensible y no ambigua.
**Labels:** everest,accesibilidad,oficinas,hu-201-adp-occ

### EV-237 - HU-201-ADP-OCC
**Summary:** [HU-201-ADP-OCC] Como analista de pruebas quiero revisar la claridad de los mensajes de error de bloqueo para confirmar que el usuario entienda si la tarjeta no existe, ya esta bloqueada o el banco no responde
**Expected:** El usuario entienda si la tarjeta no existe, ya esta bloqueada o el banco no responde.
**Labels:** everest,accesibilidad,oficinas,hu-201-adp-occ

### EV-238 - HU-201-ADP-OCC
**Summary:** [HU-201-ADP-OCC] Como analista de pruebas quiero revisar la legibilidad de tarjeta causal y estado para confirmar que los datos sensibles se presenten de forma protegida y entendible
**Expected:** Los datos sensibles se presenten de forma protegida y entendible.
**Labels:** everest,accesibilidad,oficinas,hu-201-adp-occ

### EV-253 - HU-203-ADP-AVV
**Summary:** [HU-203-ADP-AVV] Como analista de pruebas quiero revisar la claridad de la confirmacion de actualizacion para confirmar que la confirmacion indique que datos fueron actualizados sin lenguaje tecnico innecesario
**Expected:** La confirmacion indique que datos fueron actualizados sin lenguaje tecnico innecesario.
**Labels:** everest,accesibilidad,oficinas,hu-203-adp-avv

### EV-254 - HU-203-ADP-AVV
**Summary:** [HU-203-ADP-AVV] Como analista de pruebas quiero revisar la claridad de errores de datos invalidos para confirmar que el usuario entienda que dato debe corregir o validar
**Expected:** El usuario entienda que dato debe corregir o validar.
**Labels:** everest,accesibilidad,oficinas,hu-203-adp-avv

### EV-255 - HU-203-ADP-AVV
**Summary:** [HU-203-ADP-AVV] Como analista de pruebas quiero revisar la legibilidad de datos de contacto y preferencia para confirmar que telefonos, correos y preferencias se presenten con rotulos consistentes
**Expected:** Telefonos, correos y preferencias se presenten con rotulos consistentes.
**Labels:** everest,accesibilidad,oficinas,hu-203-adp-avv

### EV-271 - HU-203-ADP-BDB
**Summary:** [HU-203-ADP-BDB] Como analista de pruebas quiero revisar la claridad de la confirmacion de actualizacion para confirmar que la confirmacion indique que datos fueron actualizados sin lenguaje tecnico innecesario
**Expected:** La confirmacion indique que datos fueron actualizados sin lenguaje tecnico innecesario.
**Labels:** everest,accesibilidad,oficinas,hu-203-adp-bdb

### EV-272 - HU-203-ADP-BDB
**Summary:** [HU-203-ADP-BDB] Como analista de pruebas quiero revisar la claridad de errores de datos invalidos para confirmar que el usuario entienda que dato debe corregir o validar
**Expected:** El usuario entienda que dato debe corregir o validar.
**Labels:** everest,accesibilidad,oficinas,hu-203-adp-bdb

### EV-273 - HU-203-ADP-BDB
**Summary:** [HU-203-ADP-BDB] Como analista de pruebas quiero revisar la legibilidad de datos de contacto y preferencia para confirmar que telefonos, correos y preferencias se presenten con rotulos consistentes
**Expected:** Telefonos, correos y preferencias se presenten con rotulos consistentes.
**Labels:** everest,accesibilidad,oficinas,hu-203-adp-bdb

### EV-289 - HU-203-ADP-BPO
**Summary:** [HU-203-ADP-BPO] Como analista de pruebas quiero revisar la claridad de la confirmacion de actualizacion para confirmar que la confirmacion indique que datos fueron actualizados sin lenguaje tecnico innecesario
**Expected:** La confirmacion indique que datos fueron actualizados sin lenguaje tecnico innecesario.
**Labels:** everest,accesibilidad,oficinas,hu-203-adp-bpo

### EV-290 - HU-203-ADP-BPO
**Summary:** [HU-203-ADP-BPO] Como analista de pruebas quiero revisar la claridad de errores de datos invalidos para confirmar que el usuario entienda que dato debe corregir o validar
**Expected:** El usuario entienda que dato debe corregir o validar.
**Labels:** everest,accesibilidad,oficinas,hu-203-adp-bpo

### EV-291 - HU-203-ADP-BPO
**Summary:** [HU-203-ADP-BPO] Como analista de pruebas quiero revisar la legibilidad de datos de contacto y preferencia para confirmar que telefonos, correos y preferencias se presenten con rotulos consistentes
**Expected:** Telefonos, correos y preferencias se presenten con rotulos consistentes.
**Labels:** everest,accesibilidad,oficinas,hu-203-adp-bpo

### EV-307 - HU-203-ADP-OCC
**Summary:** [HU-203-ADP-OCC] Como analista de pruebas quiero revisar la claridad de la confirmacion de actualizacion para confirmar que la confirmacion indique que datos fueron actualizados sin lenguaje tecnico innecesario
**Expected:** La confirmacion indique que datos fueron actualizados sin lenguaje tecnico innecesario.
**Labels:** everest,accesibilidad,oficinas,hu-203-adp-occ

### EV-308 - HU-203-ADP-OCC
**Summary:** [HU-203-ADP-OCC] Como analista de pruebas quiero revisar la claridad de errores de datos invalidos para confirmar que el usuario entienda que dato debe corregir o validar
**Expected:** El usuario entienda que dato debe corregir o validar.
**Labels:** everest,accesibilidad,oficinas,hu-203-adp-occ

### EV-309 - HU-203-ADP-OCC
**Summary:** [HU-203-ADP-OCC] Como analista de pruebas quiero revisar la legibilidad de datos de contacto y preferencia para confirmar que telefonos, correos y preferencias se presenten con rotulos consistentes
**Expected:** Telefonos, correos y preferencias se presenten con rotulos consistentes.
**Labels:** everest,accesibilidad,oficinas,hu-203-adp-occ
