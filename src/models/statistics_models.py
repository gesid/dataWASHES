from builtins import filter

from flask_restx import fields
from server.instance import server

states_rank_model = server.api.model(
    "States Rank",
    {
        "state": fields.String(description="The first author state", example="CE"),
        "publications": fields.Integer(description="The number of publications", example=10)
    }
)

institutions_rank_model = server.api.model(
    "Institutions Rank",
    {
        "institution": fields.String(description="The first author institution", example="Universidade Federal do Cariri (UFCA)"),
        "publications": fields.Integer(description="The number of publications", example=10)
    }
)

languages_rank_model = server.api.model(
    "Languages Rank",
    {
        "language": fields.String(description="The language of the papers", example="en"),
        "publications": fields.Integer(description="The number of publications in this language", example=10)
    }
)

publications_by_year_model = server.api.model(
    "Publications By Years",
    {
        "year": fields.Integer(description="The year of the papers", example=2024),
        "publications": fields.Integer(description="The number of publications in this year", example=25)
    }
)

keywords_cloud_model = server.api.model(
    "Keywords Cloud",
    {
        "keyword": fields.String(description="The keyword used in some paper", example="software engineering"),
        "count": fields.Integer(description="The number of occurrences", example=10)
    }
)
