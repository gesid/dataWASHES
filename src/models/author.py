from flask_restx import fields
from server.instance import server

author = server.getApi().model(
    "Author",
    {
        "Author_id": fields.Integer(description="The author unique identifier", example="10"),
        "Name": fields.String(description="Author's name", example="João"),
        "State": fields.String(description="Author's state", example="CE"),
        "Institution": fields.String(description="Author' institution", example="UFCA"),
        "Papers": fields.List(
            fields.Integer,
            description="IDs of the author's published papers",
            example="[0, 3, 12]",
        ),
    },
)

paging_model = server.getApi().model(
    "Paging",
    {
        "page": fields.Integer(description="The current page number", example="5"),
        "per_page": fields.Integer(description="Quantity of authors in one page", example="20"),
        "page_count": fields.Integer(description="Total number of pages", example="27"),
        "total_count": fields.Integer(description="Total number of authors", example="263"),
    }
)

links_model = server.getApi().model(
    "Links",
    {
        "self": fields.String(description="", example="/authors?page=5&per_page=20"),
        "first": fields.String(description="", example="/authors?page=1&per_page=20"),
        "previous": fields.String(description="", example="/authors?page=4&per_page=20"),
        "next": fields.String(description="", example="/authors?page=6&per_page=20"),
        "last": fields.String(description="", example="/authors?page=27&per_page=20"),
    }
)

author_paging = server.getApi().model(
    "AuthorPaging",
    {
        "data": fields.List(
            fields.Nested(author),
            description="Response data"
        ),
        "paging": fields.Nested(paging_model),
        "links": fields.Nested(links_model),
    }
)
