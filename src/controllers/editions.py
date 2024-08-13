from flask_restx import Resource, Namespace # type: ignore
from flask import request
from resouces import EditionDB
from models import edition, edition_paging, paper_paging, error_model
from api_utils import log_request, abort_execution
from api_utils.constants import PAGE_PARAM, PER_PAGE_PARAM

ns = Namespace(name='Editions', path='/editions')

@ns.route("/")
class EditionsList(Resource):
    """
    Editions list route
    """
    @ns.marshal_with(edition_paging, mask=None)
    @ns.doc("list_editions",
        description='''
            Returns all the editions in the dataset.
        ''',
        params={
            PAGE_PARAM: "The page number to retrieve",
            PER_PAGE_PARAM: "The number of editions to display per page"
        }
    )
    def get(self):
        """
        List of editions
        """
        editions = EditionDB()
        log_request(request.method, request.path, 200)
        return editions.get_paginated_data(ns)

@ns.route("/<int:edition_id>")
class EditionById(Resource):
    """
    Edition by ID route
    """
    @ns.response(404, "Edition not found", error_model)
    @ns.marshal_with(edition, mask=None)
    @ns.doc("get_edition_by_id",
        description='''
            Returns the edition identified by the ``edition_id``.
        ''',
        params={
            "edition_id": "The edition unique identifier"
        }
    )
    def get(self, edition_id):
        """
        Get edition by ID
        """
        editions = EditionDB()
        found_edition = editions.get_by_id(edition_id)
        if not found_edition:
            abort_execution(ns, f"Edition {edition_id} not found", 404)
        log_request(request.method, request.path, 200)
        return found_edition, 200

@ns.route("/by-year/<int:year>")
class SearchEditionsByYear(Resource):
    """
    Seaech editions by year route
    """
    @ns.response(404, "Edition not found", error_model)
    @ns.marshal_with(edition, mask=None)
    @ns.doc("search_editions_by_year",
             description='''
                 Returns the edition that occurred in the ``year`` specified.
             ''',
             params={
                 "year": "The year of the edition"
             })
    def get(self, year):
        """
        Search edition by year
        """
        editions = EditionDB()
        editions.filter_by({"Year": year})
        if editions.is_empty():
            abort_execution(ns, f"Edition not found for year {year}", 404)
        log_request(request.method, request.path, 200)
        return editions.get_data()

@ns.route("/<int:edition_id>/papers")
class EditionPapersById(Resource):
    """
    Editions papers by ID route
    """
    @ns.response(404, "Edition papers not found", error_model)
    @ns.marshal_with(paper_paging, mask=None)
    @ns.doc("get_papers_by_id",
        description='''
            Returns all the papers that were published in the edition specified by the ``edition_id``.
        ''',
        params={
            "edition_id": "The edition unique identifier",
            PAGE_PARAM: "The page number to retrieve",
            PER_PAGE_PARAM: "The number of papers to display per page"
        }
    )
    def get(self, edition_id):
        """
        Get the edition's papers
        """
        editions = EditionDB()
        papers_in_edition = editions.get_papers(edition_id)
        if not papers_in_edition:
            abort_execution(ns, f"Edition {edition_id} not found", 404)
        log_request(request.method, request.path, 200)
        return papers_in_edition.get_paginated_data(ns)
