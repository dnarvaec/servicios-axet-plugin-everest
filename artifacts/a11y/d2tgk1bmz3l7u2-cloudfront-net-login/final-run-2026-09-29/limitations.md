# Limitaciones

- Ejecución externa solo desktop; WCAG A/AA. Sin móvil.
- El checkbox de QA se marcó para exponer vistas, sin realizar biometría real.
- No se confirmaron botones de bloqueo/desbloqueo/activación ni se guardaron cambios.
- Los campos vacíos se trataron como posibles datos no provistos por el mock y se dejaron WARN cuando impedían la expectativa; no se marcaron como fallos de formato por sí solos.
- Axe reportó una violación seria de contraste WCAG 1.4.3; no hubo cambios ni reescaneo posterior.
- Dashboard legacy puede no reflejar este run; resultados autoritativos están en results.json y report.md.
