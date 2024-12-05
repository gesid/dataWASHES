from flask_restx import Resource, Namespace
from resources.database_conn import DatabaseConn
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
        query = '''
            INSERT INTO public."Users" ("UserName", "Password") 
            VALUES (%(username)s, %(password)s)
        '''
        params = {'username': username, 'password': password}
        DatabaseConn.command(query, params, fetch=False)
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
        query = '''
            SELECT * FROM public."Users" 
            WHERE "UserName" = %(username)s AND "Password" = %(password)s
        '''
        params = {'username': username, 'password': password}
        results = DatabaseConn.command(query, params)
        return any(results)

@ns.route("/authors")
class Administration(Resource):
    @jwt_required()
    def get(self):
        query = '''
            SELECT a.*, p."Link" 
            FROM public."Authors" a 
            JOIN public."Papers" p 
            ON p."PaperId" = a."PaperId"
        '''
        results = DatabaseConn.command(query)
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
            VALUES (%(name)s, %(instituition)s, %(state)s, %(paperId)s)
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
            SET "Name" = %(name)s,
                "Instituition" = %(instituition)s,
                "State" = %(state)s,
                "PaperId" = %(paperId)s
            WHERE "AuthorId" = %(authorId)s
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
        
        query = '''
            DELETE FROM public."Authors" WHERE "AuthorId" = %(authorId)s
        '''
        params = {'authorId': authorId}
        
        DatabaseConn.command(query, params, fetch=False)
        return {"message": "Author deleted"}, 200
    
@ns.route("/papers")
class Administration(Resource):
    @jwt_required()
    def get(self):
        query = 'SELECT * FROM public."Papers"'
        results = DatabaseConn.command(query)
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
            INSERT INTO public."Papers" 
            ("Title", "Year", "Abstract", "Summary", "Keywords", "Type", "Link", "References", "Citation", "ObtenDate", "EditionId")
            VALUES (%(title)s, %(year)s, %(abstract)s, %(summary)s, %(keywords)s, %(type)s, %(link)s, %(references)s, %(citation)s, %(obtenDate)s, %(editionId)s)
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
            SET "Title" = %(title)s,
                "Year" = %(year)s,
                "Abstract" = %(abstract)s,
                "Summary" = %(summary)s,
                "Keywords" = %(keywords)s,
                "Type" = %(type)s,
                "Link" = %(link)s,
                "References" = %(references)s,
                "Citation" = %(citation)s,
                "ObtenDate" = %(obtenDate)s,
                "EditionId" = %(editionId)s
            WHERE "PaperId" = %(paperId)s
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
        
        query = '''
            DELETE FROM public."Papers" WHERE "PaperId" = %(paperId)s
        '''
        params = {'paperId': paperId}
        
        DatabaseConn.command(query, params, fetch=False)
        return {"message": "Paper deleted"}, 200
    
@ns.route("/editions")
class Administration(Resource):
    @jwt_required()
    def get(self):
        try:
            query = 'SELECT * FROM public."Editions" ORDER BY "Year" DESC'
            results = DatabaseConn.command(query)
            return results, 200
        except Exception as e:
            return {"message": str(e)}, 500
        
    @jwt_required()
    def post(self):
        data = request.get_json()
        title = data.get('Title')
        year = data.get('Year')
        location = data.get('Location')
        proceedings = data.get('Proceedings')
        current_date = datetime.now().isoformat()
        
        query = '''
            INSERT INTO public."Editions" 
            ("Title", "Year", "Date", "Location", "Proceedings")
            VALUES (%(title)s, %(year)s, %(current_date)s, %(location)s, %(proceedings)s)
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
        location = data.get('Location')
        proceedings = data.get('Proceedings')
        editionId = data.get('EditionId')
        
        query = '''
            UPDATE public."Editions"
            SET "Title" = %(title)s,
                "Year" = %(year)s,
                "Location" = %(location)s,
                "Proceedings" = %(proceedings)s
            WHERE "EditionId" = %(editionId)s
        '''
        
        params = {
            'title': title,
            'year': year,
            'location': location,
            'proceedings': proceedings,
            'editionId': editionId
        }
        
        DatabaseConn.command(query, params, fetch=False)
        return {"message": "Edition updated"}, 200
    
    @jwt_required()
    def delete(self):
        data = request.get_json()
        editionId = data.get('EditionId')
        
        query = '''
            DELETE FROM public."Editions" WHERE "EditionId" = %(editionId)s
        '''
        
        params = {'editionId': editionId}
        
        DatabaseConn.command(query, params, fetch=False)
        return {"message": "Edition deleted"}, 200
