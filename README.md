# dataWASHES
Esta API permite consultar dados sobre autores, edições e artigos do Workshop sobre Aspectos Sociais, Humanos e Econômicos de Software - WASHES. Ela foi desenvolvida utilizando Flask e Flask-RESTx, e os dados são armazenados em arquivos JSON.

## Instalação
1. Clone o repositório para o seu computador:
```shell
git clone https://github.com/gesid/dataWASHES.git
```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):
```shell
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate      # Windows (cmd)
.venv\Scripts\Activate.ps1      # Windows (powershell)
```

3. Instale as dependências:
```shell
pip install -r requirements.txt
```

## Uso
1. Inicie o servidor:
```shell
python src\app.py # Windows
python src/app.py # Linux/Mac
```

2. Acesse a documentação da API em http://localhost:5000/ para obter detalhes sobre os endpoints disponíveis e como utilizá-los.
