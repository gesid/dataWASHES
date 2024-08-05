from flask_restx import Resource, Namespace
from flask import request
from resouces import EditionDB
from models import edition, paper, error_model
from utils.logging_washes import log_request

ns = Namespace(name='Editions', path='/editions')

@ns.route("/")
class EditionsList(Resource):
    @ns.marshal_list_with(edition, mask=None)
    @ns.doc("list_editions",
        description='''
            Returns all the editions in the dataset.
        '''
    )
    def get(self):
        editions = EditionDB()
        log_request(request.method, request.path, 200)
        return editions.get_data()

@ns.route("/<int:id>")
class EditionById(Resource):
    @ns.response(404, "Edition not found", error_model)
    @ns.marshal_with(edition, mask=None)
    @ns.doc("get_edition_by_id",
        description='''
            Returns the edition identified by the ``id``.
        ''',
        params={
            "id": "The edition unique identifier"
        }
    )
    def get(self, edition_id):
        editions = EditionDB()
        found_edition = editions.get_by_id(edition_id)
        if not found_edition:
            log_request(request.method, request.path, 404)
            ns.abort(404, message=f"Edition {edition_id} not found", error_code=404)
        log_request(request.method, request.path, 200)
        return found_edition, 200

@ns.route("/by-year/<int:year>")
class SearchEditions(Resource):
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
        editions = EditionDB()
        editions.filter_by({"Year": year})
        if editions.is_empty():
            log_request(request.method, request.path, 404)
            ns.abort(404, message=f"Edition not found for year {year}", error_code=404)
        log_request(request.method, request.path, 200)
        return editions.get_data()

@ns.route("/<int:id>/papers")
class PapersByEdition(Resource):
    @ns.response(404, "Edition papers not found", error_model)
    @ns.marshal_list_with(paper, mask=None)
    @ns.doc("get_papers_by_id",
        description='''
            Returns all the papers that were published in the edition specified by the ``id``.
        ''',
        params={
            "id": "The edition unique identifier"
        }
    )
    def get(self, edition_id):
        editions = EditionDB()
        papers_in_edition = editions.get_papers(edition_id)

        if not papers_in_edition:
            log_request(request.method, request.path, 404)
            ns.abort(404, message=f"Edition {edition_id} not found", error_code=404)
        log_request(request.method, request.path, 200)
        return papers_in_edition, 200
