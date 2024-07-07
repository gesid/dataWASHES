from server import server
from controllers import authorsNs, editionsNs, papersNs, exemploNs
    
server.api.add_namespace(editionsNs)
server.api.add_namespace(papersNs)
server.api.add_namespace(authorsNs)
server.api.add_namespace(exemploNs)

server.run()
