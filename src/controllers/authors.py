from flask_restx import Resource, Namespace
from src.resouces.database import papers_db, authors_db
from src.models.models import author, paper

ns = Namespace(name="Authors", path="/authors")

@ns.route("/")
class AuthorsList(Resource):
    @ns.marshal_list_with(author, mask=None)
    @ns.doc("list_authors")
    def get(self):
        return authors_db


@ns.route("/<int:id>")
@ns.response(404, "Author not found")
class Author(Resource):
    @ns.marshal_with(author, mask=None)
    @ns.doc("get_author")
    def get(self, id):
        for author in authors_db:
            if author["Author_id"] == id:
                return author
        ns.abort(404, message=f"Author with id {id} doesn't exist")


@ns.route("/by-name/<string:name>")
@ns.response(404, "Author not found")
class SearchAuthor(Resource):
    @ns.marshal_list_with(author, mask=None)
    @ns.doc("search_author", 
            params={
                "name": "An author name"
            }
    )
    def get(self, name):
        queried_authors = [
            author for author in authors_db if name.lower() in author["Name"].lower()
        ]
        if queried_authors:
            return queried_authors
        ns.abort(404, message=f"Author {name} doesn't exist")


@ns.route("/<int:id>/papers")
class PapersByAuthor(Resource):
    @ns.marshal_list_with(paper, mask=None)
    @ns.doc("get_papers_by_author")
    def get(self, id):
        author_papers = [
            paper
            for paper in papers_db
            if any(author["Author_id"] == id for author in paper["Authors"])
        ]
        return author_papers
