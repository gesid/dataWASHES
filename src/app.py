from controllers import authorsNs, editionsNs, papersNs
from server import server

server.api.add_namespace(editionsNs)
server.api.add_namespace(papersNs)
server.api.add_namespace(authorsNs)

server.run()
