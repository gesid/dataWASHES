from flask_restx import Resource, Namespace
from flask import jsonify
from resouces import editions_db, papers_db
from models import edition, paper
from flask import request
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
        log_request(request.method, request.path, 200)
        return editions_db

@ns.route("/<int:id>")
@ns.response(404, "Edition not found")
class EditionById(Resource):
    @ns.marshal_with(edition, mask=None)
    @ns.doc("get_edition_by_id", 
        description='''
            Returns the edition identified by the ``id``.
        ''',
        params={
            "id": "The edition unique identifier"
        }
    )
    def get(self, id):
        edition = next((e for e in editions_db if e["Edition_id"] == id), None)
        if edition is None:
            log_request(request.method, request.path, 404)
            return jsonify({"error": "Edition not found"}), 404
        log_request(request.method, request.path, 200)
        return edition

@ns.route("/by-year/<int:year>")
@ns.response(404, "Edition not found")
class SearchEditions(Resource):
    @ns.marshal_with(edition, mask=None)
    @ns.doc("search_editions_by_year",
             description='''
                 Returns the edition that occurred in the ``year`` specified.
             ''',
             params={
                 "year": "The year of the edition"
             })
    def get(self, year):
        if year is None:
            log_request(request.method, request.path, 404)
            return jsonify({"error": "Missing 'year' parameter"}), 404

        # Adicionando condicional somente para os anos com editions existentes
        if not (2016 <= year <= 2023):
            log_request(request.method, request.path, 404)
            return jsonify({"error": "Year not within range (2016-2023)"}), 404

        matched_editions = [e for e in editions_db if e["Year"] == int(year)]
        if matched_editions:
            log_request(request.method, request.path, 200)
            return matched_editions, 200
        else:
            log_request(request.method, request.path, 404)
            return jsonify({"error": "Edition not found for year {}".format(year)}), 404

@ns.route("/<int:id>/papers")
@ns.response(404, "Edition not found")
class PapersByEdition(Resource):
    @ns.marshal_list_with(paper, mask=None)
    @ns.doc("get_papers_by_id", 
        description='''
            Returns all the papers that were published in the edition specified by the ``id``.
        ''',
        params={
            "id": "The edition unique identifier"
        }
    )
    def get(self, id):
        edition = next((e for e in editions_db if e["Edition_id"] == id), None)
        if edition is None:
            log_request(request.method, request.path, 404)
            return jsonify({"error": "Edition not found"}), 404
        papers_in_edition = [
            paper for paper in papers_db if paper["Paper_id"] in edition["Papers"]
        ]
        log_request(request.method, request.path, 200)
        return papers_in_edition
