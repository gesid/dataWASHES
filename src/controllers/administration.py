from flask_restx import Resource, Namespace
from resouces.database_conn import DatabaseConn

ns = Namespace(name='Administration', path='/administration')

@ns.route("/authors")
class Administration(Resource):
    def get(self):
        results = DatabaseConn.command("SELECT * FROM Authors")
        return results
    
@ns.route("/papers")
class Administration(Resource):
    def get(self):
        results = DatabaseConn.command("SELECT * FROM Papers")
        return results
    
@ns.route("/editions")
class Administration(Resource):
    def get(self):
        results = DatabaseConn.command("SELECT * FROM Editions")
        return results