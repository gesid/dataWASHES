# Mode de uso do script "paperJSON.py"

Esse script transforma a planilha (dataset) dataWASHES em um arquivo JSON contendo os artigos.

O JSON gerado é no formato especificado inicialmente para os objetos "papers" da API.

Os seguintes passos devem ser realizados para gerar um arquivo JSON a partir da planilha:

1. A planilha do dataWASHES deve estar no mesmo diretório do script
2. Antes de executar o código verifique se o nome do arquivo da planilha corresponde com o argumento passado para a função "pd.read_excel()" do código.
3. Deve-se checar também se os nomes das colunas correspondem com as referências usadas no código.
4. Caso a planilha possua mais de uma página, deve-se passar mais um argumento para a função mencionado, informando qual a página da planilha deve ser lida.
5. Executando o código deve ser gerado um arquivo JSON no mesmo diretório.
6. Antes de levar o arquivo para uso deve-se notar que o conteúdo não está formatado, pode-se usar o site [JSON Formatter](https://jsonformatter.curiousconcept.com/#) para formatar o conteúdo e sobrescreve-lo depois.
7. Por fim também deve notar que alguns caracteres aparecem como códigos unicode, para decodificalos para texto a ferramente do site [Decodificador e codificador Unicode](https://magictool.ai/tool/unicode-decoder-encoder/pt/) pode ser usada.
