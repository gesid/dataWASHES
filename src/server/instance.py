from flask import Flask, render_template
from flask_restx import Api

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

        self.api = Api(
            self.app,
            title='dataWASHES API',
            description='dataWASHES is an open source Application Programming Interface (API) that aims to facilitate streamlined programmatic access to the Workshop on Social, Human, and Economic Aspects of Software (WASHES) proceedings.',
            doc='/doc/',
        )

    def run(self):
        self.app.run(debug=True)

    def getApi(self):
        return self.api

    def getApp(self):
        return self.app

server = Server()
