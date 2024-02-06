## PAPERS

Recuperar todos os papers:
Consulta: `GET /papers`
Descrição: Recupera todos os papers disponíveis na API.

Recuperar um paper Específico por ID:
Consulta: `GET /papers/{id}`
Descrição: Recupera informações detalhadas sobre um artigo específico com base no seu ID.

Recuperar papers por Ano:
Consulta: `GET /papers?year={year}`
Descrição: Recupera todos os papers publicados em um ano específico.

Recuperar papers por Autor:
Consulta: `GET /papers?autor={autor}`
Descrição: Recupera todos os papers escritos por um autor específico.

Recuperar papers por Palavras-chave:
Consulta: `GET /papers?palavras_chave={palavras}`
Descrição: Recupera papers que contenham palavras-chave específicas.

Pesquisar papers por título:
Rota: `/papers/search?title={keyword}`
Descrição: Permite a pesquisa de papers com base em palavras-chave no título.

Recuperar papers por Tipo (Completo, Curto ou Poster):
Consulta: `GET /papers?tipo={tipo}`
Descrição: Recupera papers com base em seu tipo (Completo, Curto ou Poster).

Recuperar papers por ano:
Rota: `/papers/by-year/{ano}`
Descrição: Retorna uma lista de papers publicados em um ano específico.

Recuperar papers por Estado da Instituição dos Autores:
Consulta: `GET /papers?estado={estado}`
Descrição: Recupera papers cujos autores pertencem a instituições em um estado específico.

Recuperar Resumos de papers:
Consulta: `GET /papers/resumos`
Descrição: Recupera resumos de todos os papers para uma rápida visualização.

Pesquisar papers por Título ou Conteúdo:
Consulta: `GET /papers?pesquisa={termo}`
Descrição: Permite aos usuários pesquisar papers com base em um termo presente no título ou conteúdo.

## AUTORES

Rota: /authors
Descrição: Retorna uma lista de todos os autores disponíveis na API.
Recuperar informações de um autor específico:

Rota: /authors/{author_id}
Descrição: Retorna detalhes específicos de um autor com base no ID do autor.
Pesquisar autores por nome:

Rota: /authors/search?name={nome}
Descrição: Permite a pesquisa de autores com base no nome.
Recuperar todos os papers de um autor específico:

Rota: /authors/{author_id}/papers
Descrição: Retorna todos os papers escritos por um autor específico.

## EDIÇÕES

Recuperar todas as edições:

Rota: /editions
Descrição: Retorna uma lista de todas as edições disponíveis na API.
Recuperar informações de uma edição específica:

Rota: /editions/{edition_id}
Descrição: Retorna detalhes específicos de uma edição com base no ID da edição.
Pesquisar edições por ano:

Rota: /editions/search?year={ano}
Descrição: Permite a pesquisa de edições com base no ano de publicação.
Recuperar todos os papers de uma edição específica:

Rota: /editions/{edition_id}/papers
Descrição: Retorna todos os papers associados a uma edição específica.

## Exportar arquivo em json ou csv

## Documentação utilizando swagger

```json

data = [
{
"Edição_id": 5,
"Paper_id": 1,
"Ano": 2020,
"Título do artigo": "Uso da Netnografia para a Geração de Personas e Requisitos para Sistemas com foco em pessoas com Transtorno do Espectro Autista: Um Relato de Experiência",
    "Autores": {
    "Nome": "Anna Beatriz Marques",
    "Instituição": "Universidade Federal do Ceará (Campus de Russas)",
    "Estado": "CE"
    },
"Abstract": "The early stages of software development require a good understanding of the target audience and their needs...",
"Resumo": "As fases iniciais do desenvolvimento de software requerem um bom entendimento do público-alvo e suas necessidades...",
"Palavras-chave": "#",
"Artigo completo, artigo curto ou poster?": "Completo",
"Link para download": "https://sol.sbc.org.br/index.php/washes/article/view/11192"
},

]
```

```python
from flask import Flask, jsonify, request

app = Flask(**name**)

editions = [
{
'id': 1,
'title': 'O Organizar de Práticas Cooperativas no Contexto de um Ambiente de Estágio em Desenvolvimento de Software'
},
{
'id': 2,
'title': 'Teste 2'
},
]

@app.route('/')
def index():
return 'Hello, Flask!'
@app.route('/editions', methods=['GET'])
def get_editions():
return jsonify(editions)

@app.route('/papers', methods=['GET'])
def get_editions():
return jsonify(editions)

@app.route('/editions/<int:id>', methods=['GET'])
def get_id(id):
for edition in editions:
if edition.get('id') == id:
return jsonify(edition)

#@app.route('/editions/<int:id>/<int:year>', methods=['GET'])

#@app.route('/editions/papers', methods=['GET'])

if **name** == '**main**':
app.run(debug=True)

# endpoints

# localhost/editions (GET)

# localhost/edition/id (GET)

# localhost/edition/id/year (GET)

#Ano
#Título do artigo
#Autores
#Instituições dos autores
#Estado
#Abstract
#Resumo
#Palavras-chave
#Artigo completo, artigo curto ou poster
#Link para download
```
