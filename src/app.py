from flask import render_template
from controllers import authorsNs, editionsNs, papersNs
from server import server

@server.app.route('/swagger')
def swagger_template():
    return render_template('swagger_ui.html')

server.api.add_namespace(editionsNs)
server.api.add_namespace(papersNs)
server.api.add_namespace(authorsNs)

server.run()
