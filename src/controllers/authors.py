from flask_restx import Resource, Namespace, fields
from flask import request
from src.server.instance import server
import json

author = server.getApi().model(
    "Author",
    {
        "Author_id": fields.Integer(
            description="The author unique identifier", example="10"
        ),
        "Name": fields.String(description="Author's name", example="João"),
        "State": fields.String(description="Author's state", example="CE"),
        "Institution": fields.String(description="Author' institution", example="UFCA"),
        "Papers": fields.List(
            fields.Integer,
            description="IDs of the author's published papers",
            example="[0, 3, 12]",
        ),
    },
)

ns = Namespace("authors")

with open("data/authors.json", "r", encoding="utf8") as authors_file:
    authors_db = json.load(authors_file)

with open("data/papers.json", "r", encoding="utf8") as papers_file:
    papers_db = json.load(papers_file)

@ns.route("/")
class AuthorsList(Resource):
    @ns.doc("list_authors")
    @ns.marshal_list_with(author)
    def get(self):
        return authors_db


@ns.route("/<int:id>")
@ns.response(404, "Author not found")
class Author(Resource):
    @ns.doc("get_author")
    @ns.marshal_with(author)
    def get(self, id):
        for a in authors_db:
            if a["Author_id"] == id:
                return a
        ns.abort(404, message="Author {} doesn't exist".format(id))


@ns.route("/search")
class SearchAuthor(Resource):
    @ns.doc("search_author")
    def get(self):
        name = request.args.get("name")
        queried_authors = [
            author for author in authors_db if name.lower() in author["Name"].lower()
        ]
        return queried_authors


@ns.route("/<int:id>/papers")
class PapersByAuthor(Resource):
    @ns.doc("get_papers_by_author")
    def get(self, id):
        author_papers = [
            paper
            for paper in papers_db
            if any(author["Author_id"] == id for author in paper["Authors"])
        ]
        return author_papers
