from flask import request
from flask_restx import Resource, Namespace  # type: ignore
from resources import PaperDB
from models import paper, paper_paging, abstracts, reference, citation, error_model
from api_utils import log_request, abort_execution, PaginateError
from api_utils.constants import PAGE_PARAM, PER_PAGE_PARAM

ns = Namespace(name="Papers", path="/papers")


@ns.route("/")
class PapersList(Resource):
    """
    Papers list route
    """

    @ns.marshal_with(paper_paging, mask=None)
    @ns.response(404, "No papers found", error_model)
    @ns.response(400, "Invalid parameter", error_model)
    @ns.doc(
        "list_papers",
        params={
            "year": "The year of publication",
            "type": f"The type of the paper ({PaperDB.paper_types_str()})",
            "author": "The name of at least one of the authors",
            "institution": "The institution name of at least one of the authors",
            "state": "The state acronym of at least one of the authors",
            "abstract": "The abstract of the paper",
            "resumo": "O resumo do artigo",
            "keyword": "Papers keyword",
            "search": "Generic word present in title or abstract of papers",
            "reference": "A specific reference used in the paper",
            "citation": "A specific article that cites this article",
            PAGE_PARAM: "The page number to retrieve",
            PER_PAGE_PARAM: "The number of items to display per page"
        },
        description='''
            Returns all the paper in the dataset.
            The list of paper can be filtered using the header arguments specified below.
        ''',
        hide=True
    )
    def get(self):
        """
        List of papers
        """
        # Grouping GET parameters into a dictionary
        query_object = {
            "Paper_id": request.args.get("id"),
            "Year": request.args.get("year"),
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
        try:
            # Executing query
            filtered_papers.filter_by(query_object)
            if filtered_papers.is_empty():
                abort_execution(ns, "No papers found", 404)
            paginated_papers = filtered_papers.get_paginated_response()
            log_request(200)
            return paginated_papers
        except ValueError as e:
            abort_execution(ns, str(e), 400)
        except PaginateError as e:
            abort_execution(ns, str(e), 400)


@ns.route("/abstracts")
class PapersAbstracts(Resource):
    """
    Papers abstracts route
    """

    @ns.marshal_list_with(abstracts, mask=None)
    @ns.doc(
        "get_paper_abstracts",
        description='''
            Returns the ``abstract`` and ``ID`` of all the papers in the dataset. 
        '''
    )
    def get(self):
        """
        List of all papers' abstracts
        """
        papers = PaperDB()
        log_request(200)
        return papers.get_abstracts(), 200


@ns.route("/by-title/<string:search>")
class SearchPapersByTitle(Resource):
    """
    Search papers by title route
    """

    @ns.marshal_list_with(paper, mask=None)
    @ns.response(404, "No papers found", error_model)
    @ns.doc(
        "search_papers_by_title",
        description='''
            Returns all the papers where the string ``search`` is included in the title.
        ''',
        params={
            "search": "Generic word present in title",
        }
    )
    def get(self, search: str):
        """
        Search papers by title
        """
        papers = PaperDB()
        papers.filter_by({"Title": search})
        if papers.is_empty():
            abort_execution(ns, "No papers found with the specified title", 404)
        log_request(200)
        return papers.data, 200


@ns.route("/by-year/<int:year>")
class PapersByYear(Resource):
    """
    Papers by year route
    """

    @ns.marshal_list_with(paper, mask=None)
    @ns.response(404, "No papers found", error_model)
    @ns.doc(
        "get_papers_by_year",
        description='''
            Returns all the papers published in the ``year`` specified.
        ''',
        params={
            "year": "The year of publication",
        }
    )
    def get(self, year: int):
        """
        Search papers by year
        """
        papers = PaperDB()
        papers.filter_by({"Year": str(year)})
        if papers.is_empty():
            abort_execution(ns, "No papers found for the specified year", 404)
        log_request(200)
        return papers.data, 200


@ns.route("/<int:paper_id>")
class PaperById(Resource):
    """
    Paper by id route
    """

    @ns.response(404, "Paper not found", error_model)
    @ns.marshal_with(paper, mask=None)
    @ns.doc(
        "get_paper_by_id",
        description='''
            Returns the paper identified by the ``paper_id``.
        ''',
        params={
            "paper_id": "The paper unique identifier",
        }
    )
    def get(self, paper_id: int):
        """
        Get paper by ID
        """
        papers = PaperDB()
        found_paper = papers.get_by_id(paper_id)
        if not found_paper:
            abort_execution(ns, f"Paper identified by '{paper_id}' not found", 404)
        log_request(200)
        return found_paper, 200


@ns.route("/<int:paper_id>/citations")
class PaperCitations(Resource):
    """
    Papers citations route
    """

    @ns.response(404, "Paper not found", error_model)
    @ns.marshal_with(citation, mask=None)
    @ns.doc(
        "get_paper_citations",
        description='''
            Returns the citations of the paper identified by the ``paper_id``.
        ''',
        params={
            "paper_id": "The paper unique identifier",
        }
    )
    def get(self, paper_id: int):
        """
        Get the paper's citations by ID
        """
        papers = PaperDB()
        citations = papers.get_citations_by_id(paper_id)
        if not citations:
            abort_execution(ns, f"No citations found for paper '{paper_id}'", error_code=404)
        log_request(200)
        return citations, 200


@ns.route("/<int:paper_id>/references")
class PaperReferences(Resource):
    """
    Papers references
    """

    @ns.response(404, "Paper not found", error_model)
    @ns.marshal_with(reference, mask=None)
    @ns.doc(
        "get_paper_references",
        description='''
            Returns the ``references`` of the paper identified by the ``paper_id``
        ''',
        params={
            "paper_id": "The paper unique identifier",
        }
    )
    def get(self, paper_id: int):
        """
        Get the paper's references by ID
        """
        papers = PaperDB()
        references = papers.get_references_by_id(paper_id)
        if not references:
            abort_execution(ns, f"No references found for paper {paper_id}", 404)
        log_request(200)
        return references, 200
