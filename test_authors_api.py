import pytest
import requests

ENDPOINT = "http://127.0.0.1:5000/"

# Teste para validar rota authors
def test_get_authors():
    response = requests.get(f"{ENDPOINT}/authors")
    assert response.status_code == 200

# Teste para validar authors by name
def test_get_authors_by_name():
    valid_names = ["João"]
    invalid_names = ["non-existent-author", "123-invalid-name"]

    # Nomes válidos
    for name in valid_names:
        url = f"{ENDPOINT}/authors/by-name/{name}"
        response = requests.get(url)
        assert response.status_code == 200

    # Nomes inválidos
    for name in invalid_names:
        url = f"{ENDPOINT}/authors/by-name/{name}"
        response = requests.get(url)
        assert response.status_code == 404

# Teste para authors com IDs válidas
def test_get_authors_valid_ids():
    authors_id = range(0, 263)

    for author_id in authors_id:
        url = f"{ENDPOINT}/authors/{author_id}"
        response = requests.get(url)
        assert response.status_code == 200

# Teste para authors com IDs inválidas
def test_get_authors_invalid_ids():
    invalid_authors_id = [-1, "invalid"]

    for author_id in invalid_authors_id:
        url = f"{ENDPOINT}/authors/{author_id}"
        response = requests.get(url)
        assert response.status_code == 404

# Teste para authors válidos e seus respectivos artigos
def test_get_papers_for_valid_author_ids():
    author_ids = range(0, 263)

    for author_id in author_ids:
        response = requests.get(f"{ENDPOINT}/authors/{author_id}/papers")
        assert response.status_code == 200

# Teste para authors inválidos e seus respectivos artigos
def test_get_papers_for_invalid_author_ids():
    invalid_author_ids = [-1, -15, 3333]

    for author_id in invalid_author_ids:
        response = requests.get(f"{ENDPOINT}/authors/{author_id}/papers")
        assert response.status_code == 404

if __name__ == "__main__":
    pytest.main()