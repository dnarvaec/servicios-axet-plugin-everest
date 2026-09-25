from pathlib import Path
import unicodedata

import openpyxl


ROOT = Path(__file__).resolve().parent.parent
EXCEL = ROOT / "casos de prueba" / "casos everest.xlsx"
OUTPUT = ROOT / "casos de prueba" / "reporte_hu201_203.md"


def normalize(text):
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


workbook = openpyxl.load_workbook(EXCEL, read_only=True, data_only=True)
worksheet = workbook.active
headers = {str(cell.value).strip(): index for index, cell in enumerate(worksheet[1]) if cell.value}


def value(row, name):
    index = headers.get(name)
    return str(row[index].value or "").strip() if index is not None else ""


summary = {}
for row in worksheet.iter_rows(min_row=2):
    story = value(row, "Story Linkages")
    if not (story.startswith("HU-201") or story.startswith("HU-203")):
        continue
    item = summary.setdefault(story, {"funcionales": 0, "biometricos": [], "accesibilidad": []})
    issue = value(row, "Issue Key")
    case_summary = value(row, "Summary")
    test_type = value(row, "TestCase Type")
    searchable = normalize(" ".join(value(row, name) for name in ("Summary", "Description", "Expected Result")))
    if test_type == "Funcional":
        item["funcionales"] += 1
        if "biometr" in searchable or "biometric" in searchable:
            item["biometricos"].append((issue, case_summary))
    elif test_type == "Accesibilidad":
        item["accesibilidad"].append((issue, case_summary))


lines = [
    "# Relacion HU-201 y HU-203",
    "",
    "| HU | Funcionales total | Funcionales sin biometricos | Biometricos | Accesibilidad |",
    "|---|---:|---:|---:|---:|",
]
for story in sorted(summary):
    item = summary[story]
    biometric_count = len(item["biometricos"])
    accessibility_count = len(item["accesibilidad"])
    functional_without_biometric = item["funcionales"] - biometric_count
    lines.append(
        "| {} | {} | {} | {} | {} |".format(
            story,
            item["funcionales"],
            functional_without_biometric,
            biometric_count,
            accessibility_count,
        )
    )

lines.append("")
lines.append("## Biometricos")
for story in sorted(summary):
    rows = summary[story]["biometricos"]
    lines.append("")
    lines.append("### {} ({})".format(story, len(rows)))
    for issue, case_summary in rows:
        lines.append("- {}: {}".format(issue, case_summary))

lines.append("")
lines.append("## Accesibilidad")
for story in sorted(summary):
    rows = summary[story]["accesibilidad"]
    lines.append("")
    lines.append("### {} ({})".format(story, len(rows)))
    for issue, case_summary in rows:
        lines.append("- {}: {}".format(issue, case_summary))

OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(OUTPUT)