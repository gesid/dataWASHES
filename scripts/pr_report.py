"""Geração do relatório de auditoria (Markdown) dos Pull Requests do bot de sync.

Os scripts ``sync_washes_dataset.py`` e ``miner_citations.py`` rodam em
processos separados e ainda assim precisam contribuir para um único corpo de
PR. Para isso, ambos registram seus eventos neste módulo, que persiste o
estado em disco e, ao final, renderiza ``pr_summary.md``.

Fluxo de uso no CI:

    python scripts/pr_report.py --init    # zera o estado e guarda snapshot
    python scripts/sync_washes_dataset.py # registra artigos novos
    python scripts/miner_citations.py      # registra citações atualizadas
    python scripts/pr_report.py --render   # escreve pr_summary.md
"""

import argparse
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DATA_DIR = os.path.join(ROOT, "data")
JSON_GENERATOR_DIR = os.path.join(DATA_DIR, "JSON Generator")

STATE_PATH = os.path.join(ROOT, ".pr_summary_state.json")
SUMMARY_PATH = os.path.join(ROOT, "pr_summary.md")

PAPERS_FILE = os.path.join(DATA_DIR, "papers.json")
AUTHORS_FILE = os.path.join(DATA_DIR, "authors.json")

NO_CHANGE_NOTE = "Nenhuma alteração de citações ou artigos nesta rodada"

CITATION_COUNT_RE = re.compile(r"^Citado por\s+(\d+)\s*$", re.IGNORECASE)
BLANK_MARKER = "#"


def _empty_state():
    return {
        "new_papers": [],
        "citation_changes": [],
        "notes": [],
    }


def load_state():
    if not os.path.exists(STATE_PATH):
        return _empty_state()
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as handle:
            state = json.load(handle)
    except (json.JSONDecodeError, OSError):
        return _empty_state()
    for key, default in _empty_state().items():
        state.setdefault(key, default)
    return state


def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)


def record_new_paper(title, year, authors=None, edition=None):
    """Registra um artigo recém-ingerido da SOL SBC."""
    state = load_state()
    state["new_papers"].append(
        {
            "title": str(title or "").strip(),
            "year": year,
            "authors": list(authors or []),
            "edition": edition,
        }
    )
    save_state(state)


def record_citation_change(paper_id, title, old_value, new_value):
    """Registra a atualização de citações de um artigo já existente."""
    state = load_state()
    state["citation_changes"].append(
        {
            "paper_id": paper_id,
            "title": str(title or "").strip(),
            "old": "" if old_value is None else str(old_value).strip(),
            "new": "" if new_value is None else str(new_value).strip(),
        }
    )
    save_state(state)


def record_note(text):
    state = load_state()
    state["notes"].append(str(text).strip())
    save_state(state)


def parse_citation_count(value):
    """Extrai a contagem numérica de citações, ou None quando não aplicável.

    A coluna ``Citações`` é heterogênea na base: convive placeholders ``#``,
    rótulos ``Citado por N`` e listas de referências APA coladas manualmente.
    Só o formato ``Citado por N`` carrega uma contagem aproveitável.
    """
    if value is None:
        return None
    text = str(value).strip()
    if not text or text == BLANK_MARKER:
        return None
    match = CITATION_COUNT_RE.match(text)
    if match:
        return int(match.group(1))
    if text.isdigit():
        return int(text)
    return None


def _read_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def snapshot_dataset():
    """Guarda cópia dos JSONs de produção para comparação posterior."""
    state = load_state()
    snapshot = {}
    for key, path in (("papers", PAPERS_FILE), ("authors", AUTHORS_FILE)):
        payload = _read_json(path)
        if payload is not None:
            snapshot[key] = payload
    state["snapshot"] = snapshot
    save_state(state)


def _cell(value):
    """Normaliza um valor de citação para exibição no relatório."""
    if value is None:
        return ""
    text = str(value).strip()
    return text if text else BLANK_MARKER


def _escape(text, limit=None):
    """Escapa texto para uma célula de tabela Markdown em uma só linha."""
    flat = " ".join(str(text or "").split())
    flat = flat.replace("|", "\\|")
    if limit and len(flat) > limit:
        flat = flat[: limit - 1].rstrip() + "…"
    return flat or BLANK_MARKER


