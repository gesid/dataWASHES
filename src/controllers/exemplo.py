from flask_restx import Namespace, Resource
from resources.database_conn import DatabaseConn

ns = Namespace(name="Exemplo", path="/exemplo")


@ns.route("/")
class Exemplo(Resource):
    def get(self):
        results = DatabaseConn.command("SELECT * FROM Authors")
        return results

