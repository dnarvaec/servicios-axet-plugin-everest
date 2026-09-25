from pathlib import Path
import unicodedata

import openpyxl


ROOT = Path(__file__).resolve().parent.parent
EXCEL_PATH = ROOT / "casos de prueba" / "casos everest.xlsx"
OUTPUT_PATH = ROOT / "casos de prueba" / "casos_funcionales_no_biometricos_ni_accesibilidad.md"


def normalize(text):
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def main():
    workbook = openpyxl.load_workbook(EXCEL_PATH, read_only=True, data_only=True)
    worksheet = workbook.active
    headers = {str(cell.value).strip(): index for index, cell in enumerate(worksheet[1]) if cell.value}

    def value(row, column_name):
        index = headers.get(column_name)
        if index is None:
            return ""
        return str(row[index].value or "").strip()

    excluded_terms = ("biometric", "biometr", "accesibilidad", "accesible", "wcag")
    rows = []
    for row in worksheet.iter_rows(min_row=2):
        test_type = value(row, "TestCase Type")
        searchable_text = " ".join(
            value(row, column_name)
            for column_name in ("Summary", "Description", "Labels", "Expected Result")
        )
        normalized = normalize(searchable_text)
        if test_type == "Funcional" and not any(term in normalized for term in excluded_terms):
            rows.append((value(row, "Issue Key"), value(row, "Story Linkages"), value(row, "Summary")))

    lines = [
        "# Casos funcionales sin biometricos ni accesibilidad",
        "",
        f"Total: {len(rows)}",
        "",
        "| Issue Key | HU | Summary |",
        "|---|---|---|",
    ]
    for issue_key, story, summary in rows:
        safe_summary = summary.replace("|", "\\|")
        lines.append(f"| {issue_key} | {story} | {safe_summary} |")

    OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Total: {len(rows)}")
    print(f"Archivo: {OUTPUT_PATH}")
    for issue_key, story, summary in rows:
        print(f"{issue_key}\t{story}\t{summary}")


if __name__ == "__main__":
    main()