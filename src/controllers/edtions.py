from flask import jsonify
from flask_restx import Resource, Namespace
import json

ns = Namespace('Editions')

with open('data/editions.json', 'r', encoding='utf8') as editions_file:
    editions_db = json.load(editions_file)

@ns.route('/')
class EditionsList(Resource):
    def get(self):
        return jsonify(editions_db)
