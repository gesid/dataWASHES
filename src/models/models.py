from flask_restx import fields
from server.instance import server

chairs = server.getApi().model(
    "Chair",
    {
        "Name": fields.String(description="Chair's name", example="João"),
        "Instituition": fields.String(
            description="Chair's institution",
            example="UFCA - Universidade Federal do Cariri",
        ),
        "State": fields.String(description="Chair's state", example="CE"),
    },
)

edition = server.getApi().model(
    "Edition",
    {
        "Year": fields.Integer(
            description="Edition year of occurrence", example="2023"
        ),
        "Edition_id": fields.Integer(
            description="The edition unique identifier", example="7"
        ),
        "Title": fields.String(
            description="Edition's title",
            example="Anais do VIII Workshop sobre Aspectos Sociais, Humanos e Econômicos de Software",
        ),
        "Location": fields.String(
            description="Edition's location", example="Cabo Branco - PB"
        ),
        "Date": fields.String(
            description="Edition's date of occurrence", example="06/08/2023"
        ),
        "Proceedings": fields.String(
            description="Edition's preceedings",
            example="https://sol.sbc.org.br/index.php/washes/issue/view/1116",
        ),
        "Papers": fields.List(
            fields.Integer,
            description="Papers IDs of the edition",
            example="[0, 2, 12, 72]",
        ),
        "Chairs": fields.List(fields.Nested(chairs), description="Edition's chairs"),
    },
)

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