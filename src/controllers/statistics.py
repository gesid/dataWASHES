from flask_restx import Namespace, Resource # type: ignore

ns = Namespace("Statistics", path='/statistics')

@ns.route("/author/publications/")
class MostPublishedAuthor(Resource):
    """
    Most published author route
    """
    @ns.doc(
        description='''
            Returns the rank of authors by number of publications
        '''
    )
    def get(self):
        """
        Rank authors by number of publications
        """
        return 1
