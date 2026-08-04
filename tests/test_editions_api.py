import pytest

def test_get_editions(client):
    response = client.get("/editions/", follow_redirects=True)
    assert response.status_code == 200
    res = response.get_json()
    data = res["data"] if isinstance(res, dict) and "data" in res else res
    assert isinstance(data, list)
    assert len(data) == 11  # 11 edições (2016 a 2026)

def test_get_editions_by_years(client):
    for year in range(2016, 2027):
        response = client.get(f"/editions/by-year/{year}")
        assert response.status_code == 200
        res = response.get_json()
        data = res["data"] if isinstance(res, dict) and "data" in res else res
        edition = data[0] if isinstance(data, list) else data
        assert edition["Year"] == year

    for year in [2000, 2040]:
        response = client.get(f"/editions/by-year/{year}")
        assert response.status_code == 404

def test_get_edition_valid_ids(client):
    for edition_id in range(0, 11):
        response = client.get(f"/editions/{edition_id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["Edition_id"] == edition_id

def test_get_edition_invalid_ids(client):
    for edition_id in [99, -1]:
        response = client.get(f"/editions/{edition_id}")
        assert response.status_code == 404

def test_get_papers_for_valid_edition_ids(client):
    for edition_id in range(0, 11):
        response = client.get(f"/editions/{edition_id}/papers")
        assert response.status_code == 200
        res = response.get_json()
        papers = res["data"] if isinstance(res, dict) and "data" in res else res
        assert isinstance(papers, list)

def test_get_papers_for_invalid_edition_ids(client):
    for edition_id in [99, 100, 105]:
        response = client.get(f"/editions/{edition_id}/papers")
        assert response.status_code == 404