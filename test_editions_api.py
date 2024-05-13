import pytest
import requests

ENDPOINT = "http://127.0.0.1:5000/"

# Teste para validar rota editions
def test_get_editions():
    response = requests.get(f"{ENDPOINT}/editions")
    assert response.status_code == 200

# Teste para anos válidos e inválidos
def test_get_editions_by_years():
    valid_years = range(2016, 2023)
    invalid_years = [2000, 2040]

    # Anos válidos
    for year in valid_years:
        url = f"{ENDPOINT}/editions/by-year/{year}"
        response = requests.get(url)
        assert response.status_code == 200

    # Anos inválidos
    for year in invalid_years:
        url = f"{ENDPOINT}/editions/by-year/{year}"
        response = requests.get(url)
        assert response.status_code == 404


# Teste para edições com IDs válidas
def test_get_edition_valid_ids():
    edition_ids = range(0, 8)

    for edition_id in edition_ids:
        url = f"{ENDPOINT}/editions/{edition_id}"
        response = requests.get(url)
        assert response.status_code == 200

# Teste para edições com IDs inválidas
def test_get_edition_invalid_ids():
    invalid_edition_ids = [99, -1, "invalid"]

    for edition_id in invalid_edition_ids:
        url = f"{ENDPOINT}/editions/{edition_id}"
        response = requests.get(url)
        assert response.status_code == 404

# Teste para edições válidas e seus respectivos artigos
def test_get_papers_for_valid_edition_ids():
    edition_ids = range(0, 8)

    for edition_id in edition_ids:
        response = requests.get(f"{ENDPOINT}/editions/{edition_id}/papers")
        assert response.status_code == 200

# Teste para edições inválidas e seus respectivos artigos
def test_get_papers_for_invalid_edition_ids():
    invalid_edition_ids = [10, 15, 20]

    for edition_id in invalid_edition_ids:
        response = requests.get(f"{ENDPOINT}/editions/{edition_id}/papers")
        assert response.status_code == 404

if __name__ == "__main__":
    pytest.main()