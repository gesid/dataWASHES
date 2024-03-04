from flask import Flask, jsonify, request
import json

with open("data/editions.json", "r") as editions_file:
    editions = json.load(editions_file)

with open("data/papers.json", "r") as papers_file:
    papers = json.load(papers_file)

with open("data/authors.json", "r") as authors_file:
    authors = json.load(authors_file)

app = Flask(__name__)


@app.route("/")
def index():
    return "Homepage"


@app.route("/editions/<int:id>", methods=["GET"])
def get_edition_by_id(id):
    edition = next(
        (edition for edition in editions if edition["Edition_id"] == id), None
    )

    if edition is None:
        return jsonify({"error": "edition not found"}), 404

    return jsonify(edition)


# Main routes
@app.route("/editions", methods=["GET"])
def get_editions():
    return jsonify(editions)


@app.route("/editions/search", methods=["GET"])
def search_editions_by_year():
    year = request.args.get("year")
    if not year:
        return jsonify({"error": "Missing 'year' parameter"}), 400

    matched_editions = [edition for edition in editions if edition["Year"] == int(year)]
    return jsonify(matched_editions)


@app.route("/editions/<int:edition_id>/papers", methods=['GET'])
def get_papers_by_edition_id(edition_id):
    edition = next((edition for edition in editions if edition["Edition_id"] == edition_id), None)
    if edition is None:
        return jsonify({"error": "Edition not found"}), 404

    papers_in_edition = [paper for paper in papers if paper["Paper_id"] in edition["Papers"]]
    return jsonify(papers_in_edition)



@app.route("/authors", methods=["GET"])
def get_authors():
    return jsonify(authors)


@app.route("/authors/<int:id>", methods=["GET"])
def get_author_by_id(id):
    author = next(
        (author for author in authors if str(author["Author_id"]) == id), None
    )

    if author is None:
        return jsonify({"error": "author not found"}), 404

    return jsonify(author)


@app.route("/authors/search", methods=["GET"])
def search_author():
    name = request.args.get("name")
    queried_authors = [
        author for author in authors if name.lower() in author["Name"].lower()
    ]

    return jsonify(queried_authors)


@app.route("/authors/<int:id>/papers", methods=["GET"])
def get_papers_by_author(id):
    author_papers = [
        paper
        for paper in papers
        if any(author["Author_id"] == id for author in paper["Authors"])
    ]
    return jsonify(author_papers)


@app.route("/papers", methods=["GET"])
def filter_papers():
    year = request.args.get("year")
    paper_id = request.args.get("id")
    paper_type = request.args.get("type")
    author_name = request.args.get("author")
    institution_name = request.args.get("institution")
    author_state = request.args.get("state")
    abstract_query = request.args.get("abstract")
    resumo_query = request.args.get("resumo")
    keyword = request.args.get("keyword")
    generic_query = request.args.get("pesquisa")

    filtered_papers = papers

    if year:
        filtered_papers = [
            paper for paper in filtered_papers if str(paper["Year"]) == year
        ]

    if paper_id:
        filtered_papers = [
            paper for paper in filtered_papers if str(paper["Paper_id"]) == paper_id
        ]

    if paper_type:
        filtered_papers = [
            paper
            for paper in filtered_papers
            if paper["Type"].lower() == paper_type.lower()
        ]

    if author_name:
        filtered_papers = [
            paper
            for paper in filtered_papers
            if any(
                author["Name"].lower() == author_name.lower()
                for author in paper["Authors"]
            )
        ]

    if institution_name:
        filtered_papers = [
            paper
            for paper in filtered_papers
            if any(
                author["Institution"] == institution_name for author in paper["Authors"]
            )
        ]

    if author_state:
        filtered_papers = [
            paper
            for paper in filtered_papers
            if any(
                author["State"].lower() == author_state.lower()
                for author in paper["Authors"]
            )
        ]

    if abstract_query:
        filtered_papers = [
            paper
            for paper in filtered_papers
            if abstract_query.lower() in paper["Abstract"].lower()
        ]

    if resumo_query:
        filtered_papers = [
            paper
            for paper in filtered_papers
            if resumo_query.lower() in paper["Resumo"].lower()
        ]

    if keyword:
        filtered_papers = [
            paper
            for paper in filtered_papers
            if keyword.lower() in paper["Keywords"].lower()
        ]

    if generic_query:
        filtered_papers = [
            paper
            for paper in papers
            if generic_query.lower() in paper["Title"].lower()
            or generic_query.lower() in paper["Abstract"].lower()
        ]

    return jsonify(filtered_papers)


@app.route("/papers/<int:id>", methods=["GET"])
def paper_by_id(id):
    paper = next((paper for paper in papers if str(paper["Paper_id"]) == id), None)

    if paper is None:
        return jsonify({"error": "paper not found"}), 404

    return jsonify(paper)


@app.route("/papers/search", methods=["GET"])
def search_papers_by_title():
    keyword = request.args.get("title")
    if not keyword:
        return jsonify({"error": "Missing 'title' parameter"}), 400

    matched_papers = [
        paper for paper in papers if keyword.lower() in paper["Title"].lower()
    ]
    return jsonify(matched_papers)


@app.route("/papers/by-year/<int:ano>", methods=["GET"])
def get_papers_by_year(ano):
    matched_papers = [paper for paper in papers if paper["Year"] == ano]
    return jsonify(matched_papers)


@app.route("/papers/resumos", methods=["GET"])
def get_paper_abstracts():
    abstracts = [paper["Abstract"] for paper in papers]
    return jsonify(abstracts)


if __name__ == "__main__":
    app.run(debug=True)
