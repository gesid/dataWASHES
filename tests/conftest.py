import json
import os
import sys
import pytest

# Adiciona a raiz do projeto e o diretório 'src' ao sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from src.server.instance import server
from src.controllers import (
    editions_ns,
    papers_ns,
    authors_ns,
    statistics_ns
)

# Garante que os namespaces estejam registrados na API
try:
    server.api.add_namespace(editions_ns)
    server.api.add_namespace(papers_ns)
    server.api.add_namespace(authors_ns)
    server.api.add_namespace(statistics_ns)
except Exception:
    pass

@pytest.fixture
def client():
    """Cria um cliente de teste do Flask rodando diretamente em memória."""
    server.app.config['TESTING'] = True
    with server.app.test_client() as client:
        yield client

@pytest.fixture
def total_papers():
    path = os.path.join("data", "papers.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return len(json.load(f))
    return 137

@pytest.fixture
def total_authors():
    path = os.path.join("data", "authors.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return len(json.load(f))
    return 300