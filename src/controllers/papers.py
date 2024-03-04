from flask import request
from flask_restx import Resource, Namespace, fields
from src.server.instance import server
import json

ns = Namespace('Papers')

author = server.getApi().model('Paper Author', {
    'Name': fields.String(description='Author\'s name', example='Maria'),
    'Institution': fields.String(description='Author\' institution', example='Universidade Federal do Cariri'),
    'State': fields.String(description='Author\'s state', exmple='CE', example='CE'),
    'Author_id': fields.Integer(description='The author unique identifier', example='34'),
})

paper = server.getApi().model('Paper', {
    'Authors': fields.List(fields.Nested(author), description='A list of the paper authors IDs'),
    'Paper_id': fields.Integer(description='The paper unique identifier', example='3'),
    'Title': fields.String(description='Paper title', example='Um Modelo para o Gerenciamento de Padrões de Projeto em Java'),
    'Year': fields.Integer(description='Publication year of the paper', example='2022'),
    'Abstract': fields.String(description='Abstract of the paper', example='Design  patterns  are  defined  as  reusable  solutions  to  recurring problems. These solutions...'),
    'Resumo': fields.String(description='Resumo do artigo', example='Os padrões de projeto são definidos como soluções reusáveis para problemas  recorrentes.  Essas...'),
    'Keywords': fields.String(description='Paper keywords', example='Java, Modelo, Gerenciamento'),
    'Type': fields.String(description='The type of publication', enum=['Curto', 'Poster', 'Completo']),
    'Download_link': fields.String(description='A link to download the paper', example='https://example.com'),
})

with open('data/papers.json', 'r', encoding='utf8') as papers_file:
    papers_db = json.load(papers_file)

@ns.route('/')
class PapersList(Resource):

    @ns.doc('list_papers', params={
        'year': 'An year',
        'id': 'A paper ID',
        'type': 'A type of paper',
        'name': 'A author name',
        'institution': 'An institution',
        'state': 'A state',
        'abstract': 'A abstract',
        'resumo': 'Um resumo',
    })
    @ns.marshal_list_with(paper)
    def get(self):
        year = request.args.get('year')
        paper_id = request.args.get('id')
        paper_type = request.args.get('type')
        author_name = request.args.get('name')
        institution_name = request.args.get('institution')
        author_state = request.args.get('state')
        abstract_query = request.args.get('abstract')
        resumo_query = request.args.get('resumo')


        filtered_papers = papers_db

        if year:
            filtered_papers = [paper for paper in filtered_papers if str(paper['Year']) == year]

        if paper_id:
            filtered_papers = [paper for paper in filtered_papers if str(paper['Paper_id']) == paper_id]

        if paper_type:
            filtered_papers = [paper for paper in filtered_papers if paper['Type'] == paper_type]

        if author_name:
            filtered_papers = [paper for paper in filtered_papers if any(author['Name'] == author_name for author in paper['Authors'])]
            
        if institution_name:
            filtered_papers = [paper for paper in filtered_papers if any(author['Institution'] == institution_name for author in paper['Authors'])]
        
        if author_state:
            filtered_papers = [paper for paper in filtered_papers if any(author['State'] == author_state for author in paper['Authors'])]
        
        if abstract_query:
            filtered_papers = [paper for paper in filtered_papers if abstract_query.lower() in paper['Abstract'].lower()]

        if resumo_query:
            filtered_papers = [paper for paper in filtered_papers if resumo_query.lower() in paper['Resumo'].lower()]
        print(filtered_papers)
        return filtered_papers
