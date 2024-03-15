import json

with open("../data/authors.json", "r", encoding="utf8") as authors_file:
    authors_db = json.load(authors_file)

with open("../data/papers.json", "r", encoding="utf8") as papers_file:
    papers_db = json.load(papers_file)

with open("../data/editions.json", "r", encoding="utf8") as editions_file:
    editions_db = json.load(editions_file)