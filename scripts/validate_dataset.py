# scripts/validate_dataset.py
import json, os, openpyxl

EXCEL_PATH = os.path.join("data", "JSON Generator", "dataWASHES-data.xlsx")
PAPERS_PATH = os.path.join("data", "papers.json")
EDITIONS_PATH = os.path.join("data", "editions.json")

def validate():
    print("🔍 Executando validação de integridade dos arquivos...")
    errors = []

    # 1. Checa se o Excel tem 22 colunas
    wb = openpyxl.load_workbook(EXCEL_PATH)
    ws = wb.active
    if len([cell.value for cell in ws[1]]) != 22:
        errors.append("Planilha Excel com número incorreto de colunas.")

    # 2. Checa se os IDs de papers.json batem com editions.json
    with open(PAPERS_PATH, "r", encoding="utf-8") as f:
        papers = json.load(f)
    with open(EDITIONS_PATH, "r", encoding="utf-8") as f:
        editions = json.load(f)

    paper_ids = {p["Paper_id"] for p in papers}
    edition_paper_ids = {pid for e in editions for pid in e.get("Papers", [])}

    orphans = paper_ids - edition_paper_ids
    if orphans:
        errors.append(f"{len(orphans)} artigos em papers.json não estão em nenhuma edição!")

    if errors:
        print("\n❌ ERROS ENCONTRADOS:", errors)
        exit(1)
    else:
        print("✅ Tudo perfeito! Planilha e JSONs estão 100% alinhados.")

if __name__ == "__main__":
    validate()