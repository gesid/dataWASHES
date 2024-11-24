import pytest
import requests

ENDPOINT = "http://127.0.0.1:5000/"

# Teste para validação do parâmetro 'Year' no endpoint papers
def test_get_papers_with_valid_year_parameter():
    year = 2022
    response = requests.get(f"{ENDPOINT}/papers/?year={year}")
    assert response.status_code == 200

def test_get_papers_with_invalid_year_parameter():
    invalid_year = "invalido" 
    response = requests.get(f"{ENDPOINT}/papers/?year={invalid_year}")
    assert response.status_code == 400

def test_get_papers_without_year_parameter():
    response = requests.get(f"{ENDPOINT}/papers/")
    assert response.status_code == 200

# Teste para validação do parâmetro 'ID' no endpoint papers
def test_get_papers_with_valid_id_parameter():
    id = 1
    response = requests.get(f"{ENDPOINT}/papers/?id={id}")
    assert response.status_code == 200

def test_get_papers_with_invalid_id_returns_404():
    invalid_id = 999999
    response = requests.get(f"{ENDPOINT}/papers/{invalid_id}")
    assert response.status_code == 404

# Teste para validar abstracts
def test_get_abstracts():
    response = requests.get(f"{ENDPOINT}/papers/abstracts")
    assert response.status_code == 200

# Teste para validação do search by title
def test_get_papers_by_title():
    search_term = "Internet"

    response = requests.get(f"{ENDPOINT}/papers/by-title/{search_term}")
    assert response.status_code == 200

def test_get_papers_by_title_invalid_search():
    invalid_search = "magic"

    response = requests.get(f"{ENDPOINT}/papers/by-title/{invalid_search}")
    assert response.status_code == 404

# Teste para validação do search by year
def test_get_papers_by_year():
    years = range(2016, 2024)

    for year in years:
        response = requests.get(f"{ENDPOINT}/papers/by-year/{year}")
        assert response.status_code == 200

def test_get_papers_by_invalid_year():
    invalid_year = 3333

    response = requests.get(f"{ENDPOINT}/papers/by-year/{invalid_year}")
    assert response.status_code == 404

# Teste para validação das IDs
def test_get_valid_paper_ids():
    paper_ids = range(0, 79)

    for paper_id in paper_ids:
        response = requests.get(f"{ENDPOINT}/papers/{paper_id}")
        assert response.status_code == 200

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

def test_get_references_for_invalid_paper_ids():
    paper_ids = [1000, 1001, 1002]

    for paper_id in paper_ids:
        response = requests.get(f"{ENDPOINT}/papers/{paper_id}/references")
        assert response.status_code == 404

# Teste para citações
def test_get_citations_for_valid_paper_ids():
    paper_ids = range(0, 79)

    for paper_id in paper_ids:
        response = requests.get(f"{ENDPOINT}/papers/{paper_id}/citations")
        assert response.status_code == 200

def test_get_citations_for_invalid_paper_ids():
    paper_ids = [1000, 1001, 1002]

    for paper_id in paper_ids:
        response = requests.get(f"{ENDPOINT}/papers/{paper_id}/citations")
        assert response.status_code == 404

if __name__ == "__main__":
    pytest.main()