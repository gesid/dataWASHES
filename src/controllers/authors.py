from flask_restx import Resource, Namespace, fields
from src.server.instance import server
import json

author = server.getApi().model('Author', {
    'Author_id': fields.Integer(description='The author unique identifier'),
    'Name': fields.String(description='Author\'s name', ),
    'State': fields.String(description='Author\'s state'),
    'Institution': fields.String(description='Author\' institution'),
    'Papers': fields.List(fields.Integer, description='IDs of the author\'s published papers')
})

ns = Namespace('Authors')

with open('data/authors.json', 'r', encoding='utf8') as authors_file:
    authors_db = json.load(authors_file)

@ns.route('/')
class AuthorsList(Resource):
    @ns.doc('list_authors')
    @ns.marshal_list_with(author)
    def get(self):
        return authors_db
