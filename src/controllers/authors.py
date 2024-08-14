from flask_restx import Resource, Namespace # type: ignore
from flask import request
from resouces import AuthorDB
from models import author, author_paging, paper, error_model
from api_utils import log_request, abort_execution
from api_utils.constants import PAGE_PARAM, PER_PAGE_PARAM

ns = Namespace(name="Authors", path="/authors")

@ns.route("/")
class AuthorsList(Resource):
    """
    Authors list route
    """
    @ns.response(400, "Invalid parameter", error_model)
    @ns.marshal_with(author_paging, mask=None)
    @ns.doc(
        "list_authors", 
        description='''
            Returns all the authors in the dataset. 
        ''',
        params={
            PAGE_PARAM: "The page number to retrieve",
            PER_PAGE_PARAM: "The number of authors to display per page"
        }
    )
    def get(self):
        """
        List of authors
        """
        authors = AuthorDB()
        log_request(200)
        return authors.get_paginated_data(ns)

@ns.route("/<int:author_id>")
class AuthorById(Resource):
    """
    Author by id route
    """
    @ns.response(404, "Author not found", error_model)
    @ns.marshal_with(author, mask=None)
    @ns.doc(
        "get_author", 
        description='''
            Returns the author identified by the ``author_id``. 
        ''',
        params={
            "author_id": "The author unique identifier"
        }
    )
    def get(self, author_id):
        """
        Get author by ID
        """
        authors = AuthorDB()
        found_author = authors.get_by_id(author_id)
        if not found_author:
            abort_execution(ns, f"Author with id {author_id} doesn't exist", 404)
        log_request(200)
        return found_author, 200

@ns.route("/by-name/<string:name>")
class SearchAuthorByName(Resource):
    """
    Search author by name route
    """
    @ns.response(400, "Invalid parameter", error_model)
    @ns.response(404, "Author not found", error_model)
    @ns.marshal_with(author_paging, mask=None)
    @ns.doc(
        "search_author", 
        description='''
            Returns the authors whose names match the ``name`` specified. 
        ''',
        params={
            "name": "The author name",
            PAGE_PARAM: "The page number to retrieve",
            PER_PAGE_PARAM: "The number of authors to display per page"
        }
    )
    def get(self, name):
        """
        Search authors by Name
        """
        authors = AuthorDB()
        authors.filter_by({"Name": name})
        if authors.is_empty():
            abort_execution(ns, f"Author '{name}' doesn't exist", 404)
        log_request(200)
        return authors.get_paginated_data(ns)

@ns.route("/<int:author_id>/papers")
class PapersByAuthor(Resource):
    """
    Papers by author route
    """
    @ns.response(404, "Author papers not found", error_model)
    @ns.marshal_list_with(paper, mask=None)
    @ns.doc(
        "get_papers_by_author", 
        description='''
            Returns the papers of the author specified by ``author_id``. 
        '''
        ,
        params={
            "author_id": "The author unique identifier"
        }
    )
    def get(self, author_id):
        """
        Get author's papers
        """
        authors = AuthorDB()
        author_papers = authors.get_papers(author_id)
        if not author_papers:
            abort_execution(ns, f"Author with ID {author_id} not found.", 404)
        log_request(200)
        return author_papers, 200
