"""
Sube casos de prueba (Excel, formato `casos de prueba/plantilla_base.xlsx`) como
Test Cases de QMetry (QTM4J), via la API interna `/rest/qtm4j/ui/latest/testcases`.

Autenticacion: Basic Auth con JIRA_USERNAME/JIRA_API_TOKEN.

Columna "Folders" (opcional, col U):
    Admite rutas con subcarpetas separadas por "/":
        Ejemplo:  TX-01 Retiro OTP/Happy Path/Funcional
    Cada nivel de la ruta que no exista en QMetry se crea automaticamente con el
    padre correcto antes de subir el primer caso de esa ruta.
    Celda vacia -> raiz del proyecto (folderId = -1).

Uso:
    python jira_uploader.py "casos de prueba/suite.xlsx" [fila_inicio]
"""
import os
import sys

import openpyxl
import requests
from dotenv import load_dotenv

COLUMNAS_ESPERADAS_ES = [
    "Resumen", "Descripcion", "Escenario", "Accion", "Datos", "Resultado Esperado",
]
COLUMNAS_ESPERADAS_EN = [
    "Summary", "Description", "Precondition", "Step Summary", "Test Data", "Expected Result",
]
COLUMNA_FOLDERS = "Folders"

FOLDER_ID_RAIZ = -1
PRIORITY_NOMBRE_DEFAULT = "High"
STATUS_NOMBRE_DEFAULT = "To Do"
PRIORITY_ID_FALLBACK = 1906
STATUS_ID_FALLBACK = 4290

_MAPA_EN_A_INTERNO = {
    "Summary": "Resumen",
    "Description": "Descripcion",
    "Precondition": "Escenario",
    "Step Summary": "Accion",
    "Test Data": "Datos",
    "Expected Result": "Resultado Esperado",
}


# ---------------------------------------------------------------------------
# Catalogo de estados y prioridades (lookup dinamico)
# ---------------------------------------------------------------------------

def _cargar_prioridad_id(sesion, config):
    """
    Consulta el catalogo de prioridades de QMetry y devuelve el ID
    correspondiente a PRIORITY_NOMBRE_DEFAULT ("High").
    Si falla, devuelve PRIORITY_ID_FALLBACK.
    """
    url = config["jira_url"] + "/rest/qtm4j/ui/latest/priorities"
    try:
        resp = sesion.get(url, timeout=30)
        if not resp.ok:
            print(
                "  [AVISO] No se pudo cargar catalogo de prioridades "
                "(HTTP " + str(resp.status_code) + "). Usando fallback id=" + str(PRIORITY_ID_FALLBACK)
            )
            return PRIORITY_ID_FALLBACK
        datos = resp.json()
        lista = datos if isinstance(datos, list) else (
            datos.get("data") or datos.get("content") or datos.get("priorities") or []
        )
        for item in lista:
            nombre = (item.get("name") or item.get("priorityName") or "").strip()
            if nombre.lower() == PRIORITY_NOMBRE_DEFAULT.lower():
                pid = item.get("id") or item.get("priorityId")
                print("  [Catalogo] Prioridad '" + PRIORITY_NOMBRE_DEFAULT + "' -> id=" + str(pid))
                return pid
        print(
            "  [AVISO] Prioridad '" + PRIORITY_NOMBRE_DEFAULT
            + "' no encontrada en catalogo. Usando fallback id=" + str(PRIORITY_ID_FALLBACK)
        )
        return PRIORITY_ID_FALLBACK
    except Exception as exc:
        print("  [AVISO] Error consultando prioridades: " + str(exc) + ". Usando fallback id=" + str(PRIORITY_ID_FALLBACK))
        return PRIORITY_ID_FALLBACK


