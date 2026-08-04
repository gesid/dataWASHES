# 🔄 Atualização dos dados

Atualmente, o WASHES é um evento anual. A cada nova edição do evento, novos artigos são publicados e precisam ser analisados e inseridos no dataset do projeto.

- [Link para os anais do WASHES](https://sol.sbc.org.br/index.php/washes/issue/archive)

No projeto, existem quatro arquivos JSON que servem como base de dados. Sempre que uma nova edição do WASHES ocorre, eles devem ser atualizados. São eles:

- [papers.json](../../data/papers.json)
- [editions.json](../../data/editions.json)
- [authors.json](../../data/authors.json)
- [award_papers.json](../../data/award_papers.json)

---

## ⚡ Fluxo de Atualização Automatizado (CI/CD)

O **dataWASHES** conta com um pipeline de automação construído com **GitHub Actions, Python e IA**. A base de dados oficial reside diretamente no repositório no arquivo `data/JSON Generator/dataWASHES-data.xlsx`.

Todo dia 1º de cada mês, o GitHub Actions executa automaticamente a seguinte rotina:
1. **Scraping:** Verifica se há uma nova edição do WASHES no SOL SBC. Se houver, baixa todos os metadados de artigos, resumos, autores e afiliações.
2. **Inteligência Artificial:** Utiliza a API do **Groq (Llama-3.3 70B)** para ler os resumos e classificar automaticamente os 6 campos metodológicos dos artigos.
3. **Citações:** Executa o minerador Python via **ScraperAPI** para buscar citações reais no Google Scholar.
4. **Pull Request:** Atualiza a planilha `.xlsx`, regera os arquivos JSON e **abre um Pull Request (PR) automático** no GitHub.

### 🧑‍💻 O Papel do Mantenedor:
Quando o robô abrir o Pull Request:
1. Acesse a branch criada pelo bot (`auto-data-sync`).
2. Abra a planilha `dataWASHES-data.xlsx` e **revise as colunas metodológicas** classificadas pela IA, ajustando se necessário.
3. Se houver artigos premiados na edição (divulgados no Instagram/site do evento), atualize manualmente o arquivo `award_papers.json`.
4. Aprove o Pull Request (Merge para a `main`).
5. Faça o [Deploy no PythonAnywhere](deploy.md).

---

## 💻 Execução Manual Local (Avançado)

Caso o mantenedor deseje forçar a atualização rodando os scripts localmente, é necessário configurar um arquivo `.env` na raiz do projeto com as chaves:
```env
GROQ_API_KEY=sua_chave_do_groq
SCRAPER_API_KEY=sua_chave_da_scraperapi
```

Em seguida, execute os scripts:
```bash
# 1. Busca novas edições, usa a IA para classificar, atualiza a planilha e regera os JSONs
python scripts/sync_washes_dataset.py

# 2. Atualiza as citações dos artigos pendentes via Google Scholar
python scripts/miner_citations.py
```

---

## 📄 Estrutura dos Dados

### Artigos (`papers.json`)

Um artigo possui os seguintes campos:
- **Paper_id**: Identificador único numérico gerado automaticamente.
- **Title**: Título completo do artigo.
- **Language**: Idioma em que o artigo foi escrito.
- **Year**: Ano de publicação.
- **Abstract**: Resumo do artigo em inglês.
- **Resumo**: Resumo do artigo em português.
- **Keywords**: Palavras-chave do artigo.
- **Type**: Tipo de publicação (`Full paper`, `Short paper`, `Poster`).
- **Download_link**: Link oficial para o artigo no SOL SBC.
- **References**: Lista de referências bibliográficas (com `#` se vazio).
- **Cited_by**: Citações obtidas automaticamente via Google Scholar.
- **Updated_in**: Data da última atualização.
- **Authors**: Lista de autores do artigo.
- **Approach**: Abordagem metodológica (`Qualitativa`, `Quantitativa`, `Mista`).
- **Objective**: Objetivo principal (`Exploratória`, `Descritiva`, `Explicativa`).
- **Procedures**: Procedimentos (`Estudo de caso`, `Survey`, `Revisão de literatura`, etc.).
- **Data_collection**: Método de coleta (`Questionário`, `Entrevista`, `Observação`, etc.).
- **Quantitative_Data_Analysis**: Métodos quantitativos (`Estatística descritiva`, etc.).
- **Qualitative_Data_Analysis**: Métodos qualitativos (`Análise de conteúdo`, `Análise temática`, etc.).

> **Nota:** Todos os campos acima, incluindo a classificação metodológica, são atualmente pré-preenchidos de forma autônoma pela IA. O papel do mantenedor é apenas **revisar** a classificação gerada no Excel.

### Citações
O preenchimento das citações (`Cited_by`) é automatizado pelo script `scripts/miner_citations.py`. Contudo, caso o robô falhe ou o mantenedor precise fazer uma correção manual legada:
1. Pesquise o artigo pelo título no [Google Acadêmico](https://scholar.google.com/).
2. Clique na opção **"Citado por X"**.
3. Clique em **"Citar"** para cada trabalho, copie no padrão **"APA"** e cole na planilha.

![image](../images/cited_by-4.png)

### Autor (`authors.json`)

Um autor possui os seguintes campos:
- **Author_id**: Identificador único do autor no sistema.
- **Name**: Nome completo do autor.
- **Institution**: Nome completo da instituição à qual o autor está vinculado.
- **Institution_acronym**: Sigla da instituição do autor.
- **State**: Estado brasileiro da instituição (inferido automaticamente).
- **Papers**: Lista de identificadores (**Paper_id**) dos artigos associados a este autor.

Observe a forma de organização na planilha: na **primeira linha de cada artigo**, são informados os dados do artigo e do **primeiro autor**. Os **demais autores** são preenchidos nas linhas seguintes, deixando os campos relacionados ao artigo em branco.

![image](../images/authors.png)

### Edições (`editions.json`)

A atualização do arquivo `editions.json` é feita automaticamente pelo `sync_washes_dataset.py`, que calcula a sequência de `Paper_id`s. Uma edição possui:
- **Edition_id**: Identificador único numérico da edição.
- **Year**: Ano em que a edição do evento ocorreu.
- **Title**: Título completo dos anais da edição.
- **Location**: Local (cidade e estado) onde o evento foi realizado.
- **Date**: Data de publicação.
- **Proceedings**: Link para a página oficial dos anais da edição.
- **Chairs**: Lista de coordenadores(as) da edição.
- **Papers**: Lista de identificadores (**Paper_id**) dos artigos publicados.

### Artigos Premiados (`award_papers.json`)

Os objetos do arquivo `award_papers.json` são cópias dos objetos de `papers.json`, onde alguns campos foram removidos e o campo **Award** (Classificação/Premiação: ex. 1º Lugar, 2º Lugar) foi adicionado.

Geralmente, os artigos premiados são divulgados na página de Instagram do WASHES ou em anúncios da coordenação durante o evento. Esta é a única etapa que **permanece estritamente manual**, devendo o mantenedor editar o arquivo `award_papers.json` caso haja premiações no ano vigente.