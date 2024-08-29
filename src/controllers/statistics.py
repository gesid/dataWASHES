from flask_restx import Namespace, Resource  # type: ignore
from resources import StatisticsCalculator
from models import (
    author,
    paper,
    error_model,
    states_rank_model,
    institutions_rank_model,
    keywords_cloud_model,
    languages_rank_model,
    publications_by_year_model,
)
from api_utils import abort_execution

ns = Namespace("Statistics", path='/statistics')
MAX_RANK_SIZE: int = 100


def abort_if_invalid_rank_size(rank_size: int) -> None:
    if rank_size <= 0 or rank_size > MAX_RANK_SIZE:
        abort_execution(ns, f"Invalid value for rank_size parameter (0 < rank_size <= {MAX_RANK_SIZE})", 400)


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
                "rank_size": f"Total number of authors to return (<= {MAX_RANK_SIZE})"
            }
            )
    def get(self, rank_size: int):
        """
        Rank authors by number of publications
        """
        abort_if_invalid_rank_size(rank_size)
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
                "rank_size": f"Total number of papers to return (<= {MAX_RANK_SIZE})"
            }
            )
    def get(self, rank_size: int):
        """
        Rank papers by number of citations
        """
        abort_if_invalid_rank_size(rank_size)
        return StatisticsCalculator.most_cited_papers()[:rank_size], 200


@ns.route("/papers/publications/by-years")
class PublicationsByYear(Resource):
    """
    Papers publications by year route
    """

    @ns.marshal_list_with(publications_by_year_model, mask=None)
    @ns.doc("papers_publications_by_years",
            description='''
                Returns the number of papers published by the years 
            ''',
            )
    def get(self):
        """
        Publications by years.
        """
        return StatisticsCalculator.publications_by_years(), 200


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
                "rank_size": f"Total number of institutions to return (<= {MAX_RANK_SIZE})"
            }
            )
    def get(self, rank_size: int):
        """
        Rank institutions by number of publications
        """
        abort_if_invalid_rank_size(rank_size)
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
                "rank_size": f"Total number of states to return (<= {MAX_RANK_SIZE})"
            }
            )
    def get(self, rank_size: int):
        """
        Rank states by number of publications
        """
        abort_if_invalid_rank_size(rank_size)
        return StatisticsCalculator.states_rank()[:rank_size], 200


@ns.route("/languages/rank-by/publications/<int:rank_size>")
class LanguagesRank(Resource):
    """
    Language rank route
    """

    @ns.marshal_list_with(languages_rank_model, mask=None)
    @ns.doc("languages_rank",
            description='''
                Returns the rank os languages by number of publications
            ''',
            )
    def get(self, rank_size: int):
        """
        Rank languages by number of publications
        """
        abort_if_invalid_rank_size(rank_size)
        return StatisticsCalculator.papers_by_languages()[:rank_size], 200


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
