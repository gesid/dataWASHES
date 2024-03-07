from src.server.instance import server
from src.controllers.authors import ns as authorsNs
from src.controllers.editions import ns as editionsNs
from src.controllers.papers import ns as papersNs
    
server.api.add_namespace(editionsNs)
server.api.add_namespace(papersNs)
server.api.add_namespace(authorsNs)

server.run()