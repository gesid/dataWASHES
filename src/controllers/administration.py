from flask_restx import Resource, Namespace
from resouces.database_conn import DatabaseConn
import hashlib
from flask_jwt_extended import create_access_token, jwt_required
from flask import jsonify, request
from datetime import datetime
from datetime import timedelta

ns = Namespace(name='Administration', path='/administration')

@ns.route("/createusers")
class Administration(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        DatabaseConn.command(f'INSERT INTO public."Users" ("UserName", "Password") VALUES (\'{username}\', \'{password}\')', fetch=False)
        return {"message": "User created"}
    
@ns.route("/login")
class Administration(Resource):
    def post(self):
        try :
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            password = hashlib.sha256(password.encode('utf-8')).hexdigest()

            if self.verify_user(username, password):
                access_token = create_access_token(identity=username)
                return {"access_token": access_token, "expiration": (datetime.utcnow() + timedelta(hours=1)).isoformat()}, 200
            return {"message": "Invalid credentials"}, 400
        except Exception as e:
            return {"message": str(e)}

    def verify_user(self, username, password):
        results = DatabaseConn.command(f'SELECT * FROM public."Users" WHERE "UserName" = \'{username}\' AND "Password" = \'{password}\'')
        return any(results)

@ns.route("/authors")
class Administration(Resource):
    @jwt_required()
    def get(self):
        results = DatabaseConn.command('SELECT a.*, p."Link" FROM public."Authors" a JOIN public."Papers" p ON p."PaperId" = a."PaperId"')
        return results, 200
    
    @jwt_required()
    def post(self):
        data = request.get_json()
        name = data.get('name')
        paper_id = data.get('paper_id')

        DatabaseConn.command(f'INSERT INTO public."Authors" ("Name", "PaperId") VALUES (\'{name}\', {paper_id})', fetch=False)
        return {"message": "Author created"}, 201

    @jwt_required()
    def put(self, author_id):
        data = request.get_json()
        name = data.get('name')
        paper_id = data.get('paper_id')

        DatabaseConn.command(f'UPDATE public."Authors" SET "Name" = \'{name}\', "PaperId" = {paper_id} WHERE "AuthorId" = {author_id}', fetch=False)
        return {"message": "Author updated"}, 200

    @jwt_required()
    def delete(self, author_id):
        DatabaseConn.command(f'DELETE FROM public."Authors" WHERE "AuthorId" = {author_id}', fetch=False)
        return {"message": "Author deleted"}, 200
    
@ns.route("/papers")
class Administration(Resource):
    @jwt_required()
    def get(self):
        results = DatabaseConn.command('SELECT * FROM public."Papers"')
        return results, 200
    
    @jwt_required()
    def post(self):
        data = request.get_json()
        title = data.get('title')
        link = data.get('link')

        DatabaseConn.command(f'INSERT INTO public."Papers" ("Title", "Link") VALUES (\'{title}\', \'{link}\')', fetch=False)
        return {"message": "Paper created"}, 201

    @jwt_required()
    def put(self, paper_id):
        data = request.get_json()
        title = data.get('title')
        link = data.get('link')

        DatabaseConn.command(f'UPDATE public."Papers" SET "Title" = \'{title}\', "Link" = \'{link}\' WHERE "PaperId" = {paper_id}', fetch=False)
        return {"message": "Paper updated"}, 200

    @jwt_required()
    def delete(self, paper_id):
        DatabaseConn.command(f'DELETE FROM public."Papers" WHERE "PaperId" = {paper_id}', fetch=False)
        return {"message": "Paper deleted"}, 200
    
@ns.route("/editions")
class Administration(Resource):
    @jwt_required()
    def get(self):
        try:
            results = DatabaseConn.command('SELECT * FROM public."Editions"')
            return results, 200
        except Exception:
            return jsonify({"error": "Assinatura do token inválida."}), 401
        
    @jwt_required()
    def post(self):
        data = request.get_json()
        title = data.get('Title')
        year = data.get('Year')
        location = data.get('Location')
        proceedings = data.get('Proceedings')
        current_date = datetime.now().isoformat()
        
        query = '''
            INSERT INTO public."Editions" ("Title", "Year", "Date", "Location", "Proceedings")
            VALUES (:title, :year, :current_date, :location, :proceedings)
        '''
        
        params = {
            'title': title,
            'year': year,
            'current_date': current_date,
            'location': location,
            'proceedings': proceedings
        }
        
        DatabaseConn.command(query, params, fetch=False)
        return {"message": "Edition created"}, 201

    @jwt_required()
    def put(self):
        data = request.get_json()
        title = data.get('Title')
        year = data.get('Year')
        edition_id = data.get('EditionId')
        date = data.get('Date')
        location = data.get('Location')
        proceedings = data.get('Proceedings')
        
        query = '''
            UPDATE public."Editions" 
            SET "Title" = :title, 
                "Year" = :year, 
                "Date" = :date, 
                "Location" = :location, 
                "Proceedings" = :proceedings 
            WHERE "EditionId" = :edition_id
        '''
        
        params = {
            'title': title,
            'year': year,
            'date': date,
            'location': location,
            'proceedings': proceedings,
            'edition_id': edition_id
        }

        DatabaseConn.command(query, params, fetch=False)
        return {"message": "Edition updated"}, 200

    @jwt_required()
    def delete(self):
        data = request.get_json()
        edition_id = data.get('EditionId')
        
        query = 'DELETE FROM public."Editions" WHERE "EditionId" = :edition_id'
        params = {'edition_id': edition_id}
        
        DatabaseConn.command(query, params, fetch=False)
        return {"message": "Edition deleted"}, 200

    