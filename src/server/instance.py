from flask import Flask, render_template
from flask_restx import Api # type: ignore
from flask_cors import CORS # type: ignore
import pyodbc # type: ignore


class Server():
    def __init__(self):

        self.app = Flask(
            __name__,
             template_folder='../templates',
            static_folder='../static',
        )

        @self.app.route('/')
        def swagger_template():
            return render_template('swagger_ui.html')

        CORS(self.app)
        self.app.config['CORS_HEADERS'] = 'Content-Type'

        self.api = Api(
            self.app,
            title='dataWASHES API',
            description='dataWASHES is an open source Application Programming Interface (API) that aims to facilitate streamlined programmatic access to the Workshop on Social, Human, and Economic Aspects of Software (WASHES) proceedings.',
            doc='/doc/',
        )
        #self.conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=washesDb.mssql.somee.com;DATABASE=washesDb;UID=washes_SQLLogin_1;PWD=gwzzwtovvh')

    def run(self):
        self.app.run(debug=True)

    def getApi(self):
        return self.api

    def getApp(self):
        return self.app

    '''def getConn(self):
        return self.conn'''

server: Server = Server()
