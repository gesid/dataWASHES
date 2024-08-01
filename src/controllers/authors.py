from flask_restx import Resource, Namespace
from resouces import AuthorDB
from models import author, paper
from flask import request
from utils.logging_washes import log_request

ns = Namespace(name="Authors", path="/authors")

@ns.route("/")
class AuthorsList(Resource):
    @ns.marshal_list_with(author, mask=None)
    @ns.doc(
        "list_authors", 
        description='''
            Returns all the authors in the dataset. 
        '''
    )
    def get(self):
        authors = AuthorDB()
        log_request(request.method, request.path, 200)
        return authors.get_data()

@ns.route("/<int:id>")
@ns.response(404, "Author not found")
class Author(Resource):
    @ns.marshal_with(author, mask=None)
    @ns.doc(
        "get_author", 
        description='''
            Returns the author identified by the ``id``. 
        ''',
        params={
            "id": "The author unique identifier"
        }
    )
    def get(self, id):
        authors = AuthorDB()
        found_author = authors.get_by_id(id)
        if not found_author:
            log_request(request.method, request.path, 404)
            ns.abort(404, message=f"Author with id {id} doesn't exist")
        log_request(request.method, request.path, 200)
        return found_author, 200

@ns.route("/by-name/<string:name>")
@ns.response(404, "Author not found")
class SearchAuthor(Resource):
    @ns.marshal_list_with(author, mask=None)
    @ns.doc(
        "search_author", 
        description='''
            Returns the authors whose names match the ``name`` specified. 
        ''',
        params={
            "name": "The author name"
        }
    )
    def get(self, name):
        authors = AuthorDB()
        authors.filter_by({"Name": name})
        if authors.is_empty():
            log_request(request.method, request.path, 404)
            ns.abort(404, message=f"Author {name} doesn't exist")
        log_request(request.method, request.path, 200)
        return authors.get_data()

@ns.route("/<int:id>/papers")
class PapersByAuthor(Resource):
    @ns.marshal_list_with(paper, mask=None)
    @ns.doc(
        "get_papers_by_author", 
        description='''
            Returns the papers of the author specified by ``id``. 
        '''
        ,
        params={
            "id": "The author unique identifier"
        }
    )
    def get(self, id):
        authors = AuthorDB()
        author_papers = authors.get_papers(id)
        if not author_papers:
            log_request(request.method, request.path, 404)
            ns.abort(404, message=f"Author with ID {id} not found.")
        log_request(request.method, request.path, 200)
        return author_papers, 200
