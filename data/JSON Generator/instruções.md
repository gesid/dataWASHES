# Instruções dos Geradores de JSON (`papersJSON.py` e `authorsJSON.py`)

Estes scripts transformam a planilha (dataset) `dataWASHES-data.xlsx` em arquivos JSON contendo os artigos (`papers.json`) e os autores (`authors.json`), no formato especificado para os objetos da API do dataWASHES.

## ⚠️ Sanitização Automática de Valores Nulos (RFC 8259)

Ambos os scripts (`papersJSON.py` e `authorsJSON.py`) aplicam **sanitização automática** logo após a leitura da planilha:

```python
df = df.fillna("#").replace([float("inf"), float("-inf")], "#")
```

Isso é necessário porque células vazias ou inválidas da planilha são interpretadas pelo pandas como `NaN`, `NaT`, `inf` ou `-inf`. Esses valores **não são tokens válidos segundo a norma [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) (JSON Data Interchange Format)** — que define apenas `null`, `true`, `false`, números e strings como valores permitidos. Um `json.dump` sem tratamento geraria o token inválido `NaN`, produzindo um arquivo JSON quebrado que bibliotecas rigorosas (e navegadores) recusam parsear.

Com o `.fillna("#")`, todo valor ausente é substituído pela string `"#"` antes da serialização, garantindo que o JSON gerado seja sempre **100% válido e interoperável**. Na API, o caractere `#` deve ser tratado como "campo não preenchido".

## Modo de uso

Os seguintes passos devem ser realizados para gerar um arquivo JSON a partir da planilha:

1. A planilha do dataWASHES deve estar no mesmo diretório do script.
2. Antes de executar o código verifique se o nome do arquivo da planilha corresponde com o argumento passado para a função `pd.read_excel()` do código.
3. Deve-se checar também se os nomes das colunas correspondem com as referências usadas no código.
4. Caso a planilha possua mais de uma página, deve-se passar mais um argumento para a função mencionada, informando qual página da planilha deve ser lida.
5. Executando o código será gerado um arquivo JSON no mesmo diretório.

> **Nota:** No pipeline automatizado, esses scripts são invocados pelo `scripts/sync_washes_dataset.py` (função `regenerate_dataset_files()`), que copia automaticamente os JSONs gerados para a pasta `data/` do projeto.

## Observações históricas (fluxo manual legado)

6. Antes de levar o arquivo para uso deve-se notar que o conteúdo não está formatado, pode-se usar o site [JSON Formatter](https://jsonformatter.curiousconcept.com/#) para formatar o conteúdo e sobrescrevê-lo depois.
7. Por fim, também deve notar que alguns caracteres aparecem como códigos unicode; para decodificá-los para texto, a ferramenta do site [Decodificador e codificador Unicode](https://magictool.ai/tool/unicode-decoder-encoder/pt/) pode ser usada.
