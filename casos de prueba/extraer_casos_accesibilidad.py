from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import openpyxl


ROOT = Path(__file__).resolve().parent.parent
EXCEL = ROOT / "casos de prueba" / "casos everest.xlsx"
ATTACHED_HTML = Path(r"c:\Users\jherrodr\Downloads\mock-test-ref (1).html")
WORKSPACE_HTML = ROOT / "tests" / "automatizacion api" / "serenity rest" / "src" / "test" / "resources" / "colecciones" / "mock-test-ref.html"
OUT_DIR = ROOT / "artifacts" / "a11y" / "casos-everest-login"
OUT_JSON = OUT_DIR / "casos_accesibilidad_extraidos.json"
OUT_MD = OUT_DIR / "casos_accesibilidad_extraidos.md"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFD", value.lower())
    return "".join(ch for ch in value if unicodedata.category(ch) != "Mn")


def cell(row, headers, name: str) -> str:
    index = headers.get(name)
    return str(row[index].value or "").strip() if index is not None else ""


def extract_pools(html_path: Path) -> list[dict[str, str]]:
    if not html_path.exists():
        return []
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    cards = re.findall(r'<div class="pool-card">(.*?)</div>', html, flags=re.S)
    pools = []
    for card in cards:
        badge = re.search(r'<span class="pool-badge [^"]+">(.*?)</span>', card, flags=re.S)
        doc_num = re.search(r'<span class="doc-num">(.*?)</span>', card, flags=re.S)
        doc_type = re.search(r'<span class="doc-type">(.*?)</span>', card, flags=re.S)
        doc_name = re.search(r'<span class="doc-name">(.*?)</span>', card, flags=re.S)
        products = re.search(r'<span class="doc-products">(.*?)</span>', card, flags=re.S)
        if doc_num and doc_type:
            pools.append({
                "pool": re.sub(r"\s+", " ", badge.group(1)).strip() if badge else "",
                "tipoDocumento": re.sub(r"\s+", " ", doc_type.group(1)).strip(),
                "numeroDocumento": re.sub(r"\s+", " ", doc_num.group(1)).strip(),
                "nombre": re.sub(r"\s+", " ", doc_name.group(1)).strip() if doc_name else "",
                "productos": re.sub(r"\s+", " ", products.group(1)).strip() if products else "",
            })
    return pools


def main() -> None:
    workbook = openpyxl.load_workbook(EXCEL, read_only=True, data_only=True)
    worksheet = workbook.active
    headers = {str(value.value).strip(): index for index, value in enumerate(worksheet[1]) if value.value}
    cases = []
    for row in worksheet.iter_rows(min_row=2):
        labels = cell(row, headers, "Labels")
        if "accesibilidad" not in normalize(labels):
            continue
        cases.append({
            "issueKey": cell(row, headers, "Issue Key"),
            "summary": cell(row, headers, "Summary"),
            "description": cell(row, headers, "Description"),
            "precondition": cell(row, headers, "Precondition"),
            "steps": cell(row, headers, "Step Summary"),
            "testData": cell(row, headers, "Test Data"),
            "expectedResult": cell(row, headers, "Expected Result"),
            "priority": cell(row, headers, "Priority"),
            "labels": labels,
            "storyLinkages": cell(row, headers, "Story Linkages"),
            "component": cell(row, headers, "Components"),
        })

    html_path = ATTACHED_HTML if ATTACHED_HTML.exists() else WORKSPACE_HTML
    payload = {
        "sourceExcel": str(EXCEL),
        "htmlDataSource": str(html_path),
        "totalAccessibilityCases": len(cases),
        "documentPools": extract_pools(html_path),
        "cases": cases,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Casos de accesibilidad extraidos",
        "",
        f"Total: {len(cases)}",
        "",
        "## Datos de prueba",
        "",
        "| Pool | Tipo | Documento | Nombre | Productos |",
        "|---|---|---|---|---|",
    ]
    for pool in payload["documentPools"]:
        lines.append("| {pool} | {tipoDocumento} | {numeroDocumento} | {nombre} | {productos} |".format(**pool))
    lines.extend(["", "## Casos", ""])
    for case in cases:
        lines.extend([
            f"### {case['issueKey']} - {case['storyLinkages']}",
            f"**Summary:** {case['summary']}",
            f"**Expected:** {case['expectedResult']}",
            f"**Labels:** {case['labels']}",
            "",
        ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"TOTAL={len(cases)}")


if __name__ == "__main__":
    main()