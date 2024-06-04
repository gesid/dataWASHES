from flask_restx import Resource, Namespace
from flask import jsonify
from resouces.database_conn import DatabaseConn

ns = Namespace(name='Exemplo', path='/exemplo')

@ns.route("/")
class Exemplo(Resource):
    def get(self):
        results = DatabaseConn.command("SELECT * FROM Authors")
        return jsonify(results)