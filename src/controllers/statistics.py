from flask_restx import Namespace, Resource  # type: ignore
from resouces import StatisticsCalculator
from models import author, paper, error_model

ns = Namespace("Statistics", path='/statistics')


@ns.route("/author/rank/publications/<int:rank_size>/")
class MostPublishedAuthor(Resource):
    """
    Most published author route
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
        return StatisticsCalculator.authors_rank(rank_size), 200


@ns.route("/papers/rank/citations/<int:rank_size>")
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
        return StatisticsCalculator.most_cited_papers(rank_size), 200
