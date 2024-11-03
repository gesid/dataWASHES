from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from datetime import timedelta

class Server():
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.app.config['CORS_HEADERS'] = 'Content-Type'
        self.app.config['JWT_SECRET_KEY'] = 'washes_secret_key_2024_!@#erdce2324fwdsvs'
        self.app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
        self.api = Api(
            self.app,
            title='dataWASHES API',
            description='dataWASHES is an open source Application Programming Interface (API) that aims to facilitate streamlined programmatic access to the Workshop on Social, Human, and Economic Aspects of Software (WASHES) proceedings.',
            doc='/'
        )
        
        self.jwt = JWTManager(self.app)
        self.conn = create_engine(SQLALCHEMY_DATABASE_URI)

    def run(self):
        self.app.run()

    def getApi(self):
        return self.api
    
    def getApp(self):
        return self.app
    
    def getConn(self):
        return self.conn

server = Server()
