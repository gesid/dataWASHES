import pytest

def test_get_authors(client):
    response = client.get("/authors/", follow_redirects=True)
    assert response.status_code == 200
    res = response.get_json()
    data = res["data"] if isinstance(res, dict) and "data" in res else res
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_authors_by_name(client):
    # Nomes válidos
    response = client.get("/authors/by-name/João")
    assert response.status_code == 200
    res = response.get_json()
    data = res["data"] if isinstance(res, dict) and "data" in res else res
    assert isinstance(data, list)
    assert len(data) > 0

    # Nomes inválidos
    for name in ["non-existent-author", "123-invalid-name"]:
        response = client.get(f"/authors/by-name/{name}")
        assert response.status_code == 404

def test_get_authors_valid_ids(client, total_authors):
    sample_ids = list(range(0, 5)) + list(range(total_authors - 5, total_authors))
    for author_id in sample_ids:
        response = client.get(f"/authors/{author_id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["Author_id"] == author_id
        assert "Name" in data

def test_get_authors_invalid_ids(client):
    for author_id in [-1, 99999]:
        response = client.get(f"/authors/{author_id}")
        assert response.status_code == 404

def test_get_papers_for_valid_author_ids(client):
    response = client.get("/authors/0/papers")
    assert response.status_code == 200
    res = response.get_json()
    data = res["data"] if isinstance(res, dict) and "data" in res else res
    assert isinstance(data, list)

def test_get_papers_for_invalid_author_ids(client):
    for author_id in [-1, -15, 99999]:
        response = client.get(f"/authors/{author_id}/papers")
        assert response.status_code == 404