from flask_restx import fields
from server.instance import server

states_rank_model = server.get_api().model(
    "States Rank",
    {
        "state": fields.String(description="The first author state", example="CE"),
        "publications": fields.Integer(description="The number of publications", example=10)
    }
)

institutions_rank_model = server.get_api().model(
    "Institutions Rank",
    {
        "institution": fields.String(description="The first author institution", example="Universidade Federal do Cariri (UFCA)"),
        "publications": fields.Integer(description="The number of publications", example=10)
    }
)

keywords_cloud_model = server.get_api().model(
    "Keywords Cloud",
    {
        "keyword": fields.String(description="The keyword used in some paper", example="software engineering"),
        "count": fields.Integer(description="The number of occurrences", example=10)
    }
)
