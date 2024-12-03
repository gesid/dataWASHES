from flask import Flask, render_template
from flask_restx import Api  # type: ignore
from flask_cors import CORS  # type: ignore
import os

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

        CORS(self.__app)
        self.__app.config['CORS_HEADERS'] = 'Content-Type'

        self.__api = Api(
            self.__app,
            title='dataWASHES API',
            description='dataWASHES is an open source Application Programming Interface (API) that aims to facilitate '
                        'streamlined programmatic access to the Workshop on Social, Human, and Economic Aspects of '
                        'Software (WASHES) proceedings.',
            doc='/doc/',
        )

    @property
    def api(self) -> Api:
        return self.__api

    @api.setter
    def api(self, value) -> None:
        pass

    @property
    def app(self) -> Flask:
        return self.__app

    @app.setter
    def app(self, value) -> None:
        pass

    # def run(self) -> None:
    #     self.app.run(debug=True)

    def run(self) -> None:
        port = int(os.environ.get('PORT', 5000))
        self.app.run(debug=True, host='0.0.0.0', port=port)

server: Server = Server()
