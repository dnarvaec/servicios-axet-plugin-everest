# Limitaciones de la corrida

- Externa, solo escritorio; no se modificó la aplicación ni se guardaron datos.
- Se marcó el gate simulado de QA para llegar a las vistas de productos. No se afirma biometría real.
- Los botones de bloqueo/desbloqueo/activación no se confirmaron y no se guardó el formulario de edición.
- La validación de correo inválido no mostró error en blur y dejó Guardar habilitado; no se envió el formulario por riesgo de mutación.
- Axe detectó contraste 2.84:1 en MIS HERRAMIENTAS (WCAG 1.4.3); no hubo revalidación posterior.
- 79 claves únicas, sin N/A/BLOCKED; WARN indica criterio de producto/operación no disponible en la UI observada, con evidencia específica por clave.
