import ast
from pathlib import Path

source = Path(r"c:\Users\jherrodr\Downloads\EverestAutomatizacion\demo-servicios-axet-plugin\casos de prueba\generar_casos_everest.py")
module = ast.parse(source.read_text(encoding="utf-8"))
value = None
for node in module.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CASOS_POR_HU" for t in node.targets):
        value = ast.literal_eval(node.value)
        break
if value is None:
    raise RuntimeError("CASOS_POR_HU not found")

excluded = ("biometr", "huella", "dactilar", "accesibilidad", "legibilidad", "contraste", "lector de pantalla")
rows = []
for hu, spec in value.items():
    for index, case in enumerate(spec["cases"], 1):
        text = " ".join(str(v) for v in case.values()).lower()
        if case.get("Tipo de test") != "Funcional" or any(term in text for term in excluded):
            continue
        rows.append((hu, index, case))

out = Path(r"c:\Users\jherrodr\Downloads\EverestAutomatizacion\demo-servicios-axet-plugin\pending_functional_cases.txt")
with out.open("w", encoding="utf-8") as f:
    f.write(f"TOTAL_EXCLUDED_BIOMETRIC_ACCESSIBILITY={len(rows)}\n")
    for hu, index, case in rows:
        f.write(f"\n=== {hu} CASE_INDEX={index} ===\n")
        for key in ("Resumen", "Descripcion", "Escenario", "Accion", "Datos", "Resultado Esperado", "Prioridad"):
            f.write(f"{key}: {case.get(key, '')}\n")
print(f"WROTE {out} COUNT={len(rows)}")
