import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import openpyxl

# --- 1. CARREGAR AMBIENTE (.env) ---
ENV_PATH = ".env"
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY", "")

EXCEL_PATH = os.path.join("data", "JSON Generator", "dataWASHES-data.xlsx")
EDITIONS_PATH = os.path.join("data", "editions.json")
PAPERS_PATH = os.path.join("data", "papers.json")
ARCHIVE_URL = "https://sol.sbc.org.br/index.php/washes/issue/archive"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DATA_DIR = os.path.join(BASE_DIR, "data")
JSON_GENERATOR_DIR = os.path.join(DATA_DIR, "JSON Generator")

KNOWN_STATES = {
    "UFC": "CE", "UFCA": "CE", "UECE": "CE", "IFCE": "CE", "UNIFOR": "CE",
    "UFRJ": "RJ", "UNIRIO": "RJ", "UFF": "RJ", "UERJ": "RJ",
    "UFPA": "PA", "UFRA": "PA", "UFMG": "MG", "UFV": "MG", "UFLA": "MG",
    "USP": "SP", "UFSCar": "SP", "UNICAMP": "SP", "UNIFESP": "SP", "SiDi": "SP", "Zup": "SP",
    "UTFPR": "PR", "UFPR": "PR", "UENP": "PR", "UEM": "PR",
    "UFPE": "PE", "UPE": "PE", "UFRPE": "PE", "Cesar School": "PE",
    "UFPB": "PB", "UFMS": "MS", "UFMT": "MT", "UFAM": "AM",
    "UFG": "GO", "UnB": "DF", "UFAC": "AC", "UFRN": "RN", "UFBA": "BA"
}

SYSTEM_PROMPT = """Você é um especialista em Metodologia de Pesquisa em Engenharia de Software.
Sua tarefa é analisar o Título, Abstract, Resumo e Palavras-chave de um artigo acadêmico e classificá-lo ESTRITAMENTE conforme a taxonomia abaixo.

Opções permitidas por campo:
1. "abordagem": Escolha entre ["Qualitativa", "Quantitativa", "Mista"]
2. "objetivos": Escolha entre ["Exploratória", "Descritiva", "Explicativa"]
3. "procedimentos": Escolha entre ["Estudo de caso", "Survey", "Experimento", "Revisão de literatura", "Pesquisa documental", "Pesquisa-Ação", "Experimental"]
4. "coleta": Escolha entre ["Questionário", "Entrevista", "Observação", "Análise documental", "Coleta automatizada", "Experimento", "Questionário e Observação", "Observação e Entrevista"]
5. "quantitativa": Escolha entre ["Estatística descritiva", "Teste de hipótese", "#"]
6. "qualitativa": Escolha entre ["Análise de conteúdo", "Análise temática", "Análise narrativa", "Análise comparativa", "Teoria fundamentada", "Análise de cenário", "Análise de discurso", "#"]

Responda APENAS um objeto JSON válido contendo exatamente essas 6 chaves."""

def classify_paper_with_groq(title, abstract_en, resumo_pt, keywords, retries=3):
    if not GROQ_API_KEY:
        print("   ⚠️ GROQ_API_KEY não configurada no .env.")
        return None

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    user_prompt = f"Título: {title}\nAbstract: {abstract_en}\nResumo: {resumo_pt}\nKeywords: {keywords}"

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1
    }

    for attempt in range(1, retries + 1):
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=30)
            if res.status_code == 200:
                return json.loads(res.json()["choices"][0]["message"]["content"])
            elif res.status_code == 429:
                print(f"   ⏳ Rate limit do Groq. Aguardando 5s (tentativa {attempt}/{retries})...")
                time.sleep(5)
            else:
                return None
        except Exception:
            time.sleep(2)

    return None

def get_citation_from_scholar(title, retries=2):
    if not SCRAPER_API_KEY:
        return "#"

    scholar_url = f"https://scholar.google.com/scholar?q={urllib.parse.quote(title)}&hl=pt-BR"
    payload = {
        'api_key': SCRAPER_API_KEY,
        'url': scholar_url,
        'country_code': 'us',
        'render': 'true'
    }

    for attempt in range(1, retries + 1):
        try:
            res = requests.get('https://api.scraperapi.com', params=payload, timeout=45)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                cited_by = soup.find("a", string=lambda t: t and ("Citado por" in t or "Cited by" in t))
                return cited_by.text.strip() if cited_by else "#"
            elif res.status_code in (401, 403):
                print("   ❌ Chave ScraperAPI inválida ou limite de créditos atingido.")
                return None
            elif res.status_code == 429:
                print(f"   ⏳ Rate limit da ScraperAPI. Aguardando 5s (tentativa {attempt}/{retries})...")
                time.sleep(5)
            else:
                print(f"   ⚠️ Resposta inesperada da ScraperAPI: status {res.status_code}.")
        except Exception as exc:
            print(f"   ⚠️ Erro de rede na ScraperAPI: {exc}. Retentando em 2s...")
            time.sleep(2)
    return None

