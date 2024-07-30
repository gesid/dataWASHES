from flask_restx import fields
from server import server
from .paging import paging_model_construct

paperAuthor = server.getApi().model(
    "Paper Author",
    {
        "Name": fields.String(description="Author's name", example="Maria"),
        "Institution": fields.String(
            description="Author' institution", example="Universidade Federal do Cariri"
        ),
        "State": fields.String(description="Author's state", exmple="CE", example="CE"),
        "Author_id": fields.Integer(
            description="The author unique identifier", example="34"
        ),
    },
)

paper = server.getApi().model(
    "Paper",
    {
        "Authors": fields.List(
            fields.Nested(paperAuthor),
            description="A list of the paper authors IDs"
        ),
        "Paper_id": fields.Integer(
            description="The paper unique identifier", example="3"
        ),
        "Title": fields.String(
            description="Paper title",
            example="Um Modelo para o Gerenciamento de Padrões de Projeto em Java",
        ),
        "Year": fields.Integer(
            description="Publication year of the paper", example="2022"
        ),
        "Abstract": fields.String(
            description="Abstract of the paper",
            example="Design  patterns  are  defined  as  reusable  solutions  to  recurring problems. These solutions...",
        ),
        "Resumo": fields.String(
            description="Resumo do artigo",
            example="Os padrões de projeto são definidos como soluções reusáveis para problemas  recorrentes.  Essas...",
        ),
        "Keywords": fields.String(
            description="Paper keywords",
            example="Java, Modelo, Gerenciamento"
        ),
        "Type": fields.String(
            description="The type of publication",
            enum=["Short paper", "Poster", "Full paper"]
        ),
        "Download_link": fields.String(
            description="A link to download the paper",
            example="https://example.com"
        ),
        "References": fields.List(
            fields.String,
            description="List of references used in the paper",
        ),
        "Cited_by": fields.List(
            fields.String,
            description="List of articles that cite this article",
        ),
        "Updated_in": fields.String(
            description="Date of last update of the ``Cited_by`` field",
            example="2024-04-10"
        ),
    },
)

paper_paging = paging_model_construct("Paper Paging", paper)

abstracts = server.getApi().model(
    "Abstract",
    {
        "Paper_id": fields.Integer(description="The paper unique identifier", example="7"),
        "Abstract": fields.String(description="The abstract of the paper", example="Continuous  learning  of  software...")
    }
)

# Adicionando modelo para representar as referências de um artigo
reference = server.getApi().model(
    "Reference",
    {
        "Paper_id": fields.Integer(
            description="The paper unique identifier", example="3"
        ),
        "References": fields.List(
            fields.String,
            description="List of references used in the paper",
        ),
    },
)

# Adicionado modelo para representar as citações de um artigo
citation = server.getApi().model(
    "Citation",
    {
        "Paper_id": fields.Integer(
            description="The paper unique identifier", example="3"
        ),
        "Cited_by": fields.List(
            fields.String,
            description="List of articles that cite this article",
        ),
    },
)
