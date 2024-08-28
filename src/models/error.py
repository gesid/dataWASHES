from flask_restx import fields
from server.instance import server

error_model = server.get_api().model(
    "Error",
    {
        "error_code": fields.Integer(
            description="The error code",
            example="404"
        ),
        "message": fields.String(
            description="The error description",
            example="An error has occurred"
        ),
    },
)
