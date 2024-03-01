from flask_restx import Resource, Namespace, fields
from src.server.instance import server
import json

ns = Namespace('Editions')

chairs = server.getApi().model('Chair', {
    'Name': fields.String(description='Chair\'s name', example='João'),
    'Instituition': fields.String(description='Chair\'s institution', example='UFCA - Universidade Federal do Cariri'),
    'State': fields.String(description='Chair\'s state', example='CE')
})

edition = server.getApi().model('Edition', {
    'Year': fields.Integer(description='Edition year of occurrence', example='2023'),
    'Edition_id': fields.Integer(description='The edition unique identifier', example='7'),
    'Title': fields.String(description='Edition\'s title', example='Anais do VIII Workshop sobre Aspectos Sociais, Humanos e Econômicos de Software'),
    'Location': fields.String(description='Edition\'s location', example='Cabo Branco - PB'),
    'Date': fields.String(description='Edition\'s date of occurrence', example='06/08/2023'),
    'Proceedings': fields.String(description='Edition\'s preceedings', example='https://sol.sbc.org.br/index.php/washes/issue/view/1116'),
    'Papers': fields.List(fields.Integer, description='Papers IDs of the edition', example='[0, 2, 12, 72]'),
    'Chairs': fields.List(fields.Nested(chairs), description='Edition\'s chairs')
})

with open('data/editions.json', 'r', encoding='utf8') as editions_file:
    editions_db = json.load(editions_file)

@ns.route('/')
class EditionsList(Resource):
    @ns.marshal_list_with(edition)
    @ns.doc('list_editions')
    def get(self):
        return editions_db
