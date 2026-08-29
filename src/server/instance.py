import os

from flask import Flask, jsonify, render_template
from flask_cors import CORS  # type: ignore
from flask_restx import Api  # type: ignore


class Server:
    def __init__(self):
        self.__app = Flask(
            __name__,
            template_folder='../templates',
            static_folder='../static',
        )

        @self.__app.route('/')
        def swagger_template():
            return render_template('swagger_ui.html')

        # Restringe o CORS às rotas públicas da API. Os namespaces são
        # registrados em app.py com os paths /papers, /authors, /editions
        # e /statistics.
        CORS(self.__app, resources={
            r"/papers/*": {"origins": "*"},
            r"/authors/*": {"origins": "*"},
            r"/editions/*": {"origins": "*"},
            r"/statistics/*": {"origins": "*"},
        })
        self.__app.config['CORS_HEADERS'] = 'Content-Type'

        @self.__app.errorhandler(404)
        def handle_not_found(_error):
            return jsonify({"error_code": 404, "message": "Route not found"}), 404

        self.__api = Api(
            self.__app,
            title='dataWASHES',
            description='dataWASHES is an open source Application Programming Interface (API) that aims to facilitate '
                        'streamlined programmatic access to the Workshop on Social, Human, and Economic Aspects of '
                        'Software (WASHES) proceedings.',
            doc='/doc/',
        )

    @property
    def api(self) -> Api:
        return self.__api

    @property
    def app(self) -> Flask:
        return self.__app

    def run(self) -> None:
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', '').strip().lower() in {'1', 'true', 'yes', 'on'}
        self.app.run(debug=debug, host='0.0.0.0', port=port)


server: Server = Server()
