import pytest

def test_get_papers_without_year_parameter(client):
    response = client.get("/papers/", follow_redirects=True)
    assert response.status_code == 200
    res = response.get_json()
    data = res["data"] if isinstance(res, dict) and "data" in res else res
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_papers_with_valid_year_parameter(client):
    # Passa per_page=100 para trazer todos os 22 artigos de 2026 na mesma página
    response = client.get("/papers/?year=2026&per_page=100")
    assert response.status_code == 200
    res = response.get_json()
    data = res["data"] if isinstance(res, dict) and "data" in res else res
    assert isinstance(data, list)
    assert len(data) == 22  # 22 artigos do WASHES 2026

def test_get_papers_with_invalid_year_parameter(client):
    response = client.get("/papers/?year=invalido")
    assert response.status_code == 400

def test_get_papers_with_valid_id_parameter(client):
    response = client.get("/papers/?id=1")
    assert response.status_code == 200
    res = response.get_json()
    data = res["data"] if isinstance(res, dict) and "data" in res else res
    assert len(data) > 0
    assert "Title" in data[0] or "Paper_id" in data[0]

def test_get_papers_with_invalid_id_returns_404(client):
    response = client.get("/papers/999999")
    assert response.status_code == 404

def test_get_abstracts(client):
    response = client.get("/papers/abstracts")
    assert response.status_code == 200

def test_get_papers_by_title(client):
    response = client.get("/papers/by-title/Internet")
    assert response.status_code == 200
    res = response.get_json()
    data = res["data"] if isinstance(res, dict) and "data" in res else res
    assert isinstance(data, list)

def test_get_papers_by_title_invalid_search(client):
    response = client.get("/papers/by-title/termo_completamente_inexistente_123")
    assert response.status_code == 404

def test_get_papers_by_year(client):
    for year in range(2016, 2027):
        response = client.get(f"/papers/by-year/{year}")
        assert response.status_code == 200
        res = response.get_json()
        data = res["data"] if isinstance(res, dict) and "data" in res else res
        assert isinstance(data, list)
        assert len(data) > 0

def test_get_papers_by_invalid_year(client):
    response = client.get("/papers/by-year/3333")
    assert response.status_code == 404

def test_get_valid_paper_ids(client, total_papers):
    sample_ids = list(range(0, 5)) + list(range(total_papers - 5, total_papers))
    for paper_id in sample_ids:
        response = client.get(f"/papers/{paper_id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["Paper_id"] == paper_id
        assert "Title" in data

def test_get_invalid_paper_ids(client):
    for paper_id in [9999, 10000]:
        response = client.get(f"/papers/{paper_id}")
        assert response.status_code == 404

def test_get_references_for_valid_paper_ids(client):
    response = client.get("/papers/0/references")
    assert response.status_code == 200

def test_get_references_for_invalid_paper_ids(client):
    response = client.get("/papers/9999/references")
    assert response.status_code == 404

def test_get_citations_for_valid_paper_ids(client):
    response = client.get("/papers/0/citations")
    assert response.status_code == 200

def test_get_citations_for_invalid_paper_ids(client):
    response = client.get("/papers/9999/citations")
    assert response.status_code == 404