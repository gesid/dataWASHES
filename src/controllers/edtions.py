from flask_restx import Resource, Namespace, fields
from src.server.instance import server
import json

ns = Namespace('Editions')

chairs = server.getApi().model('Chair', {
    'Name': fields.String(description='Chair\'s name'),
    'Instituition': fields.String(description='Chair\'s institution'),
    'State': fields.String(description='Chair\'s state')
})

edition = server.getApi().model('Edition', {
    'Year': fields.Integer(description='Edition year of occurrence'),
    'Edition_id': fields.Integer(description='The edition unique identifier'),
    'Title': fields.String(description='Edition\'s title'),
    'Location': fields.String(description='Edition\'s location'),
    'Date': fields.String(description='Edition\'s date of occurrence'),
    'Proceedings': fields.String(description='Edition\'s preceedings'),
    'Papers': fields.List(fields.Integer, description='Papers IDs of the edition'),
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