def _diff_dataset(state):
    """Compara o snapshot com o estado atual dos JSONs de produção.

    Detecta papers inseridos, removidos e renumerados (remapeados), já que a
    remoção de um artigo desloca o ``Paper_id`` de todos os seguintes. Sem
    snapshot não há base de comparação, e nada é reportado como inserido.
    """
    snapshot = state.get("snapshot") or {}
    current_papers = _read_json(PAPERS_FILE) or []
    after = {p["Title"]: p for p in current_papers}

    snap_papers = snapshot.get("papers")
    if snap_papers is None:
        return [], [], after, []

    before = {p["Title"]: p for p in snap_papers}
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    remapped = []
    for title in sorted(set(before) & set(after)):
        old_id = before[title].get("Paper_id")
        new_id = after[title].get("Paper_id")
        if old_id != new_id:
            remapped.append(
                {
                    "title": title,
                    "year": after[title].get("Year"),
                    "old_id": old_id,
                    "new_id": new_id,
                }
            )
    return removed, remapped, after, added


def _author_names(paper):
    names = []
    for author in paper.get("Authors") or []:
        name = str(author.get("Name", "")).strip()
        if name and name != BLANK_MARKER:
            names.append(name)
    return names


def _render_new_papers(state, added, current_papers):
    """Seções de artigos novos: eventos registrados + diff contra o snapshot.

    ``added`` vem do contraste snapshot/atual. O título nunca pode ser
    derivado do dataset isolado, senão uma rodada sem snapshot listaria o
    acervo inteiro como inserido.
    """
    lines = ["## 🆕 Artigos inseridos da SOL SBC", ""]

    by_title = {p["Title"]: p for p in current_papers}
    recorded = {r.get("title"): r for r in state["new_papers"]}

    entries = []
    for title in added:
        paper = by_title.get(title) or {}
        event = recorded.get(title) or {}
        entries.append(
            {
                "title": title,
                "year": event.get("year") or paper.get("Year"),
                "authors": event.get("authors") or _author_names(paper),
            }
        )

    entries.sort(key=lambda item: (item.get("year") or 0, item["title"]))

    if not entries:
        lines.append("Nenhum artigo novo foi incorporado nesta rodada.")
        lines.append("")
        return lines

    lines.append("| Ano | Título | Autores |")
    lines.append("| :--: | ----- | ------ |")
    for entry in entries:
        authors = ", ".join(entry["authors"]) or BLANK_MARKER
        lines.append(
            "| %s | %s | %s |"
            % (
                entry.get("year") if entry.get("year") is not None else BLANK_MARKER,
                _escape(entry["title"]),
                _escape(authors, limit=160),
            )
        )
    lines.append("")
    lines.append("**Total de artigos inseridos:** %d" % len(entries))
    lines.append("")
    return lines


def _render_removals(removed, remapped):
    lines = ["## 🗑️ Artigos removidos ou remapeados", ""]

    if not removed and not remapped:
        lines.append("Nenhum artigo removido ou remapeado nesta rodada.")
        lines.append("")
        return lines

    if removed:
        lines.append("**Removidos da base:**")
        lines.append("")
        for title in removed:
            lines.append("- %s" % _escape(title))
        lines.append("")

    if remapped:
        lines.append(
            "**Renumerados (`Paper_id` deslocado em razão de remoção anterior "
            "na planilha):**"
        )
        lines.append("")
        lines.append("| Ano | Título | `Paper_id` anterior | `Paper_id` atual |")
        lines.append("| :--: | ----- | :------------------: | :---------------: |")
        for item in remapped:
            lines.append(
                "| %s | %s | %s | %s |"
                % (
                    item.get("year") if item.get("year") is not None else BLANK_MARKER,
                    _escape(item["title"]),
                    item.get("old_id"),
                    item.get("new_id"),
                )
            )
        lines.append("")

    lines.append(
        "**Total de artigos removidos:** %d &nbsp;·&nbsp; "
        "**Total renumerados:** %d" % (len(removed), len(remapped))
    )
    lines.append("")
    return lines


