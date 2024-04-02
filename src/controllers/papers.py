from flask import request, jsonify
from flask_restx import Resource, Namespace
from resouces import papers_db
from models import paper, abstracts

ns = Namespace(name="Papers", path="/papers")

@ns.route("/")
class PapersList(Resource):

    @ns.marshal_list_with(paper, mask=None)
    @ns.doc(
        "list_papers",
        params={
            "year": "The paper year of publishment",
            "id": "The paper identifier",
            "type": "The type of the paper",
            "name": "The name of at list one of the authors",
            "institution": "The institution name of at least one of the authors",
            "state": "The state acronym of at least one of the authors",
            "abstract": "The abstract of the paper",
            "resumo": "O resumo do artigo",
            "keyword": "Papers keyword",
            "search": "Generic word present in title or abstract of papers",
        }, 
        description='''
            Returns all the paper in the dataset.
            The list of paper can be filtered using the header arguments specified below.
        '''
    )
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
        generic_query = request.args.get("search")

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
        for paper in papers_db:
            if paper["Paper_id"] == id:
                return paper
        ns.abort(404, message=f"Paper {id} not found")


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
            return jsonify({"error": "Missing 'title' parameter"}), 400
        matched_papers = [p for p in papers_db if keyword.lower() in p["Title"].lower()]
        return matched_papers


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
        matched_papers = [p for p in papers_db if p["Year"] == year]
        return matched_papers


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
        abstracts = [{"Paper_id": p["Paper_id"], "Abstract": p["Abstract"]} for p in papers_db]
        return abstracts
