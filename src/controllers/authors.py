from flask_restx import Resource, Namespace
from flask import request
from resouces import papers_db, authors_db
from models import author, author_paging, paper_paging
from api_utils import paginate, log_request


ns = Namespace(name="Authors", path="/authors")

@ns.route("/")
class AuthorsList(Resource):
    @ns.marshal_list_with(author_paging, mask=None)
    @ns.doc(
        "list_authors", 
        description='''
            Returns all the authors in the dataset. 
        ''',
        params={
            "page": "The page number to retrieve",
            "per_page": "The number of authors to display per page"
        }
    )
    def get(self):
        try:
            authors = paginate(authors_db)
        except ValueError as e:
            log_request(request.method, request.path, 400)
            ns.abort(400, message=str(e))
        log_request(request.method, request.path, 200)
        return authors


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
        for author in authors_db:
            if author["Author_id"] == id:
                log_request(request.method, request.path, 200)
                return author
        log_request(request.method, request.path, 404)
        ns.abort(404, message=f"Author with id {id} doesn't exist")


@ns.route("/by-name/<string:name>")
@ns.response(404, "Author not found")
class SearchAuthor(Resource):
    @ns.marshal_list_with(author_paging, mask=None)
    @ns.doc(
        "search_author", 
        description='''
            Returns the authors whose names match the ``name`` specified. 
        ''',
        params={
            "name": "The author name",
            "page": "The page number to retrieve",
            "per_page": "The number of authors to display per page"
        }
    )
    def get(self, name):
        queried_authors = [
            author for author in authors_db if name.lower() in author["Name"].lower()
        ]
        if not queried_authors:
            log_request(request.method, request.path, 404)
            ns.abort(404, message=f"Author {name} doesn't exist")

        try:
            queried_authors = paginate(queried_authors)
        except ValueError as e:
            log_request(request.method, request.path, 400)
            ns.abort(400, message=str(e))

        log_request(request.method, request.path, 200)
        return queried_authors


@ns.route("/<int:id>/papers")
class PapersByAuthor(Resource):
    @ns.marshal_list_with(paper_paging, mask=None)
    @ns.doc(
        "get_papers_by_author", 
        description='''
            Returns the papers of the author specified by ``id``. 
        '''
        ,
        params={
            "id": "The author unique identifier",
            "page": "The page number to retrieve",
            "per_page": "The number of papers to display per page"
        }
    )
    def get(self, id):
        author_papers = [
            paper
            for paper in papers_db
            if any(author["Author_id"] == id for author in paper["Authors"])
        ]

        if not author_papers:
            log_request(request.method, request.path, 404)
            return {"message": f"Author with ID {id} not found."}, 404
        
        try:
            author_papers = paginate(author_papers)
        except ValueError as e:
            log_request(request.method, request.path, 400)
            ns.abort(400, message=str(e))

        log_request(request.method, request.path, 200)
        return author_papers
