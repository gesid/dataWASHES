from flask_restx import Resource, Namespace
from resouces.database_conn import DatabaseConn
import hashlib
from flask_jwt_extended import create_access_token, jwt_required
from flask import jsonify, request

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
        DatabaseConn.command(f'INSERT INTO public."Users" ("UserName", "Password") VALUES (\'{username}\', \'{password}\')', fetch=False)
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
        try :
            username = request.args.get('username')
            password = request.args.get('password')
            password = hashlib.sha256(password.encode('utf-8')).hexdigest()

            if self.verify_user(username, password):
                access_token = create_access_token(identity=username)
                return {"access_token": access_token}
            return {"message": "Invalid credentials"}
        except Exception as e:
            return {"message": str(e)}

    def verify_user(self, username, password):
        results = DatabaseConn.command(f'SELECT * FROM public."Users" WHERE "UserName" = \'{username}\' AND "Password" = \'{password}\'', isJsonify=False)
        return any(results)

@ns.route("/authors")
class Administration(Resource):
    @jwt_required()
    def get(self):
        results = DatabaseConn.command('SELECT a.*, p."Link" FROM public."Authors" a JOIN public."Papers" p ON p."PaperId" = a."PaperId"')
        return results, 200
    
@ns.route("/papers")
class Administration(Resource):
    @jwt_required()
    def get(self):
        results = DatabaseConn.command('SELECT * FROM public."Papers"')
        return results, 200
    
@ns.route("/editions")
class Administration(Resource):
    @jwt_required()
    def get(self):
        try:
            results = DatabaseConn.command('SELECT * FROM public."Editions"')
            return results, 200
        except Exception:
            return jsonify({"error": "Assinatura do token inválida."}), 401

    