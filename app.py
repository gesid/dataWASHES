from flask import Flask, jsonify, request
import json

with open('data/editions.json', 'r', encoding='utf8') as editions_file:
    editions = json.load(editions_file)

with open('data/papers.json', 'r', encoding='utf8') as papers_file:
    papers = json.load(papers_file)

with open('data/authors.json', 'r', encoding='utf8') as authors_file:
    authors = json.load(authors_file)

app = Flask(__name__)

@app.route('/')
def index():
    return 'Homepage'

# Main routes
@app.route('/editions', methods=['GET'])
def get_editions():
    return jsonify(editions)

@app.route('/authors', methods=['GET'])
def get_authors():
    return jsonify(authors)

@app.route('/papers', methods=['GET'])
def filter_papers():
    year = request.args.get('year')
    paper_id = request.args.get('id')
    paper_type = request.args.get('type')
    author_name = request.args.get('name')
    institution_name = request.args.get('institution')
    author_state = request.args.get('state')
    abstract_query = request.args.get('abstract')
    resumo_query = request.args.get('resumo')


    filtered_papers = papers

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

if __name__ == '__main__':
    app.run(debug=True)
