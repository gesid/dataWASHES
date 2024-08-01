from flask import request
from flask_restx import Resource, Namespace
from resouces import PaperDB
from models import paper, abstracts, reference, citation
from utils.logging_washes import log_request

ns = Namespace(name="Papers", path="/papers")

@ns.route("/")
class PapersList(Resource):

    @ns.marshal_list_with(paper, mask=None)
    @ns.doc(
        "list_papers",
        params={
            "type": "The type of the paper",
            "author": "The name of at least one of the authors",
            "institution": "The institution name of at least one of the authors",
            "state": "The state acronym of at least one of the authors",
            "abstract": "The abstract of the paper",
            "resumo": "O resumo do artigo",
            "keyword": "Papers keyword",
            "search": "Generic word present in title or abstract of papers",
            "reference": "A specific reference used in the paper",
            "citation": "A specific article that cites this article",
        },
        description='''
            Returns all the paper in the dataset.
            The list of paper can be filtered using the header arguments specified below.
        '''
    )
    def get(self):
        query_object = {
            "Type": request.args.get("type"),
            "Author": request.args.get("author"),
            "Institution": request.args.get("institution"),
            "State": request.args.get("state"),
            "Abstract": request.args.get("abstract"),
            "Resumo": request.args.get("resumo"),
            "Keywords": request.args.get("keyword"),
            "Search": request.args.get("search"),
            "Cited_by": request.args.get("citation"),
            "References": request.args.get("reference"),
        }

        filtered_papers = PaperDB()
        filtered_papers.filter_by(query_object)

        if filtered_papers.is_empty():
            log_request(request.method, request.path, 404)
            ns.abort(404, massage="No papers found")

        log_request(request.method, request.path, 200)
        return filtered_papers.get_data()

@ns.route("/abstracts")
class GetPaperAbstracts(Resource):
    @ns.marshal_list_with(abstracts, mask=None)
    @ns.doc(
        "get_paper_abstracts", 
        description='''
            Returns the ``abstract`` and ``ID`` of all the papers in the dataset. 
        '''
    )
    def get(self):
        papers = PaperDB()
        log_request(request.method, request.path, 200)
        return papers.get_abstracts(), 200

      
@ns.route("/by-title/<string:search>")
class SearchPapersByTitle(Resource):
    @ns.marshal_list_with(paper, mask=None)
    @ns.doc(
        "search_papers_by_title", 
        description='''
            Returns all the papers where the string ``search`` is included in the title.
        ''',
        params={
            "search": "Generic word present in title",
        }
    )
    def get(self, search):
        keyword = search
        if not keyword:
            log_request(request.method, request.path, 400)
            ns.abort(400, message="Missing 'title' parameter")

        papers = PaperDB()
        papers.filter_by({"Title": keyword})

        if papers.is_empty():
            log_request(request.method, request.path, 404)
            ns.abort(404, message="No papers found with the specified title")

        log_request(request.method, request.path, 200)
        return papers.get_data()

@ns.route("/by-year/<int:year>")
class GetPapersByYear(Resource):
    @ns.marshal_list_with(paper, mask=None)
    @ns.doc(
        "get_papers_by_year", 
        description='''
            Returns all the papers published in the ``year`` specified.
        ''',
        params={
            "year": "The year of publishment",
        }
    )
    def get(self, year):
        papers = PaperDB()

        if not year:
            log_request(request.method, request.path, 400)
            ns.abort(400, message="Missing 'year' parameter")

        papers.filter_by({"Year": year})
        if papers.is_empty():
            log_request(request.method, request.path, 404)
            ns.abort(404, message="No papers found for the specified year.")

        log_request(request.method, request.path, 200)
        return papers.get_data()

@ns.route("/<int:id>")
@ns.response(404, "Paper not found")
class PaperById(Resource):
    @ns.marshal_with(paper, mask=None)
    @ns.doc(
        "get_paper_by_id", 
        description='''
            Returns the paper identified by the ``id``.
        ''',
        params={
            "id": "The paper unique identifier",
        }
    )
    def get(self, id):
        papers = PaperDB()
        found_paper = papers.get_by_id(id)

        if not found_paper:
            log_request(request.method, request.path, 404)
            ns.abort(404, message=f"Paper {id} not found")
        log_request(request.method, request.path, 200)
        return found_paper, 200

# Adicionando rota para obter as citações de um artigo identificado pelo `id`.
@ns.route("/<int:id>/citations")
class GetPaperCitations(Resource):
    @ns.response(404, "Paper not found")
    @ns.marshal_with(citation, mask=None)
    @ns.doc(
        "get_paper_citations",
        description='''
            Returns the citations of the paper identified by the ``id``.
        ''',
        params={
            "id": "The paper unique identifier",
        }
    )
    def get(self, id):
        papers = PaperDB()
        citations = papers.get_citations_by_id(id)

        if not citations:
            log_request(request.method, request.path, 404)
            ns.abort(404, message=f"No citations found for paper {id}")

        log_request(request.method, request.path, 200)
        return citations, 200

# Adicionando rota para obter as referências de um artigo identificado pelo `id`.
@ns.route("/<int:id>/references")
class GetPaperReferences(Resource):
    @ns.response(404, "Paper not found")
    @ns.marshal_with(reference, mask=None)
    @ns.doc(
        "get_paper_references",
        description='''
            Returns the ``references`` of the paper identified by the ``id``
        ''',
        params={
            "id": "The paper unique identifier",
        }
    )
    def get(self, id):
        papers = PaperDB()
        references = papers.get_references_by_id(id)

        if not references:
            log_request(request.method, request.path, 404)
            ns.abort(404, message=f"No references found for paper {id}")

        log_request(request.method, request.path, 200)
        return references, 200
