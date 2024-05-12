import pytest
import requests

ENDPOINT = "http://127.0.0.1:5000/"

# Teste para validação dos papers
def test_get_papers():
    test_cases = [
        # Teste de caso 1: Filtro por ano
        {
            "year": 2023,
            "expected_status_code": 200
        },
        # Teste de caso 2: Filtro por ID
        {
            "id": 1,
            "expected_status_code": 200
        },
        # Teste de caso 3: Filtro por tipo
        {
            "type": "",
            "expected_status_code": 200
        },
        # Teste de caso 4: Filtro por nome
        {
            "name": "",
            "expected_status_code": 200
        },
        # Teste de caso 5: Filtro por instituição
        {
            "institution": "",
            "expected_status_code": 200
        },
        # Teste de caso 6: Filtro por estado (published, accepted, etc.)
        {
            "state": "",
            "expected_status_code": 200
        },
        # Teste de caso 7: Filtro por abstract
        {
            "abstract": "",
            "expected_status_code": 200
        },
        # Teste de caso 8: Filtro por resumo
        {
            "resumo": "",
            "expected_status_code": 200
        },
        # Teste de caso 9: Filtro por palavras-chave
        {
            "keyword": "",
            "expected_status_code": 200
        },
        # Teste de caso 10: Filtro por busca
        {
            "search": "",
            "expected_status_code": 200
        },
        # Teste de caso 11: Filtro por referências
        {
            "reference": "",
            "expected_status_code": 200
        },
        # Teste de caso 12: Filtro por citações
        {
            "citation": "",
            "expected_status_code": 200
        }
    ]

    for test_case in test_cases:
        url = f"{ENDPOINT}/papers?"
        for param, value in test_case.items():
            url += f"{param}={value}&"

        response = requests.get(url)
        assert response.status_code == test_case["expected_status_code"]

# Teste para validar abstracts
def test_get_abstracts():
    response = requests.get(f"{ENDPOINT}/papers/abstracts")
    assert response.status_code == 200

# Teste para validação do search by title
def test_get_papers_by_title():
    search_term = "Internet"

    response = requests.get(f"{ENDPOINT}/papers/by-title/{search_term}")
    assert response.status_code == 200

# Teste para search by title inválidos
def test_get_papers_by_title_with_empty_search():
    empty_search = ""

    response = requests.get(f"{ENDPOINT}/papers/by-title/{empty_search}")
    assert response.status_code == 404

# Teste para validação do search by year
def test_get_papers_by_year():
    years = range(2016, 2024)

    for year in years:
        response = requests.get(f"{ENDPOINT}/papers/by-year/{year}")
        assert response.status_code == 200

# Teste para search by year inválidos
def test_get_papers_by_invalid_year():
    years = []

    for year in years:
        response = requests.get(f"{ENDPOINT}/papers/by-year/{year}")
        assert response.status_code == 404

# Teste para validação das IDs
def test_get_valid_paper_ids():
    paper_ids = range(0, 79)

    for paper_id in paper_ids:
        response = requests.get(f"{ENDPOINT}/papers/{paper_id}")
        assert response.status_code == 200

# Teste para IDs inválidas
def test_get_invalid_paper_ids():
    paper_ids = [1000, 1001, 1002]

    for paper_id in paper_ids:
        response = requests.get(f"{ENDPOINT}/papers/{paper_id}")
        assert response.status_code == 404

# Teste para validar referências
def test_get_references_for_valid_paper_ids():
    paper_ids = range(0, 79)

    for paper_id in paper_ids:
        response = requests.get(f"{ENDPOINT}/papers/{paper_id}/references")
        assert response.status_code == 200

# Teste para referências inválidas
def test_get_references_for_invalid_paper_ids():
    paper_ids = [1000, 1001, 1002]

    for paper_id in paper_ids:
        response = requests.get(f"{ENDPOINT}/papers/{paper_id}/references")
        assert response.status_code == 404

# Teste para citações válidas
def test_get_citations_for_valid_paper_ids():
    paper_ids = range(0, 79)

    for paper_id in paper_ids:
        response = requests.get(f"{ENDPOINT}/papers/{paper_id}/citations")
        assert response.status_code == 200

# Teste para citações inválidas
def test_get_citations_for_invalid_paper_ids():
    paper_ids = [1000, 1001, 1002]

    for paper_id in paper_ids:
        response = requests.get(f"{ENDPOINT}/papers/{paper_id}/citations")
        assert response.status_code == 404

if __name__ == "__main__":
    pytest.main()