@echo off
setlocal
cd /d "%~dp0"

where mvn >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Maven no esta disponible en PATH. Instala Maven 3.9+ y vuelve a ejecutar.
  exit /b 1
)

if /I "%~1"=="all" (
  echo Ejecutando todos los casos BLOQUEO_TC, incluidos los marcados @mock_gap...
  mvn verify "-Dcucumber.filter.tags=@bloqueo_tc"
) else (
  echo Ejecutando casos BLOQUEO_TC con trigger deterministico disponible en coleccion/HTML...
  mvn verify "-Dcucumber.filter.tags=@bloqueo_tc and not @mock_gap"
)

exit /b %ERRORLEVEL%
