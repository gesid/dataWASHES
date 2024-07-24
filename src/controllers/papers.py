from flask import request, jsonify
from flask_restx import Resource, Namespace
from resouces import papers_db
from models import paper, abstracts, reference, citation
from utils.logging_washes import log_request,  log_request_papers_error, log_request_papers_success
# Adicionadas importações dos modelos de referências e citações

ns = Namespace(name="Papers", path="/papers")

@ns.route("/")
class PapersList(Resource):

    @ns.marshal_list_with(paper, mask=None)
    @ns.doc(
        "list_papers",
        params={
            "year": "The paper year of publishment",
            "id": "The paper identifier",
            "type": "The type of the paper",
            "author": "The name of at least one of the authors",
            "institution": "The institution name of at least one of the authors",
            "state": "The state acronym of at least one of the authors",
            "abstract": "The abstract of the paper",
            "resumo": "O resumo do artigo",
            "keyword": "Papers keyword",
            "search": "Generic word present in title or abstract of papers",
            "reference": "A specific reference used in the paper",
            "citation": "A specific article that cites this article",
        }, 
        description='''
            Returns all the paper in the dataset.
            The list of paper can be filtered using the header arguments specified below.
        '''
    )
    def get(self):
        year = request.args.get("year")
        paper_id = request.args.get("id")
        paper_type = request.args.get("type")
        author_name = request.args.get("author")
        institution_name = request.args.get("institution")
        author_state = request.args.get("state")
        abstract_query = request.args.get("abstract")
        resumo_query = request.args.get("resumo")
        keyword = request.args.get("keyword")
        generic_query = request.args.get("search")
        citation_query = request.args.get("citation")
        reference_query = request.args.get("reference")

        filtered_papers = papers_db

        if year:
            try:
                year = int(year)
                if year not in [paper["Year"] for paper in filtered_papers]:
                    log_request_papers_error(request.method, request.path, "year", year, 404)
                    return jsonify({"error": "No papers found for the specified year."}), 404
                filtered_papers = [paper for paper in filtered_papers if paper["Year"] == year] 
            except ValueError:
                log_request_papers_error(request.method, request.path, "year", year, 400)
                return jsonify({"error": "Invalid year format"}), 400

        if paper_id:
            try:
                paper_id = int(paper_id)
            except ValueError:
                log_request_papers_error(request.method, request.path, "id", paper_id, 400)
                return jsonify({'error': 'ID de artigo inválido. O ID deve ser um número inteiro.'}), 400

            filtered_papers = [paper for paper in filtered_papers if paper.get("Paper_id") == paper_id]

            if not filtered_papers:
                log_request_papers_error(request.method, request.path, "id", paper_id, 404)
                return jsonify({'error': 'Artigo não encontrado'}), 404

        if paper_type:
            try:
                paper_type = paper_type.lower().capitalize()
                if paper_type not in {paper["Type"] for paper in filtered_papers}:
                    log_request_papers_error(request.method, request.path, "type", paper_type, 404)
                    return jsonify({"error": "Tipo de artigo não encontrado."}), 404
                filtered_papers = [
                    paper for paper in filtered_papers if paper["Type"] == paper_type
                ]
            except Exception as e:
                log_request_papers_error(request.method, request.path, "type", paper_type, 400)
                return jsonify({"error": f"Erro ao filtrar pelo tipo de artigo: {str(e)}"}), 400

        if author_name:
            try:
                filtered_papers = [
                    paper
                    for paper in filtered_papers
                    if any(author_name.lower() in author["Name"].lower() for author in paper["Authors"])
                ]
                if not filtered_papers:
                    log_request_papers_error(request.method, request.path, "author", author_name, 404)
                    return jsonify({"error": "Nenhum artigo encontrado para o autor especificado."}), 404
            except Exception as e:
                log_request_papers_error(request.method, request.path, "author", author_name, 404)
                return jsonify({"error": f"Erro ao filtrar pelo nome do autor: {str(e)}"}), 400

        if institution_name:
            try:
                filtered_papers = [
                    paper
                    for paper in filtered_papers
                    if any(institution_name.lower() in author["Institution"].lower() for author in paper["Authors"])
                ]
                if not filtered_papers:
                    log_request_papers_error(request.method, request.path, "institution", institution_name, 404)
                    return jsonify({"error": "Nenhum artigo encontrado para a instituição especificada."}), 404
            except Exception as e:
                log_request_papers_error(request.method, request.path, "institution", institution_name, 400)
                return jsonify({"error": f"Erro ao filtrar pelo nome da instituição: {str(e)}"}), 400

        if author_state:
            try:
                filtered_papers = [
                    paper
                    for paper in filtered_papers
                    if any(author_state.lower() in author["State"].lower() for author in paper["Authors"])
                ]
                if not filtered_papers:
                    log_request_papers_error(request.method, request.path, "state", author_state, 404)
                    return jsonify({"error": "Nenhum artigo encontrado para o estado especificado."}), 404
            except Exception as e:
                log_request_papers_error(request.method, request.path, "state", author_state, 400)
                return jsonify({"error": f"Erro ao filtrar pelo estado do autor: {str(e)}"}), 400

        if abstract_query:
            try:
                filtered_papers = [
                    paper
                    for paper in filtered_papers
                    if abstract_query.lower() in paper["Abstract"].lower()
                ]
                if not filtered_papers:
                    log_request_papers_error(request.method, request.path, "abstract", abstract_query, 404)
                    return jsonify({"error": "Nenhum artigo encontrado para a consulta de resumo."}), 404
            except Exception as e:
                log_request_papers_error(request.method, request.path, "abstract", abstract_query, 400)
                return jsonify({"error": f"Erro ao filtrar pelo resumo: {str(e)}"}), 400

        if resumo_query:
            try:
                filtered_papers = [
                    paper
                    for paper in filtered_papers
                    if resumo_query.lower() in paper["Resumo"].lower()
                ]
                if not filtered_papers:
                    log_request_papers_error(request.method, request.path, "resumo", resumo_query, 404)
                    return jsonify({"error": "Nenhum artigo encontrado para a consulta de resumo."}), 404
            except Exception as e:
                log_request_papers_error(request.method, request.path, "resumo", resumo_query, 400)
                return jsonify({"error": f"Erro ao filtrar pelo resumo: {str(e)}"}), 400

        if keyword:
            try:
                filtered_papers = [
                    paper
                    for paper in filtered_papers
                    if keyword.lower() in paper["Keywords"].lower()
                ]
                if not filtered_papers:
                    log_request_papers_error(request.method, request.path, "keyword", keyword, 404)
                    return jsonify({"error": "Nenhum artigo encontrado para a palavra-chave especificada."}), 404
            except Exception as e:
                log_request_papers_error(request.method, request.path, "keyword", keyword, 400)
                return jsonify({"error": f"Erro ao filtrar pela palavra-chave: {str(e)}"}), 400

        if generic_query:
            try:
                filtered_papers = [
                    paper
                    for paper in filtered_papers
                    if generic_query.lower() in paper["Title"].lower()
                    or generic_query.lower() in paper["Abstract"].lower()
                ]
                if not filtered_papers:
                    log_request_papers_error(request.method, request.path, "search", generic_query, 404)
                    return jsonify({"error": "Nenhum artigo encontrado para a consulta genérica."}), 404
            except Exception as e:
                log_request_papers_error(request.method, request.path, "search", generic_query, 400)
                return jsonify({"error": f"Erro ao filtrar pela consulta genérica: {str(e)}"}), 400

        if reference_query:
            try:
                filtered_papers = [
                    paper
                    for paper in filtered_papers
                    if reference_query in paper.get("References", [])
                ]
                if not filtered_papers:
                    log_request_papers_error(request.method, request.path, "reference", reference_query, 404)
                    return jsonify({"error": "Nenhum artigo encontrado para a referência especificada."}), 404
            except Exception as e:
                log_request_papers_error(request.method, request.path, "reference", reference_query, 400)
                return jsonify({"error": f"Erro ao filtrar pela referência: {str(e)}"}), 400

        if citation_query:
            try:
                filtered_papers = [
                    paper
                    for paper in filtered_papers
                    if citation_query in paper.get("Cited_by", [])
                ]
                if not filtered_papers:
                    log_request_papers_error(request.method, request.path, "citation", citation_query, 404)
                    return jsonify({"error": "Nenhum artigo encontrado para a citação especificada."}), 404
            except Exception as e:
                log_request_papers_error(request.method, request.path, "citation", citation_query, 400)
                return jsonify({"error": f"Erro ao filtrar pela citação: {str(e)}"}), 400

        all_paths_and_arguments = f"year/{year}/id/{paper_id}/type/{paper_type}/author/{author_name}/institution/{institution_name}/state/{author_state}/abstract/{abstract_query}/resumo/{resumo_query}/keyword/{keyword}/search/{generic_query}/reference/{reference_query}/citation/{citation_query}"
        
        log_request_papers_success(request.method, request.path, 200, all_paths_and_arguments)
        return filtered_papers