def _render_citations(state):
    changes = state["citation_changes"]
    lines = ["## 📈 Citações atualizadas (Google Scholar)", ""]

    if not changes:
        lines.append("Nenhuma citação foi atualizada nesta rodada.")
        lines.append("")
        return lines

    lines.append("| `Paper_id` | Título | Antes | Depois | Δ |")
    lines.append("| :-------: | ----- | :---: | :----: | :-: |")
    for change in changes:
        old_raw = change.get("old") or ""
        new_raw = change.get("new") or ""
        old_count = parse_citation_count(old_raw)
        new_count = parse_citation_count(new_raw)

        if old_count is not None and new_count is not None:
            delta = new_count - old_count
            delta_text = "%+d" % delta if delta else "0"
            old_text = str(old_count)
            new_text = str(new_count)
        else:
            old_text = _cell(old_raw) or BLANK_MARKER
            new_text = _cell(new_raw) or BLANK_MARKER
            delta_text = "n/d"

        lines.append(
            "| %s | %s | %s | %s | %s |"
            % (
                change.get("paper_id") if change.get("paper_id") is not None else BLANK_MARKER,
                _escape(change.get("title"), limit=110),
                _escape(old_text, limit=40),
                _escape(new_text, limit=40),
                delta_text,
            )
        )

    lines.append("")
    lines.append("**Total de citações atualizadas:** %d" % len(changes))
    lines.append("")
    return lines


def _render_metrics(papers, authors):
    lines = ["## 📊 Métricas finais do dataset", ""]
    papers = papers or []
    authors = authors or []

    editions = sorted({p.get("Year") for p in papers if p.get("Year") is not None})
    span = (
        "%d – %d" % (editions[0], editions[-1]) if editions else BLANK_MARKER
    )
    awarded = 0
    award_file = os.path.join(DATA_DIR, "award_papers.json")
    for edition in _read_json(award_file) or []:
        awarded += len(edition.get("Papers") or [])

    lines.append("| Métrica | Valor |")
    lines.append("| ------ | ----: |")
    lines.append("| Artigos | %d |" % len(papers))
    lines.append("| Autores | %d |" % len(authors))
    lines.append("| Edições | %d |" % len(editions))
    lines.append("| Período | %s |" % span)
    lines.append("| Artigos premiados | %d |" % awarded)
    lines.append("")
    return lines


def render_summary():
    """Monta o Markdown do relatório e grava em ``pr_summary.md``."""
    state = load_state()
    removed, remapped, after, added = _diff_dataset(state)
    current_papers = _read_json(PAPERS_FILE) or []
    authors = _read_json(AUTHORS_FILE) or []

    lines = ["## 📋 Relatório de auditoria — sync automático do dataWASHES", ""]

    has_changes = bool(
        state["new_papers"] or state["citation_changes"] or removed or remapped or added
    )
    if has_changes:
        lines.append(
            "Este Pull Request foi aberto automaticamente pelo pipeline de "
            "sincronização do dataset (SOL SBC + Groq + Google Scholar)."
        )
    else:
        lines.append("**%s.**" % NO_CHANGE_NOTE)
    lines.append("")

    lines.extend(_render_new_papers(state, added, current_papers))
    lines.extend(_render_removals(removed, remapped))
    lines.extend(_render_citations(state))
    lines.extend(_render_metrics(current_papers, authors))

    for note in state["notes"]:
        lines.append("> %s" % note)
    if state["notes"]:
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "_Gerado por `scripts/pr_report.py`. Legenda: `#` marca campo não "
        "preenchido; `n/d` indica contagem de citações não aplicável "
        "(a célula guarda texto livre em vez de um número)._"
    )
    lines.append("")

    content = "\n".join(lines)

    with open(SUMMARY_PATH, "w", encoding="utf-8") as handle:
        handle.write(content)
    return content


def reset():
    """Limpa estado e relatório de execuções anteriores."""
    for path in (STATE_PATH, SUMMARY_PATH):
        if os.path.exists(path):
            os.remove(path)


def main():
    parser = argparse.ArgumentParser(
        description="Gera o relatório de auditoria (pr_summary.md) dos PRs do bot"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Zera o estado, captura snapshot dos JSONs e apaga relatório antigo",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Escreve o pr_summary.md a partir do estado acumulado",
    )
    args = parser.parse_args()

    if args.init:
        reset()
        snapshot_dataset()
        print(f"📸 Snapshot do dataset capturado em {os.path.relpath(STATE_PATH, ROOT)}")
    if args.render:
        render_summary()
        print(f"📝 Relatório gerado em {os.path.relpath(SUMMARY_PATH, ROOT)}")
    if not args.init and not args.render:
        parser.print_help()


if __name__ == "__main__":
    main()