def get_existing_years():
    if not os.path.exists(EDITIONS_PATH):
        return set()
    with open(EDITIONS_PATH, "r", encoding="utf-8") as f:
        editions = json.load(f)
    return {e["Year"] for e in editions}

def scrape_archive_issues():
    res = requests.get(ARCHIVE_URL, timeout=30)
    soup = BeautifulSoup(res.text, "html.parser")
    issues = []
    for summary in soup.find_all("div", class_="obj_issue_summary"):
        title_a = summary.find("a", class_="title")
        if not title_a:
            continue
        title_text = title_a.text.strip()
        issue_url = title_a["href"]
        year_match = re.search(r"^(\d{4})", title_text)
        if year_match:
            year = int(year_match.group(1))
            issues.append({"year": year, "title": title_text, "url": issue_url})
    return sorted(issues, key=lambda x: x["year"])

def scrape_article(article_url):
    res = requests.get(article_url, timeout=30)
    soup = BeautifulSoup(res.text, "html.parser")

    title_el = soup.find("h1", class_="page_title")
    title = title_el.text.strip() if title_el else ""

    abstract_en = "#"
    resumo_pt = "#"
    for item in soup.find_all("div", class_="item abstract"):
        txt = item.text.strip()
        if "Abstract" in txt or re.search(r"^[a-zA-Z]", txt[:20]):
            abstract_en = txt.replace("Abstract", "").strip()
        else:
            resumo_pt = txt.replace("Resumo", "").strip()

    # Captura precisa de Autores e Instituições via Meta Tags OJS
    authors = []
    author_names = [m["content"].strip() for m in soup.find_all("meta", attrs={"name": "citation_author"})]
    author_insts = [m["content"].strip() for m in soup.find_all("meta", attrs={"name": "citation_author_institution"})]

    for i, name in enumerate(author_names):
        inst = author_insts[i] if i < len(author_insts) else "#"
        acronym = inst.split("-")[-1].strip() if "-" in inst else inst
        state = KNOWN_STATES.get(acronym, "#")
        for k, v in KNOWN_STATES.items():
            if k.lower() in inst.lower():
                state = v
                break
        authors.append({"name": name, "inst": inst or "#", "acronym": acronym or "#", "state": state})

    if not authors:
        authors = [{"name": "#", "inst": "#", "acronym": "#", "state": "#"}]

    keywords = [m["content"].strip() for m in soup.find_all("meta", attrs={"name": "citation_keywords"}) if m.get("content")]
    keywords_str = ", ".join(keywords) if keywords else "#"

    return {
        "title": title,
        "abstract_en": abstract_en,
        "resumo_pt": resumo_pt,
        "keywords": keywords_str,
        "authors": authors,
        "url": article_url
    }

def regenerate_dataset_files() -> None:
    """
    Rebuild ``authors.json`` and ``papers.json`` from the updated spreadsheet.

    The generators are executed with the working directory set to the JSON
    Generator folder (they read ``dataWASHES-data.xlsx`` and write relative to
    the current directory). The generated files are then moved to ``data/``,
    which is the folder consumed by the API.
    """
    for script in ("authorsJSON.py", "papersJSON.py"):
        subprocess.run([sys.executable, script], cwd=JSON_GENERATOR_DIR, check=True)

    for json_name in ("authors.json", "papers.json"):
        generated = os.path.join(JSON_GENERATOR_DIR, json_name)
        destination = os.path.join(DATA_DIR, json_name)
        if os.path.exists(generated):
            shutil.move(generated, destination)


