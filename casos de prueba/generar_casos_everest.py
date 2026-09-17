from __future__ import annotations

import json
from pathlib import Path
from copy import copy
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from docx import Document

ROOT = Path(__file__).resolve().parent.parent
HU_DIR = ROOT / "insumos_cp" / "hu"
CHECKLIST_PATH = ROOT / "insumos_cp" / "Checklist de Historia de Usuario para generación de casos de prueba.docx"
FORMAT_JIRA_PATH = ROOT / "insumos_cp" / "Formato Jira.xlsx"
OUTPUT_PATH = ROOT / "casos de prueba" / "casos everest.xlsx"

TIPOS_INCLUIDOS = {"Funcional", "Accesibilidad"}

# Definición detallada de casos de prueba funcionales y de accesibilidad por cada HU
CASOS_POR_HU = {'HU-101-ADP-AVV-consulta-cliente.md': {'id': 'HU-101-ADP-AVV-CLIENTE',
                                        'title': 'Adaptador AV Villas — Consulta de Datos del Cliente',
                                        'domain': 'consulta de datos del cliente en AV Villas',
                                        'cases': [{'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-AVV-CLIENTE] Como analista de pruebas '
                                                              'quiero consultar los datos personales y de contacto de '
                                                              'un cliente existente para confirmar la recepción '
                                                              'exitosa y normalizada de su información',
                                                   'Descripcion': 'Validar que al solicitar la consulta de datos del '
                                                                  'cliente con tipo y número de documento válidos, el '
                                                                  'sistema retorne exitosamente nombre completo, '
                                                                  'segmento y datos de contacto normalizados.',
                                                   'Escenario': 'Cliente registrado y activo en AV Villas. Servicios '
                                                                'dependientes disponibles.',
                                                   'Accion': 'Enviar solicitud de consulta de cliente con tipo de '
                                                             "documento 'C' y número de documento '86068761' con "
                                                             'headers de contexto bancario.',
                                                   'Datos': "operacion: CONSULTA_CLIENTE, tipoDocumento: 'C', "
                                                            "numeroDocumento: '86068761', X-Destination-Bank: BAVV, "
                                                            'X-Origin-Bank: BAVV, X-Trace-Id: test-trace-001, '
                                                            'X-IdentDispositivo: 10.0.0.1, X-IdFuncionario: '
                                                            '1016034423, X-Oficina: 001',
                                                   'Resultado Esperado': 'Respuesta exitosa con los datos personales '
                                                                         '(nombre, tipo y número de documento, '
                                                                         'segmento) y de contacto (celular, correo, '
                                                                         'dirección) normalizados.',
                                                   'Prioridad': 'High'},
                                                  {'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-AVV-CLIENTE] Como analista de pruebas '
                                                              'quiero consultar los datos de un cliente no registrado '
                                                              'para confirmar que el sistema responde con la '
                                                              'notificación de cliente no encontrado',
                                                   'Descripcion': 'Validar el comportamiento del sistema cuando se '
                                                                  'consulta un documento que no existe en la base de '
                                                                  'datos del banco.',
                                                   'Escenario': 'Documento de cliente no registrado en los sistemas de '
                                                                'AV Villas.',
                                                   'Accion': 'Enviar solicitud de consulta de cliente con número de '
                                                             'documento inexistente.',
                                                   'Datos': "operacion: CONSULTA_CLIENTE, tipoDocumento: 'CC', "
                                                            "numeroDocumento: '9999999999', X-Destination-Bank: BAVV",
                                                   'Resultado Esperado': 'El sistema retorna estado de negocio 206 con '
                                                                         "mensaje 'Cliente no encontrado en AVV' sin "
                                                                         'interrumpir el flujo.',
                                                   'Prioridad': 'High'},
                                                  {'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-AVV-CLIENTE] Como analista de pruebas '
                                                              'quiero intentar una consulta enviando una operación no '
                                                              'soportada para confirmar que el sistema rechaza la '
                                                              'solicitud defensivamente',
                                                   'Descripcion': 'Validar que si se recibe un valor de operación no '
                                                                  'soportado por este adaptador, se rechaza la '
                                                                  'solicitud de forma controlada.',
                                                   'Escenario': 'Solicitud enviada con código de operación inválido o '
                                                                'no soportado por el adaptador.',
                                                   'Accion': 'Enviar solicitud con valor de operacion '
                                                             "'OPERACION_INVALIDA'.",
                                                   'Datos': "operacion: 'OPERACION_INVALIDA', obj_operacion con datos "
                                                            'de cliente, X-Destination-Bank: BAVV',
                                                   'Resultado Esperado': 'El sistema rechaza la petición retornando '
                                                                         'código 400 por operación no soportada.',
                                                   'Prioridad': 'Medium'},
                                                  {'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-AVV-CLIENTE] Como analista de pruebas '
                                                              'quiero consultar los datos del cliente omitiendo el '
                                                              'número de documento para confirmar la validación y '
                                                              'respuesta de error correspondiente',
                                                   'Descripcion': 'Validar que la omisión de datos indispensables de '
                                                                  'identificación en la solicitud genere el rechazo o '
                                                                  'error esperado por el servicio.',
                                                   'Escenario': 'Solicitud con cuerpo incompleto sin número de '
                                                                'documento.',
                                                   'Accion': 'Enviar solicitud de consulta con obj_operacion omitiendo '
                                                             'el campo numeroDocumento.',
                                                   'Datos': 'operacion: CONSULTA_CLIENTE, obj_operacion: { '
                                                            "tipoDocumento: 'CC' }",
                                                   'Resultado Esperado': 'El servicio bancario rechaza la petición y '
                                                                         'se propaga el error estructurado '
                                                                         'correspondiente.',
                                                   'Prioridad': 'Medium'},
                                                  {'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-AVV-CLIENTE] Como analista de pruebas '
                                                              'quiero consultar los datos del cliente con un tipo de '
                                                              'documento no admitido para confirmar el rechazo de la '
                                                              'solicitud',
                                                   'Descripcion': 'Validar el comportamiento ante un tipo de documento '
                                                                  'con formato o valor no admitido por las reglas de '
                                                                  'negocio bancarias.',
                                                   'Escenario': 'Solicitud con tipo de documento con formato no '
                                                                'permitido.',
                                                   'Accion': "Enviar solicitud con tipoDocumento 'XYZ' y número de "
                                                             'documento válido.',
                                                   'Datos': "operacion: CONSULTA_CLIENTE, tipoDocumento: 'XYZ', "
                                                            "numeroDocumento: '86068761'",
                                                   'Resultado Esperado': 'El sistema informa error de validación o '
                                                                         'rechazo desde el servicio bancario sin '
                                                                         'inconsistencias.',
                                                   'Prioridad': 'Medium'},
                                                  {'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-AVV-CLIENTE] Como analista de pruebas '
                                                              'quiero consultar un cliente con nombres y direcciones '
                                                              'extensos para confirmar la correcta integridad y '
                                                              'completitud de la respuesta',
                                                   'Descripcion': 'Validar que clientes con datos de contacto o '
                                                                  'nombres en el límite superior de longitud sean '
                                                                  'mapeados y retornados íntegramente.',
                                                   'Escenario': 'Cliente con datos extensos registrado en AV Villas.',
                                                   'Accion': 'Enviar solicitud de consulta sobre cliente con nombres y '
                                                             'direcciones compuestas.',
                                                   'Datos': "operacion: CONSULTA_CLIENTE, tipoDocumento: 'CC', "
                                                            'numeroDocumento de cliente con datos extensos',
                                                   'Resultado Esperado': 'La respuesta normalizada incluye la '
                                                                         'totalidad de nombres, apellidos y '
                                                                         'direcciones sin truncamiento.',
                                                   'Prioridad': 'Low'},
                                                  {'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-AVV-CLIENTE] Como analista de pruebas '
                                                              'quiero simular una falla o indisponibilidad en el '
                                                              'servicio bancario para confirmar el manejo de error y '
                                                              'trazabilidad',
                                                   'Descripcion': 'Validar que ante indisponibilidad, error 502 o '
                                                                  'timeout del servicio bancario de AV Villas, el '
                                                                  'sistema propague el error estándar correspondiente.',
                                                   'Escenario': 'Servicio bancario de datos de cliente no disponible o '
                                                                'respondiendo con timeout.',
                                                   'Accion': 'Ejecutar consulta de cliente mientras el servicio '
                                                             'bancario subyacente genera timeout o error interno.',
                                                   'Datos': 'operacion: CONSULTA_CLIENTE, datos válidos de cliente en '
                                                            'ambiente con servicio bancario caído.',
                                                   'Resultado Esperado': 'El sistema responde con código 502 o 504 '
                                                                         'según corresponda, registrando la traza de '
                                                                         'auditoría en la cola SQS correspondiente.',
                                                   'Prioridad': 'Medium'},
                                                  {'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-AVV-CLIENTE] Como analista de pruebas '
                                                              'quiero validar la autenticación biométrica de huella '
                                                              'dactilar exitosa (OK) para confirmar que el sistema '
                                                              'autoriza la consulta de datos del cliente en AV Villas',
                                                   'Descripcion': 'Validar que al presentar una huella biométrica '
                                                                  'válida y coincidente (validación OK), el sistema '
                                                                  'autentique satisfactoriamente la identidad del '
                                                                  'cliente y permita el procesamiento de la consulta '
                                                                  'de datos del cliente en AV Villas.',
                                                   'Escenario': 'Cliente presente en canal presencial/oficina con '
                                                                'huella biométrica registrada y coincidente (Match OK) '
                                                                'en el servicio de biometría.',
                                                   'Accion': 'Ejecutar la validación biométrica de huella con '
                                                             'resultado exitoso (OK) previa a la solicitud de la '
                                                             'consulta de datos del cliente en AV Villas.',
                                                   'Datos': 'Identificación de cliente válida, captura de huella '
                                                            'dactilar: match OK (100% coincidencia), contexto de '
                                                            'oficina/asesor.',
                                                   'Resultado Esperado': 'Autenticación biométrica aprobada (OK) y '
                                                                         'ejecución exitosa de la consulta de datos '
                                                                         'del cliente en AV Villas retornando la '
                                                                         'información correspondiente.',
                                                   'Prioridad': 'High'},
                                                  {'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-AVV-CLIENTE] Como analista de pruebas '
                                                              'quiero validar el rechazo por huella dactilar no '
                                                              'coincidente o inválida (No OK) para confirmar que el '
                                                              'sistema bloquea la consulta de datos del cliente en AV '
                                                              'Villas',
                                                   'Descripcion': 'Validar que ante una huella biométrica no '
                                                                  'coincidente o no reconocida (validación No OK), el '
                                                                  'sistema rechace la autenticación y bloquee el '
                                                                  'procesamiento de la consulta de datos del cliente '
                                                                  'en AV Villas.',
                                                   'Escenario': 'Intento de operación con huella biométrica no '
                                                                'coincidente o rechazada (Match No OK) por el servicio '
                                                                'de biometría.',
                                                   'Accion': 'Ejecutar la validación biométrica de huella enviando una '
                                                             'muestra no coincidente (No OK).',
                                                   'Datos': 'Identificación de cliente, captura de huella dactilar: '
                                                            'match No OK (no coincidencia / rechazo biométrico).',
                                                   'Resultado Esperado': 'El sistema deniega el acceso por validación '
                                                                         'biométrica No OK, no procesa la consulta de '
                                                                         'datos del cliente en AV Villas y retorna el '
                                                                         'mensaje de autenticación fallida.',
                                                   'Prioridad': 'High'},
                                                  {'Tipo de test': 'Accesibilidad',
                                                   'Resumen': '[HU-101-ADP-AVV-CLIENTE] Como analista de pruebas '
                                                              'quiero verificar que la información de identificación y '
                                                              'contacto del cliente sea clara, estructurada y '
                                                              'comprensible para consumo humano',
                                                   'Descripcion': 'Validar que los datos del cliente retornados '
                                                                  '(nombres, segmento, teléfonos, direcciones) cuenten '
                                                                  'con rotulado inequívoco y orden lógico para su '
                                                                  'consumo y visualización.',
                                                   'Escenario': 'Respuesta de consulta de cliente procesada por el '
                                                                'sistema.',
                                                   'Accion': 'Revisar la semántica, etiquetas y jerarquía de los datos '
                                                             'personales y de contacto en la salida.',
                                                   'Datos': 'Respuesta normalizada de cliente con datos completos.',
                                                   'Resultado Esperado': 'Los datos están etiquetados de forma '
                                                                         'explícita, sin abreviaturas ambiguas y '
                                                                         'facilitando su lectura por asesores y '
                                                                         'herramientas de accesibilidad.',
                                                   'Prioridad': 'Medium'},
                                                  {'Tipo de test': 'Accesibilidad',
                                                   'Resumen': '[HU-101-ADP-AVV-CLIENTE] Como analista de pruebas '
                                                              'quiero verificar que los mensajes de estado y error de '
                                                              'consulta de cliente sean legibles y orientativos',
                                                   'Descripcion': 'Validar que ante clientes no encontrados o errores '
                                                                  'de consulta, los mensajes entregados describan la '
                                                                  'situación sin jerga técnica incomprensible.',
                                                   'Escenario': 'Mensajes generados por casos de cliente no encontrado '
                                                                'o datos incorrectos.',
                                                   'Accion': 'Inspeccionar los textos de StatusDesc y mensajes de '
                                                             'validación.',
                                                   'Datos': 'Respuestas de error y estado 206/400 del flujo.',
                                                   'Resultado Esperado': 'Los mensajes proporcionan descripciones '
                                                                         'funcionales claras y accionables para el '
                                                                         'usuario final.',
                                                   'Prioridad': 'Medium'},
                                                  {'Tipo de test': 'Accesibilidad',
                                                   'Resumen': '[HU-101-ADP-AVV-CLIENTE] Como analista de pruebas '
                                                              'quiero verificar la consistencia en el formato de '
                                                              'números telefónicos y correos para su correcta '
                                                              'interpretación',
                                                   'Descripcion': 'Validar que los datos de contacto posean formatos '
                                                                  'legibles y estandarizados.',
                                                   'Escenario': 'Cliente con múltiples medios de contacto en respuesta '
                                                                'normalizada.',
                                                   'Accion': 'Verificar la estructura y separadores de datos de '
                                                             'contacto.',
                                                   'Datos': 'Bloque de datos de contacto en la respuesta de cliente.',
                                                   'Resultado Esperado': 'La información es uniforme, legible y no '
                                                                         'presenta concatenaciones confusas.',
                                                   'Prioridad': 'Low'}]},
 'HU-101-ADP-AVV-consulta-productos.md': {'id': 'HU-101-ADP-AVV',
                                          'title': 'Adaptador AV Villas — Consulta de Productos',
                                          'domain': 'consulta de productos en AV Villas',
                                          'cases': [{'Tipo de test': 'Funcional',
                                                     'Resumen': '[HU-101-ADP-AVV] Como analista de pruebas quiero '
                                                                'consultar el portafolio de productos de un cliente '
                                                                'activo para confirmar la recepción consolidada de '
                                                                'cuentas, CDT, carteras y tarjetas',
                                                     'Descripcion': 'Validar la consulta de resumen de productos para '
                                                                    'un cliente con portafolio multiactivo en AV '
                                                                    'Villas.',
                                                     'Escenario': 'Cliente con cuentas de ahorro, créditos, CDT y '
                                                                  'tarjetas en AV Villas.',
                                                     'Accion': 'Enviar solicitud de consulta de productos con '
                                                               "tipoDocumento 'CC' y numeroDocumento '86068761'.",
                                                     'Datos': "operacion: CONSULTA_PRODUCTOS, tipoDocumento: 'CC', "
                                                              "numeroDocumento: '86068761', X-Destination-Bank: BAVV, "
                                                              'X-RqUID: 99966666, X-IPAddr: 10.0.0.1, X-ClientDt: '
                                                              '2026-09-08T10:00:00.000, X-SessKey: cualquier-sesion',
                                                     'Resultado Esperado': 'Respuesta exitosa con el resumen de '
                                                                           'cuentas, CDT, carteras y tarjetas de '
                                                                           'crédito activas del cliente.',
                                                     'Prioridad': 'High'},
                                                    {'Tipo de test': 'Funcional',
                                                     'Resumen': '[HU-101-ADP-AVV] Como analista de pruebas quiero '
                                                                'consultar los productos de un cliente que no tiene '
                                                                'productos activos para confirmar la respuesta de '
                                                                'cliente sin productos',
                                                     'Descripcion': 'Validar que cuando el cliente existe pero no '
                                                                    'posee productos activos, el sistema responda '
                                                                    'adecuadamente con el código de negocio '
                                                                    'respectivo.',
                                                     'Escenario': 'Cliente registrado en AV Villas sin productos '
                                                                  'activos asociados.',
                                                     'Accion': 'Enviar solicitud de consulta de productos para un '
                                                               'cliente sin productos vigentes.',
                                                     'Datos': "operacion: CONSULTA_PRODUCTOS, tipoDocumento: 'CC', "
                                                              'numeroDocumento de cliente sin productos',
                                                     'Resultado Esperado': 'El sistema retorna código 206 con '
                                                                           "StatusDesc 'El cliente no tiene productos "
                                                                           "en AVV'.",
                                                     'Prioridad': 'High'},
                                                    {'Tipo de test': 'Funcional',
                                                     'Resumen': '[HU-101-ADP-AVV] Como analista de pruebas quiero '
                                                                'consultar productos de un cliente no registrado para '
                                                                'confirmar la notificación de cliente no encontrado',
                                                     'Descripcion': 'Validar el comportamiento ante consulta de '
                                                                    'productos de una identificación inexistente.',
                                                     'Escenario': 'Identificación de cliente no registrada en AV '
                                                                  'Villas.',
                                                     'Accion': 'Enviar solicitud de consulta de productos con '
                                                               'documento inexistente.',
                                                     'Datos': "operacion: CONSULTA_PRODUCTOS, tipoDocumento: 'CC', "
                                                              "numeroDocumento: '00000000'",
                                                     'Resultado Esperado': 'El sistema retorna estado 206 con mensaje '
                                                                           "'Cliente no encontrado en AVV'.",
                                                     'Prioridad': 'High'},
                                                    {'Tipo de test': 'Funcional',
                                                     'Resumen': '[HU-101-ADP-AVV] Como analista de pruebas quiero '
                                                                'solicitar la consulta de productos con una operación '
                                                                'no soportada para confirmar el rechazo de la petición',
                                                     'Descripcion': 'Validar el control defensivo del adaptador ante '
                                                                    'códigos de operación erróneos.',
                                                     'Escenario': 'Solicitud con código de operacion no '
                                                                  'correspondiente a CONSULTA_PRODUCTOS.',
                                                     'Accion': 'Enviar solicitud con valor de operacion '
                                                               "'CONSULTA_INVALIDA'.",
                                                     'Datos': "operacion: 'CONSULTA_INVALIDA', X-Destination-Bank: "
                                                              'BAVV',
                                                     'Resultado Esperado': 'El sistema lanza excepción y responde '
                                                                           'código 400 por operación no soportada.',
                                                     'Prioridad': 'Medium'},
                                                    {'Tipo de test': 'Funcional',
                                                     'Resumen': '[HU-101-ADP-AVV] Como analista de pruebas quiero '
                                                                'consultar productos omitiendo los datos de '
                                                                'identificación para confirmar la validación del '
                                                                'sistema',
                                                     'Descripcion': 'Validar que la petición sin parámetros de '
                                                                    'identificación sea rechazada.',
                                                     'Escenario': 'Petición con obj_operacion vacío o nulo.',
                                                     'Accion': 'Enviar solicitud de consulta de productos con '
                                                               'obj_operacion vacío.',
                                                     'Datos': 'operacion: CONSULTA_PRODUCTOS, obj_operacion: {}',
                                                     'Resultado Esperado': 'El sistema rechaza la petición con el '
                                                                           'mensaje de error correspondiente.',
                                                     'Prioridad': 'Medium'},
                                                    {'Tipo de test': 'Funcional',
                                                     'Resumen': '[HU-101-ADP-AVV] Como analista de pruebas quiero '
                                                                'verificar la consulta de productos para un cliente '
                                                                'con más de 10 productos para confirmar la completitud '
                                                                'del listado',
                                                     'Descripcion': 'Validar que clientes con alto volumen de '
                                                                    'productos reciban la totalidad de cuentas, CDT, '
                                                                    'carteras y TC.',
                                                     'Escenario': 'Cliente con múltiples productos de diferentes '
                                                                  'familias.',
                                                     'Accion': 'Enviar solicitud de consulta de productos para cliente '
                                                               'con portafolio amplio.',
                                                     'Datos': 'operacion: CONSULTA_PRODUCTOS, identificación de '
                                                              'cliente con portafolio múltiple',
                                                     'Resultado Esperado': 'La respuesta lista todos los productos sin '
                                                                           'omitir registros ni duplicar información.',
                                                     'Prioridad': 'Medium'},
                                                    {'Tipo de test': 'Funcional',
                                                     'Resumen': '[HU-101-ADP-AVV] Como analista de pruebas quiero '
                                                                'simular un error técnico o timeout en el servicio '
                                                                'SOAP bancario para confirmar el manejo de error y '
                                                                'Circuit Breaker',
                                                     'Descripcion': 'Validar la resiliencia del adaptador y el retorno '
                                                                    'de error 502/504 ante falla del servicio SOAP '
                                                                    'bancario.',
                                                     'Escenario': 'Servicio SOAP de productos de AV Villas caído o '
                                                                  'fuera de tiempo.',
                                                     'Accion': 'Ejecutar consulta de productos simulando '
                                                               'indisponibilidad en el backend bancario.',
                                                     'Datos': 'operacion: CONSULTA_PRODUCTOS, datos válidos de cliente '
                                                              'en ambiente con backend caído',
                                                     'Resultado Esperado': 'El sistema responde con código 502 o 504 y '
                                                                           'activa el mecanismo de Circuit Breaker de '
                                                                           'Resilience4j.',
                                                     'Prioridad': 'Medium'},
                                                    {'Tipo de test': 'Funcional',
                                                     'Resumen': '[HU-101-ADP-AVV] Como analista de pruebas quiero '
                                                                'validar la autenticación biométrica de huella '
                                                                'dactilar exitosa (OK) para confirmar que el sistema '
                                                                'autoriza la consulta de productos en AV Villas',
                                                     'Descripcion': 'Validar que al presentar una huella biométrica '
                                                                    'válida y coincidente (validación OK), el sistema '
                                                                    'autentique satisfactoriamente la identidad del '
                                                                    'cliente y permita el procesamiento de la consulta '
                                                                    'de productos en AV Villas.',
                                                     'Escenario': 'Cliente presente en canal presencial/oficina con '
                                                                  'huella biométrica registrada y coincidente (Match '
                                                                  'OK) en el servicio de biometría.',
                                                     'Accion': 'Ejecutar la validación biométrica de huella con '
                                                               'resultado exitoso (OK) previa a la solicitud de la '
                                                               'consulta de productos en AV Villas.',
                                                     'Datos': 'Identificación de cliente válida, captura de huella '
                                                              'dactilar: match OK (100% coincidencia), contexto de '
                                                              'oficina/asesor.',
                                                     'Resultado Esperado': 'Autenticación biométrica aprobada (OK) y '
                                                                           'ejecución exitosa de la consulta de '
                                                                           'productos en AV Villas retornando la '
                                                                           'información correspondiente.',
                                                     'Prioridad': 'High'},
                                                    {'Tipo de test': 'Funcional',
                                                     'Resumen': '[HU-101-ADP-AVV] Como analista de pruebas quiero '
                                                                'validar el rechazo por huella dactilar no coincidente '
                                                                'o inválida (No OK) para confirmar que el sistema '
                                                                'bloquea la consulta de productos en AV Villas',
                                                     'Descripcion': 'Validar que ante una huella biométrica no '
                                                                    'coincidente o no reconocida (validación No OK), '
                                                                    'el sistema rechace la autenticación y bloquee el '
                                                                    'procesamiento de la consulta de productos en AV '
                                                                    'Villas.',
                                                     'Escenario': 'Intento de operación con huella biométrica no '
                                                                  'coincidente o rechazada (Match No OK) por el '
                                                                  'servicio de biometría.',
                                                     'Accion': 'Ejecutar la validación biométrica de huella enviando '
                                                               'una muestra no coincidente (No OK).',
                                                     'Datos': 'Identificación de cliente, captura de huella dactilar: '
                                                              'match No OK (no coincidencia / rechazo biométrico).',
                                                     'Resultado Esperado': 'El sistema deniega el acceso por '
                                                                           'validación biométrica No OK, no procesa la '
                                                                           'consulta de productos en AV Villas y '
                                                                           'retorna el mensaje de autenticación '
                                                                           'fallida.',
                                                     'Prioridad': 'High'},
                                                    {'Tipo de test': 'Accesibilidad',
                                                     'Resumen': '[HU-101-ADP-AVV] Como analista de pruebas quiero '
                                                                'verificar que la agrupación por tipo de producto '
                                                                '(cuentas, CDT, carteras, tarjetas) sea clara y '
                                                                'organizada',
                                                     'Descripcion': 'Validar que la estructura de salida diferencie '
                                                                    'nítidamente cada categoría de producto financiero '
                                                                    'para facilitar la comprensión del usuario.',
                                                     'Escenario': 'Respuesta con múltiples familias de productos '
                                                                  'generada por el adaptador.',
                                                     'Accion': 'Evaluar la jerarquía, agrupación y claridad de las '
                                                               'secciones de productos.',
                                                     'Datos': 'Listado de productos consolidado del cliente.',
                                                     'Resultado Esperado': 'Cada categoría de producto está claramente '
                                                                           'delimitada y categorizada, permitiendo '
                                                                           'navegación y lectura sin confusiones.',
                                                     'Prioridad': 'Medium'},
                                                    {'Tipo de test': 'Accesibilidad',
                                                     'Resumen': '[HU-101-ADP-AVV] Como analista de pruebas quiero '
                                                                'verificar la claridad en el rotulado de saldos, '
                                                                'sobregiros y cupos disponibles',
                                                     'Descripcion': 'Validar que los valores monetarios de cada '
                                                                    'producto presenten etiquetas explícitas y '
                                                                    'comprensibles.',
                                                     'Escenario': 'Productos con saldos y cupos en respuesta de '
                                                                  'consulta.',
                                                     'Accion': 'Revisar la terminología de saldos y cupos en la '
                                                               'salida.',
                                                     'Datos': 'Saldos de cuentas, carteras y cupo disponible de TC.',
                                                     'Resultado Esperado': 'Los campos diferencian con total claridad '
                                                                           'entre saldo total, saldo disponible, '
                                                                           'sobregiro y deuda.',
                                                     'Prioridad': 'Medium'},
                                                    {'Tipo de test': 'Accesibilidad',
                                                     'Resumen': '[HU-101-ADP-AVV] Como analista de pruebas quiero '
                                                                'verificar la legibilidad y coherencia en los mensajes '
                                                                'informativos cuando no existen productos',
                                                     'Descripcion': 'Validar que el mensaje informativo para clientes '
                                                                    'sin productos sea respetuoso, claro y '
                                                                    'comprensible.',
                                                     'Escenario': 'Consulta sobre cliente sin productos financieros.',
                                                     'Accion': 'Revisar el mensaje emitido por el sistema.',
                                                     'Datos': 'Respuesta con código 206 y mensaje descriptivo.',
                                                     'Resultado Esperado': 'El mensaje informa claramente la ausencia '
                                                                           'de productos sin causar confusión ni '
                                                                           'alarmas técnicas.',
                                                     'Prioridad': 'Low'}]},
 'HU-101-ADP-BDB-consulta-general.md': {'id': 'HU-101-ADP-BDB',
                                        'title': 'Adaptador Banco de Bogotá — Consulta General de Cliente y Productos',
                                        'domain': 'consulta general de cliente y productos en Banco de Bogotá',
                                        'cases': [{'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-BDB] Como analista de pruebas quiero '
                                                              'consultar de forma unificada los datos del cliente y '
                                                              'sus productos en Banco de Bogotá para confirmar la '
                                                              'consolidación completa en una sola respuesta',
                                                   'Descripcion': 'Validar que mediante una única llamada a la '
                                                                  'operación CONSULTA_GENERAL se obtengan consolidados '
                                                                  'los datos personales del cliente y su listado '
                                                                  'completo de productos.',
                                                   'Escenario': 'Cliente con productos activos registrado en Banco de '
                                                                'Bogotá.',
                                                   'Accion': 'Enviar solicitud de consulta general con tipoDocumento '
                                                             "'CC' y numeroDocumento '12345678'.",
                                                   'Datos': "operacion: CONSULTA_GENERAL, tipoDocumento: 'CC', "
                                                            "numeroDocumento: '12345678', X-Destination-Bank: BBOG, "
                                                            'X-Origin-Bank: BBOG, X-Trace-Id: trace-local-001, '
                                                            'X-RqUID: a18eafa0-ce60-11e0-9572-000010867937, X-Channel: '
                                                            'OFICINAS, X-IPAddr: 127.0.0.1, X-Name: ofic-consultas-orq',
                                                   'Resultado Esperado': 'Respuesta exitosa consolidada que contiene '
                                                                         'datos del cliente (nombre, documento, '
                                                                         'segmento) y productos (cuentas, CDT, '
                                                                         'carteras y TC).',
                                                   'Prioridad': 'High'},
                                                  {'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-BDB] Como analista de pruebas quiero '
                                                              'consultar un cliente que no tiene productos registrados '
                                                              'en Banco de Bogotá para confirmar la respuesta '
                                                              'controlada',
                                                   'Descripcion': 'Validar que cuando el cliente existe pero carece de '
                                                                  'productos, se retornen sus datos básicos con la '
                                                                  'notificación de ausencia de productos.',
                                                   'Escenario': 'Cliente registrado en Banco de Bogotá sin productos '
                                                                'financieros asociados.',
                                                   'Accion': 'Enviar solicitud de consulta general para cliente sin '
                                                             'productos.',
                                                   'Datos': "operacion: CONSULTA_GENERAL, tipoDocumento: 'CC', "
                                                            'numeroDocumento de cliente sin productos',
                                                   'Resultado Esperado': 'El sistema retorna código 206 con mensaje '
                                                                         "'El cliente no tiene productos en BdB'.",
                                                   'Prioridad': 'High'},
                                                  {'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-BDB] Como analista de pruebas quiero '
                                                              'consultar un cliente inexistente en Banco de Bogotá '
                                                              'para confirmar el mensaje de cliente no encontrado',
                                                   'Descripcion': 'Validar el comportamiento ante consulta general de '
                                                                  'un documento no registrado en el banco.',
                                                   'Escenario': 'Documento no registrado en los sistemas de Banco de '
                                                                'Bogotá.',
                                                   'Accion': 'Enviar solicitud de consulta general con documento no '
                                                             'existente.',
                                                   'Datos': "operacion: CONSULTA_GENERAL, tipoDocumento: 'CC', "
                                                            "numeroDocumento: '9876543210'",
                                                   'Resultado Esperado': 'El sistema retorna código 206 con StatusDesc '
                                                                         "'Cliente no encontrado en BdB'.",
                                                   'Prioridad': 'High'},
                                                  {'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-BDB] Como analista de pruebas quiero '
                                                              'validar la respuesta parcial cuando un bloque de '
                                                              'información presenta novedad para confirmar que la '
                                                              'información disponible no se pierde',
                                                   'Descripcion': 'Validar que si un bloque de datos llega con error '
                                                                  'pero el otro es exitoso, el adaptador retorna la '
                                                                  'información disponible con el indicador de bloque '
                                                                  'faltante (RO-05).',
                                                   'Escenario': 'Servicio de Banco de Bogotá retorna datos de cliente '
                                                                'pero error parcial en productos.',
                                                   'Accion': 'Ejecutar consulta general en escenario de respuesta '
                                                             'parcial.',
                                                   'Datos': 'operacion: CONSULTA_GENERAL, datos válidos en escenario '
                                                            'de falla parcial del backend',
                                                   'Resultado Esperado': 'El sistema retorna los datos disponibles con '
                                                                         'el indicador de bloque faltante sin generar '
                                                                         'fallo total.',
                                                   'Prioridad': 'High'},
                                                  {'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-BDB] Como analista de pruebas quiero enviar '
                                                              'una solicitud con operación no soportada para confirmar '
                                                              'el rechazo controlado de la petición',
                                                   'Descripcion': 'Validar el control defensivo ante código de '
                                                                  'operación desconocido.',
                                                   'Escenario': 'Petición con operacion no contemplada en el adaptador '
                                                                'de Banco de Bogotá.',
                                                   'Accion': "Enviar solicitud con operacion 'CONSULTA_ERRONEA'.",
                                                   'Datos': "operacion: 'CONSULTA_ERRONEA', X-Destination-Bank: BBOG",
                                                   'Resultado Esperado': 'El adaptador lanza excepción y retorna '
                                                                         'código 400 al orquestador.',
                                                   'Prioridad': 'Medium'},
                                                  {'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-BDB] Como analista de pruebas quiero '
                                                              'consultar omitiendo los headers de identificación '
                                                              'bancaria para confirmar la validación del sistema',
                                                   'Descripcion': 'Validar el rechazo ante la falta de headers '
                                                                  'obligatorios de contexto bancario.',
                                                   'Escenario': 'Solicitud sin headers requeridos como '
                                                                'X-Destination-Bank o X-Origin-Bank.',
                                                   'Accion': 'Enviar solicitud omitiendo header X-Destination-Bank.',
                                                   'Datos': 'operacion: CONSULTA_GENERAL, sin header '
                                                            'X-Destination-Bank',
                                                   'Resultado Esperado': 'El sistema rechaza la solicitud indicando la '
                                                                         'ausencia del contexto requerido.',
                                                   'Prioridad': 'Medium'},
                                                  {'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-BDB] Como analista de pruebas quiero '
                                                              'simular timeout o falla de autenticación con el '
                                                              'servicio REST de Banco de Bogotá para confirmar el '
                                                              'código de error y auditoría',
                                                   'Descripcion': 'Validar el mapeo de timeout (504) o error de '
                                                                  'autenticación (502) y la publicación en la cola de '
                                                                  'auditoría SQS.',
                                                   'Escenario': 'Falla de conectividad, autenticación o timeout en '
                                                                'customer-management-v3 de BdB.',
                                                   'Accion': 'Ejecutar consulta general provocando timeout o fallo de '
                                                             'credenciales hacia el backend.',
                                                   'Datos': 'operacion: CONSULTA_GENERAL, credenciales inválidas o '
                                                            'endpoint con latencia excesiva',
                                                   'Resultado Esperado': 'El adaptador mapea el error a 502 o 504 y '
                                                                         'publica el evento en la cola SQS de '
                                                                         'auditoría.',
                                                   'Prioridad': 'Medium'},
                                                  {'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-BDB] Como analista de pruebas quiero '
                                                              'validar la autenticación biométrica de huella dactilar '
                                                              'exitosa (OK) para confirmar que el sistema autoriza la '
                                                              'consulta general de cliente y productos en Banco de '
                                                              'Bogotá',
                                                   'Descripcion': 'Validar que al presentar una huella biométrica '
                                                                  'válida y coincidente (validación OK), el sistema '
                                                                  'autentique satisfactoriamente la identidad del '
                                                                  'cliente y permita el procesamiento de la consulta '
                                                                  'general de cliente y productos en Banco de Bogotá.',
                                                   'Escenario': 'Cliente presente en canal presencial/oficina con '
                                                                'huella biométrica registrada y coincidente (Match OK) '
                                                                'en el servicio de biometría.',
                                                   'Accion': 'Ejecutar la validación biométrica de huella con '
                                                             'resultado exitoso (OK) previa a la solicitud de la '
                                                             'consulta general de cliente y productos en Banco de '
                                                             'Bogotá.',
                                                   'Datos': 'Identificación de cliente válida, captura de huella '
                                                            'dactilar: match OK (100% coincidencia), contexto de '
                                                            'oficina/asesor.',
                                                   'Resultado Esperado': 'Autenticación biométrica aprobada (OK) y '
                                                                         'ejecución exitosa de la consulta general de '
                                                                         'cliente y productos en Banco de Bogotá '
                                                                         'retornando la información correspondiente.',
                                                   'Prioridad': 'High'},
                                                  {'Tipo de test': 'Funcional',
                                                   'Resumen': '[HU-101-ADP-BDB] Como analista de pruebas quiero '
                                                              'validar el rechazo por huella dactilar no coincidente o '
                                                              'inválida (No OK) para confirmar que el sistema bloquea '
                                                              'la consulta general de cliente y productos en Banco de '
                                                              'Bogotá',
                                                   'Descripcion': 'Validar que ante una huella biométrica no '
                                                                  'coincidente o no reconocida (validación No OK), el '
                                                                  'sistema rechace la autenticación y bloquee el '
                                                                  'procesamiento de la consulta general de cliente y '
                                                                  'productos en Banco de Bogotá.',
                                                   'Escenario': 'Intento de operación con huella biométrica no '
                                                                'coincidente o rechazada (Match No OK) por el servicio '
                                                                'de biometría.',
                                                   'Accion': 'Ejecutar la validación biométrica de huella enviando una '
                                                             'muestra no coincidente (No OK).',
                                                   'Datos': 'Identificación de cliente, captura de huella dactilar: '
                                                            'match No OK (no coincidencia / rechazo biométrico).',
                                                   'Resultado Esperado': 'El sistema deniega el acceso por validación '
                                                                         'biométrica No OK, no procesa la consulta '
                                                                         'general de cliente y productos en Banco de '
                                                                         'Bogotá y retorna el mensaje de autenticación '
                                                                         'fallida.',
                                                   'Prioridad': 'High'},
                                                  {'Tipo de test': 'Accesibilidad',
                                                   'Resumen': '[HU-101-ADP-BDB] Como analista de pruebas quiero '
                                                              'verificar la estructura y jerarquía en la visualización '
                                                              'unificada de cliente y productos',
                                                   'Descripcion': 'Validar que la respuesta consolidada presente una '
                                                                  'separación nítida entre la información personal del '
                                                                  'cliente y sus productos financieros.',
                                                   'Escenario': 'Respuesta consolidada completa generada por el '
                                                                'adaptador.',
                                                   'Accion': 'Verificar la jerarquía de secciones, títulos y orden de '
                                                             'campos en la salida.',
                                                   'Datos': 'Respuesta consolidada de cliente y portafolio de Banco de '
                                                            'Bogotá.',
                                                   'Resultado Esperado': 'La información está jerárquicamente '
                                                                         'estructurada, facilitando la comprensión y '
                                                                         'navegación del asesor.',
                                                   'Prioridad': 'Medium'},
                                                  {'Tipo de test': 'Accesibilidad',
                                                   'Resumen': '[HU-101-ADP-BDB] Como analista de pruebas quiero '
                                                              'verificar que las advertencias de respuestas parciales '
                                                              'sean claras y autoexplicativas',
                                                   'Descripcion': 'Validar que si se produce una respuesta parcial, el '
                                                                  'mensaje indique con precisión qué sección no estuvo '
                                                                  'disponible.',
                                                   'Escenario': 'Respuesta parcial con advertencia de bloque no '
                                                                'disponible.',
                                                   'Accion': 'Revisar la redacción del indicador y mensaje de '
                                                             'información parcial.',
                                                   'Datos': 'Respuesta de consulta general con bloque parcial.',
                                                   'Resultado Esperado': 'El mensaje describe claramente la sección '
                                                                         'afectada sin causar confusión sobre los '
                                                                         'datos sí entregados.',
                                                   'Prioridad': 'Medium'},
                                                  {'Tipo de test': 'Accesibilidad',
                                                   'Resumen': '[HU-101-ADP-BDB] Como analista de pruebas quiero '
                                                              'verificar el formato y rotulado uniforme de números de '
                                                              'cuentas, carteras y saldos monetarios',
                                                   'Descripcion': 'Validar que los datos numéricos y monetarios '
                                                                  'cuenten con presentación legible y estandarizada.',
                                                   'Escenario': 'Productos financieros con saldos en respuesta de '
                                                                'consulta general.',
                                                   'Accion': 'Revisar etiquetas de moneda, números de producto y '
                                                             'saldos disponibles.',
                                                   'Datos': 'Listado de cuentas y créditos en la respuesta '
                                                            'consolidada.',
                                                   'Resultado Esperado': 'Los datos numéricos y financieros son '
                                                                         'inequívocos, legibles y fácilmente '
                                                                         'interpretables.',
                                                   'Prioridad': 'Low'}]},
 'HU-102-ADP-AVV-cartera-detallada.md': {'id': 'HU-102-ADP-AVV',
                                         'title': 'Adaptador AV Villas — Consulta Detallada de Cartera',
                                         'domain': 'consulta detallada de cartera en AV Villas',
                                         'cases': [{'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-AVV] Como analista de pruebas quiero '
                                                               'consultar el detalle de una obligación de cartera '
                                                               'activa para confirmar la obtención de sus saldos y '
                                                               'estado',
                                                    'Descripcion': 'Validar que al enviar número de obligación y '
                                                                   'documento válidos se retorne el detalle completo '
                                                                   'de la cartera en AV Villas.',
                                                    'Escenario': 'Obligación de crédito activa existente en AV Villas.',
                                                    'Accion': 'Enviar solicitud de consulta detallada de cartera con '
                                                              "tipoDocumento 'CC', numeroDocumento '12345678' y "
                                                              "numeroObligacion '26456554'.",
                                                    'Datos': 'operacion: CONSULTA_DETALLADA_CARTERA, tipoDocumento: '
                                                             "'CC', numeroDocumento: '12345678', numeroObligacion: "
                                                             "'26456554', X-Destination-Bank: BAVV, X-Origin-Bank: "
                                                             'BAVV, X-Trace-Id: trace-001, X-RqUID: test-rquid-001, '
                                                             'X-IPAddr: 10.0.0.1, X-ClientDt: 2026-09-08T10:00:00.000, '
                                                             'X-SessKey: test-session-key, X-NextDay: '
                                                             '2026-09-09T10:00:00',
                                                    'Resultado Esperado': 'Respuesta exitosa con información detallada '
                                                                          'de la obligación (saldos, estado, tipo de '
                                                                          'cartera y fechas).',
                                                    'Prioridad': 'High'},
                                                   {'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-AVV] Como analista de pruebas quiero '
                                                               'consultar una obligación que no existe para confirmar '
                                                               'la respuesta de error o no encontrada',
                                                    'Descripcion': 'Validar el comportamiento ante un número de '
                                                                   'obligación inexistente o no perteneciente al '
                                                                   'cliente.',
                                                    'Escenario': 'Número de obligación no registrado en AV Villas.',
                                                    'Accion': "Enviar solicitud con numeroObligacion '9999999999'.",
                                                    'Datos': 'operacion: CONSULTA_DETALLADA_CARTERA, tipoDocumento: '
                                                             "'CC', numeroDocumento: '12345678', numeroObligacion: "
                                                             "'9999999999'",
                                                    'Resultado Esperado': 'El sistema retorna el error estándar '
                                                                          'informando que la obligación no fue '
                                                                          'encontrada.',
                                                    'Prioridad': 'High'},
                                                   {'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-AVV] Como analista de pruebas quiero '
                                                               'solicitar la consulta de cartera omitiendo el número '
                                                               'de obligación para confirmar el rechazo de la '
                                                               'solicitud',
                                                    'Descripcion': 'Validar la obligatoriedad del campo '
                                                                   'numeroObligacion en la consulta detallada de '
                                                                   'cartera.',
                                                    'Escenario': 'Petición sin el campo obligatorio numeroObligacion.',
                                                    'Accion': 'Enviar solicitud con obj_operacion conteniendo '
                                                              'únicamente datos de identificación.',
                                                    'Datos': 'operacion: CONSULTA_DETALLADA_CARTERA, obj_operacion: { '
                                                             "tipoDocumento: 'CC', numeroDocumento: '12345678' }",
                                                    'Resultado Esperado': 'El sistema rechaza la solicitud informando '
                                                                          'la ausencia del identificador de la '
                                                                          'obligación.',
                                                    'Prioridad': 'Medium'},
                                                   {'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-AVV] Como analista de pruebas quiero '
                                                               'intentar la consulta de cartera con una operación no '
                                                               'soportada para confirmar el rechazo 400',
                                                    'Descripcion': 'Validar que códigos de operación no soportados '
                                                                   'sean rechazados defensivamente por el adaptador.',
                                                    'Escenario': 'Solicitud con operacion distinta a '
                                                                 'CONSULTA_DETALLADA_CARTERA.',
                                                    'Accion': 'Enviar solicitud con valor de operacion '
                                                              "'CARTERA_DESCONOCIDA'.",
                                                    'Datos': "operacion: 'CARTERA_DESCONOCIDA', X-Destination-Bank: "
                                                             'BAVV',
                                                    'Resultado Esperado': 'El adaptador lanza excepción y retorna '
                                                                          'código 400 al orquestador.',
                                                    'Prioridad': 'Medium'},
                                                   {'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-AVV] Como analista de pruebas quiero '
                                                               'consultar una obligación con caracteres no numéricos '
                                                               'para confirmar la validación del identificador',
                                                    'Descripcion': 'Validar el comportamiento cuando el número de '
                                                                   'obligación contiene letras o caracteres '
                                                                   'especiales.',
                                                    'Escenario': 'Número de obligación con formato inválido.',
                                                    'Accion': "Enviar solicitud con numeroObligacion 'OBL-ABC-123'.",
                                                    'Datos': 'operacion: CONSULTA_DETALLADA_CARTERA, numeroObligacion: '
                                                             "'OBL-ABC-123'",
                                                    'Resultado Esperado': 'El servicio bancario o adaptador rechaza la '
                                                                          'solicitud por formato no válido.',
                                                    'Prioridad': 'Medium'},
                                                   {'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-AVV] Como analista de pruebas quiero '
                                                               'consultar una obligación en estado especial de mora o '
                                                               'castigada para confirmar el detalle del estado de '
                                                               'deuda',
                                                    'Descripcion': 'Validar que obligaciones con estados especiales '
                                                                   'reporten correctamente sus saldos en mora e '
                                                                   'intereses.',
                                                    'Escenario': 'Obligación de cartera en mora registrada en AV '
                                                                 'Villas.',
                                                    'Accion': 'Enviar solicitud de consulta detallada sobre obligación '
                                                              'con mora.',
                                                    'Datos': 'operacion: CONSULTA_DETALLADA_CARTERA, numeroObligacion '
                                                             'de crédito en mora',
                                                    'Resultado Esperado': 'La respuesta refleja fielmente los días de '
                                                                          'mora, saldo vencido y estado de la '
                                                                          'obligación.',
                                                    'Prioridad': 'Low'},
                                                   {'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-AVV] Como analista de pruebas quiero '
                                                               'simular un error SOAP fault o timeout en el backend de '
                                                               'AV Villas para confirmar la propagación del error y '
                                                               'auditoría',
                                                    'Descripcion': 'Validar el manejo de fallos SOAP y la activación '
                                                                   'de Circuit Breaker ante contingencias en AV '
                                                                   'Villas.',
                                                    'Escenario': 'Servicio SOAP de saldos por producto de AV Villas '
                                                                 'generando fault o timeout.',
                                                    'Accion': 'Ejecutar consulta de cartera mientras el servicio SOAP '
                                                              'genera una excepción.',
                                                    'Datos': 'operacion: CONSULTA_DETALLADA_CARTERA, datos válidos '
                                                             'bajo falla de backend',
                                                    'Resultado Esperado': 'El sistema mapea el error a código 502/504, '
                                                                          'registra en auditoría SQS y activa Circuit '
                                                                          'Breaker.',
                                                    'Prioridad': 'Medium'},
                                                   {'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-AVV] Como analista de pruebas quiero '
                                                               'validar la autenticación biométrica de huella dactilar '
                                                               'exitosa (OK) para confirmar que el sistema autoriza la '
                                                               'consulta detallada de cartera en AV Villas',
                                                    'Descripcion': 'Validar que al presentar una huella biométrica '
                                                                   'válida y coincidente (validación OK), el sistema '
                                                                   'autentique satisfactoriamente la identidad del '
                                                                   'cliente y permita el procesamiento de la consulta '
                                                                   'detallada de cartera en AV Villas.',
                                                    'Escenario': 'Cliente presente en canal presencial/oficina con '
                                                                 'huella biométrica registrada y coincidente (Match '
                                                                 'OK) en el servicio de biometría.',
                                                    'Accion': 'Ejecutar la validación biométrica de huella con '
                                                              'resultado exitoso (OK) previa a la solicitud de la '
                                                              'consulta detallada de cartera en AV Villas.',
                                                    'Datos': 'Identificación de cliente válida, captura de huella '
                                                             'dactilar: match OK (100% coincidencia), contexto de '
                                                             'oficina/asesor.',
                                                    'Resultado Esperado': 'Autenticación biométrica aprobada (OK) y '
                                                                          'ejecución exitosa de la consulta detallada '
                                                                          'de cartera en AV Villas retornando la '
                                                                          'información correspondiente.',
                                                    'Prioridad': 'High'},
                                                   {'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-AVV] Como analista de pruebas quiero '
                                                               'validar el rechazo por huella dactilar no coincidente '
                                                               'o inválida (No OK) para confirmar que el sistema '
                                                               'bloquea la consulta detallada de cartera en AV Villas',
                                                    'Descripcion': 'Validar que ante una huella biométrica no '
                                                                   'coincidente o no reconocida (validación No OK), el '
                                                                   'sistema rechace la autenticación y bloquee el '
                                                                   'procesamiento de la consulta detallada de cartera '
                                                                   'en AV Villas.',
                                                    'Escenario': 'Intento de operación con huella biométrica no '
                                                                 'coincidente o rechazada (Match No OK) por el '
                                                                 'servicio de biometría.',
                                                    'Accion': 'Ejecutar la validación biométrica de huella enviando '
                                                              'una muestra no coincidente (No OK).',
                                                    'Datos': 'Identificación de cliente, captura de huella dactilar: '
                                                             'match No OK (no coincidencia / rechazo biométrico).',
                                                    'Resultado Esperado': 'El sistema deniega el acceso por validación '
                                                                          'biométrica No OK, no procesa la consulta '
                                                                          'detallada de cartera en AV Villas y retorna '
                                                                          'el mensaje de autenticación fallida.',
                                                    'Prioridad': 'High'},
                                                   {'Tipo de test': 'Accesibilidad',
                                                    'Resumen': '[HU-102-ADP-AVV] Como analista de pruebas quiero '
                                                               'verificar que el desglose de saldos de capital, '
                                                               'intereses y mora sea claro e intuitivo',
                                                    'Descripcion': 'Validar que los diferentes conceptos de la deuda '
                                                                   'estén claramente diferenciados y rotulados para '
                                                                   'evitar malentendidos.',
                                                    'Escenario': 'Respuesta detallada de cartera procesada por el '
                                                                 'sistema.',
                                                    'Accion': 'Revisar los nombres de campos, valores y agrupaciones '
                                                              'de la deuda.',
                                                    'Datos': 'Detalle de saldos de cartera con intereses y capital.',
                                                    'Resultado Esperado': 'Los conceptos de capital, intereses '
                                                                          'corrientes e intereses de mora están '
                                                                          'nítidamente identificados.',
                                                    'Prioridad': 'Medium'},
                                                   {'Tipo de test': 'Accesibilidad',
                                                    'Resumen': '[HU-102-ADP-AVV] Como analista de pruebas quiero '
                                                               'verificar que las fechas de vencimiento y próximo pago '
                                                               'tengan un formato comprensible y estándar',
                                                    'Descripcion': 'Validar la legibilidad y coherencia de las fechas '
                                                                   'asociadas al plan de pagos de la obligación.',
                                                    'Escenario': 'Fechas de pago y vencimiento en la respuesta de '
                                                                 'cartera.',
                                                    'Accion': 'Verificar el formato de visualización de fechas.',
                                                    'Datos': 'Fechas de corte, vencimiento y próximo pago.',
                                                    'Resultado Esperado': 'Las fechas siguen un formato estándar y '
                                                                          'legible para los usuarios y sistemas '
                                                                          'asistivos.',
                                                    'Prioridad': 'Medium'},
                                                   {'Tipo de test': 'Accesibilidad',
                                                    'Resumen': '[HU-102-ADP-AVV] Como analista de pruebas quiero '
                                                               'verificar la claridad de los mensajes de error cuando '
                                                               'la obligación no existe',
                                                    'Descripcion': 'Validar que el mensaje de obligación no encontrada '
                                                                   'proporcione información clara al usuario.',
                                                    'Escenario': 'Consulta fallida por obligación no encontrada.',
                                                    'Accion': 'Revisar la descripción del error recibido.',
                                                    'Datos': 'Mensaje de error retornado.',
                                                    'Resultado Esperado': 'El mensaje indica con claridad que la '
                                                                          'obligación consultada no fue localizada.',
                                                    'Prioridad': 'Low'}]},
 'HU-102-ADP-BDB-cartera-detallada.md': {'id': 'HU-102-ADP-BDB',
                                         'title': 'Adaptador Banco de Bogotá — Consulta Detallada de Cartera',
                                         'domain': 'consulta detallada de cartera en Banco de Bogotá',
                                         'cases': [{'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-BDB] Como analista de pruebas quiero '
                                                               'consultar el detalle de un crédito activo en Banco de '
                                                               'Bogotá para confirmar la recepción directa de saldos, '
                                                               'cuota mínima y fechas',
                                                    'Descripcion': 'Validar la consulta de detalle de cartera '
                                                                   'invocando retrieveLoanBalance en '
                                                                   'balances-management-v2 con obligación válida.',
                                                    'Escenario': 'Obligación de cartera activa en Banco de Bogotá.',
                                                    'Accion': 'Enviar solicitud de consulta detallada de cartera con '
                                                              "tipoDocumento 'CC', numeroDocumento '12345678' y "
                                                              "numeroObligacion '559536650'.",
                                                    'Datos': 'operacion: CONSULTA_DETALLADA_CARTERA, tipoDocumento: '
                                                             "'CC', numeroDocumento: '12345678', numeroObligacion: "
                                                             "'559536650', X-Destination-Bank: BBOG, X-Origin-Bank: "
                                                             'BBOG, X-Trace-Id: trace-001, X-RqUID: test-rquid-001, '
                                                             'X-IPAddr: 10.0.0.1, X-Channel: OFI, X-Name: '
                                                             'ofic-consultas-adp-bbog, X-TerminalId: TERM001, '
                                                             'X-Journey: CONSULTA, x-api-key: TU_API_KEY',
                                                    'Resultado Esperado': 'Respuesta 200 OK con saldos disponibles y '
                                                                          'corrientes, saldo de pagos anteriores, '
                                                                          'cuota mínima, plazo, tasa y fecha de '
                                                                          'vencimiento.',
                                                    'Prioridad': 'High'},
                                                   {'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-BDB] Como analista de pruebas quiero '
                                                               'consultar una obligación inexistente en Banco de '
                                                               'Bogotá para confirmar la propagación del código 404',
                                                    'Descripcion': 'Validar que ante una obligación no encontrada, el '
                                                                   'adaptador propague el código 404 al orquestador.',
                                                    'Escenario': 'Obligación no registrada en Banco de Bogotá.',
                                                    'Accion': 'Enviar solicitud con numeroObligacion inexistente.',
                                                    'Datos': 'operacion: CONSULTA_DETALLADA_CARTERA, numeroObligacion: '
                                                             "'000000000'",
                                                    'Resultado Esperado': 'El adaptador propaga el código 404 '
                                                                          'indicando obligación no encontrada.',
                                                    'Prioridad': 'High'},
                                                   {'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-BDB] Como analista de pruebas quiero '
                                                               'simular un error de negocio en la consulta de cartera '
                                                               'para confirmar su mapeo al código 422',
                                                    'Descripcion': 'Validar que si Banco de Bogotá retorna un 409 '
                                                                   'Business Error, el adaptador lo mapee al código '
                                                                   '422.',
                                                    'Escenario': 'Obligación en condición de error de negocio en '
                                                                 'backend de BdB.',
                                                    'Accion': 'Ejecutar consulta sobre obligación que genera error de '
                                                              'negocio en el banco.',
                                                    'Datos': 'operacion: CONSULTA_DETALLADA_CARTERA, numeroObligacion '
                                                             'con condición de negocio especial',
                                                    'Resultado Esperado': 'El adaptador mapea el error de negocio a '
                                                                          'código 422 hacia el orquestador.',
                                                    'Prioridad': 'High'},
                                                   {'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-BDB] Como analista de pruebas quiero '
                                                               'solicitar la consulta de cartera con una operación no '
                                                               'soportada para confirmar el rechazo 400',
                                                    'Descripcion': 'Validar que el adaptador rechace operaciones no '
                                                                   'soportadas mediante excepción y código 400.',
                                                    'Escenario': 'Solicitud con operacion distinta a '
                                                                 'CONSULTA_DETALLADA_CARTERA.',
                                                    'Accion': "Enviar solicitud con operacion 'OPERACION_NO_VALIDA'.",
                                                    'Datos': "operacion: 'OPERACION_NO_VALIDA', X-Destination-Bank: "
                                                             'BBOG',
                                                    'Resultado Esperado': 'El adaptador retorna código 400 por '
                                                                          'operación no soportada.',
                                                    'Prioridad': 'Medium'},
                                                   {'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-BDB] Como analista de pruebas quiero '
                                                               'consultar omitiendo el número de obligación para '
                                                               'confirmar la validación del dato requerido',
                                                    'Descripcion': 'Validar el comportamiento ante omisión de '
                                                                   'numeroObligacion en el payload.',
                                                    'Escenario': 'Solicitud de cartera sin numeroObligacion.',
                                                    'Accion': 'Enviar solicitud omitiendo numeroObligacion.',
                                                    'Datos': 'operacion: CONSULTA_DETALLADA_CARTERA, obj_operacion: { '
                                                             "tipoDocumento: 'CC', numeroDocumento: '12345678' }",
                                                    'Resultado Esperado': 'El sistema rechaza la petición por ausencia '
                                                                          'de identificador de obligación.',
                                                    'Prioridad': 'Medium'},
                                                   {'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-BDB] Como analista de pruebas quiero '
                                                               'consultar un crédito cancelado para confirmar que se '
                                                               'entrega el estado final y saldo en cero',
                                                    'Descripcion': 'Validar el comportamiento y detalle de saldos en '
                                                                   'obligaciones finalizadas o canceladas.',
                                                    'Escenario': 'Crédito cancelado registrado en Banco de Bogotá.',
                                                    'Accion': 'Enviar consulta detallada para crédito cancelado.',
                                                    'Datos': 'operacion: CONSULTA_DETALLADA_CARTERA, numeroObligacion '
                                                             'de crédito cancelado',
                                                    'Resultado Esperado': 'La respuesta refleja el estado cancelado '
                                                                          'con saldos pendientes en cero.',
                                                    'Prioridad': 'Low'},
                                                   {'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-BDB] Como analista de pruebas quiero '
                                                               'simular un timeout (SocketTimeoutException) en el '
                                                               'servicio de balances de BdB para confirmar el retorno '
                                                               'de 504',
                                                    'Descripcion': 'Validar que la ocurrencia de '
                                                                   'SocketTimeoutException sea mapeada a 504 antes de '
                                                                   'cualquier captura genérica.',
                                                    'Escenario': 'Servicio balances-management-v2 no responde dentro '
                                                                 'del tiempo límite.',
                                                    'Accion': 'Ejecutar consulta detallada con retraso en el servicio '
                                                              'backend.',
                                                    'Datos': 'operacion: CONSULTA_DETALLADA_CARTERA, datos válidos '
                                                             'bajo latencia excesiva',
                                                    'Resultado Esperado': 'El adaptador retorna código 504 al '
                                                                          'orquestador y registra en Elastic y SQS.',
                                                    'Prioridad': 'Medium'},
                                                   {'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-BDB] Como analista de pruebas quiero '
                                                               'validar la autenticación biométrica de huella dactilar '
                                                               'exitosa (OK) para confirmar que el sistema autoriza la '
                                                               'consulta detallada de cartera en Banco de Bogotá',
                                                    'Descripcion': 'Validar que al presentar una huella biométrica '
                                                                   'válida y coincidente (validación OK), el sistema '
                                                                   'autentique satisfactoriamente la identidad del '
                                                                   'cliente y permita el procesamiento de la consulta '
                                                                   'detallada de cartera en Banco de Bogotá.',
                                                    'Escenario': 'Cliente presente en canal presencial/oficina con '
                                                                 'huella biométrica registrada y coincidente (Match '
                                                                 'OK) en el servicio de biometría.',
                                                    'Accion': 'Ejecutar la validación biométrica de huella con '
                                                              'resultado exitoso (OK) previa a la solicitud de la '
                                                              'consulta detallada de cartera en Banco de Bogotá.',
                                                    'Datos': 'Identificación de cliente válida, captura de huella '
                                                             'dactilar: match OK (100% coincidencia), contexto de '
                                                             'oficina/asesor.',
                                                    'Resultado Esperado': 'Autenticación biométrica aprobada (OK) y '
                                                                          'ejecución exitosa de la consulta detallada '
                                                                          'de cartera en Banco de Bogotá retornando la '
                                                                          'información correspondiente.',
                                                    'Prioridad': 'High'},
                                                   {'Tipo de test': 'Funcional',
                                                    'Resumen': '[HU-102-ADP-BDB] Como analista de pruebas quiero '
                                                               'validar el rechazo por huella dactilar no coincidente '
                                                               'o inválida (No OK) para confirmar que el sistema '
                                                               'bloquea la consulta detallada de cartera en Banco de '
                                                               'Bogotá',
                                                    'Descripcion': 'Validar que ante una huella biométrica no '
                                                                   'coincidente o no reconocida (validación No OK), el '
                                                                   'sistema rechace la autenticación y bloquee el '
                                                                   'procesamiento de la consulta detallada de cartera '
                                                                   'en Banco de Bogotá.',
                                                    'Escenario': 'Intento de operación con huella biométrica no '
                                                                 'coincidente o rechazada (Match No OK) por el '
                                                                 'servicio de biometría.',
                                                    'Accion': 'Ejecutar la validación biométrica de huella enviando '
                                                              'una muestra no coincidente (No OK).',
                                                    'Datos': 'Identificación de cliente, captura de huella dactilar: '
                                                             'match No OK (no coincidencia / rechazo biométrico).',
                                                    'Resultado Esperado': 'El sistema deniega el acceso por validación '
                                                                          'biométrica No OK, no procesa la consulta '
                                                                          'detallada de cartera en Banco de Bogotá y '
                                                                          'retorna el mensaje de autenticación '
                                                                          'fallida.',
                                                    'Prioridad': 'High'},
                                                   {'Tipo de test': 'Accesibilidad',
                                                    'Resumen': '[HU-102-ADP-BDB] Como analista de pruebas quiero '
                                                               'verificar la claridad en el rotulado de montos de '
                                                               'cuota mínima, saldos corrientes y plazos',
                                                    'Descripcion': 'Validar que la respuesta de saldo de crédito '
                                                                   'presente un desglose numérico comprensible y '
                                                                   'legible.',
                                                    'Escenario': 'Respuesta de crédito con múltiples conceptos de '
                                                                 'saldo y plazos.',
                                                    'Accion': 'Inspeccionar las etiquetas de cuota mínima, saldos y '
                                                              'plazos.',
                                                    'Datos': 'Campos de saldos y plazos en la respuesta del banco.',
                                                    'Resultado Esperado': 'Los campos permiten distinguir con total '
                                                                          'claridad el valor a pagar de la deuda total '
                                                                          'y los plazos restantes.',
                                                    'Prioridad': 'Medium'},
                                                   {'Tipo de test': 'Accesibilidad',
                                                    'Resumen': '[HU-102-ADP-BDB] Como analista de pruebas quiero '
                                                               'verificar que las descripciones de estados de cuenta y '
                                                               'tasas de interés sean transparentes',
                                                    'Descripcion': 'Validar que las tasas de interés y estados de la '
                                                                   'cuenta no presenten códigos numéricos oscuros.',
                                                    'Escenario': 'Detalle de crédito con tasas y estados vigentes.',
                                                    'Accion': 'Revisar los textos de estado y porcentajes de tasa.',
                                                    'Datos': 'Campos de estado y tasa en la respuesta.',
                                                    'Resultado Esperado': 'La información es autoexplicativa y '
                                                                          'fácilmente interpretable por cualquier '
                                                                          'usuario.',
                                                    'Prioridad': 'Medium'},
                                                   {'Tipo de test': 'Accesibilidad',
                                                    'Resumen': '[HU-102-ADP-BDB] Como analista de pruebas quiero '
                                                               'verificar la legibilidad y mensaje accionable ante '
                                                               'errores 404 o 422 en cartera',
                                                    'Descripcion': 'Validar que los mensajes de error en consulta de '
                                                                   'cartera orienten al usuario sobre la causa del '
                                                                   'rechazo.',
                                                    'Escenario': 'Respuestas con error 404 o 422.',
                                                    'Accion': 'Verificar la redacción de los mensajes de error.',
                                                    'Datos': 'Mensajes descriptivos de error del servicio.',
                                                    'Resultado Esperado': 'Los mensajes explican claramente si el '
                                                                          'crédito no existe o si presenta una '
                                                                          'condición particular de negocio.',
                                                    'Prioridad': 'Low'}]},
 'HU-103-ADP-AVV-tc-detallada.md': {'id': 'HU-103-ADP-AVV',
                                    'title': 'Adaptador AV Villas — Consulta Detallada de Tarjeta de Crédito',
                                    'domain': 'consulta detallada de tarjeta de crédito en AV Villas',
                                    'cases': [{'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-AVV] Como analista de pruebas quiero consultar '
                                                          'el detalle de una tarjeta de crédito activa para confirmar '
                                                          'la obtención de cupos, saldos y estado',
                                               'Descripcion': 'Validar la consulta detallada de TC en AV Villas '
                                                              'invocando getBalanceByProduct con AcctType=CCA.',
                                               'Escenario': 'Tarjeta de crédito activa existente en AV Villas.',
                                               'Accion': "Enviar solicitud de consulta de TC con tipoDocumento 'CC', "
                                                         "numeroDocumento '12345678' y referenciaTarjeta "
                                                         "'4111111111111111'.",
                                               'Datos': "operacion: CONSULTA_DETALLADA_TC, tipoDocumento: 'CC', "
                                                        "numeroDocumento: '12345678', referenciaTarjeta: "
                                                        "'4111111111111111', X-Destination-Bank: BAVV, X-Trace-Id: "
                                                        'trace-tc-adp-avv-001, X-RqUID: '
                                                        'a1b2c3d4-0001-0000-0000-000000000002, X-IPAddr: 10.0.0.1, '
                                                        'X-ClientDt: 2026-09-09T10:00:00.000, X-SessKey: '
                                                        'session-key-001, X-NextDay: 2026-09-10T00:00:00',
                                               'Resultado Esperado': 'Respuesta con detalle de tarjeta: referencia '
                                                                     'enmascarada, franquicia, estado, cupo aprobado, '
                                                                     'cupo disponible, saldo total y saldo diferido.',
                                               'Prioridad': 'High'},
                                              {'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-AVV] Como analista de pruebas quiero consultar '
                                                          'una tarjeta de crédito inexistente para confirmar el '
                                                          'retorno de error 404',
                                               'Descripcion': 'Validar el comportamiento ante consulta de una tarjeta '
                                                              'no registrada en AV Villas.',
                                               'Escenario': 'Referencia de tarjeta no existente en el banco.',
                                               'Accion': 'Enviar solicitud con referenciaTarjeta no registrada.',
                                               'Datos': 'operacion: CONSULTA_DETALLADA_TC, referenciaTarjeta: '
                                                        "'4999999999999999'",
                                               'Resultado Esperado': 'El sistema mapea el error a código 404 '
                                                                     'informando tarjeta no encontrada.',
                                               'Prioridad': 'High'},
                                              {'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-AVV] Como analista de pruebas quiero solicitar '
                                                          'la consulta de TC omitiendo la referencia de tarjeta para '
                                                          'confirmar el rechazo de la solicitud',
                                               'Descripcion': 'Validar la obligatoriedad del dato de referencia de '
                                                              'tarjeta.',
                                               'Escenario': 'Solicitud sin el campo referenciaTarjeta.',
                                               'Accion': 'Enviar solicitud omitiendo referenciaTarjeta.',
                                               'Datos': 'operacion: CONSULTA_DETALLADA_TC, obj_operacion: { '
                                                        "tipoDocumento: 'CC', numeroDocumento: '12345678' }",
                                               'Resultado Esperado': 'El sistema rechaza la petición indicando campo '
                                                                     'obligatorio ausente.',
                                               'Prioridad': 'Medium'},
                                              {'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-AVV] Como analista de pruebas quiero consultar '
                                                          'una tarjeta con operación no soportada para confirmar el '
                                                          'rechazo defensivo 400',
                                               'Descripcion': 'Validar que códigos de operación ajenos a '
                                                              'CONSULTA_DETALLADA_TC sean rechazados.',
                                               'Escenario': 'Solicitud con código de operación inválido.',
                                               'Accion': "Enviar solicitud con operacion 'TC_INVALIDA'.",
                                               'Datos': "operacion: 'TC_INVALIDA', X-Destination-Bank: BAVV",
                                               'Resultado Esperado': 'El adaptador lanza excepción y retorna 400 al '
                                                                     'orquestador.',
                                               'Prioridad': 'Medium'},
                                              {'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-AVV] Como analista de pruebas quiero consultar '
                                                          'una tarjeta con referencia en formato o longitud incorrecta '
                                                          'para confirmar la validación',
                                               'Descripcion': 'Validar el comportamiento ante números de tarjeta con '
                                                              'longitud fuera de norma o caracteres no permitidos.',
                                               'Escenario': 'Referencia de tarjeta con longitud errónea.',
                                               'Accion': 'Enviar solicitud con referenciaTarjeta de 6 dígitos.',
                                               'Datos': "operacion: CONSULTA_DETALLADA_TC, referenciaTarjeta: '123456'",
                                               'Resultado Esperado': 'El sistema rechaza la solicitud por formato no '
                                                                     'válido.',
                                               'Prioridad': 'Medium'},
                                              {'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-AVV] Como analista de pruebas quiero consultar '
                                                          'una tarjeta bloqueada o cancelada para confirmar la '
                                                          'correcta entrega de su estado y saldos',
                                               'Descripcion': 'Validar que tarjetas en estado inactivo o bloqueado '
                                                              'reflejen fielmente su condición.',
                                               'Escenario': 'Tarjeta de crédito bloqueada registrada en AV Villas.',
                                               'Accion': 'Enviar solicitud de consulta para tarjeta bloqueada.',
                                               'Datos': 'operacion: CONSULTA_DETALLADA_TC, referenciaTarjeta de '
                                                        'tarjeta bloqueada',
                                               'Resultado Esperado': 'La respuesta refleja el estado BLOQUEADA y '
                                                                     'entrega los saldos pendientes sin error.',
                                               'Prioridad': 'Low'},
                                              {'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-AVV] Como analista de pruebas quiero simular un '
                                                          'error técnico en el servicio SOAP de TC para confirmar el '
                                                          'manejo de error y Circuit Breaker',
                                               'Descripcion': 'Validar la respuesta 502/504 y registro en auditoría '
                                                              'SQS ante falla del backend bancario de tarjetas.',
                                               'Escenario': 'Servicio SOAP de tarjetas de AV Villas con error interno.',
                                               'Accion': 'Ejecutar consulta de TC bajo simulación de error en el '
                                                         'backend.',
                                               'Datos': 'operacion: CONSULTA_DETALLADA_TC, datos válidos en backend '
                                                        'con error',
                                               'Resultado Esperado': 'El sistema responde con código 502/504 y '
                                                                     'registra en la cola de auditoría SQS.',
                                               'Prioridad': 'Medium'},
                                              {'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-AVV] Como analista de pruebas quiero validar la '
                                                          'autenticación biométrica de huella dactilar exitosa (OK) '
                                                          'para confirmar que el sistema autoriza la consulta '
                                                          'detallada de tarjeta de crédito en AV Villas',
                                               'Descripcion': 'Validar que al presentar una huella biométrica válida y '
                                                              'coincidente (validación OK), el sistema autentique '
                                                              'satisfactoriamente la identidad del cliente y permita '
                                                              'el procesamiento de la consulta detallada de tarjeta de '
                                                              'crédito en AV Villas.',
                                               'Escenario': 'Cliente presente en canal presencial/oficina con huella '
                                                            'biométrica registrada y coincidente (Match OK) en el '
                                                            'servicio de biometría.',
                                               'Accion': 'Ejecutar la validación biométrica de huella con resultado '
                                                         'exitoso (OK) previa a la solicitud de la consulta detallada '
                                                         'de tarjeta de crédito en AV Villas.',
                                               'Datos': 'Identificación de cliente válida, captura de huella dactilar: '
                                                        'match OK (100% coincidencia), contexto de oficina/asesor.',
                                               'Resultado Esperado': 'Autenticación biométrica aprobada (OK) y '
                                                                     'ejecución exitosa de la consulta detallada de '
                                                                     'tarjeta de crédito en AV Villas retornando la '
                                                                     'información correspondiente.',
                                               'Prioridad': 'High'},
                                              {'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-AVV] Como analista de pruebas quiero validar el '
                                                          'rechazo por huella dactilar no coincidente o inválida (No '
                                                          'OK) para confirmar que el sistema bloquea la consulta '
                                                          'detallada de tarjeta de crédito en AV Villas',
                                               'Descripcion': 'Validar que ante una huella biométrica no coincidente o '
                                                              'no reconocida (validación No OK), el sistema rechace la '
                                                              'autenticación y bloquee el procesamiento de la consulta '
                                                              'detallada de tarjeta de crédito en AV Villas.',
                                               'Escenario': 'Intento de operación con huella biométrica no coincidente '
                                                            'o rechazada (Match No OK) por el servicio de biometría.',
                                               'Accion': 'Ejecutar la validación biométrica de huella enviando una '
                                                         'muestra no coincidente (No OK).',
                                               'Datos': 'Identificación de cliente, captura de huella dactilar: match '
                                                        'No OK (no coincidencia / rechazo biométrico).',
                                               'Resultado Esperado': 'El sistema deniega el acceso por validación '
                                                                     'biométrica No OK, no procesa la consulta '
                                                                     'detallada de tarjeta de crédito en AV Villas y '
                                                                     'retorna el mensaje de autenticación fallida.',
                                               'Prioridad': 'High'},
                                              {'Tipo de test': 'Accesibilidad',
                                               'Resumen': '[HU-103-ADP-AVV] Como analista de pruebas quiero verificar '
                                                          'la visualización clara y diferenciada de cupo aprobado, '
                                                          'disponible y saldo adeudado',
                                               'Descripcion': 'Validar que los diferentes cupos y saldos de la tarjeta '
                                                              'de crédito se presenten de forma intuitiva.',
                                               'Escenario': 'Respuesta de tarjeta con cupos y saldos detallados.',
                                               'Accion': 'Revisar los rótulos y montos monetarios en la salida.',
                                               'Datos': 'Cupo aprobado, cupo disponible, saldo diferido y total.',
                                               'Resultado Esperado': 'Cada concepto monetario está etiquetado con '
                                                                     'precisión sin posibilidad de confusión sobre los '
                                                                     'fondos disponibles.',
                                               'Prioridad': 'Medium'},
                                              {'Tipo de test': 'Accesibilidad',
                                               'Resumen': '[HU-103-ADP-AVV] Como analista de pruebas quiero verificar '
                                                          'el formato claro y comprensible de franquicia y estado de '
                                                          'la tarjeta',
                                               'Descripcion': 'Validar que franquicias (VISA, MASTERCARD) y estados '
                                                              '(ACTIVA, BLOQUEADA) se expongan en lenguaje natural.',
                                               'Escenario': 'Campos de franquicia y estado en la respuesta de TC.',
                                               'Accion': 'Verificar la legibilidad de franquicia y estado.',
                                               'Datos': 'Valores de franquicia y estado en el JSON de respuesta.',
                                               'Resultado Esperado': 'Los valores son comprensibles y no presentan '
                                                                     'códigos numéricos opacos.',
                                               'Prioridad': 'Medium'},
                                              {'Tipo de test': 'Accesibilidad',
                                               'Resumen': '[HU-103-ADP-AVV] Como analista de pruebas quiero verificar '
                                                          'la claridad del mensaje ante tarjeta no encontrada',
                                               'Descripcion': 'Validar que el mensaje de tarjeta no encontrada oriente '
                                                              'adecuadamente al usuario.',
                                               'Escenario': 'Error 404 por tarjeta inexistente.',
                                               'Accion': 'Revisar el mensaje descriptivo del error.',
                                               'Datos': 'Mensaje de respuesta ante tarjeta inexistente.',
                                               'Resultado Esperado': 'El mensaje indica con claridad que la tarjeta '
                                                                     'consultada no fue localizada.',
                                               'Prioridad': 'Low'}]},
 'HU-103-ADP-BDB-tc-detallada.md': {'id': 'HU-103-ADP-BDB',
                                    'title': 'Adaptador Banco de Bogotá — Consulta Detallada de Tarjeta de Crédito',
                                    'domain': 'consulta detallada de tarjeta de crédito en Banco de Bogotá',
                                    'cases': [{'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-BDB] Como analista de pruebas quiero consultar '
                                                          'el detalle de una tarjeta de crédito activa en Banco de '
                                                          'Bogotá para confirmar la recepción de cupos, saldos y '
                                                          'cuotas diferidas',
                                               'Descripcion': 'Validar la consulta de retrieveCreditCardBalance en '
                                                              'balances-management-v2 con tarjeta válida.',
                                               'Escenario': 'Tarjeta de crédito activa existente en Banco de Bogotá.',
                                               'Accion': "Enviar solicitud de consulta de TC con tipoDocumento 'CC', "
                                                         "numeroDocumento '12345678' y referenciaTarjeta "
                                                         "'4111111111111111'.",
                                               'Datos': "operacion: CONSULTA_DETALLADA_TC, tipoDocumento: 'CC', "
                                                        "numeroDocumento: '12345678', referenciaTarjeta: "
                                                        "'4111111111111111', X-Destination-Bank: BBOG, X-Trace-Id: "
                                                        'trace-tc-adp-bbog-001, X-RqUID: '
                                                        'a1b2c3d4-0001-0000-0000-000000000001, X-CompanyId: 0001234, '
                                                        'X-IPAddr: 10.0.0.1, X-TerminalId: TERM-001, X-NetworkOwner: '
                                                        'AVAL, X-Journey: OFICINAS',
                                               'Resultado Esperado': 'Respuesta 200 OK con referencia enmascarada, '
                                                                     'franquicia, estado, cupo aprobado, disponible, '
                                                                     'saldo total, diferido y cuotas diferidas.',
                                               'Prioridad': 'High'},
                                              {'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-BDB] Como analista de pruebas quiero consultar '
                                                          'una tarjeta de crédito no registrada en Banco de Bogotá '
                                                          'para confirmar el retorno de código 404',
                                               'Descripcion': 'Validar que si la tarjeta no existe en Banco de Bogotá, '
                                                              'el adaptador mapee y propague el código 404.',
                                               'Escenario': 'Tarjeta no existente en Banco de Bogotá.',
                                               'Accion': 'Enviar solicitud con referenciaTarjeta inexistente.',
                                               'Datos': 'operacion: CONSULTA_DETALLADA_TC, referenciaTarjeta: '
                                                        "'4000000000000000'",
                                               'Resultado Esperado': 'El sistema retorna código 404 informando que la '
                                                                     'tarjeta no fue encontrada.',
                                               'Prioridad': 'High'},
                                              {'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-BDB] Como analista de pruebas quiero consultar '
                                                          'omitiendo la referencia de la tarjeta de crédito para '
                                                          'confirmar el rechazo de la solicitud',
                                               'Descripcion': 'Validar la obligatoriedad del parámetro de tarjeta.',
                                               'Escenario': 'Solicitud sin el campo referenciaTarjeta.',
                                               'Accion': 'Enviar solicitud omitiendo referenciaTarjeta.',
                                               'Datos': 'operacion: CONSULTA_DETALLADA_TC, obj_operacion: { '
                                                        "tipoDocumento: 'CC', numeroDocumento: '12345678' }",
                                               'Resultado Esperado': 'El sistema rechaza la solicitud indicando la '
                                                                     'ausencia del identificador de tarjeta.',
                                               'Prioridad': 'Medium'},
                                              {'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-BDB] Como analista de pruebas quiero enviar una '
                                                          'solicitud de TC con operación no soportada para confirmar '
                                                          'el rechazo con código 400',
                                               'Descripcion': 'Validar el control defensivo ante código de operación '
                                                              'desconocido.',
                                               'Escenario': 'Solicitud con operacion distinta a CONSULTA_DETALLADA_TC.',
                                               'Accion': "Enviar solicitud con operacion 'OP_TC_ERRONEA'.",
                                               'Datos': "operacion: 'OP_TC_ERRONEA', X-Destination-Bank: BBOG",
                                               'Resultado Esperado': 'El adaptador lanza excepción y responde código '
                                                                     '400 al orquestador.',
                                               'Prioridad': 'Medium'},
                                              {'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-BDB] Como analista de pruebas quiero consultar '
                                                          'una tarjeta con compras diferidas a múltiples cuotas para '
                                                          'confirmar la entrega del número de cuotas activas',
                                               'Descripcion': 'Validar que el campo cuotasDiferidas y saldoDiferido '
                                                              'reporten fielmente la información de diferidos.',
                                               'Escenario': 'Tarjeta con compras diferidas vigentes.',
                                               'Accion': 'Consultar tarjeta de crédito con compras a cuotas.',
                                               'Datos': 'operacion: CONSULTA_DETALLADA_TC, referencia de tarjeta con '
                                                        'diferidos',
                                               'Resultado Esperado': 'La respuesta entrega el total de cuotas '
                                                                     'diferidas y el saldo diferido correspondiente.',
                                               'Prioridad': 'Medium'},
                                              {'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-BDB] Como analista de pruebas quiero consultar '
                                                          'una tarjeta cancelada para confirmar la entrega de estado '
                                                          'CANCELADA y saldos en cero',
                                               'Descripcion': 'Validar la respuesta ante tarjetas canceladas en Banco '
                                                              'de Bogotá.',
                                               'Escenario': 'Tarjeta en estado CANCELADA.',
                                               'Accion': 'Enviar solicitud para tarjeta cancelada.',
                                               'Datos': 'operacion: CONSULTA_DETALLADA_TC, referencia de tarjeta '
                                                        'cancelada',
                                               'Resultado Esperado': 'La respuesta refleja estado CANCELADA y no '
                                                                     'permite operaciones adicionales.',
                                               'Prioridad': 'Low'},
                                              {'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-BDB] Como analista de pruebas quiero simular un '
                                                          'error técnico o timeout en balances-management-v2 para '
                                                          'confirmar el retorno de 502/504 y auditoría',
                                               'Descripcion': 'Validar el mapeo de errores técnicos hacia 502/504 y el '
                                                              'registro en la cola SQS de auditoría.',
                                               'Escenario': 'Servicio REST de saldos de tarjetas de BdB con fallo o '
                                                            'timeout.',
                                               'Accion': 'Ejecutar consulta bajo simulación de error en el servicio '
                                                         'bancario.',
                                               'Datos': 'operacion: CONSULTA_DETALLADA_TC, datos válidos bajo '
                                                        'indisponibilidad',
                                               'Resultado Esperado': 'El sistema retorna código 502 o 504 según la '
                                                                     'naturaleza del error y registra el evento.',
                                               'Prioridad': 'Medium'},
                                              {'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-BDB] Como analista de pruebas quiero validar la '
                                                          'autenticación biométrica de huella dactilar exitosa (OK) '
                                                          'para confirmar que el sistema autoriza la consulta '
                                                          'detallada de tarjeta de crédito en Banco de Bogotá',
                                               'Descripcion': 'Validar que al presentar una huella biométrica válida y '
                                                              'coincidente (validación OK), el sistema autentique '
                                                              'satisfactoriamente la identidad del cliente y permita '
                                                              'el procesamiento de la consulta detallada de tarjeta de '
                                                              'crédito en Banco de Bogotá.',
                                               'Escenario': 'Cliente presente en canal presencial/oficina con huella '
                                                            'biométrica registrada y coincidente (Match OK) en el '
                                                            'servicio de biometría.',
                                               'Accion': 'Ejecutar la validación biométrica de huella con resultado '
                                                         'exitoso (OK) previa a la solicitud de la consulta detallada '
                                                         'de tarjeta de crédito en Banco de Bogotá.',
                                               'Datos': 'Identificación de cliente válida, captura de huella dactilar: '
                                                        'match OK (100% coincidencia), contexto de oficina/asesor.',
                                               'Resultado Esperado': 'Autenticación biométrica aprobada (OK) y '
                                                                     'ejecución exitosa de la consulta detallada de '
                                                                     'tarjeta de crédito en Banco de Bogotá retornando '
                                                                     'la información correspondiente.',
                                               'Prioridad': 'High'},
                                              {'Tipo de test': 'Funcional',
                                               'Resumen': '[HU-103-ADP-BDB] Como analista de pruebas quiero validar el '
                                                          'rechazo por huella dactilar no coincidente o inválida (No '
                                                          'OK) para confirmar que el sistema bloquea la consulta '
                                                          'detallada de tarjeta de crédito en Banco de Bogotá',
                                               'Descripcion': 'Validar que ante una huella biométrica no coincidente o '
                                                              'no reconocida (validación No OK), el sistema rechace la '
                                                              'autenticación y bloquee el procesamiento de la consulta '
                                                              'detallada de tarjeta de crédito en Banco de Bogotá.',
                                               'Escenario': 'Intento de operación con huella biométrica no coincidente '
                                                            'o rechazada (Match No OK) por el servicio de biometría.',
                                               'Accion': 'Ejecutar la validación biométrica de huella enviando una '
                                                         'muestra no coincidente (No OK).',
                                               'Datos': 'Identificación de cliente, captura de huella dactilar: match '
                                                        'No OK (no coincidencia / rechazo biométrico).',
                                               'Resultado Esperado': 'El sistema deniega el acceso por validación '
                                                                     'biométrica No OK, no procesa la consulta '
                                                                     'detallada de tarjeta de crédito en Banco de '
                                                                     'Bogotá y retorna el mensaje de autenticación '
                                                                     'fallida.',
                                               'Prioridad': 'High'},
                                              {'Tipo de test': 'Accesibilidad',
                                               'Resumen': '[HU-103-ADP-BDB] Como analista de pruebas quiero verificar '
                                                          'el desglose claro y legible de cupos aprobados, cupo '
                                                          'disponible y saldos diferidos',
                                               'Descripcion': 'Validar que los datos de cupos y saldos de TC presenten '
                                                              'etiquetas inequívocas.',
                                               'Escenario': 'Respuesta con múltiples conceptos de saldos y cupos.',
                                               'Accion': 'Revisar la presentación y rotulado de cupos y saldos.',
                                               'Datos': 'Campos cupoAprobado, cupoDisponible, saldoTotal, '
                                                        'saldoDiferido.',
                                               'Resultado Esperado': 'Cada concepto financiero es fácilmente '
                                                                     'comprensible y legible sin ambigüedades.',
                                               'Prioridad': 'Medium'},
                                              {'Tipo de test': 'Accesibilidad',
                                               'Resumen': '[HU-103-ADP-BDB] Como analista de pruebas quiero verificar '
                                                          'la claridad en la exposición del número de cuotas diferidas '
                                                          'y franquicia',
                                               'Descripcion': 'Validar que la cantidad de cuotas diferidas y el nombre '
                                                              'de la franquicia se muestren con total claridad.',
                                               'Escenario': 'Detalle de tarjeta con diferidos y franquicia.',
                                               'Accion': 'Verificar la legibilidad de cuotas diferidas y franquicia.',
                                               'Datos': 'Campos franquicia y cuotasDiferidas en la salida.',
                                               'Resultado Esperado': 'La información es autoexplicativa y '
                                                                     'comprensible.',
                                               'Prioridad': 'Medium'},
                                              {'Tipo de test': 'Accesibilidad',
                                               'Resumen': '[HU-103-ADP-BDB] Como analista de pruebas quiero verificar '
                                                          'la claridad del mensaje de error cuando la tarjeta no '
                                                          'existe en Banco de Bogotá',
                                               'Descripcion': 'Validar que el mensaje de error 404 sea orientativo '
                                                              'para el asesor o usuario.',
                                               'Escenario': 'Consulta con tarjeta no encontrada.',
                                               'Accion': 'Revisar el mensaje de error retornado.',
                                               'Datos': 'Mensaje de error del servicio.',
                                               'Resultado Esperado': 'El mensaje indica con claridad que la tarjeta '
                                                                     'consultada no existe en el banco.',
                                               'Prioridad': 'Low'}]},
 'HU-104-ADP-AVV-cdt-detallado.md': {'id': 'HU-104-ADP-AVV',
                                     'title': 'Adaptador AV Villas — Consulta Detallada de CDT',
                                     'domain': 'consulta detallada de CDT en AV Villas',
                                     'cases': [{'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-AVV] Como analista de pruebas quiero consultar '
                                                           'el detalle de un CDT activo para confirmar la obtención de '
                                                           'su monto, tasa EA, fechas y periodicidad',
                                                'Descripcion': 'Validar la consulta de CDT en AV Villas mediante '
                                                               'getBalanceByProduct con AcctType=CDA.',
                                                'Escenario': 'CDT activo y vigente en AV Villas.',
                                                'Accion': "Enviar solicitud de consulta de CDT con tipoDocumento 'CC', "
                                                          "numeroDocumento '12345678' y numeroProducto '26456554'.",
                                                'Datos': "operacion: CONSULTA_DETALLADA_CDT, tipoDocumento: 'CC', "
                                                         "numeroDocumento: '12345678', numeroProducto: '26456554', "
                                                         'X-Destination-Bank: BAVV, X-Origin-Bank: BAVV, X-Trace-Id: '
                                                         'trace-001, X-RqUID: trace-001, X-IPAddr: 10.10.111.110, '
                                                         'X-ClientDt: 2026-09-10T10:00:00, X-SessKey: sess-abc123, '
                                                         'X-NextDay: false',
                                                'Resultado Esperado': 'Respuesta con detalle de CDT: numeroProducto, '
                                                                      'monto, tasaEA, fechaApertura, fechaVencimiento, '
                                                                      'plazoDias y periodicidadIntereses.',
                                                'Prioridad': 'High'},
                                               {'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-AVV] Como analista de pruebas quiero consultar '
                                                           'un CDT no registrado en AV Villas para confirmar la '
                                                           'respuesta de error 404',
                                                'Descripcion': 'Validar que la consulta de un CDT inexistente retorne '
                                                               'código 404.',
                                                'Escenario': 'Número de CDT no existente en AV Villas.',
                                                'Accion': 'Enviar solicitud con numeroProducto no existente.',
                                                'Datos': 'operacion: CONSULTA_DETALLADA_CDT, numeroProducto: '
                                                         "'CDT-999999'",
                                                'Resultado Esperado': 'El sistema mapea el error a código 404 '
                                                                      'informando que el CDT no fue encontrado.',
                                                'Prioridad': 'High'},
                                               {'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-AVV] Como analista de pruebas quiero solicitar '
                                                           'la consulta de CDT omitiendo el número de producto para '
                                                           'confirmar el rechazo de la petición',
                                                'Descripcion': 'Validar la obligatoriedad del campo numeroProducto en '
                                                               'la consulta de CDT.',
                                                'Escenario': 'Solicitud sin el campo numeroProducto.',
                                                'Accion': 'Enviar solicitud omitiendo numeroProducto.',
                                                'Datos': 'operacion: CONSULTA_DETALLADA_CDT, obj_operacion: { '
                                                         "tipoDocumento: 'CC', numeroDocumento: '12345678' }",
                                                'Resultado Esperado': 'El sistema rechaza la petición indicando la '
                                                                      'ausencia del identificador del CDT.',
                                                'Prioridad': 'Medium'},
                                               {'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-AVV] Como analista de pruebas quiero intentar '
                                                           'la consulta de CDT con una operación no soportada para '
                                                           'confirmar el rechazo defensivo 400',
                                                'Descripcion': 'Validar que operaciones no soportadas sean rechazadas '
                                                               'con código 400.',
                                                'Escenario': 'Solicitud con operacion distinta a '
                                                             'CONSULTA_DETALLADA_CDT.',
                                                'Accion': "Enviar solicitud con operacion 'CDT_NO_VALIDO'.",
                                                'Datos': "operacion: 'CDT_NO_VALIDO', X-Destination-Bank: BAVV",
                                                'Resultado Esperado': 'El adaptador lanza excepción y retorna código '
                                                                      '400 al orquestador.',
                                                'Prioridad': 'Medium'},
                                               {'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-AVV] Como analista de pruebas quiero consultar '
                                                           'un CDT con plazo en días límite o especial para confirmar '
                                                           'el cálculo correcto de fechas',
                                                'Descripcion': 'Validar el comportamiento ante CDT con plazos cortos '
                                                               '(30 días) o largos (360+ días).',
                                                'Escenario': 'CDT constituido a plazos especiales en AV Villas.',
                                                'Accion': 'Enviar solicitud para CDT de 360 días.',
                                                'Datos': 'operacion: CONSULTA_DETALLADA_CDT, numeroProducto de CDT a '
                                                         '360 días',
                                                'Resultado Esperado': 'La respuesta refleja fielmente el plazo en días '
                                                                      'y la fecha de vencimiento concordante.',
                                                'Prioridad': 'Low'},
                                               {'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-AVV] Como analista de pruebas quiero consultar '
                                                           'un CDT ya vencido para confirmar la información de estado '
                                                           'de vencimiento',
                                                'Descripcion': 'Validar la entrega de datos en certificados que han '
                                                               'alcanzado su fecha de maduración.',
                                                'Escenario': 'CDT vencido en AV Villas.',
                                                'Accion': 'Enviar consulta para CDT en estado vencido.',
                                                'Datos': 'operacion: CONSULTA_DETALLADA_CDT, numeroProducto de CDT '
                                                         'vencido',
                                                'Resultado Esperado': 'La respuesta refleja las fechas de apertura y '
                                                                      'vencimiento históricas con exactitud.',
                                                'Prioridad': 'Low'},
                                               {'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-AVV] Como analista de pruebas quiero simular '
                                                           'un error técnico en el backend de CDT para confirmar el '
                                                           'código de error y Circuit Breaker',
                                                'Descripcion': 'Validar el retorno de error 502/504 y registro en '
                                                               'auditoría SQS ante falla del backend de CDT.',
                                                'Escenario': 'Servicio SOAP de CDT con falla de comunicación o '
                                                             'timeout.',
                                                'Accion': 'Ejecutar consulta de CDT en escenario de falla del backend.',
                                                'Datos': 'operacion: CONSULTA_DETALLADA_CDT, datos válidos bajo '
                                                         'contingencia',
                                                'Resultado Esperado': 'El sistema retorna 502/504, activa Circuit '
                                                                      'Breaker y publica en la cola SQS de auditoría.',
                                                'Prioridad': 'Medium'},
                                               {'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-AVV] Como analista de pruebas quiero validar '
                                                           'la autenticación biométrica de huella dactilar exitosa '
                                                           '(OK) para confirmar que el sistema autoriza la consulta '
                                                           'detallada de CDT en AV Villas',
                                                'Descripcion': 'Validar que al presentar una huella biométrica válida '
                                                               'y coincidente (validación OK), el sistema autentique '
                                                               'satisfactoriamente la identidad del cliente y permita '
                                                               'el procesamiento de la consulta detallada de CDT en AV '
                                                               'Villas.',
                                                'Escenario': 'Cliente presente en canal presencial/oficina con huella '
                                                             'biométrica registrada y coincidente (Match OK) en el '
                                                             'servicio de biometría.',
                                                'Accion': 'Ejecutar la validación biométrica de huella con resultado '
                                                          'exitoso (OK) previa a la solicitud de la consulta detallada '
                                                          'de CDT en AV Villas.',
                                                'Datos': 'Identificación de cliente válida, captura de huella '
                                                         'dactilar: match OK (100% coincidencia), contexto de '
                                                         'oficina/asesor.',
                                                'Resultado Esperado': 'Autenticación biométrica aprobada (OK) y '
                                                                      'ejecución exitosa de la consulta detallada de '
                                                                      'CDT en AV Villas retornando la información '
                                                                      'correspondiente.',
                                                'Prioridad': 'High'},
                                               {'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-AVV] Como analista de pruebas quiero validar '
                                                           'el rechazo por huella dactilar no coincidente o inválida '
                                                           '(No OK) para confirmar que el sistema bloquea la consulta '
                                                           'detallada de CDT en AV Villas',
                                                'Descripcion': 'Validar que ante una huella biométrica no coincidente '
                                                               'o no reconocida (validación No OK), el sistema rechace '
                                                               'la autenticación y bloquee el procesamiento de la '
                                                               'consulta detallada de CDT en AV Villas.',
                                                'Escenario': 'Intento de operación con huella biométrica no '
                                                             'coincidente o rechazada (Match No OK) por el servicio de '
                                                             'biometría.',
                                                'Accion': 'Ejecutar la validación biométrica de huella enviando una '
                                                          'muestra no coincidente (No OK).',
                                                'Datos': 'Identificación de cliente, captura de huella dactilar: match '
                                                         'No OK (no coincidencia / rechazo biométrico).',
                                                'Resultado Esperado': 'El sistema deniega el acceso por validación '
                                                                      'biométrica No OK, no procesa la consulta '
                                                                      'detallada de CDT en AV Villas y retorna el '
                                                                      'mensaje de autenticación fallida.',
                                                'Prioridad': 'High'},
                                               {'Tipo de test': 'Accesibilidad',
                                                'Resumen': '[HU-104-ADP-AVV] Como analista de pruebas quiero verificar '
                                                           'la claridad en la presentación de tasa EA, plazo en días y '
                                                           'monto del CDT',
                                                'Descripcion': 'Validar que los datos de inversión del CDT cuenten con '
                                                               'rotulado comprensible y formato legible.',
                                                'Escenario': 'Respuesta de CDT procesada por el sistema.',
                                                'Accion': 'Revisar los rótulos y valores de tasa EA, monto y plazo en '
                                                          'días.',
                                                'Datos': 'Campos monto, tasaEA, plazoDias.',
                                                'Resultado Esperado': 'Los conceptos de rentabilidad, capital y tiempo '
                                                                      'están claramente expuestos sin ambigüedad.',
                                                'Prioridad': 'Medium'},
                                               {'Tipo de test': 'Accesibilidad',
                                                'Resumen': '[HU-104-ADP-AVV] Como analista de pruebas quiero verificar '
                                                           'que las fechas de apertura y vencimiento tengan un formato '
                                                           'estándar y comprensible',
                                                'Descripcion': 'Validar la presentación uniforme de fechas en el '
                                                               'certificado de depósito a término.',
                                                'Escenario': 'Fechas en la respuesta de CDT.',
                                                'Accion': 'Verificar el formato de fechaApertura y fechaVencimiento.',
                                                'Datos': 'Fechas de constitución y vencimiento del CDT.',
                                                'Resultado Esperado': 'Las fechas siguen una estructura cronológica '
                                                                      'clara y legible.',
                                                'Prioridad': 'Medium'},
                                               {'Tipo de test': 'Accesibilidad',
                                                'Resumen': '[HU-104-ADP-AVV] Como analista de pruebas quiero verificar '
                                                           'la claridad del mensaje de error ante CDT no encontrado',
                                                'Descripcion': 'Validar que el mensaje de CDT no encontrado sea '
                                                               'comprensible para el usuario.',
                                                'Escenario': 'Error 404 por CDT no encontrado.',
                                                'Accion': 'Revisar el mensaje de error del sistema.',
                                                'Datos': 'Mensaje de respuesta de error.',
                                                'Resultado Esperado': 'El mensaje informa claramente la no existencia '
                                                                      'del CDT consultado.',
                                                'Prioridad': 'Low'}]},
 'HU-104-ADP-BDB-cdt-detallado.md': {'id': 'HU-104-ADP-BDB',
                                     'title': 'Adaptador Banco de Bogotá — Consulta Detallada de CDT',
                                     'domain': 'consulta detallada de CDT en Banco de Bogotá',
                                     'cases': [{'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-BDB] Como analista de pruebas quiero consultar '
                                                           'el detalle de un CDT activo en Banco de Bogotá para '
                                                           'confirmar la recepción de monto, tasa EA, fechas e '
                                                           'intereses acumulados',
                                                'Descripcion': 'Validar la consulta de retrieveCertificateBalance en '
                                                               'balances-management-v2 con CDT válido.',
                                                'Escenario': 'CDT activo en Banco de Bogotá.',
                                                'Accion': "Enviar solicitud de consulta de CDT con tipoDocumento 'CC', "
                                                          "numeroDocumento '12345678' y numeroProducto "
                                                          "'0000000026456554'.",
                                                'Datos': "operacion: CONSULTA_DETALLADA_CDT, tipoDocumento: 'CC', "
                                                         "numeroDocumento: '12345678', numeroProducto: "
                                                         "'0000000026456554', X-Destination-Bank: BBOG, X-Origin-Bank: "
                                                         'BBOG, X-Trace-Id: trace-001, X-RqUID: trace-001, '
                                                         'X-CompanyId: PENDIENTE_DEFINIR, X-IPAddr: 10.10.111.110, '
                                                         'X-TerminalId: TERM01, X-NetworkOwner: BBOG, X-Journey: '
                                                         'CONSULTA_CDT',
                                                'Resultado Esperado': 'Respuesta 200 OK con numeroProducto, monto, '
                                                                      'tasaEA, fechaApertura, fechaVencimiento, '
                                                                      'plazoDias, periodicidadIntereses e '
                                                                      'interesesAcumulados.',
                                                'Prioridad': 'High'},
                                               {'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-BDB] Como analista de pruebas quiero consultar '
                                                           'un CDT no registrado en Banco de Bogotá para confirmar el '
                                                           'retorno de código 404',
                                                'Descripcion': 'Validar que si el CDT no existe en Banco de Bogotá, se '
                                                               'propague el código 404.',
                                                'Escenario': 'CDT no existente en Banco de Bogotá.',
                                                'Accion': 'Enviar solicitud con numeroProducto inexistente.',
                                                'Datos': 'operacion: CONSULTA_DETALLADA_CDT, numeroProducto: '
                                                         "'CDT-000000000'",
                                                'Resultado Esperado': 'El sistema retorna código 404 informando que el '
                                                                      'certificado no fue encontrado.',
                                                'Prioridad': 'High'},
                                               {'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-BDB] Como analista de pruebas quiero solicitar '
                                                           'la consulta de CDT omitiendo el identificador de producto '
                                                           'para confirmar el rechazo de la solicitud',
                                                'Descripcion': 'Validar la obligatoriedad del parámetro de producto '
                                                               'CDT.',
                                                'Escenario': 'Solicitud sin numeroProducto.',
                                                'Accion': 'Enviar solicitud omitiendo numeroProducto.',
                                                'Datos': 'operacion: CONSULTA_DETALLADA_CDT, obj_operacion: { '
                                                         "tipoDocumento: 'CC', numeroDocumento: '12345678' }",
                                                'Resultado Esperado': 'El sistema rechaza la solicitud indicando la '
                                                                      'ausencia del identificador del CDT.',
                                                'Prioridad': 'Medium'},
                                               {'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-BDB] Como analista de pruebas quiero enviar '
                                                           'una solicitud de CDT con operación no soportada para '
                                                           'confirmar el rechazo con código 400',
                                                'Descripcion': 'Validar el control defensivo ante operación no '
                                                               'soportada.',
                                                'Escenario': 'Solicitud con operacion distinta a '
                                                             'CONSULTA_DETALLADA_CDT.',
                                                'Accion': "Enviar solicitud con operacion 'OP_CDT_DESCONOCIDA'.",
                                                'Datos': "operacion: 'OP_CDT_DESCONOCIDA', X-Destination-Bank: BBOG",
                                                'Resultado Esperado': 'El adaptador lanza excepción y responde código '
                                                                      '400 al orquestador.',
                                                'Prioridad': 'Medium'},
                                               {'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-BDB] Como analista de pruebas quiero consultar '
                                                           'un CDT con intereses acumulados liquidados a la fecha para '
                                                           'confirmar la consistencia del monto de rendimiento',
                                                'Descripcion': 'Validar que el campo interesesAcumulados refleje '
                                                               'correctamente los rendimientos generados.',
                                                'Escenario': 'CDT con rendimientos liquidados a la fecha en Banco de '
                                                             'Bogotá.',
                                                'Accion': 'Consultar CDT con rendimientos acumulados.',
                                                'Datos': 'operacion: CONSULTA_DETALLADA_CDT, numeroProducto de CDT con '
                                                         'intereses generados',
                                                'Resultado Esperado': 'La respuesta entrega el valor exacto de '
                                                                      'intereses acumulados y tasa pactada.',
                                                'Prioridad': 'Medium'},
                                               {'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-BDB] Como analista de pruebas quiero consultar '
                                                           'un CDT con periodicidad de pago mensual para confirmar la '
                                                           'entrega de la periodicidad pactada',
                                                'Descripcion': 'Validar que la periodicidad de pago (MENSUAL, '
                                                               'AL_VENCIMIENTO) sea expuesta correctamente.',
                                                'Escenario': 'CDT con periodicidad MENSUAL.',
                                                'Accion': 'Enviar consulta para CDT con periodicidad de intereses '
                                                          'mensual.',
                                                'Datos': 'operacion: CONSULTA_DETALLADA_CDT, numeroProducto de CDT con '
                                                         'pago mensual',
                                                'Resultado Esperado': 'La respuesta refleja periodicidadIntereses = '
                                                                      "'MENSUAL' con las fechas de pago "
                                                                      'correspondientes.',
                                                'Prioridad': 'Low'},
                                               {'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-BDB] Como analista de pruebas quiero simular '
                                                           'un error técnico o timeout en balances-management-v2 para '
                                                           'confirmar el retorno de 502/504 y auditoría',
                                                'Descripcion': 'Validar el retorno de 502/504 y registro en la cola '
                                                               'SQS de auditoría ante falla del backend de BdB.',
                                                'Escenario': 'Servicio de certificados de BdB con falla técnica o '
                                                             'timeout.',
                                                'Accion': 'Ejecutar consulta bajo simulación de error en el servicio '
                                                          'bancario.',
                                                'Datos': 'operacion: CONSULTA_DETALLADA_CDT, datos válidos bajo '
                                                         'contingencia',
                                                'Resultado Esperado': 'El sistema retorna 502 o 504 según corresponda '
                                                                      'y registra el evento en auditoría.',
                                                'Prioridad': 'Medium'},
                                               {'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-BDB] Como analista de pruebas quiero validar '
                                                           'la autenticación biométrica de huella dactilar exitosa '
                                                           '(OK) para confirmar que el sistema autoriza la consulta '
                                                           'detallada de CDT en Banco de Bogotá',
                                                'Descripcion': 'Validar que al presentar una huella biométrica válida '
                                                               'y coincidente (validación OK), el sistema autentique '
                                                               'satisfactoriamente la identidad del cliente y permita '
                                                               'el procesamiento de la consulta detallada de CDT en '
                                                               'Banco de Bogotá.',
                                                'Escenario': 'Cliente presente en canal presencial/oficina con huella '
                                                             'biométrica registrada y coincidente (Match OK) en el '
                                                             'servicio de biometría.',
                                                'Accion': 'Ejecutar la validación biométrica de huella con resultado '
                                                          'exitoso (OK) previa a la solicitud de la consulta detallada '
                                                          'de CDT en Banco de Bogotá.',
                                                'Datos': 'Identificación de cliente válida, captura de huella '
                                                         'dactilar: match OK (100% coincidencia), contexto de '
                                                         'oficina/asesor.',
                                                'Resultado Esperado': 'Autenticación biométrica aprobada (OK) y '
                                                                      'ejecución exitosa de la consulta detallada de '
                                                                      'CDT en Banco de Bogotá retornando la '
                                                                      'información correspondiente.',
                                                'Prioridad': 'High'},
                                               {'Tipo de test': 'Funcional',
                                                'Resumen': '[HU-104-ADP-BDB] Como analista de pruebas quiero validar '
                                                           'el rechazo por huella dactilar no coincidente o inválida '
                                                           '(No OK) para confirmar que el sistema bloquea la consulta '
                                                           'detallada de CDT en Banco de Bogotá',
                                                'Descripcion': 'Validar que ante una huella biométrica no coincidente '
                                                               'o no reconocida (validación No OK), el sistema rechace '
                                                               'la autenticación y bloquee el procesamiento de la '
                                                               'consulta detallada de CDT en Banco de Bogotá.',
                                                'Escenario': 'Intento de operación con huella biométrica no '
                                                             'coincidente o rechazada (Match No OK) por el servicio de '
                                                             'biometría.',
                                                'Accion': 'Ejecutar la validación biométrica de huella enviando una '
                                                          'muestra no coincidente (No OK).',
                                                'Datos': 'Identificación de cliente, captura de huella dactilar: match '
                                                         'No OK (no coincidencia / rechazo biométrico).',
                                                'Resultado Esperado': 'El sistema deniega el acceso por validación '
                                                                      'biométrica No OK, no procesa la consulta '
                                                                      'detallada de CDT en Banco de Bogotá y retorna '
                                                                      'el mensaje de autenticación fallida.',
                                                'Prioridad': 'High'},
                                               {'Tipo de test': 'Accesibilidad',
                                                'Resumen': '[HU-104-ADP-BDB] Como analista de pruebas quiero verificar '
                                                           'la comprensión inmediata en la presentación de capital, '
                                                           'intereses acumulados y tasa EA',
                                                'Descripcion': 'Validar que los datos de capital, tasa y rendimientos '
                                                               'acumulados presenten un rotulado claro.',
                                                'Escenario': 'Respuesta de CDT con rendimientos acumulados y tasa.',
                                                'Accion': 'Inspeccionar las etiquetas de monto, tasaEA e '
                                                          'interesesAcumulados.',
                                                'Datos': 'Campos de capital y rentabilidad del CDT.',
                                                'Resultado Esperado': 'La información es nítida y permite distinguir '
                                                                      'con total claridad entre el capital inicial y '
                                                                      'los intereses ganados.',
                                                'Prioridad': 'Medium'},
                                               {'Tipo de test': 'Accesibilidad',
                                                'Resumen': '[HU-104-ADP-BDB] Como analista de pruebas quiero verificar '
                                                           'la visualización accesible de plazos en días, periodicidad '
                                                           'y fechas',
                                                'Descripcion': 'Validar que los plazos, periodicidad y cronograma del '
                                                               'CDT sean legibles y sin abreviaturas confusas.',
                                                'Escenario': 'Plazos y cronograma de vencimiento de CDT.',
                                                'Accion': 'Verificar la legibilidad de plazoDias, '
                                                          'periodicidadIntereses y fechas.',
                                                'Datos': 'Campos de tiempo y periodicidad.',
                                                'Resultado Esperado': 'Los datos temporales se entienden de forma '
                                                                      'directa sin requerir conocimientos técnicos.',
                                                'Prioridad': 'Medium'},
                                               {'Tipo de test': 'Accesibilidad',
                                                'Resumen': '[HU-104-ADP-BDB] Como analista de pruebas quiero verificar '
                                                           'la claridad del mensaje de error cuando el CDT no existe '
                                                           'en Banco de Bogotá',
                                                'Descripcion': 'Validar que el mensaje ante error 404 sea orientativo '
                                                               'y accionable para el usuario.',
                                                'Escenario': 'Error 404 por CDT no encontrado en Banco de Bogotá.',
                                                'Accion': 'Revisar el texto del mensaje de error.',
                                                'Datos': 'Mensaje de respuesta del servicio.',
                                                'Resultado Esperado': 'El mensaje informa claramente que el '
                                                                      'certificado consultado no fue encontrado en la '
                                                                      'entidad.',
                                                'Prioridad': 'Low'}]}}


