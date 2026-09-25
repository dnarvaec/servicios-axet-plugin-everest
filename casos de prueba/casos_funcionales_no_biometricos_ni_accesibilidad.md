# Casos funcionales sin biometricos ni accesibilidad

Total: 204

| Issue Key | HU | Summary |
|---|---|---|
| EV-1 | HU-101-ADP-AVV-CLIENTE | [HU-101-ADP-AVV-CLIENTE] Como analista de pruebas quiero consultar los datos personales y de contacto de un cliente existente para confirmar la recepción exitosa y normalizada de su información |
| EV-2 | HU-101-ADP-AVV-CLIENTE | [HU-101-ADP-AVV-CLIENTE] Como analista de pruebas quiero consultar los datos de un cliente no registrado para confirmar que el sistema responde con la notificación de cliente no encontrado |
| EV-3 | HU-101-ADP-AVV-CLIENTE | [HU-101-ADP-AVV-CLIENTE] Como analista de pruebas quiero intentar una consulta enviando una operación no soportada para confirmar que el sistema rechaza la solicitud defensivamente |
| EV-4 | HU-101-ADP-AVV-CLIENTE | [HU-101-ADP-AVV-CLIENTE] Como analista de pruebas quiero consultar los datos del cliente omitiendo el número de documento para confirmar la validación y respuesta de error correspondiente |
| EV-5 | HU-101-ADP-AVV-CLIENTE | [HU-101-ADP-AVV-CLIENTE] Como analista de pruebas quiero consultar los datos del cliente con un tipo de documento no admitido para confirmar el rechazo de la solicitud |
| EV-6 | HU-101-ADP-AVV-CLIENTE | [HU-101-ADP-AVV-CLIENTE] Como analista de pruebas quiero consultar un cliente con nombres y direcciones extensos para confirmar la correcta integridad y completitud de la respuesta |
| EV-7 | HU-101-ADP-AVV-CLIENTE | [HU-101-ADP-AVV-CLIENTE] Como analista de pruebas quiero simular una falla o indisponibilidad en el servicio bancario para confirmar el manejo de error y trazabilidad |
| EV-13 | HU-101-ADP-AVV | [HU-101-ADP-AVV] Como analista de pruebas quiero consultar el portafolio de productos de un cliente activo para confirmar la recepción consolidada de cuentas, CDT, carteras y tarjetas |
| EV-14 | HU-101-ADP-AVV | [HU-101-ADP-AVV] Como analista de pruebas quiero consultar los productos de un cliente que no tiene productos activos para confirmar la respuesta de cliente sin productos |
| EV-15 | HU-101-ADP-AVV | [HU-101-ADP-AVV] Como analista de pruebas quiero consultar productos de un cliente no registrado para confirmar la notificación de cliente no encontrado |
| EV-16 | HU-101-ADP-AVV | [HU-101-ADP-AVV] Como analista de pruebas quiero solicitar la consulta de productos con una operación no soportada para confirmar el rechazo de la petición |
| EV-17 | HU-101-ADP-AVV | [HU-101-ADP-AVV] Como analista de pruebas quiero consultar productos omitiendo los datos de identificación para confirmar la validación del sistema |
| EV-18 | HU-101-ADP-AVV | [HU-101-ADP-AVV] Como analista de pruebas quiero verificar la consulta de productos para un cliente con más de 10 productos para confirmar la completitud del listado |
| EV-19 | HU-101-ADP-AVV | [HU-101-ADP-AVV] Como analista de pruebas quiero simular un error técnico o timeout en el servicio SOAP bancario para confirmar el manejo de error y Circuit Breaker |
| EV-25 | HU-101-ADP-BDB | [HU-101-ADP-BDB] Como analista de pruebas quiero consultar de forma unificada los datos del cliente y sus productos en Banco de Bogotá para confirmar la consolidación completa en una sola respuesta |
| EV-26 | HU-101-ADP-BDB | [HU-101-ADP-BDB] Como analista de pruebas quiero consultar un cliente que no tiene productos registrados en Banco de Bogotá para confirmar la respuesta controlada |
| EV-27 | HU-101-ADP-BDB | [HU-101-ADP-BDB] Como analista de pruebas quiero consultar un cliente inexistente en Banco de Bogotá para confirmar el mensaje de cliente no encontrado |
| EV-28 | HU-101-ADP-BDB | [HU-101-ADP-BDB] Como analista de pruebas quiero validar la respuesta parcial cuando un bloque de información presenta novedad para confirmar que la información disponible no se pierde |
| EV-29 | HU-101-ADP-BDB | [HU-101-ADP-BDB] Como analista de pruebas quiero enviar una solicitud con operación no soportada para confirmar el rechazo controlado de la petición |
| EV-30 | HU-101-ADP-BDB | [HU-101-ADP-BDB] Como analista de pruebas quiero consultar omitiendo los headers de identificación bancaria para confirmar la validación del sistema |
| EV-31 | HU-101-ADP-BDB | [HU-101-ADP-BDB] Como analista de pruebas quiero simular timeout o falla de autenticación con el servicio REST de Banco de Bogotá para confirmar el código de error y auditoría |
| EV-37 | HU-102-ADP-AVV | [HU-102-ADP-AVV] Como analista de pruebas quiero consultar el detalle de una obligación de cartera activa para confirmar la obtención de sus saldos y estado |
| EV-38 | HU-102-ADP-AVV | [HU-102-ADP-AVV] Como analista de pruebas quiero consultar una obligación que no existe para confirmar la respuesta de error o no encontrada |
| EV-39 | HU-102-ADP-AVV | [HU-102-ADP-AVV] Como analista de pruebas quiero solicitar la consulta de cartera omitiendo el número de obligación para confirmar el rechazo de la solicitud |
| EV-40 | HU-102-ADP-AVV | [HU-102-ADP-AVV] Como analista de pruebas quiero intentar la consulta de cartera con una operación no soportada para confirmar el rechazo 400 |
| EV-41 | HU-102-ADP-AVV | [HU-102-ADP-AVV] Como analista de pruebas quiero consultar una obligación con caracteres no numéricos para confirmar la validación del identificador |
| EV-42 | HU-102-ADP-AVV | [HU-102-ADP-AVV] Como analista de pruebas quiero consultar una obligación en estado especial de mora o castigada para confirmar el detalle del estado de deuda |
| EV-43 | HU-102-ADP-AVV | [HU-102-ADP-AVV] Como analista de pruebas quiero simular un error SOAP fault o timeout en el backend de AV Villas para confirmar la propagación del error y auditoría |
| EV-49 | HU-102-ADP-BDB | [HU-102-ADP-BDB] Como analista de pruebas quiero consultar el detalle de un crédito activo en Banco de Bogotá para confirmar la recepción directa de saldos, cuota mínima y fechas |
| EV-50 | HU-102-ADP-BDB | [HU-102-ADP-BDB] Como analista de pruebas quiero consultar una obligación inexistente en Banco de Bogotá para confirmar la propagación del código 404 |
| EV-51 | HU-102-ADP-BDB | [HU-102-ADP-BDB] Como analista de pruebas quiero simular un error de negocio en la consulta de cartera para confirmar su mapeo al código 422 |
| EV-52 | HU-102-ADP-BDB | [HU-102-ADP-BDB] Como analista de pruebas quiero solicitar la consulta de cartera con una operación no soportada para confirmar el rechazo 400 |
| EV-53 | HU-102-ADP-BDB | [HU-102-ADP-BDB] Como analista de pruebas quiero consultar omitiendo el número de obligación para confirmar la validación del dato requerido |
| EV-54 | HU-102-ADP-BDB | [HU-102-ADP-BDB] Como analista de pruebas quiero consultar un crédito cancelado para confirmar que se entrega el estado final y saldo en cero |
| EV-55 | HU-102-ADP-BDB | [HU-102-ADP-BDB] Como analista de pruebas quiero simular un timeout (SocketTimeoutException) en el servicio de balances de BdB para confirmar el retorno de 504 |
| EV-61 | HU-103-ADP-AVV | [HU-103-ADP-AVV] Como analista de pruebas quiero consultar el detalle de una tarjeta de crédito activa para confirmar la obtención de cupos, saldos y estado |
| EV-62 | HU-103-ADP-AVV | [HU-103-ADP-AVV] Como analista de pruebas quiero consultar una tarjeta de crédito inexistente para confirmar el retorno de error 404 |
| EV-63 | HU-103-ADP-AVV | [HU-103-ADP-AVV] Como analista de pruebas quiero solicitar la consulta de TC omitiendo la referencia de tarjeta para confirmar el rechazo de la solicitud |
| EV-64 | HU-103-ADP-AVV | [HU-103-ADP-AVV] Como analista de pruebas quiero consultar una tarjeta con operación no soportada para confirmar el rechazo defensivo 400 |
| EV-65 | HU-103-ADP-AVV | [HU-103-ADP-AVV] Como analista de pruebas quiero consultar una tarjeta con referencia en formato o longitud incorrecta para confirmar la validación |
| EV-66 | HU-103-ADP-AVV | [HU-103-ADP-AVV] Como analista de pruebas quiero consultar una tarjeta bloqueada o cancelada para confirmar la correcta entrega de su estado y saldos |
| EV-67 | HU-103-ADP-AVV | [HU-103-ADP-AVV] Como analista de pruebas quiero simular un error técnico en el servicio SOAP de TC para confirmar el manejo de error y Circuit Breaker |
| EV-73 | HU-103-ADP-BDB | [HU-103-ADP-BDB] Como analista de pruebas quiero consultar el detalle de una tarjeta de crédito activa en Banco de Bogotá para confirmar la recepción de cupos, saldos y cuotas diferidas |
| EV-74 | HU-103-ADP-BDB | [HU-103-ADP-BDB] Como analista de pruebas quiero consultar una tarjeta de crédito no registrada en Banco de Bogotá para confirmar el retorno de código 404 |
| EV-75 | HU-103-ADP-BDB | [HU-103-ADP-BDB] Como analista de pruebas quiero consultar omitiendo la referencia de la tarjeta de crédito para confirmar el rechazo de la solicitud |
| EV-76 | HU-103-ADP-BDB | [HU-103-ADP-BDB] Como analista de pruebas quiero enviar una solicitud de TC con operación no soportada para confirmar el rechazo con código 400 |
| EV-77 | HU-103-ADP-BDB | [HU-103-ADP-BDB] Como analista de pruebas quiero consultar una tarjeta con compras diferidas a múltiples cuotas para confirmar la entrega del número de cuotas activas |
| EV-78 | HU-103-ADP-BDB | [HU-103-ADP-BDB] Como analista de pruebas quiero consultar una tarjeta cancelada para confirmar la entrega de estado CANCELADA y saldos en cero |
| EV-79 | HU-103-ADP-BDB | [HU-103-ADP-BDB] Como analista de pruebas quiero simular un error técnico o timeout en balances-management-v2 para confirmar el retorno de 502/504 y auditoría |
| EV-85 | HU-104-ADP-AVV | [HU-104-ADP-AVV] Como analista de pruebas quiero consultar el detalle de un CDT activo para confirmar la obtención de su monto, tasa EA, fechas y periodicidad |
| EV-86 | HU-104-ADP-AVV | [HU-104-ADP-AVV] Como analista de pruebas quiero consultar un CDT no registrado en AV Villas para confirmar la respuesta de error 404 |
| EV-87 | HU-104-ADP-AVV | [HU-104-ADP-AVV] Como analista de pruebas quiero solicitar la consulta de CDT omitiendo el número de producto para confirmar el rechazo de la petición |
| EV-88 | HU-104-ADP-AVV | [HU-104-ADP-AVV] Como analista de pruebas quiero intentar la consulta de CDT con una operación no soportada para confirmar el rechazo defensivo 400 |
| EV-89 | HU-104-ADP-AVV | [HU-104-ADP-AVV] Como analista de pruebas quiero consultar un CDT con plazo en días límite o especial para confirmar el cálculo correcto de fechas |
| EV-90 | HU-104-ADP-AVV | [HU-104-ADP-AVV] Como analista de pruebas quiero consultar un CDT ya vencido para confirmar la información de estado de vencimiento |
| EV-91 | HU-104-ADP-AVV | [HU-104-ADP-AVV] Como analista de pruebas quiero simular un error técnico en el backend de CDT para confirmar el código de error y Circuit Breaker |
| EV-97 | HU-104-ADP-BDB | [HU-104-ADP-BDB] Como analista de pruebas quiero consultar el detalle de un CDT activo en Banco de Bogotá para confirmar la recepción de monto, tasa EA, fechas e intereses acumulados |
| EV-98 | HU-104-ADP-BDB | [HU-104-ADP-BDB] Como analista de pruebas quiero consultar un CDT no registrado en Banco de Bogotá para confirmar el retorno de código 404 |
| EV-99 | HU-104-ADP-BDB | [HU-104-ADP-BDB] Como analista de pruebas quiero solicitar la consulta de CDT omitiendo el identificador de producto para confirmar el rechazo de la solicitud |
| EV-100 | HU-104-ADP-BDB | [HU-104-ADP-BDB] Como analista de pruebas quiero enviar una solicitud de CDT con operación no soportada para confirmar el rechazo con código 400 |
| EV-101 | HU-104-ADP-BDB | [HU-104-ADP-BDB] Como analista de pruebas quiero consultar un CDT con intereses acumulados liquidados a la fecha para confirmar la consistencia del monto de rendimiento |
| EV-102 | HU-104-ADP-BDB | [HU-104-ADP-BDB] Como analista de pruebas quiero consultar un CDT con periodicidad de pago mensual para confirmar la entrega de la periodicidad pactada |
| EV-103 | HU-104-ADP-BDB | [HU-104-ADP-BDB] Como analista de pruebas quiero simular un error técnico o timeout en balances-management-v2 para confirmar el retorno de 502/504 y auditoría |
| EV-109 | HU-101-ADP-BPO-CLIENTE | [HU-101-ADP-BPO-CLIENTE] Adaptador BPO — Consulta Cliente - flujo principal exitoso |
| EV-110 | HU-101-ADP-BPO-CLIENTE | [HU-101-ADP-BPO-CLIENTE] Adaptador BPO — Consulta Cliente - dato obligatorio ausente |
| EV-111 | HU-101-ADP-BPO-CLIENTE | [HU-101-ADP-BPO-CLIENTE] Adaptador BPO — Consulta Cliente - operación no soportada |
| EV-112 | HU-101-ADP-BPO-CLIENTE | [HU-101-ADP-BPO-CLIENTE] Adaptador BPO — Consulta Cliente - cliente o producto no encontrado |
| EV-113 | HU-101-ADP-BPO-CLIENTE | [HU-101-ADP-BPO-CLIENTE] Adaptador BPO — Consulta Cliente - error técnico del banco |
| EV-116 | HU-101-ADP-BPO | [HU-101-ADP-BPO] Adaptador BPO — Consulta Productos - flujo principal exitoso |
| EV-117 | HU-101-ADP-BPO | [HU-101-ADP-BPO] Adaptador BPO — Consulta Productos - dato obligatorio ausente |
| EV-118 | HU-101-ADP-BPO | [HU-101-ADP-BPO] Adaptador BPO — Consulta Productos - operación no soportada |
| EV-119 | HU-101-ADP-BPO | [HU-101-ADP-BPO] Adaptador BPO — Consulta Productos - cliente o producto no encontrado |
| EV-120 | HU-101-ADP-BPO | [HU-101-ADP-BPO] Adaptador BPO — Consulta Productos - error técnico del banco |
| EV-123 | HU-101-ADP-OCC-CLIENTE | [HU-101-ADP-OCC-CLIENTE] Adaptador OCC — Consulta Cliente - flujo principal exitoso |
| EV-124 | HU-101-ADP-OCC-CLIENTE | [HU-101-ADP-OCC-CLIENTE] Adaptador OCC — Consulta Cliente - dato obligatorio ausente |
| EV-125 | HU-101-ADP-OCC-CLIENTE | [HU-101-ADP-OCC-CLIENTE] Adaptador OCC — Consulta Cliente - operación no soportada |
| EV-126 | HU-101-ADP-OCC-CLIENTE | [HU-101-ADP-OCC-CLIENTE] Adaptador OCC — Consulta Cliente - cliente o producto no encontrado |
| EV-127 | HU-101-ADP-OCC-CLIENTE | [HU-101-ADP-OCC-CLIENTE] Adaptador OCC — Consulta Cliente - error técnico del banco |
| EV-130 | HU-101-ADP-OCC | [HU-101-ADP-OCC] Adaptador OCC — Consulta Productos - flujo principal exitoso |
| EV-131 | HU-101-ADP-OCC | [HU-101-ADP-OCC] Adaptador OCC — Consulta Productos - dato obligatorio ausente |
| EV-132 | HU-101-ADP-OCC | [HU-101-ADP-OCC] Adaptador OCC — Consulta Productos - operación no soportada |
| EV-133 | HU-101-ADP-OCC | [HU-101-ADP-OCC] Adaptador OCC — Consulta Productos - cliente o producto no encontrado |
| EV-134 | HU-101-ADP-OCC | [HU-101-ADP-OCC] Adaptador OCC — Consulta Productos - error técnico del banco |
| EV-137 | HU-102-ADP-BPO | [HU-102-ADP-BPO] Adaptador BPO — Consulta Detallada - flujo principal exitoso |
| EV-138 | HU-102-ADP-BPO | [HU-102-ADP-BPO] Adaptador BPO — Consulta Detallada - dato obligatorio ausente |
| EV-139 | HU-102-ADP-BPO | [HU-102-ADP-BPO] Adaptador BPO — Consulta Detallada - operación no soportada |
| EV-140 | HU-102-ADP-BPO | [HU-102-ADP-BPO] Adaptador BPO — Consulta Detallada - cliente o producto no encontrado |
| EV-141 | HU-102-ADP-BPO | [HU-102-ADP-BPO] Adaptador BPO — Consulta Detallada - error técnico del banco |
| EV-144 | HU-102-ADP-OCC | [HU-102-ADP-OCC] Adaptador OCC — Consulta Detallada - flujo principal exitoso |
| EV-145 | HU-102-ADP-OCC | [HU-102-ADP-OCC] Adaptador OCC — Consulta Detallada - dato obligatorio ausente |
| EV-146 | HU-102-ADP-OCC | [HU-102-ADP-OCC] Adaptador OCC — Consulta Detallada - operación no soportada |
| EV-147 | HU-102-ADP-OCC | [HU-102-ADP-OCC] Adaptador OCC — Consulta Detallada - cliente o producto no encontrado |
| EV-148 | HU-102-ADP-OCC | [HU-102-ADP-OCC] Adaptador OCC — Consulta Detallada - error técnico del banco |
| EV-151 | HU-103-ORQ | [HU-103-ORQ] Orquestador — Consulta Detallada de TC - flujo principal exitoso |
| EV-152 | HU-103-ORQ | [HU-103-ORQ] Orquestador — Consulta Detallada de TC - dato obligatorio ausente |
| EV-153 | HU-103-ORQ | [HU-103-ORQ] Orquestador — Consulta Detallada de TC - operación no soportada |
| EV-154 | HU-103-ORQ | [HU-103-ORQ] Orquestador — Consulta Detallada de TC - cliente o producto no encontrado |
| EV-155 | HU-103-ORQ | [HU-103-ORQ] Orquestador — Consulta Detallada de TC - error técnico del banco |
| EV-158 | HU-104-ORQ | [HU-104-ORQ] Orquestador — Consulta Detallada de CDT - flujo principal exitoso |
| EV-159 | HU-104-ORQ | [HU-104-ORQ] Orquestador — Consulta Detallada de CDT - dato obligatorio ausente |
| EV-160 | HU-104-ORQ | [HU-104-ORQ] Orquestador — Consulta Detallada de CDT - operación no soportada |
| EV-161 | HU-104-ORQ | [HU-104-ORQ] Orquestador — Consulta Detallada de CDT - cliente o producto no encontrado |
| EV-162 | HU-104-ORQ | [HU-104-ORQ] Orquestador — Consulta Detallada de CDT - error técnico del banco |
| EV-169 | HU-201-ADP-AVV | [HU-201-ADP-AVV] Como analista de pruebas quiero ejecutar el bloqueo definitivo de tarjeta debito exitosamente para confirmar que el bloqueo definitivo se confirma y se retorna el resultado normalizado al orquestador |
| EV-170 | HU-201-ADP-AVV | [HU-201-ADP-AVV] Como analista de pruebas quiero validar el enrutamiento por banco y operacion para confirmar que el adaptador selecciona el servicio bancario correcto sin procesar operaciones inesperadas |
| EV-171 | HU-201-ADP-AVV | [HU-201-ADP-AVV] Como analista de pruebas quiero validar la constante funcional de bloqueo definitivo para confirmar que el bloqueo enviado al banco corresponde a un bloqueo definitivo |
| EV-172 | HU-201-ADP-AVV | [HU-201-ADP-AVV] Como analista de pruebas quiero validar el mapeo de causales de robo perdida y fraude para confirmar que cada causal se homologa segun la regla de integracion definida para el banco |
| EV-173 | HU-201-ADP-AVV | [HU-201-ADP-AVV] Como analista de pruebas quiero validar auditoria y trazabilidad de la operacion para confirmar que se registra el request recibido y la respuesta o error antes de retornar al orquestador |
| EV-174 | HU-201-ADP-AVV | [HU-201-ADP-AVV] Como analista de pruebas quiero validar enmascaramiento en registros y respuesta para confirmar que la informacion sensible se protege en salidas de consulta humana y registros de auditoria |
| EV-175 | HU-201-ADP-AVV | [HU-201-ADP-AVV] Como analista de pruebas quiero validar activacion de resiliencia ante fallas repetidas para confirmar que el mecanismo de proteccion evita llamadas indefinidas y retorna un error controlado |
| EV-176 | HU-201-ADP-AVV | [HU-201-ADP-AVV] Como analista de pruebas quiero rechazar una operacion no soportada para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro |
| EV-177 | HU-201-ADP-AVV | [HU-201-ADP-AVV] Como analista de pruebas quiero manejar una falla de comunicacion con el banco para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro |
| EV-178 | HU-201-ADP-AVV | [HU-201-ADP-AVV] Como analista de pruebas quiero manejar un timeout del banco para confirmar que se retorna codigo 504 al orquestador con mensaje funcional claro |
| EV-184 | HU-201-ADP-BDB | [HU-201-ADP-BDB] Como analista de pruebas quiero ejecutar el bloqueo definitivo de tarjeta debito exitosamente para confirmar que la tarjeta queda con bloqueo definitivo y la respuesta se normaliza hacia el orquestador |
| EV-185 | HU-201-ADP-BDB | [HU-201-ADP-BDB] Como analista de pruebas quiero validar el enrutamiento por banco y operacion para confirmar que el adaptador selecciona el servicio bancario correcto sin procesar operaciones inesperadas |
| EV-186 | HU-201-ADP-BDB | [HU-201-ADP-BDB] Como analista de pruebas quiero validar la constante funcional de bloqueo definitivo para confirmar que el bloqueo enviado al banco corresponde a un bloqueo definitivo |
| EV-187 | HU-201-ADP-BDB | [HU-201-ADP-BDB] Como analista de pruebas quiero validar el mapeo de causales de robo perdida y fraude para confirmar que cada causal se homologa segun la regla de integracion definida para el banco |
| EV-188 | HU-201-ADP-BDB | [HU-201-ADP-BDB] Como analista de pruebas quiero validar auditoria y trazabilidad de la operacion para confirmar que se registra el request recibido y la respuesta o error antes de retornar al orquestador |
| EV-189 | HU-201-ADP-BDB | [HU-201-ADP-BDB] Como analista de pruebas quiero validar enmascaramiento en registros y respuesta para confirmar que la informacion sensible se protege en salidas de consulta humana y registros de auditoria |
| EV-190 | HU-201-ADP-BDB | [HU-201-ADP-BDB] Como analista de pruebas quiero validar activacion de resiliencia ante fallas repetidas para confirmar que el mecanismo de proteccion evita llamadas indefinidas y retorna un error controlado |
| EV-191 | HU-201-ADP-BDB | [HU-201-ADP-BDB] Como analista de pruebas quiero confirmar la respuesta cuando la tarjeta no existe para confirmar que se retorna codigo 404 al orquestador con mensaje funcional claro |
| EV-192 | HU-201-ADP-BDB | [HU-201-ADP-BDB] Como analista de pruebas quiero confirmar la respuesta cuando la tarjeta ya esta bloqueada para confirmar que se retorna codigo 409 al orquestador con mensaje funcional claro |
| EV-193 | HU-201-ADP-BDB | [HU-201-ADP-BDB] Como analista de pruebas quiero confirmar el mapeo de error de negocio para confirmar que se retorna codigo 422 al orquestador con mensaje funcional claro |
| EV-194 | HU-201-ADP-BDB | [HU-201-ADP-BDB] Como analista de pruebas quiero rechazar una operacion no soportada para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro |
| EV-195 | HU-201-ADP-BDB | [HU-201-ADP-BDB] Como analista de pruebas quiero manejar credenciales o acceso de integracion invalido para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro |
| EV-196 | HU-201-ADP-BDB | [HU-201-ADP-BDB] Como analista de pruebas quiero manejar un timeout del banco para confirmar que se retorna codigo 504 al orquestador con mensaje funcional claro |
| EV-202 | HU-201-ADP-BPO | [HU-201-ADP-BPO] Como analista de pruebas quiero ejecutar el bloqueo definitivo de tarjeta debito exitosamente para confirmar que los prerequisitos de identidad y consulta de tarjeta se cumplen, el bloqueo se confirma y la respuesta se normaliza |
| EV-203 | HU-201-ADP-BPO | [HU-201-ADP-BPO] Como analista de pruebas quiero validar el enrutamiento por banco y operacion para confirmar que el adaptador selecciona el servicio bancario correcto sin procesar operaciones inesperadas |
| EV-204 | HU-201-ADP-BPO | [HU-201-ADP-BPO] Como analista de pruebas quiero validar la constante funcional de bloqueo definitivo para confirmar que el bloqueo enviado al banco corresponde a un bloqueo definitivo |
| EV-205 | HU-201-ADP-BPO | [HU-201-ADP-BPO] Como analista de pruebas quiero validar el mapeo de causales de robo perdida y fraude para confirmar que cada causal se homologa segun la regla de integracion definida para el banco |
| EV-206 | HU-201-ADP-BPO | [HU-201-ADP-BPO] Como analista de pruebas quiero validar auditoria y trazabilidad de la operacion para confirmar que se registra el request recibido y la respuesta o error antes de retornar al orquestador |
| EV-207 | HU-201-ADP-BPO | [HU-201-ADP-BPO] Como analista de pruebas quiero validar enmascaramiento en registros y respuesta para confirmar que la informacion sensible se protege en salidas de consulta humana y registros de auditoria |
| EV-208 | HU-201-ADP-BPO | [HU-201-ADP-BPO] Como analista de pruebas quiero validar activacion de resiliencia ante fallas repetidas para confirmar que el mecanismo de proteccion evita llamadas indefinidas y retorna un error controlado |
| EV-209 | HU-201-ADP-BPO | [HU-201-ADP-BPO] Como analista de pruebas quiero validar prerequisitos de identidad y consulta de tarjeta para confirmar que el bloqueo se ejecuta solo despues de cumplir los prerequisitos |
| EV-210 | HU-201-ADP-BPO | [HU-201-ADP-BPO] Como analista de pruebas quiero detener el bloqueo cuando falla la verificacion de identidad para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro |
| EV-211 | HU-201-ADP-BPO | [HU-201-ADP-BPO] Como analista de pruebas quiero detener el bloqueo cuando no se obtiene la tarjeta del cliente para confirmar que se retorna codigo 404 al orquestador con mensaje funcional claro |
| EV-212 | HU-201-ADP-BPO | [HU-201-ADP-BPO] Como analista de pruebas quiero confirmar la respuesta cuando la tarjeta no existe para confirmar que se retorna codigo 404 al orquestador con mensaje funcional claro |
| EV-213 | HU-201-ADP-BPO | [HU-201-ADP-BPO] Como analista de pruebas quiero rechazar una operacion no soportada para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro |
| EV-214 | HU-201-ADP-BPO | [HU-201-ADP-BPO] Como analista de pruebas quiero manejar una IP no autorizada por el banco para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro |
| EV-215 | HU-201-ADP-BPO | [HU-201-ADP-BPO] Como analista de pruebas quiero manejar un error de certificado o seguridad para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro |
| EV-216 | HU-201-ADP-BPO | [HU-201-ADP-BPO] Como analista de pruebas quiero manejar un timeout del banco para confirmar que se retorna codigo 504 al orquestador con mensaje funcional claro |
| EV-222 | HU-201-ADP-OCC | [HU-201-ADP-OCC] Como analista de pruebas quiero ejecutar el bloqueo definitivo de tarjeta debito exitosamente para confirmar que el banco confirma la cancelacion definitiva y la respuesta se normaliza con estado bloqueada |
| EV-223 | HU-201-ADP-OCC | [HU-201-ADP-OCC] Como analista de pruebas quiero validar el enrutamiento por banco y operacion para confirmar que el adaptador selecciona el servicio bancario correcto sin procesar operaciones inesperadas |
| EV-224 | HU-201-ADP-OCC | [HU-201-ADP-OCC] Como analista de pruebas quiero validar la constante funcional de bloqueo definitivo para confirmar que el bloqueo enviado al banco corresponde a un bloqueo definitivo |
| EV-225 | HU-201-ADP-OCC | [HU-201-ADP-OCC] Como analista de pruebas quiero validar el mapeo de causales de robo perdida y fraude para confirmar que cada causal se homologa segun la regla de integracion definida para el banco |
| EV-226 | HU-201-ADP-OCC | [HU-201-ADP-OCC] Como analista de pruebas quiero validar auditoria y trazabilidad de la operacion para confirmar que se registra el request recibido y la respuesta o error antes de retornar al orquestador |
| EV-227 | HU-201-ADP-OCC | [HU-201-ADP-OCC] Como analista de pruebas quiero validar enmascaramiento en registros y respuesta para confirmar que la informacion sensible se protege en salidas de consulta humana y registros de auditoria |
| EV-228 | HU-201-ADP-OCC | [HU-201-ADP-OCC] Como analista de pruebas quiero validar activacion de resiliencia ante fallas repetidas para confirmar que el mecanismo de proteccion evita llamadas indefinidas y retorna un error controlado |
| EV-229 | HU-201-ADP-OCC | [HU-201-ADP-OCC] Como analista de pruebas quiero confirmar la respuesta cuando la tarjeta no existe para confirmar que se retorna codigo 404 al orquestador con mensaje funcional claro |
| EV-230 | HU-201-ADP-OCC | [HU-201-ADP-OCC] Como analista de pruebas quiero confirmar la respuesta cuando el estado no permite bloqueo para confirmar que se retorna codigo 422 al orquestador con mensaje funcional claro |
| EV-231 | HU-201-ADP-OCC | [HU-201-ADP-OCC] Como analista de pruebas quiero rechazar una operacion no soportada para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro |
| EV-232 | HU-201-ADP-OCC | [HU-201-ADP-OCC] Como analista de pruebas quiero manejar una falla de comunicacion con el banco para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro |
| EV-233 | HU-201-ADP-OCC | [HU-201-ADP-OCC] Como analista de pruebas quiero manejar un timeout del banco para confirmar que se retorna codigo 504 al orquestador con mensaje funcional claro |
| EV-239 | HU-203-ADP-AVV | [HU-203-ADP-AVV] Como analista de pruebas quiero ejecutar la actualizacion de datos del cliente exitosamente para confirmar que la actualizacion se confirma con codigo exitoso y mensaje normalizado |
| EV-240 | HU-203-ADP-AVV | [HU-203-ADP-AVV] Como analista de pruebas quiero validar el enrutamiento por banco y operacion para confirmar que el adaptador selecciona el servicio bancario correcto sin procesar operaciones inesperadas |
| EV-241 | HU-203-ADP-AVV | [HU-203-ADP-AVV] Como analista de pruebas quiero validar auditoria y trazabilidad de la actualizacion para confirmar que se registra el request recibido y la respuesta o error antes de retornar al orquestador |
| EV-242 | HU-203-ADP-AVV | [HU-203-ADP-AVV] Como analista de pruebas quiero validar proteccion de credenciales y configuracion para confirmar que no se usan credenciales hardcodeadas y la configuracion depende del ambiente activo |
| EV-243 | HU-203-ADP-AVV | [HU-203-ADP-AVV] Como analista de pruebas quiero validar activacion de resiliencia ante fallas repetidas para confirmar que el mecanismo de proteccion evita llamadas indefinidas y retorna un error controlado |
| EV-244 | HU-203-ADP-AVV | [HU-203-ADP-AVV] Como analista de pruebas quiero mapear tipos de documento permitidos para confirmar que tipo de documento traducido al codigo requerido por el banco |
| EV-245 | HU-203-ADP-AVV | [HU-203-ADP-AVV] Como analista de pruebas quiero enviar solo campos presentes para actualizar para confirmar que el banco recibe solo los datos informados, sin nulos ni vacios |
| EV-246 | HU-203-ADP-AVV | [HU-203-ADP-AVV] Como analista de pruebas quiero obtener los datos del asesor desde el contexto para confirmar que los datos del asesor se toman del contexto autorizado y no del cuerpo de la solicitud |
| EV-247 | HU-203-ADP-AVV | [HU-203-ADP-AVV] Como analista de pruebas quiero confirmar el mapeo de error de negocio para confirmar que se retorna codigo 422 al orquestador con mensaje funcional claro |
| EV-248 | HU-203-ADP-AVV | [HU-203-ADP-AVV] Como analista de pruebas quiero rechazar una operacion no soportada para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro |
| EV-249 | HU-203-ADP-AVV | [HU-203-ADP-AVV] Como analista de pruebas quiero manejar una falla de comunicacion con el banco para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro |
| EV-250 | HU-203-ADP-AVV | [HU-203-ADP-AVV] Como analista de pruebas quiero manejar un timeout del banco para confirmar que se retorna codigo 504 al orquestador con mensaje funcional claro |
| EV-256 | HU-203-ADP-BDB | [HU-203-ADP-BDB] Como analista de pruebas quiero ejecutar la actualizacion de datos del cliente exitosamente para confirmar que la actualizacion se confirma como exitosa y se retorna mensaje normalizado |
| EV-257 | HU-203-ADP-BDB | [HU-203-ADP-BDB] Como analista de pruebas quiero validar el enrutamiento por banco y operacion para confirmar que el adaptador selecciona el servicio bancario correcto sin procesar operaciones inesperadas |
| EV-258 | HU-203-ADP-BDB | [HU-203-ADP-BDB] Como analista de pruebas quiero validar auditoria y trazabilidad de la actualizacion para confirmar que se registra el request recibido y la respuesta o error antes de retornar al orquestador |
| EV-259 | HU-203-ADP-BDB | [HU-203-ADP-BDB] Como analista de pruebas quiero validar proteccion de credenciales y configuracion para confirmar que no se usan credenciales hardcodeadas y la configuracion depende del ambiente activo |
| EV-260 | HU-203-ADP-BDB | [HU-203-ADP-BDB] Como analista de pruebas quiero validar activacion de resiliencia ante fallas repetidas para confirmar que el mecanismo de proteccion evita llamadas indefinidas y retorna un error controlado |
| EV-261 | HU-203-ADP-BDB | [HU-203-ADP-BDB] Como analista de pruebas quiero generar un identificador unico por solicitud para confirmar que cada intento usa un identificador nuevo para trazabilidad |
| EV-262 | HU-203-ADP-BDB | [HU-203-ADP-BDB] Como analista de pruebas quiero enviar solo campos presentes para actualizar para confirmar que el cuerpo contiene solo los datos informados por el orquestador |
| EV-263 | HU-203-ADP-BDB | [HU-203-ADP-BDB] Como analista de pruebas quiero mapear correctamente los telefonos por tipo para confirmar que cada telefono queda clasificado segun su tipo funcional |
| EV-264 | HU-203-ADP-BDB | [HU-203-ADP-BDB] Como analista de pruebas quiero confirmar el rechazo por datos invalidos para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro |
| EV-265 | HU-203-ADP-BDB | [HU-203-ADP-BDB] Como analista de pruebas quiero confirmar el rechazo por cliente no encontrado para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro |
| EV-266 | HU-203-ADP-BDB | [HU-203-ADP-BDB] Como analista de pruebas quiero manejar credenciales o acceso de integracion invalido para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro |
| EV-267 | HU-203-ADP-BDB | [HU-203-ADP-BDB] Como analista de pruebas quiero rechazar una operacion no soportada para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro |
| EV-268 | HU-203-ADP-BDB | [HU-203-ADP-BDB] Como analista de pruebas quiero manejar un timeout del banco para confirmar que se retorna codigo 504 al orquestador con mensaje funcional claro |
| EV-274 | HU-203-ADP-BPO | [HU-203-ADP-BPO] Como analista de pruebas quiero ejecutar la actualizacion de datos del cliente exitosamente para confirmar que la actualizacion se confirma en el MDM y se retorna resultado normalizado |
| EV-275 | HU-203-ADP-BPO | [HU-203-ADP-BPO] Como analista de pruebas quiero validar el enrutamiento por banco y operacion para confirmar que el adaptador selecciona el servicio bancario correcto sin procesar operaciones inesperadas |
| EV-276 | HU-203-ADP-BPO | [HU-203-ADP-BPO] Como analista de pruebas quiero validar auditoria y trazabilidad de la actualizacion para confirmar que se registra el request recibido y la respuesta o error antes de retornar al orquestador |
| EV-277 | HU-203-ADP-BPO | [HU-203-ADP-BPO] Como analista de pruebas quiero validar proteccion de credenciales y configuracion para confirmar que no se usan credenciales hardcodeadas y la configuracion depende del ambiente activo |
| EV-278 | HU-203-ADP-BPO | [HU-203-ADP-BPO] Como analista de pruebas quiero validar activacion de resiliencia ante fallas repetidas para confirmar que el mecanismo de proteccion evita llamadas indefinidas y retorna un error controlado |
| EV-279 | HU-203-ADP-BPO | [HU-203-ADP-BPO] Como analista de pruebas quiero construir el contexto del operador y del cliente para confirmar que el sobre de integracion separa correctamente operador y cliente |
| EV-280 | HU-203-ADP-BPO | [HU-203-ADP-BPO] Como analista de pruebas quiero generar identificadores unicos de transaccion para confirmar que cada intento queda trazable con identificadores nuevos |
| EV-281 | HU-203-ADP-BPO | [HU-203-ADP-BPO] Como analista de pruebas quiero enviar solo nodos con datos presentes para confirmar que el banco recibe solo estructuras correspondientes a los campos informados |
| EV-282 | HU-203-ADP-BPO | [HU-203-ADP-BPO] Como analista de pruebas quiero confirmar el rechazo por datos invalidos para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro |
| EV-283 | HU-203-ADP-BPO | [HU-203-ADP-BPO] Como analista de pruebas quiero confirmar el rechazo por cliente no encontrado para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro |
| EV-284 | HU-203-ADP-BPO | [HU-203-ADP-BPO] Como analista de pruebas quiero rechazar una operacion no soportada para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro |
| EV-285 | HU-203-ADP-BPO | [HU-203-ADP-BPO] Como analista de pruebas quiero manejar un error interno del banco para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro |
| EV-286 | HU-203-ADP-BPO | [HU-203-ADP-BPO] Como analista de pruebas quiero manejar un timeout del banco para confirmar que se retorna codigo 504 al orquestador con mensaje funcional claro |
| EV-292 | HU-203-ADP-OCC | [HU-203-ADP-OCC] Como analista de pruebas quiero ejecutar la actualizacion de datos del cliente exitosamente para confirmar que el banco confirma la actualizacion y el adaptador retorna respuesta exitosa normalizada |
| EV-293 | HU-203-ADP-OCC | [HU-203-ADP-OCC] Como analista de pruebas quiero validar el enrutamiento por banco y operacion para confirmar que el adaptador selecciona el servicio bancario correcto sin procesar operaciones inesperadas |
| EV-294 | HU-203-ADP-OCC | [HU-203-ADP-OCC] Como analista de pruebas quiero validar auditoria y trazabilidad de la actualizacion para confirmar que se registra el request recibido y la respuesta o error antes de retornar al orquestador |
| EV-295 | HU-203-ADP-OCC | [HU-203-ADP-OCC] Como analista de pruebas quiero validar proteccion de credenciales y configuracion para confirmar que no se usan credenciales hardcodeadas y la configuracion depende del ambiente activo |
| EV-296 | HU-203-ADP-OCC | [HU-203-ADP-OCC] Como analista de pruebas quiero validar activacion de resiliencia ante fallas repetidas para confirmar que el mecanismo de proteccion evita llamadas indefinidas y retorna un error controlado |
| EV-297 | HU-203-ADP-OCC | [HU-203-ADP-OCC] Como analista de pruebas quiero obtener token de integracion antes de actualizar datos para confirmar que la operacion usa un token valido obtenido por el adaptador |
| EV-298 | HU-203-ADP-OCC | [HU-203-ADP-OCC] Como analista de pruebas quiero reutilizar token vigente sin solicitar uno nuevo para confirmar que el adaptador usa el token en cache antes de su expiracion |
| EV-299 | HU-203-ADP-OCC | [HU-203-ADP-OCC] Como analista de pruebas quiero renovar token expirado y reintentar una vez para confirmar que el adaptador renueva el token y completa la actualizacion si el segundo intento es exitoso |
| EV-300 | HU-203-ADP-OCC | [HU-203-ADP-OCC] Como analista de pruebas quiero confirmar el rechazo por datos invalidos para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro |
| EV-301 | HU-203-ADP-OCC | [HU-203-ADP-OCC] Como analista de pruebas quiero manejar error al obtener token de integracion para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro |
| EV-302 | HU-203-ADP-OCC | [HU-203-ADP-OCC] Como analista de pruebas quiero manejar token invalido despues del reintento para confirmar que se retorna codigo 502 al orquestador con mensaje funcional claro |
| EV-303 | HU-203-ADP-OCC | [HU-203-ADP-OCC] Como analista de pruebas quiero rechazar una operacion no soportada para confirmar que se retorna codigo 400 al orquestador con mensaje funcional claro |
| EV-304 | HU-203-ADP-OCC | [HU-203-ADP-OCC] Como analista de pruebas quiero manejar un timeout del banco para confirmar que se retorna codigo 504 al orquestador con mensaje funcional claro |
