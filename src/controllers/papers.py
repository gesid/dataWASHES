from flask import jsonify, request
from flask_restx import Resource, Namespace
import json

ns = Namespace('Papers')

with open('data/papers.json', 'r', encoding='utf8') as papers_file:
    papers_db = json.load(papers_file)

@ns.route('/')
class PapersList(Resource):

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

        return jsonify(filtered_papers)