@ns.route("/abstracts")
class GetPaperAbstracts(Resource):
    @ns.marshal_list_with(abstracts, mask=None)
    @ns.doc(
        "get_paper_abstracts", 
        description='''
            Returns the ``abstract`` and ``ID`` of all the papers in the dataset. 
        '''
    )
    def get(self):
        abstracts = [{"Paper_id": p["Paper_id"], "Abstract": p["Abstract"]} for p in papers_db]
        log_request(request.method, request.path, 200)
        return abstracts

      
@ns.route("/by-title/<string:search>")
class SearchPapersByTitle(Resource):
    @ns.marshal_list_with(paper, mask=None)
    @ns.doc(
        "search_papers_by_title", 
        description='''
            Returns all the papers where the string ``search`` is included in the title.
        ''',
        params={
            "search": "Generic word present in title",
        }
    )
    def get(self, search):
        keyword = search
        if not keyword:
            log_request(request.method, request.path, 400)
            return jsonify({"error": "Missing 'title' parameter"}), 400
        matched_papers = [p for p in papers_db if keyword.lower() in p["Title"].lower()]
        if matched_papers:
            log_request(request.method, request.path, 200)
            return matched_papers
        else:
            log_request(request.method, request.path, 404)
            return jsonify({"error": "No papers found with the specified title"}), 404


