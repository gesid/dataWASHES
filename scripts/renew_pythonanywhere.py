import os
import time
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("PYTHONANYWHERE_USERNAME", "datawashes")
PASSWORD = os.getenv("PYTHONANYWHERE_PASSWORD", "")

def renew_pythonanywhere():
    if not PASSWORD:
        print("❌ Senha do PythonAnywhere não configurada nas Secrets.")
        return

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
            print("ℹ️ O botão de renovação ainda não estava disponível ou já foi renovado.")

        browser.close()

if __name__ == "__main__":
    renew_pythonanywhere()