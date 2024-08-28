import json
from os import path

CURRENT_DIR = path.dirname(__file__)
DATA_DIR = path.join(CURRENT_DIR, "..", "..", "data")

with open(path.join(DATA_DIR, "authors.json"), "r", encoding="utf8") as authors_file:
    authors_db = json.load(authors_file)

with open(path.join(DATA_DIR, "papers.json"), "r", encoding="utf8") as papers_file:
    papers_db = json.load(papers_file)

with open(path.join(DATA_DIR, "editions.json"), "r", encoding="utf8") as editions_file:
    editions_db = json.load(editions_file)