@ns.route("/by-year/<int:year>")
class GetPapersByYear(Resource):
    @ns.marshal_list_with(paper, mask=None)
    @ns.doc(
        "get_papers_by_year", 
        description='''
            Returns all the papers published in the ``year`` specified.
        ''',
        params={
            "year": "The year of publishment",
        }
    )
    def get(self, year):
        matched_papers = [p for p in papers_db if p["Year"] == year]
        if not matched_papers:
            log_request(request.method, request.path, 404)
            return {"message": "No papers found for the specified year."}, 404
        
        log_request(request.method, request.path, 200)
        return matched_papers


@ns.route("/<int:id>")
@ns.response(404, "Paper not found")
class PaperById(Resource):
    @ns.marshal_with(paper, mask=None)
    @ns.doc(
        "get_paper_by_id", 
        description='''
            Returns the paper identified by the ``id``.
        ''',
        params={
            "id": "The paper unique identifier",
        }
    )
    def get(self, id):
        for paper in papers_db:
            if paper["Paper_id"] == id:
                log_request(request.method, request.path, 200)
                return paper
        
        log_request(request.method, request.path, 404)
        ns.abort(404, message=f"Paper {id} not found")
      
# Adicionando rota para obter as citações de um artigo identificado pelo `id`.
@ns.route("/<int:id>/citations")
class GetPaperCitations(Resource):
    @ns.response(404, "Paper not found")
    @ns.marshal_list_with(citation, mask=None)
    @ns.doc(
        "get_paper_citations",
        description='''
            Returns the citations of the paper identified by the ``id``.
        ''',
        params={
            "id": "The paper unique identifier",
        }
    )
    def get(self, id):
        citations = []
        for paper in papers_db:
            if paper["Paper_id"] == id:
                citations = paper.get("Cited_by", [])
                break
        if not citations:
            log_request(request.method, request.path, 404)
            ns.abort(404, message=f"No citations found for paper {id}")
        
        log_request(request.method, request.path, 200)
        return [{"Paper_id": id, "Cited_by": citations}]

# Adicionando rota para obter as referências de um artigo identificado pelo `id`.
@ns.route("/<int:id>/references")
class GetPaperReferences(Resource):
    @ns.response(404, "Paper not found")
    @ns.marshal_list_with(reference, mask=None)
    @ns.doc(
        "get_paper_references",
        description='''
            Returns the ``references`` of the paper identified by the ``id``
        ''',
        params={
            "id": "The paper unique identifier",
        }
    )
    def get(self, id):
        references = []
        for paper in papers_db:
            if paper["Paper_id"] == id:
                references = paper.get("References", [])
                break
        if not references:
            log_request(request.method, request.path, 404)
            ns.abort(404, message=f"No references found for paper {id}")

        log_request(request.method, request.path, 200)
        return [{"Paper_id": id, "References": references}]
