from flask import Flask, render_template
from flask_restx import Api  # type: ignore
from flask_cors import CORS  # type: ignore
import os
from flask_jwt_extended import JWTManager
from config import SQLALCHEMY_DATABASE_URI
from datetime import timedelta
import psycopg2

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
        
        self.__app.config['JWT_SECRET_KEY'] = 'washes_secret_key_2024_!@#erdce2324fwdsvs'
        self.__app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

        self.__api = Api(
            self.__app,
            title='dataWASHES API',
            description='dataWASHES is an open source Application Programming Interface (API) that aims to facilitate '
                        'streamlined programmatic access to the Workshop on Social, Human, and Economic Aspects of '
                        'Software (WASHES) proceedings.',
            doc='/doc/',
        )
        
        self.jwt = JWTManager(self.__app)

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
    
    def getConn(self):
        conn = psycopg2.connect(SQLALCHEMY_DATABASE_URI)
        return conn

    # def run(self) -> None:
    #     self.app.run(debug=True)

    def run(self) -> None:
        port = int(os.environ.get('PORT', 5000))
        self.app.run(debug=True, host='0.0.0.0', port=port)

server: Server = Server()