def _cargar_estado_id(sesion, config):
    """
    Consulta el catalogo de estados de QMetry (tipo TEST_CASE) y devuelve
    el ID correspondiente a STATUS_NOMBRE_DEFAULT ("To Do").
    Si falla, devuelve STATUS_ID_FALLBACK.
    """
    url = config["jira_url"] + "/rest/qtm4j/ui/latest/statuses"
    try:
        resp = sesion.get(url, params={"type": "TEST_CASE"}, timeout=30)
        if not resp.ok:
            # Intentar sin parametro type
            resp = sesion.get(url, timeout=30)
        if not resp.ok:
            print(
                "  [AVISO] No se pudo cargar catalogo de estados "
                "(HTTP " + str(resp.status_code) + "). Usando fallback id=" + str(STATUS_ID_FALLBACK)
            )
            return STATUS_ID_FALLBACK
        datos = resp.json()
        lista = datos if isinstance(datos, list) else (
            datos.get("data") or datos.get("content") or datos.get("statuses") or []
        )
        for item in lista:
            nombre = (item.get("name") or item.get("statusName") or "").strip()
            if nombre.lower() == STATUS_NOMBRE_DEFAULT.lower():
                sid = item.get("id") or item.get("statusId")
                print("  [Catalogo] Estado '" + STATUS_NOMBRE_DEFAULT + "' -> id=" + str(sid))
                return sid
        print(
            "  [AVISO] Estado '" + STATUS_NOMBRE_DEFAULT
            + "' no encontrado en catalogo. Usando fallback id=" + str(STATUS_ID_FALLBACK)
        )
        return STATUS_ID_FALLBACK
    except Exception as exc:
        print("  [AVISO] Error consultando estados: " + str(exc) + ". Usando fallback id=" + str(STATUS_ID_FALLBACK))
        return STATUS_ID_FALLBACK


# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------

def _cargar_configuracion():
    load_dotenv()
    faltantes = [
        v for v in ("JIRA_URL", "JIRA_USERNAME", "JIRA_API_TOKEN", "QMETRY_PROJECT_ID")
        if not os.getenv(v)
    ]
    if faltantes:
        raise RuntimeError("Faltan variables en .env: " + ", ".join(faltantes))
    return {
        "jira_url": os.environ["JIRA_URL"].rstrip("/"),
        "username": os.environ["JIRA_USERNAME"],
        "token": os.environ["JIRA_API_TOKEN"],
        "project_id": int(os.environ["QMETRY_PROJECT_ID"]),
    }


# ---------------------------------------------------------------------------
# Lectura del Excel
# ---------------------------------------------------------------------------

def _indice_columnas(hoja):
    cabeceras_raw = {celda.value: celda.column for celda in hoja[1] if celda.value}

    if all(c in cabeceras_raw for c in COLUMNAS_ESPERADAS_EN):
        cabeceras = {}
        for nombre_en, nombre_es in _MAPA_EN_A_INTERNO.items():
            cabeceras[nombre_es] = cabeceras_raw[nombre_en]
        for nombre, col in cabeceras_raw.items():
            if nombre not in _MAPA_EN_A_INTERNO:
                cabeceras[nombre] = col
        print("  [Info] Formato detectado: QMetry nativo (ingles)")
        return cabeceras

    faltantes = [c for c in COLUMNAS_ESPERADAS_ES if c not in cabeceras_raw]
    if not faltantes:
        print("  [Info] Formato detectado: interno (espanol)")
        return cabeceras_raw

    raise ValueError(
        "El Excel no tiene las columnas esperadas.\n"
        "Formato espanol faltantes: " + str([c for c in COLUMNAS_ESPERADAS_ES if c not in cabeceras_raw]) + "\n"
        "Formato QMetry faltantes:  " + str([c for c in COLUMNAS_ESPERADAS_EN if c not in cabeceras_raw])
    )


# ---------------------------------------------------------------------------
# Gestion de carpetas -- soporte de subcarpetas anidadas
# ---------------------------------------------------------------------------

def _cargar_carpetas_existentes(sesion, config):
    """
    Devuelve {ruta_completa_lower: folder_id}.
    Construye rutas completas usando el campo 'parentId' de cada carpeta.
    """
    url = (
        config["jira_url"]
        + "/rest/qtm4j/ui/latest/projects/"
        + str(config["project_id"])
        + "/testcase-folders"
    )
    resp = sesion.get(url, params={"sort": "NAME:ASC"}, timeout=30)
    if not resp.ok:
        print(
            "  [AVISO] No se pudieron cargar carpetas existentes "
            "(HTTP " + str(resp.status_code) + "). Se crearan todas las necesarias."
        )
        return {}

    datos = resp.json()
    if isinstance(datos, list):
        elementos = datos
    elif isinstance(datos, dict):
        elementos = (
            datos.get("data")
            or datos.get("content")
            or datos.get("folders")
            or datos.get("testcase-folders")
            or []
        )
    else:
        elementos = []

    id_map = {}
    for e in elementos:
        if not isinstance(e, dict):
            continue
        nombre = (e.get("folderName") or e.get("name") or "").strip()
        eid = e.get("id")
        parent = e.get("parentId")
        if nombre and eid is not None:
            id_map[eid] = {"name": nombre, "parentId": parent}

    def _ruta_completa(eid, visitados=None):
        if visitados is None:
            visitados = set()
        if eid not in id_map or eid in visitados:
            return ""
        visitados.add(eid)
        info = id_map[eid]
        parent = info["parentId"]
        if parent is None or parent == FOLDER_ID_RAIZ or parent not in id_map:
            return info["name"]
        padre_ruta = _ruta_completa(parent, visitados)
        return (padre_ruta + "/" + info["name"]) if padre_ruta else info["name"]

    resultado = {}
    for eid in id_map:
        ruta = _ruta_completa(eid)
        if ruta:
            resultado[ruta.lower()] = eid

    return resultado


