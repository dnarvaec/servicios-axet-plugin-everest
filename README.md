# Everest — Automatización API Grupo Aval

Automatización de pruebas de API (Serenity BDD + Screenplay + Cucumber) para las
4 transacciones expuestas por el orquestador Everest, más un generador/uploader
de casos de prueba hacia Jira.

## Estructura del repositorio

```
.
├── agentes/                          # Documentación viva (contrato de API, guías de automatización)
├── casos de prueba/                  # Suites de casos generadas (Excel)
├── HU *.xlsx                         # Historias de usuario fuente
├── jira_uploader.py                  # Sube casos de prueba (Excel) a Jira
├── requirements.txt                  # Dependencias Python de jira_uploader.py
└── tests/automatizacion api/serenity rest/   # Proyecto Maven de automatización (Java 17)
    ├── pom.xml
    └── src/test/
        ├── java/serenityrest/
        │   ├── runner/              # CucumberRunnerTest (JUnit 5 Platform Suite)
        │   ├── stepdefinitions/     # 4 clases *StepDefinitions + Hooks.java compartido
        │   ├── screenplay/          # Abilities y Questions de Serenity Screenplay
        │   └── utils/               # ApiEndpoints, TestData, DataDrivenExcelReader, ApiAssertions
        └── resources/
            ├── features/            # .feature por transacción (retiro, deposito, recaudo, pagos)
            ├── datadriven/           # datadriven.xlsx — única fuente de datos de prueba
            └── serenity.conf
```

## Transacciones cubiertas

| TX | Descripción | Endpoint |
|----|-------------|----------|
| TX-01 | Retiro de efectivo con OTP | `POST /api/v1/pagos/retiro` |
| TX-02 | Depósitos y consignaciones en efectivo | `POST /api/v1/pagos/deposito` |
| TX-03 | Recaudo de convenios (consulta + pago, 2 pasos) | `POST /everest/orq/consultas/api/v1/consulta` → `POST /api/v1/pagos/pago-factura` |
| TX-04 | Pago de obligaciones y TC Aval | `POST /api/v1/pagos/pago-obligaciones` |

Detalle completo del contrato (headers, body, catálogo de códigos de estado) en
[`agentes/Análisis Colección Postman - Everest AVC.md`](agentes/Análisis%20Colección%20Postman%20-%20Everest%20AVC.md).

## Stack

- Java 17 · Maven
- [Serenity BDD](https://serenity-bdd.github.io/) con patrón **Screenplay** (sin capa `Task`:
  las `Interaction` como `Post.to(...)` se invocan directamente desde `actor.attemptsTo(...)`)
- Cucumber (`cucumber-junit-platform-engine`) sobre JUnit 5 Platform Suite
- REST Assured (vía `serenity-screenplay-rest`)
- Apache POI — lectura de `datadriven.xlsx`

## Cómo correr la suite

```powershell
cd "tests\automatizacion api\serenity rest"
mvn clean verify
```

`mvn clean verify` sincroniza automáticamente los `Ejemplos:` de cada `.feature` contra
`datadriven.xlsx` (fase `process-test-classes`, ver `FeatureOutlinePrecondition`), ejecuta
los tests con `maven-failsafe-plugin` y genera el reporte Serenity aunque fallen los tests.

El reporte HTML queda en `target/site/serenity/index.html`.

Para filtrar por una sola transacción, usa las tags de Cucumber ya definidas en los
`.feature` (`@retiro`, `@deposito`, `@recaudo`, `@tx03`, `@smoke`, `@e2e`, etc.):

```powershell
mvn clean verify "-Dcucumber.filter.tags=@retiro"
```

## Excel como única fuente de verdad

`datadriven.xlsx` tiene una hoja por transacción (`retiro`, `deposito`, `recaudo`,
`pago_obligaciones`). Cada fila es un **caso** (columna `Caso`), y las columnas usan
prefijos reservados:

- `header.<Nombre-Header>` → headers HTTP del request
- `expected.statusCode` / `expected.severity` / `expected.statusDesc` → resultado de
  negocio esperado (`msgRsHdr.status.*` del body)
- `expected.httpStatusCode` → código HTTP esperado de la respuesta
- el resto de columnas → campos del payload (rutas anidadas tipo `operacionobj.CurAmt.Amt`)

No hay valores hardcodeados en Java ni en los `.feature` — todo (payload, headers,
resultado esperado) se lee dinámicamente del Excel vía `TestData` / `DataDrivenExcelReader`.

**Para agregar un caso nuevo a una TX existente**: solo agregar una fila al Excel — el
número de `Ejemplos` se regenera solo en el siguiente `mvn verify`, sin tocar Java ni `.feature`.

## Estado conocido

Al momento de este README, el mock de CloudFront (`https://d2q3sea1wnkwiy.cloudfront.net`)
no tiene conectividad real con Postillion/API Connect — los 5 endpoints devuelven `404`.
Esto es un problema de entorno, no de la automatización (confirmado con `Invoke-WebRequest`
directo, fuera de Maven). Los tests fallan hoy por esa causa; el pipeline y la lógica de
aserciones están validados y listos para cuando la conectividad se restablezca.

## Generación y subida de casos a Jira

```powershell
python jira_uploader.py "casos de prueba/retiro_otp.xlsx"
```

Configuración de conexión en `.env` (ver plantilla de variables requeridas en el propio
archivo — nunca versionar `.env` con credenciales reales, ya está en `.gitignore`).