def _ensure_template():
    if not FORMAT_JIRA_PATH.exists():
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "TestCases"
        headers = [
            "Issue Key",
            "Summary",
            "Description",
            "Precondition",
            "Status",
            "Priority",
            "Assignee",
            "Reporter",
            "Estimated Time",
            "Labels",
            "Components",
            "Sprint",
            "Fix Versions",
            "Is Shareable Step",
            "Shareable Testcase Issue Key",
            "Shareable Testcase Version No.",
            "Step Summary",
            "Test Data",
            "Expected Result",
            "Version",
            "Folders",
            "TestCase Type",
            "Created By",
            "Created Date",
            "Updated By",
            "Updated Date",
            "Story Linkages",
            "Comment Count",
            "Attachment Count",
            "Story Count",
        ]
        ws.append(headers)
        wb.save(FORMAT_JIRA_PATH)


def generate_excel():
    _ensure_template()
    wb = openpyxl.load_workbook(FORMAT_JIRA_PATH)
    ws = wb.active

    # Limpiar filas existentes
    if ws.max_row > 1:
        ws.delete_rows(2, ws.max_row - 1)

    headers = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1)]
    header_map = {str(name).strip(): idx for idx, name in enumerate(headers, start=1) if name}

    row_idx = 2
    issue_id = 1
    total_funcionales = 0
    total_accesibilidad = 0
    cases_summary = {}

    thin_border = Border(
        left=Side(style="thin", color="D3D3D3"),
        right=Side(style="thin", color="D3D3D3"),
        top=Side(style="thin", color="D3D3D3"),
        bottom=Side(style="thin", color="D3D3D3"),
    )

    for hu_file, hu_data in CASOS_POR_HU.items():
        hu_id = hu_data["id"]
        hu_title = hu_data["title"]
        cases = hu_data["cases"]
        cases_summary[hu_file] = {
            "id": hu_id,
            "title": hu_title,
            "funcionales": 0,
            "accesibilidad": 0,
            "total": len(cases),
            "cases": [],
        }

        for case in cases:
            tc_type = case["Tipo de test"]
            if tc_type == "Funcional":
                total_funcionales += 1
                cases_summary[hu_file]["funcionales"] += 1
            elif tc_type == "Accesibilidad":
                total_accesibilidad += 1
                cases_summary[hu_file]["accesibilidad"] += 1

            cases_summary[hu_file]["cases"].append(case)

            issue_key = f"EV-{issue_id}"
            values = {
                "Issue Key": issue_key,
                "Summary": case["Resumen"],
                "Description": case["Descripcion"],
                "Precondition": case["Escenario"],
                "Status": "To Do",
                "Priority": case.get("Prioridad", "Medium"),
                "Assignee": "",
                "Reporter": "",
                "Estimated Time": "",
                "Labels": f"everest,{tc_type.lower()},oficinas,consultas",
                "Components": hu_title,
                "Sprint": "Sprint 1",
                "Fix Versions": "v1.0.0",
                "Is Shareable Step": "No",
                "Shareable Testcase Issue Key": "",
                "Shareable Testcase Version No.": "",
                "Step Summary": f"1. Configurar contexto y datos de prueba: {case['Accion']} | 2. Enviar solicitud al adaptador bancario correspondiente | 3. Validar que la respuesta y estado correspondan al resultado esperado",
                "Test Data": case["Datos"],
                "Expected Result": case["Resultado Esperado"],
                "Version": "1",
                "Folders": hu_id,
                "TestCase Type": tc_type,
                "Created By": "QA Automation Team",
                "Created Date": "2026-09-14",
                "Updated By": "QA Automation Team",
                "Updated Date": "2026-09-14",
                "Story Linkages": hu_id,
                "Comment Count": "0",
                "Attachment Count": "0",
                "Story Count": "1",
            }

            for name, col_idx in header_map.items():
                cell = ws.cell(row=row_idx, column=col_idx, value=values.get(name, ""))
                cell.border = thin_border
                cell.alignment = Alignment(vertical="top", wrap_text=True)

            row_idx += 1
            issue_id += 1

    # Estilos del encabezado
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    for c in range(1, ws.max_column + 1):
        cell = ws.cell(row=1, column=c)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Ajuste de ancho de columnas
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(cell.value or "")) for cell in col[:10])
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUTPUT_PATH)

    return total_funcionales, total_accesibilidad, issue_id - 1, cases_summary


if __name__ == "__main__":
    func, acc, total, summary = generate_excel()
    print(f"Total HUs procesadas: {len(summary)}")
    print(f"Total Casos Generados: {total}")
    print(f" - Funcionales: {func}")
    print(f" - Accesibilidad: {acc}")
    print(f"Archivo generado en: {OUTPUT_PATH}")