def _crear_carpeta(sesion, config, nombre_carpeta, parent_id=FOLDER_ID_RAIZ):
    """
    Crea una carpeta en QMetry bajo el padre indicado.
    Devuelve el id de la carpeta creada.
    Lanza RuntimeError si la API responde con error.
    """
    url = (
        config["jira_url"]
        + "/rest/qtm4j/ui/latest/projects/"
        + str(config["project_id"])
        + "/testcase-folders"
    )
    payload = {
        "folderName": nombre_carpeta.strip(),
        "parentId": parent_id,
    }
    resp = sesion.post(url, json=payload, timeout=30)
    if resp.ok:
        datos = resp.json()
        folder_id = datos.get("id") or datos.get("folderId")
        if folder_id is not None:
            return folder_id
        raise RuntimeError("Carpeta creada pero sin 'id' en respuesta: " + str(datos))
    raise RuntimeError("HTTP " + str(resp.status_code) + ": " + resp.text[:300])


def _resolver_folder_id(sesion, config, valor_celda, cache_folders):
    """
    Resuelve el folderId para un valor de celda que puede ser:
      - vacio / None  -> FOLDER_ID_RAIZ
      - nombre simple -> "TX-01 Retiro OTP"
      - ruta anidada  -> "TX-01 Retiro OTP/Happy Path/Funcional"

    Crea cada nivel que no exista, usando el padre correcto.
    Actualiza cache_folders en el proceso.
    Nunca interrumpe la subida: si falla, devuelve FOLDER_ID_RAIZ + aviso.
    """
    nombre_limpio = str(valor_celda).strip() if valor_celda is not None else ""
    if not nombre_limpio:
        return FOLDER_ID_RAIZ

    segmentos = [s.strip() for s in nombre_limpio.split("/") if s.strip()]
    if not segmentos:
        return FOLDER_ID_RAIZ

    parent_id = FOLDER_ID_RAIZ
    ruta_acumulada = ""

    for segmento in segmentos:
        ruta_acumulada = (ruta_acumulada + "/" + segmento).lstrip("/")
        clave = ruta_acumulada.lower()

        if clave in cache_folders:
            parent_id = cache_folders[clave]
            continue

        try:
            folder_id = _crear_carpeta(sesion, config, segmento, parent_id)
            cache_folders[clave] = folder_id
            parent_id = folder_id
            print("  [Carpeta] Creada: '" + ruta_acumulada + "' -> id=" + str(folder_id))
        except RuntimeError as err:
            texto_err = str(err).lower()
            if any(x in texto_err for x in ("409", "already exist", "duplicate", "exists")):
                print("  [Carpeta] '" + ruta_acumulada + "' ya existe, recargando catalogo...")
                cache_folders.update(_cargar_carpetas_existentes(sesion, config))
                if clave in cache_folders:
                    parent_id = cache_folders[clave]
                else:
                    print(
                        "  [AVISO] No se pudo resolver '"
                        + ruta_acumulada
                        + "' tras recarga. El caso ira a la raiz."
                    )
                    return FOLDER_ID_RAIZ
            else:
                print(
                    "  [AVISO] Error creando carpeta '"
                    + ruta_acumulada
                    + "': "
                    + str(err)
                    + ". El caso ira a la raiz."
                )
                return FOLDER_ID_RAIZ

    return parent_id


# ---------------------------------------------------------------------------
# Payload y creacion del Test Case
# ---------------------------------------------------------------------------

