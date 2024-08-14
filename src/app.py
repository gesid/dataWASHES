from flask import make_response
from controllers import authorsNs, editionsNs, papersNs
from server import server
from api_utils import convert_to_csv


@server.api.representation('text/csv')
def data_csv(data, code, headers):
    """Get result in csv"""
    resp = make_response(convert_to_csv(data), code)
    resp.headers.extend(headers)
    return resp


server.api.add_namespace(editionsNs)
server.api.add_namespace(papersNs)
server.api.add_namespace(authorsNs)

server.run()
