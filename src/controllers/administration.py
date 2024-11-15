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
        name = data.get('Name')
        instituition = data.get('Instituition')
        state = data.get('State')
        paperId = data.get('PaperId')
        
        query = '''
            INSERT INTO public."Authors" ("Name", "Instituition", "State", "PaperId")
            VALUES (:name, :instituition, :state, :paperId)
        '''
        params = {
            'name': name,
            'instituition': instituition,
            'state': state,
            'paperId': paperId
        }
        
        DatabaseConn.command(query, params, fetch=False)
        return {"message": "Author created"}, 201

    @jwt_required()
    def put(self):
        data = request.get_json()
        name = data.get('Name')
        instituition = data.get('Instituition')
        state = data.get('State')
        paperId = data.get('PaperId')
        authorId = data.get('AuthorId')
        
        query = '''
            UPDATE public."Authors"
            SET "Name" = :name,
                "Instituition" = :instituition,
                "State" = :state,
                "PaperId" = :paperId
            WHERE "AuthorId" = :authorId
        '''
        params = {
            'name': name,
            'instituition': instituition,
            'state': state,
            'paperId': paperId,
            'authorId': authorId
        }
        
        DatabaseConn.command(query, params, fetch=False)
        return {"message": "Author updated"}, 200

    @jwt_required()
    def delete(self):
        data = request.get_json()
        authorId = data.get('AuthorId')
        
        DatabaseConn.command(f'DELETE FROM public."Authors" WHERE "AuthorId" = {authorId}', fetch=False)
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
        title = data.get('Title')
        year = data.get('Year')
        abstract = data.get('Abstract')
        summary = data.get('Summary')
        keywords = data.get('Keywords')
        type = data.get('Type')
        link = data.get('Link')
        references = data.get('References')
        citation = data.get('Citation')
        obtenDate = datetime.now().isoformat()
        editionId = data.get('EditionId')
        
        query = '''
            INSERT INTO public."Papers" ("Title", "Year", "Abstract", "Summary", "Keywords", "Type", "Link", "References", "Citation", "ObtenDate", "EditionId")
            VALUES (:title, :year, :abstract, :summary, :keywords, :type, :link, :references, :citation, :obtenDate, :editionId)
        '''
        
        params = {
            'title': title,
            'year': year,
            'abstract': abstract,
            'summary': summary,
            'keywords': keywords,
            'type': type,
            'link': link,
            'references': references,
            'citation': citation,
            'obtenDate': obtenDate,
            'editionId': editionId
        }
        
        DatabaseConn.command(query, params, fetch=False)
        return {"message": "Paper created"}, 201


    @jwt_required()
    def put(self):
        data = request.get_json()
        title = data.get('Title')
        year = data.get('Year')
        abstract = data.get('Abstract')
        summary = data.get('Summary')
        keywords = data.get('Keywords')
        type = data.get('Type')
        link = data.get('Link')
        references = data.get('References')
        citation = data.get('Citation')
        obtenDate = data.get('ObtenDate')
        editionId = data.get('EditionId')
        paperId = data.get('PaperId')
        
        query = '''
            UPDATE public."Papers"
            SET "Title" = :title,
                "Year" = :year,
                "Abstract" = :abstract,
                "Summary" = :summary,
                "Keywords" = :keywords,
                "Type" = :type,
                "Link" = :link,
                "References" = :references,
                "Citation" = :citation,
                "ObtenDate" = :obtenDate,
                "EditionId" = :editionId
            WHERE "PaperId" = :paperId
        '''
        
        params = {
            'title': title,
            'year': year,
            'abstract': abstract,
            'summary': summary,
            'keywords': keywords,
            'type': type,
            'link': link,
            'references': references,
            'citation': citation,
            'obtenDate': obtenDate,
            'editionId': editionId,
            'paperId': paperId
        }
            

        DatabaseConn.command(query, params, fetch=False)
        return {"message": "Paper updated"}, 200
        
    @jwt_required()
    def delete(self):
        data = request.get_json()
        paperId = data.get('PaperId')
        DatabaseConn.command(f'DELETE FROM public."Papers" WHERE "PaperId" = {paperId}', fetch=False)
        return {"message": "Paper deleted"}, 200
    
@ns.route("/editions")
class Administration(Resource):
    @jwt_required()
    def get(self):
        try:
            results = DatabaseConn.command('SELECT * FROM public."Editions" ORDER BY "Year" DESC')
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

    