def _payload_test_case(fila, cols, config, folder_id, priority_id, status_id):
    def _val(nombre):
        col = cols.get(nombre)
        if col is None:
            return ""
        celda = fila[col - 1]
        return str(celda.value).strip() if celda.value is not None else ""

    payload = {
        "summary": _val("Resumen"),
        "description": _val("Descripcion"),
        "precondition": _val("Escenario"),
        "projectId": config["project_id"],
        "priority": priority_id,
        "status": status_id,
        "steps": [
            {
                "stepDetails": _val("Accion"),
                "testData": _val("Datos"),
                "expectedResult": _val("Resultado Esperado"),
            }
        ],
    }
    if folder_id != FOLDER_ID_RAIZ:
        payload["folderId"] = folder_id
    return payload


def _crear_test_case(sesion, config, payload):
    url = config["jira_url"] + "/rest/qtm4j/ui/latest/testcases"
    resp = sesion.post(url, json=payload, timeout=30)
    if resp.ok:
        datos = resp.json()
        clave = datos.get("key") or datos.get("id") or str(datos)
        return clave
    raise RuntimeError("HTTP " + str(resp.status_code) + ": " + resp.text[:400])


# ---------------------------------------------------------------------------
# Flujo principal
# ---------------------------------------------------------------------------

def subir_casos_a_qmetry(ruta_excel, fila_inicio=2):
    """
    Lee el Excel y sube cada fila como Test Case a QMetry.
    Imprime un resumen con las claves creadas y las filas fallidas.
    """
    config = _cargar_configuracion()

    sesion = requests.Session()
    sesion.auth = (config["username"], config["token"])
    sesion.headers.update({"Content-Type": "application/json"})

    if not os.path.exists(ruta_excel):
        raise FileNotFoundError("No se encontro el archivo: " + ruta_excel)

    wb = openpyxl.load_workbook(ruta_excel, data_only=True)
    hoja = wb.active
    cols = _indice_columnas(hoja)

    print("  [Catalogo] Cargando prioridades y estados desde QMetry...")
    priority_id = _cargar_prioridad_id(sesion, config)
    status_id = _cargar_estado_id(sesion, config)

    usa_folders = COLUMNA_FOLDERS in cols
    cache_folders = {}
    if usa_folders:
        print("  [Carpetas] Cargando carpetas existentes en QMetry...")
        cache_folders = _cargar_carpetas_existentes(sesion, config)
        print("  [Carpetas] " + str(len(cache_folders)) + " ruta(s) encontrada(s).")

    creados = []
    fallidos = []
    total_filas = hoja.max_row - 1

    print("\nSubiendo " + str(total_filas) + " caso(s) desde fila " + str(fila_inicio) + "...\n")

    for num_fila in range(fila_inicio, hoja.max_row + 1):
        fila = hoja[num_fila]

        if all(c.value is None for c in fila):
            continue

        folder_id = FOLDER_ID_RAIZ
        if usa_folders:
            col_folder = cols[COLUMNA_FOLDERS]
            valor_folder = fila[col_folder - 1].value
            folder_id = _resolver_folder_id(sesion, config, valor_folder, cache_folders)

        payload = _payload_test_case(fila, cols, config, folder_id, priority_id, status_id)

        if not payload.get("summary"):
            print("  [SKIP] Fila " + str(num_fila) + ": Resumen vacio.")
            continue

        try:
            clave = _crear_test_case(sesion, config, payload)
            creados.append((num_fila, clave))
            print("  [OK] Fila " + str(num_fila) + " -> " + str(clave))
        except RuntimeError as err:
            fallidos.append((num_fila, payload.get("summary", ""), str(err)))
            print("  [ERROR] Fila " + str(num_fila) + ": " + str(err))

    separador = "-" * 60
    print("\n" + separador)
    print("Creados : " + str(len(creados)))
    for num_fila, clave in creados:
        print("  fila " + str(num_fila) + " -> " + str(clave))
    print("Fallidos: " + str(len(fallidos)))
    for num_fila, resumen, detalle in fallidos:
        print("  fila " + str(num_fila) + " [" + resumen + "] -> " + detalle)
    print(separador)


# ---------------------------------------------------------------------------
# Punto de entrada CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python jira_uploader.py \"casos de prueba/suite.xlsx\" [fila_inicio]")
        sys.exit(1)
    ruta = sys.argv[1]
    inicio = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    subir_casos_a_qmetry(ruta, inicio)
