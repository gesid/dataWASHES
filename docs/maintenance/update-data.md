# Atualização dos dados

Atualmente, o WASHES é um evento anual. A cada nova edição do evento, novos artigos são publicados e precisam ser analisados e inseridos no dataset do projeto.

- [Link para os anais do WASHES](https://sol.sbc.org.br/index.php/washes/issue/archive)

No projeto, existem quatro arquivos JSON que servem como base de dados. Sempre que uma nova edição do WASHES ocorre, eles devem ser atualizados. São eles:

- [papers.json](../../data/papers.json)
- [editions.json](../../data/editions.json)
- [authors.json](../../data/authors.json)
- [award_papers.json](../../data/award_papers.json)

O processo de atualização desses dados segue os seguintes passos:

1. Acessar os anais da nova edição do WASHES;
2. A partir dos dados de cada artigo, atualizar a planilha onde ficam acumulados todos os dados. **IMPORTANTE:** deve-se seguir os padrões de preenchimento (por exemplo, usar `#` para sinalizar que um campo não possui dados);
3. Levar a planilha atualizada para o caminho `data/JSON Generator`;
4. Executar o script [data/JSON Generator/authorsJSON.py](../../data/JSON%20Generator/authorsJSON.py) para gerar um novo arquivo JSON de autores;
5. Executar o script [data/JSON Generator/papersJSON.py](../../data/JSON%20Generator/papersJSON.py) para gerar um novo arquivo JSON de artigos;
6. Ajustar as formatações dos JSONs gerados:
   - No diretório `data/JSON Generator/` há um arquivo de [instruções](../../data/JSON%20Generator/instruções.md) com mais detalhes sobre a execução dos scripts e as ferramentas utilizadas para formatar os arquivos JSON gerados;
7. Substituir os arquivos `authors.json` e `papers.json` pelos novos arquivos gerados pelos scripts;
8. Atualizar manualmente o arquivo `editions.json`, adicionando a nova edição;
9. Atualizar manualmente o arquivo `award_papers.json` com as informações dos artigos premiados;
10. Realizar o deploy das mudanças.

## Artigos

Um artigo possui os seguintes campos:

- **Paper_id**: Identificador único do artigo no sistema.
- **Title**: Título completo do artigo.
- **Language**: Idioma em que o artigo foi escrito.
- **Year**: Ano de publicação.
- **Abstract**: Resumo do artigo em inglês.
- **Resumo**: Resumo do artigo em português.
- **Keywords**: Palavras-chave que descrevem os principais temas do artigo.
- **Type**: Tipo de publicação (ex.: Full paper, Short paper).
- **Download_link**: Link para acesso ou download do artigo completo.
- **References**: Lista de referências bibliográficas citadas no artigo.
- **Cited_by**: Lista de trabalhos que citam este artigo.
- **Updated_in**: Data da última atualização do registro.
- **Authors**: Lista de autores do artigo.
- **Approach**: Abordagem metodológica da pesquisa.
- **Objective**: Objetivo principal do estudo.
- **Procedures**: Procedimentos metodológicos adotados.
- **Data_collection**: Forma como os dados foram coletados.
- **Quantitative_Data_Analysis**: Métodos de análise quantitativa dos dados.
- **Qualitative_Data_Analysis**: Métodos de análise qualitativa dos dados.

Quando uma nova edição do WASHES é lançada, a maioria dos dados que precisam ser coletados sobre os artigos está disponível na página dos anais daquela edição. A maioria dos campos pode ser atualizada a partir das informações encontradas no site, exceto:

- **Paper_id**: esse campo é gerado automaticamente pelo script `papersJSON.py`;
- **Cited_by**: esse campo é atualizado manualmente a partir do [Google Acadêmico](https://scholar.google.com/);
- Os campos **Approach** (Quanto à abordagem), **Objective** (Quanto aos objetivos), **Procedures** (Quanto aos procedimentos), **Data_collection** (Método para coleta de dados), **Quantitative_Data_Analysis** (Método para análise de dados quantitativos) e **Qualitative_Data_Analysis** (Método para análise de dados qualitativos) são preenchidos com a categoria mais adequada para o artigo. Isso é feito manualmente, a partir do julgamento de quem está atualizando os dados. Como se tratam de categorias, ao preencher esses campos, deve-se atentar para a escrita exata de cada categoria, conforme utilizada anteriormente, e apenas adicionar uma nova categoria se realmente for necessário.

**Obs.:** O campo **Referências** na planilha deve conter todas as referências usadas no artigo, com uma linha em branco entre cada referência. Já no campo **Citações**, essa linha em branco não é utilizada; apenas garanta que cada citação esteja em uma única linha.

### Citações

Caso ainda esteja sendo utilizado o método manual para preencher este campo, siga os passos abaixo:

1. Pesquisar o artigo pelo título no [Google Acadêmico](https://scholar.google.com/).

![image](../images/cited_by-1.png)

2. Se houver a opção **"Citado por X"**, clique nela, pois o artigo possui citações. Caso contrário, o artigo não possui citações, e o campo pode ser preenchido com `#`.

![image](../images/cited_by-2.png)

3. Como mostrado na imagem, o exemplo possui duas citações. Para cada citação, clique na opção **"Citar"**.

![image](../images/cited_by-3.png)

4. Um pop-up será aberto com algumas opções de citação. A opção a ser escolhida é o padrão **"APA"**. Copie a citação e cole na planilha.

5. Após repetir o processo para todas as citações, a planilha deve estar no seguinte formato:

![image](../images/cited_by-4.png)

## Autor

