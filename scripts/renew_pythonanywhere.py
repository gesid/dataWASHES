import os
import sys
import time
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("PYTHONANYWHERE_USERNAME", "datawashes")
PASSWORD = os.getenv("PYTHONANYWHERE_PASSWORD", "")


def fail(message):
    """Encerra com código != 0 para que o step de alerta do CI seja disparado."""
    print(f"\n❌ ERRO FATAL: {message}")
    sys.exit(1)

def renew_pythonanywhere():
    if not PASSWORD:
        fail(
            "a secret PYTHONANYWHERE_PASSWORD não está configurada. "
            "Sem ela o robô não consegue renovar a hospedagem."
        )

    print("🤖 Iniciando robô de renovação no PythonAnywhere...")
    
    with sync_playwright() as p:
        # Abre o navegador Chromium invisível
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Faz Login
        print("🔑 Acessando tela de login...")
        page.goto("https://www.pythonanywhere.com/login/")
        page.fill("input[name='auth-username']", USERNAME)
        page.fill("input[name='auth-password']", PASSWORD)
        page.click("button#id_next")
        
        page.wait_for_load_state("networkidle")

        # Login falhado deixa o formulário visível; nesse caso o painel nunca
        # carrega e um seletor genérico poderia "encontrar" algo por engano.
        if page.query_selector("input[name='auth-password']"):
            browser.close()
            fail(
                "login no PythonAnywhere recusado (usuário/senha inválidos ou "
                "CAPTCHA apresentado). A hospedagem não foi renovada."
            )

        # 2. Vai para a página do Web App
        print("🌐 Navegando para a aba Web...")
        page.goto(f"https://www.pythonanywhere.com/user/{USERNAME}/webapps/#tab_id_{USERNAME}_pythonanywhere_com")
        time.sleep(3)

        # 3. Clica no botão amarelo "Run until 1 month from today"
        btn = page.query_selector("input[value*='Run until']") or page.query_selector("button:has-text('Run until')")
        
        if btn:
            btn.click()
            print("🎉 SUCESSO: Botão de renovação estendido por mais 30 dias!")
        else:
            browser.close()
            fail(
                "o botão 'Run until 1 month from today' não foi encontrado no "
                "painel. A renovação não foi feita e o site pode sair do ar."
            )

        browser.close()

if __name__ == "__main__":
    renew_pythonanywhere()