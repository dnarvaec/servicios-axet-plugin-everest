# Ejecucion local - HU-202 Bloqueo TC

La suite se ejecuta con Maven/Cucumber desde un prompt local. No usa GitHub Copilot, OpenAI API ni tokens de modelos.

## Ejecucion recomendada

```bat
ejecutar_bloqueo_tc_local.cmd
```

Ejecuta `@bloqueo_tc and not @mock_gap`: casos cuyo trigger es deterministico segun la coleccion Postman o el HTML de referencia.

## Ejecutar todos los casos HU-202

```bat
ejecutar_bloqueo_tc_local.cmd all
```

Los escenarios `@mock_gap` existen para mantener trazabilidad con `casos everest.xlsx`, pero la coleccion/HTML entregados no exponen un trigger deterministico para reproducir 401/408/timeout de conectividad en algunos flujos BDB/OCC. No se inventaron valores magicos.

## Ejecucion Maven directa

```bat
mvn verify "-Dcucumber.filter.tags=@bloqueo_tc and not @mock_gap"
```
