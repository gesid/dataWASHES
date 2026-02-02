# 🧪 dataWASHES

**dataWASHES** é uma API aberta que permite acesso programático aos dados das *proceedings* do Workshop on Social, Human, and Economic Aspects of Software (WASHES).  
Esse projeto faz parte do grupo de pesquisa GESID e foi pensado para facilitar estudos e análises sobre o histórico do evento.

---

## 📌 Índice

- [Motivação](#motiva%C3%A7%C3%A3o)
- [Proposta](#proposta)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Manutenção](#manuten%C3%A7%C3%A3o)

---

## 🔍 Motivação

Given the importance of the WASHES workshop and its extensive archive of papers, este projeto nasce da necessidade de automatizar o acesso aos *proceedings*, que atualmente estão disponíveis apenas manualmente através do SBC OpenLib (SOL).

---

## 💡 Proposta

O **dataWASHES** é uma API que:
- Permite buscar programaticamente artigos, edições e autores;
- Facilita análises secundárias e pesquisa de dados;
- É open-source e colaborativo.

---

## 📁 Estrutura do Projeto

| Caminho                  | Descrição                                      |
|--------------------------|------------------------------------------------|
| `data/`                  | Dados brutos                                   |
| `src/`                   | Código-fonte principal da API                  |
| `tests/`                 | Testes automatizados                           |
| `.github/workflows/`     | Pipelines de CI/CD e validações automáticas    |
| `requirements.txt`       | Dependências do projeto                        |
| `README.md`              | Instruções para usar o projeto                 |
| `ideas.md`               | Ideias e propostas de evolução                 |
| `LICENSE`                | Licença do projeto                             |

---

## 🔧 Manutenção

Para que o projeto se mantenha saudável e relevante duas pincipais atividades de manutenção devem ser realizadas:

1. [Atualizar dados](./maintenance/update-data.md)
1. [Deploy no PythonAnywhere](./maintenance/deploy.md)