from server.instance import server
from controllers.authors import ns as authorsNs
from controllers.editions import ns as editionsNs
from controllers.papers import ns as papersNs
    
server.api.add_namespace(editionsNs)
server.api.add_namespace(papersNs)
server.api.add_namespace(authorsNs)

server.run()
