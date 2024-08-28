from flask_restx import fields
from server import server
from .paging import paging_model_construct

author = server.get_api().model(
    "Author",
    {
        "Author_id": fields.Integer(
            description="The author unique identifier",
            example="10"
        ),
        "Name": fields.String(
            description="Author's name",
            example="João"
        ),
        "State": fields.String(
            description="Author's state",
            example="CE"
        ),
        "Institution": fields.String(
            description="Author' institution",
            example="UFCA"
        ),
        "Papers": fields.List(
            fields.Integer,
            description="IDs of the author's published papers",
            example="[0, 3, 12]",
        ),
    },
)

author_paging = paging_model_construct("Author Paging", author)
