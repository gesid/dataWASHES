from flask_restx import fields, Model
from server import server

paging_model = server.getApi().model(
    "Paging",
    {
        "page": fields.Integer(description="The current page number", example="5"),
        "per_page": fields.Integer(description="Quantity of authors in one page", example="20"),
        "page_count": fields.Integer(description="Total number of pages", example="14"),
        "total_count": fields.Integer(description="Total number of authors", example="263"),
    }
)

links_model = server.getApi().model(
    "Links",
    {
        "self": fields.String(description="Link to the current page", example="/path?page=5&per_page=20"),
        "first": fields.String(description="Link to the first page", example="/path?page=1&per_page=20"),
        "previous": fields.String(description="Link to the previous page", example="/path?page=4&per_page=20"),
        "next": fields.String(description="Link to the next page", example="/path?page=6&per_page=20"),
        "last": fields.String(description="Link to the last page", example="/path?page=14&per_page=20"),
    }
)

def paging_model_construct(name: str, model: Model) -> Model:
    """Return a paging model"""

    return server.getApi().model(
        name,
        {
            "data": fields.List(
                fields.Nested(model),
                description="Response data"
            ),
            "paging": fields.Nested(paging_model, description="Paging information"),
            "links": fields.Nested(links_model, description="Links to other pages"),
        }
    )
