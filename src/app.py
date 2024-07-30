from controllers import authorsNs, editionsNs, papersNs, exemploNs
from server import server

server.api.add_namespace(editionsNs)
server.api.add_namespace(papersNs)
server.api.add_namespace(authorsNs)
server.api.add_namespace(exemploNs)

server.run()
