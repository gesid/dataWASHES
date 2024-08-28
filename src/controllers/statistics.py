from flask_restx import Namespace, Resource  # type: ignore
from resources import StatisticsCalculator
from models import author, paper, error_model, states_rank_model, institutions_rank_model, keywords_cloud_model

ns = Namespace("Statistics", path='/statistics')


@ns.route("/authors/rank-by/publications/<int:rank_size>/")
class MostPublishedAuthors(Resource):
    """
    Most published authors route
    """

    @ns.response(400, "Invalid parameter", error_model)
    @ns.marshal_list_with(author, mask=None)
    @ns.doc("authors_rank_publications",
            description='''
                Returns the rank of authors by number of publications
        ''',
            params={
                "rank_size": "Total number of papers to returns (<= 100)"
            }
            )
    def get(self, rank_size: int):
        """
        Rank authors by number of publications
        """
        if rank_size <= 0 or rank_size > 100:
            ns.abort(400, message="Invalid value for rank_size parameter (0 < rank_size <= 100)", error_code=400)
        return StatisticsCalculator.authors_rank()[:rank_size], 200


@ns.route("/papers/rank-by/citations/<int:rank_size>")
class MostCitedPaper(Resource):
    """
    Most cited papers route
    """

    @ns.response(400, "Invalid parameter", error_model)
    @ns.marshal_list_with(paper, mask=None)
    @ns.doc("papers_rank_citations",
            description='''
                Returns the rank of authors by number of publications
            ''',
            params={
                "rank_size": "Total number of papers to returns (<= 100)"
            }
            )
    def get(self, rank_size: int):
        """
        Rank papers by number of citations
        """
        if rank_size <= 0 or rank_size > 100:
            ns.abort(400, message="Invalid value for rank_size parameter (0 < rank_size <= 100)", error_code=400)
        return StatisticsCalculator.most_cited_papers()[:rank_size], 200


@ns.route("/institutions/rank-by/publications/<int:rank_size>")
class InstitutionRank(Resource):
    """
    Institution rank route
    """

    @ns.response(400, "Invalid parameter", error_model)
    @ns.marshal_list_with(institutions_rank_model, mask=None)
    @ns.doc("institution_rank",
            description='''
                Returns the rank of institutions by number of publications
            ''',
            params={
                "rank_size": "Total number of papers to returns (<= 100)"
            }
            )
    def get(self, rank_size: int):
        """
        Rank institutions by number of publications
        """
        if rank_size <= 0 or rank_size > 100:
            ns.abort(400, message="Invalid value for rank_size parameter (0 < rank_size <= 100)", error_code=400)
        return StatisticsCalculator.institution_rank()[:rank_size], 200


@ns.route("/states/rank-by/publications/<int:rank_size>")
class StatesRank(Resource):
    """
    States rank route
    """

    @ns.response(400, "Invalid parameter", error_model)
    @ns.marshal_list_with(states_rank_model, mask=None)
    @ns.doc("states_rank",
            description='''
                Returns the rank of states by number of publications
            ''',
            params={
                "rank_size": "Total number of papers to returns (<= 100)"
            }
            )
    def get(self, rank_size: int):
        """
        Rank states by number of publications
        """
        if rank_size <= 0 or rank_size > 100:
            ns.abort(400, message="Invalid value for rank_size parameter (0 < rank_size <= 100)", error_code=400)
        return StatisticsCalculator.states_rank()[:rank_size], 200


@ns.route("/keywords/cloud/")
class KeywordsCloud(Resource):
    """
    Keywords cloud route
    """

    @ns.marshal_list_with(keywords_cloud_model, mask=None)
    @ns.doc("keywords_cloud",
            description='''
                Returns the paper's keywords cloud
            ''',
            )
    def get(self):
        """
        Count occurrence of keywords
        """
        return StatisticsCalculator.keywords_cloud(), 200
