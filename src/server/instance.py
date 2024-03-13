from flask import Flask
from flask_restx import Api

class Server():
    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(
            self.app,
            title='dataWASHES API',
            description='An API to request data on what the WASHES community discussed about software engineering economics in the last few years.',
            doc='/'
        )

    def run(self):
        self.app.run( debug=True )

    def getApi(self):
        return self.api
    
    def getApp(self):
        return self.app

server = Server()
