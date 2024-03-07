from flask_restx import Resource, Namespace, fields
from flask import jsonify, request
from src.server.instance import server
import json

ns = Namespace("editions")

chairs = server.getApi().model(
    "Chair",
    {
        "Name": fields.String(description="Chair's name", example="João"),
        "Instituition": fields.String(
            description="Chair's institution",
            example="UFCA - Universidade Federal do Cariri",
        ),
        "State": fields.String(description="Chair's state", example="CE"),
    },
)

edition = server.getApi().model(
    "Edition",
    {
        "Year": fields.Integer(
            description="Edition year of occurrence", example="2023"
        ),
        "Edition_id": fields.Integer(
            description="The edition unique identifier", example="7"
        ),
        "Title": fields.String(
            description="Edition's title",
            example="Anais do VIII Workshop sobre Aspectos Sociais, Humanos e Econômicos de Software",
        ),
        "Location": fields.String(
            description="Edition's location", example="Cabo Branco - PB"
        ),
        "Date": fields.String(
            description="Edition's date of occurrence", example="06/08/2023"
        ),
        "Proceedings": fields.String(
            description="Edition's preceedings",
            example="https://sol.sbc.org.br/index.php/washes/issue/view/1116",
        ),
        "Papers": fields.List(
            fields.Integer,
            description="Papers IDs of the edition",
            example="[0, 2, 12, 72]",
        ),
        "Chairs": fields.List(fields.Nested(chairs), description="Edition's chairs"),
    },
)

with open("data/editions.json", "r", encoding="utf8") as editions_file:
    editions_db = json.load(editions_file)

with open("data/papers.json", "r", encoding="utf8") as papers_file:
    papers_db = json.load(papers_file)

@ns.route("/")
class EditionsList(Resource):
    @ns.marshal_list_with(edition)
    @ns.doc("list_editions")
    def get(self):
        return editions_db


@ns.route("/<int:id>")
@ns.response(404, "Edition not found")
class EditionById(Resource):
    @ns.doc("get_edition_by_id")
    def get(self, id):
        edition = next((e for e in editions_db if e["Edition_id"] == id), None)
        if edition is None:
            return jsonify({"error": "Edition not found"}), 404
        return edition


@ns.route("/search")
class SearchEditions(Resource):
    @ns.doc("search_editions_by_year")
    def get(self):
        year = request.args.get("year")
        if not year:
            return jsonify({"error": "Missing 'year' parameter"}), 400
        matched_editions = [e for e in editions_db if e["Year"] == int(year)]
        return matched_editions


@ns.route("/<int:edition_id>/papers")
@ns.response(404, "Edition not found")
class PapersByEdition(Resource):
    @ns.doc("get_papers_by_edition_id")
    def get(self, edition_id):
        edition = next((e for e in editions_db if e["Edition_id"] == edition_id), None)
        if edition is None:
            return jsonify({"error": "Edition not found"}), 404
        papers_in_edition = [
            paper for paper in papers_db if paper["Paper_id"] in edition["Papers"]
        ]
        return papers_in_edition
