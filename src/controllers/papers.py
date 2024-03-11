from flask import request, jsonify
from flask_restx import Resource, Namespace, fields
from src.server.instance import server
import json

ns = Namespace("papers")

author = server.getApi().model(
    "Paper Author",
    {
        "Name": fields.String(description="Author's name", example="Maria"),
        "Institution": fields.String(
            description="Author' institution", example="Universidade Federal do Cariri"
        ),
        "State": fields.String(description="Author's state", exmple="CE", example="CE"),
        "Author_id": fields.Integer(
            description="The author unique identifier", example="34"
        ),
    },
)

paper = server.getApi().model(
    "Paper",
    {
        "Authors": fields.List(
            fields.Nested(author), description="A list of the paper authors IDs"
        ),
        "Paper_id": fields.Integer(
            description="The paper unique identifier", example="3"
        ),
        "Title": fields.String(
            description="Paper title",
            example="Um Modelo para o Gerenciamento de Padrões de Projeto em Java",
        ),
        "Year": fields.Integer(
            description="Publication year of the paper", example="2022"
        ),
        "Abstract": fields.String(
            description="Abstract of the paper",
            example="Design  patterns  are  defined  as  reusable  solutions  to  recurring problems. These solutions...",
        ),
        "Resumo": fields.String(
            description="Resumo do artigo",
            example="Os padrões de projeto são definidos como soluções reusáveis para problemas  recorrentes.  Essas...",
        ),
        "Keywords": fields.String(
            description="Paper keywords", example="Java, Modelo, Gerenciamento"
        ),
        "Type": fields.String(
            description="The type of publication", enum=["Curto", "Poster", "Completo"]
        ),
        "Download_link": fields.String(
            description="A link to download the paper", example="https://example.com"
        ),
    },
)

with open("data/papers.json", "r", encoding="utf8") as papers_file:
    papers_db = json.load(papers_file)


@ns.route("/")
class PapersList(Resource):

    @ns.doc(
        "list_papers",
        params={
            "year": "An year",
            "id": "A paper ID",
            "type": "A type of paper",
            "name": "A author name",
            "institution": "An institution",
            "state": "A state",
            "abstract": "A abstract",
            "resumo": "Um resumo",
        },
    )
    @ns.marshal_list_with(paper)
    def get(self):
        year = request.args.get("year")
        paper_id = request.args.get("id")
        paper_type = request.args.get("type")
        author_name = request.args.get("name")
        institution_name = request.args.get("institution")
        author_state = request.args.get("state")
        abstract_query = request.args.get("abstract")
        resumo_query = request.args.get("resumo")
        keyword = request.args.get("keyword")
        generic_query = request.args.get("pesquisa")

        filtered_papers = papers_db

        if year:
            filtered_papers = [
                paper for paper in filtered_papers if str(paper["Year"]) == year
            ]

        if paper_id:
            filtered_papers = [
                paper for paper in filtered_papers if str(paper["Paper_id"]) == paper_id
            ]

        if paper_type:
            filtered_papers = [
                paper for paper in filtered_papers if paper["Type"] == paper_type
            ]

        if author_name:
            filtered_papers = [
                paper
                for paper in filtered_papers
                if any(author["Name"] == author_name for author in paper["Authors"])
            ]

        if institution_name:
            filtered_papers = [
                paper
                for paper in filtered_papers
                if any(
                    author["Institution"] == institution_name
                    for author in paper["Authors"]
                )
            ]

        if author_state:
            filtered_papers = [
                paper
                for paper in filtered_papers
                if any(author["State"] == author_state for author in paper["Authors"])
            ]

        if abstract_query:
            filtered_papers = [
                paper
                for paper in filtered_papers
                if abstract_query.lower() in paper["Abstract"].lower()
            ]

        if resumo_query:
            filtered_papers = [
                paper
                for paper in filtered_papers
                if resumo_query.lower() in paper["Resumo"].lower()
            ]

        if keyword:
            filtered_papers = [
                paper
                for paper in filtered_papers
                if keyword.lower() in paper["Keywords"].lower()
            ]

        if generic_query:
            filtered_papers = [
                paper
                for paper in filtered_papers
                if generic_query.lower() in paper["Title"].lower()
                or generic_query.lower() in paper["Abstract"].lower()
            ]

        return filtered_papers


@ns.route("/<int:id>")
@ns.response(404, "Paper not found")
class PaperById(Resource):
    @ns.doc("get_paper_by_id")
    @ns.marshal_with(paper)
    def get(self, id):
        for p in papers_db:
            if p["Paper_id"] == id:
                return p
        ns.abort(404, message="Paper {} not found".format(id))


@ns.route("/search")
class SearchPapersByTitle(Resource):
    @ns.doc("search_papers_by_title")
    def get(self):
        keyword = request.args.get("title")
        if not keyword:
            return jsonify({"error": "Missing 'title' parameter"}), 400
        matched_papers = [p for p in papers_db if keyword.lower() in p["Title"].lower()]
        return matched_papers


@ns.route("/by-year/<int:year>")
class GetPapersByYear(Resource):
    @ns.doc("get_papers_by_year")
    def get(self, year):
        matched_papers = [p for p in papers_db if p["Year"] == year]
        return matched_papers


@ns.route("/abstracts")
class GetPaperAbstracts(Resource):
    @ns.doc("get_paper_abstracts")
    def get(self):
        abstracts = [{"Paper_id": p["Paper_id"], "Abstract": p["Abstract"]} for p in papers_db]
        return abstracts
