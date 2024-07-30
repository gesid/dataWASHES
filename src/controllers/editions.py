from flask_restx import Resource, Namespace
from flask import jsonify
from resouces import editions_db, papers_db
from models import edition, edition_paging, paper_paging
from api_utils import paginate

ns = Namespace(name='Editions', path='/editions')

@ns.route("/")
class EditionsList(Resource):
    @ns.marshal_list_with(edition_paging, mask=None)
    @ns.doc("list_editions", 
        description='''
            Returns all the editions in the dataset.
        ''',
        params={
            "page": "The page number to retrieve",
            "per_page": "The number of editions to display per page"
        }
    )
    def get(self):
        try:
            editions = paginate(editions_db)
        except ValueError as e:
            ns.abort(400, message=str(e))
        return editions

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
            return jsonify({"error": "Edition not found"}), 404
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
        }
    )
    def get(self, year):
        if year is None:
            return jsonify({"error": "Missing 'year' parameter"}), 404
        matched_editions = [e for e in editions_db if e["Year"] == int(year)]
        return matched_editions

@ns.route("/<int:id>/papers")
@ns.response(404, "Edition not found")
class PapersByEdition(Resource):
    @ns.marshal_list_with(paper_paging, mask=None)
    @ns.doc("get_papers_by_id", 
        description='''
            Returns all the papers that were published in the edition specified by the ``id``.
        ''',
        params={
            "id": "The edition unique identifier",
            "page": "The page number to retrieve",
            "per_page": "The number of papers to display per page"
        }
    )
    def get(self, id):
        edition = next((e for e in editions_db if e["Edition_id"] == id), None)
        if edition is None:
            return jsonify({"error": "Edition not found"}), 404
        papers_in_edition = [
            paper for paper in papers_db if paper["Paper_id"] in edition["Papers"]
        ]

        try:
            papers_in_edition = paginate(papers_in_edition)
        except ValueError as e:
            ns.abort(400, message=str(e))
            
        return papers_in_edition
