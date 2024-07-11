from flask_restx import Resource, Namespace
from resouces.database_conn import DatabaseConn
import hashlib
from flask_jwt_extended import create_access_token, jwt_required
from flask import request

ns = Namespace(name='Administration', path='/administration')

@ns.route("/createusers")
class Administration(Resource):
    @ns.doc(
        "createusers", 
        description='''
        Create a new user
        ''',
        params={
            "username": "The username of the user to be created",
            "password": "The password of the user to be created"
        }
    )
    @jwt_required()
    def post(self):
        username = request.args.get('username')
        password = request.args.get('password')

        password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        DatabaseConn.command(f"INSERT INTO Users (username, password) VALUES ('{username}', '{password}')", fetch=False)
        return {"message": "User created"}
    
@ns.route("/login")
class Administration(Resource):
    @ns.doc(
        "login", 
        description='''
        Log in to the system
        ''',
        params={
            "username": "The username of the user to be logged in",
            "password": "The password of the user to be logged in"
        }
    )
    def post(self):
        username = request.args.get('username')
        password = request.args.get('password')
        password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        if self.verify_user(username, password):
            access_token = create_access_token(identity=username)
            return {"access_token": access_token}
        return {"message": "Invalid credentials"}

    def verify_user(self, username, password):
        results = DatabaseConn.command(f"SELECT * FROM Users WHERE username = '{username}' AND password = '{password}'")
        if not results:
            return False
        return True

@ns.route("/authors")
class Administration(Resource):
    def get(self):
        results = DatabaseConn.command("SELECT * FROM Authors")
        return results
    
@ns.route("/papers")
class Administration(Resource):
    def get(self):
        results = DatabaseConn.command("SELECT * FROM Papers")
        return results
    
@ns.route("/editions")
class Administration(Resource):
    def get(self):
        results = DatabaseConn.command("SELECT * FROM Editions")
        return results