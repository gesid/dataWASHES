from flask_restx import Resource, Namespace
from flask import jsonify
from src.resouces.database import editions_db, papers_db
from src.models.models import edition, paper

ns = Namespace(name='Editions', path='/editions')

@ns.route("/")
class EditionsList(Resource):
    @ns.marshal_list_with(edition, mask=None)
    @ns.doc("list_editions")
    def get(self):
        return editions_db


@ns.route("/<int:id>")
@ns.response(404, "Edition not found")
class EditionById(Resource):
    @ns.marshal_with(edition, mask=None)
    @ns.doc("get_edition_by_id")
    def get(self, id):
        edition = next((e for e in editions_db if e["Edition_id"] == id), None)
        if edition is None:
            return jsonify({"error": "Edition not found"}), 404
        return edition


@ns.route("/by-year/<int:year>")
@ns.response(404, "Edition not found")
class SearchEditions(Resource):
    @ns.marshal_with(edition, mask=None)
    @ns.doc("search_editions_by_year")
    def get(self, year):
        if year is None:
            return jsonify({"error": "Missing 'year' parameter"}), 404
        matched_editions = [e for e in editions_db if e["Year"] == int(year)]
        return matched_editions


@ns.route("/<int:edition_id>/papers")
@ns.response(404, "Edition not found")
class PapersByEdition(Resource):
    @ns.marshal_list_with(paper, mask=None)
    @ns.doc("get_papers_by_edition_id")
    def get(self, edition_id):
        edition = next((e for e in editions_db if e["Edition_id"] == edition_id), None)
        if edition is None:
            return jsonify({"error": "Edition not found"}), 404
        papers_in_edition = [
            paper for paper in papers_db if paper["Paper_id"] in edition["Papers"]
        ]
        return papers_in_edition
