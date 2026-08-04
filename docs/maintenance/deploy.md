# 🚀 Deploy no PythonAnywhere

O **dataWASHES** está hospedado na plataforma PythonAnywhere. Com a atual automação de dados no repositório, o processo de deploy em produção tornou-se muito mais simples e seguro, eliminando a necessidade de uploads manuais.

### ⚠️ Pré-requisito: Credenciais de Produção
1. Solicite o **Usuário e Senha** da conta PythonAnywhere do dataWASHES com o administrador do projeto.
2. Certifique-se de que os dados novos já foram aprovados via *Pull Request* e estão disponíveis na branch `main` do repositório no GitHub.

---

## ⚡ Atualizando o servidor via Console (Método Recomendado)

Como o repositório no GitHub é a fonte única da verdade, a maneira mais rápida de atualizar a API é sincronizar o servidor com o GitHub.

1. Faça login na conta do [PythonAnywhere](https://www.pythonanywhere.com/).
2. Na aba **Consoles**, clique em **Bash** para abrir o terminal na nuvem.
3. Navegue até a pasta do projeto:
   ```bash
   cd /home/datawashes/mysite
   ```
4. Puxe as atualizações recentes da branch `main`:
   ```bash
   git pull origin main
   ```
*Pronto! Todos os arquivos JSON da pasta `data/` e códigos da pasta `src/` foram atualizados instantaneamente.*

---

## 🔄 Passo Final Obrigatório: Recarregar a API

Sempre que houver **novos dados JSON** ou **alterações no código**, é estritamente necessário reiniciar a aplicação web.

1. Acesse a aba **Web** no painel superior do PythonAnywhere.
2. Clique no botão verde **"Reload datawashes.pythonanywhere.com"**.

Isso forçará a API a limpar o cache e carregar os dados das edições e artigos recém-sincronizados. Sem o *Reload*, a API continuará exibindo os dados antigos mesmo com os arquivos atualizados no servidor.

---

## 🛠️ Configuração WSGI (Referência)

A execução da aplicação é gerenciada pelo arquivo **WSGI configuration file** (acessível pela aba **Web**). O conteúdo deste arquivo vincula o diretório `/mysite` à execução do Flask:

```python
import sys

# Adiciona o diretório do projeto ao sys.path
project_home = '/home/datawashes/mysite'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Importa a aplicação Flask e inicializa as rotas
from src import app
app.main()
application = app.server.app  # noqa
```

*(Nota: O código em `src/app.py` possui uma estrutura inteligente com `if __name__ == '__main__':` que impede o conflito entre o servidor de desenvolvimento local e o servidor WSGI de produção).*

---

## ⏳ Importante: Expiração Mensal da Conta Gratuita

A versão gratuita do PythonAnywhere mantém a aplicação ativa por ciclos de **1 mês**. Após esse prazo, a API sairá do ar automaticamente. 

Para evitar a queda do serviço:
1. O administrador deve acessar o painel do PythonAnywhere mensalmente.
2. Clicar no botão amarelo **"Run until X"** na aba **Web** para renovar a hospedagem por mais 30 dias.

![image](../images/deploy-6.png)