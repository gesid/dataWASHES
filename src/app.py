from server import server
from controllers import authorsNs, editionsNs, papersNs
    
server.api.add_namespace(editionsNs)
server.api.add_namespace(papersNs)
server.api.add_namespace(authorsNs)

server.run()