def sync():
    if not os.path.exists(EXCEL_PATH):
        print(f"❌ Planilha principal não encontrada em: {EXCEL_PATH}")
        return

    existing_years = get_existing_years()
    print(f"📌 Anos cadastrados atualmente: {sorted(list(existing_years))}")

    all_issues = scrape_archive_issues()
    missing_issues = [i for i in all_issues if i["year"] not in existing_years]

    if not missing_issues:
        print("🎉 Nenhuma nova edição encontrada no SOL SBC. Dataset 100% atualizado!")
        return

    print(f"\n✨ Encontradas {len(missing_issues)} novas edições no SOL SBC!")

    wb = openpyxl.load_workbook(EXCEL_PATH)
    ws = wb.active

    for issue in missing_issues:
        year = issue["year"]
        print(f"\n🚀 Ingerindo WASHES {year} ({issue['url']})...")

        res = requests.get(issue["url"], timeout=30)
        soup = BeautifulSoup(res.text, "html.parser")

        count = 0
        for sec_div in soup.find_all("div", class_="section"):
            h2 = sec_div.find("h2")
            sec_title = h2.text.strip() if h2 else "Geral"
            paper_type = "Short paper" if "curto" in sec_title.lower() else "Full paper"

            for summary in sec_div.find_all("div", class_="obj_article_summary"):
                count += 1
                a_tag = summary.find("div", class_="title").find("a")
                art_url = a_tag["href"]

                print(f"\n📄 [{count}] Processando: '{a_tag.text.strip()[:45]}...'")
                art_meta = scrape_article(art_url)

                # Classificação por IA (Groq)
                print("   🤖 Classificando metodologia via Groq (Llama 3 70B)...")
                method = classify_paper_with_groq(art_meta["title"], art_meta["abstract_en"], art_meta["resumo_pt"], art_meta["keywords"])
                time.sleep(2.5)

                if not method:
                    method = {"abordagem": "#", "objetivos": "#", "procedimentos": "#", "coleta": "#", "quantitativa": "#", "qualitativa": "#"}

                # Mineração de Citações
                print("   🔍 Checando citações no Google Scholar...")
                citation = get_citation_from_scholar(art_meta["title"])
                if citation is None:
                    print("   ⏩ Citação não obtida por erro da ScraperAPI; registrando placeholder '#'.")
                    citation = "#"

                # Gravar no Excel
                edition_num = len(get_existing_years()) + 1
                first_a = art_meta["authors"][0]
                row_1 = [
                    edition_num, year, art_meta["title"], "pt",
                    first_a["name"], first_a["inst"], first_a["acronym"], first_a["state"],
                    art_meta["abstract_en"], art_meta["resumo_pt"], art_meta["keywords"], paper_type, art_url,
                    "#", citation, today_str,
                    method.get("abordagem", "#"), method.get("objetivos", "#"), method.get("procedimentos", "#"),
                    method.get("coleta", "#"), method.get("quantitativa", "#"), method.get("qualitativa", "#")
                ]
                row_1[15] = datetime.now()
                ws.append(row_1)

                for co in art_meta["authors"][1:]:
                    ws.append([
                        None, None, None, None,
                        co["name"], co["inst"], co["acronym"], co["state"],
                        None, None, None, None, None, None, None, None, None, None, None, None, None, None
                    ])

        print(f"✅ Edição {year} gravada na planilha.")

    wb.save(EXCEL_PATH)
    print("\n🔄 Atualizando 'authors.json' e 'papers.json'...")
    regenerate_dataset_files()
    print("\n📌 Sincronizando 'editions.json' com os papers recém-gerados...")
    for issue in missing_issues:
        update_editions_json(issue["year"], issue["url"])
    print("\n🎉 Sincronização concluída com sucesso na planilha principal!")

def update_editions_json(year, proceedings_url):
    with open(EDITIONS_PATH, "r", encoding="utf-8") as f:
        editions = json.load(f)
    with open(PAPERS_PATH, "r", encoding="utf-8") as f:
        papers = json.load(f)

    new_paper_ids = [p["Paper_id"] for p in papers if p.get("Year") == year]
    last_edition_id = max([e["Edition_id"] for e in editions]) if editions else -1

    new_edition = {
        "Year": year,
        "Edition_id": last_edition_id + 1,
        "Title": f"Anais da Edição de {year} do Workshop sobre Aspectos Sociais, Humanos e Econômicos de Software",
        "Location": "#",
        "Date": datetime.now().strftime("%d/%m/%Y"),
        "Proceedings": proceedings_url,
        "Chairs": [],
        "Papers": new_paper_ids
    }
    editions.append(new_edition)

    with open(EDITIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(editions, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    sync()