from flask_restx import Resource, Namespace
from resouces.database_conn import DatabaseConn

ns = Namespace(name='Exemplo', path='/exemplo')

@ns.route("/authors")
class Exemplo(Resource):
    def get(self):
        results = DatabaseConn.command("SELECT * FROM Authors")
        return results
    
@ns.route("/papers")
class Exemplo(Resource):
    def get(self):
        results = DatabaseConn.command("SELECT * FROM Papers")
        return results
    
@ns.route("/editions")
class Exemplo(Resource):
    def get(self):
        results = DatabaseConn.command("SELECT * FROM Editions")
        return results