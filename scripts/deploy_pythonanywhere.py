import os
import time
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("PYTHONANYWHERE_USERNAME", "datawashes")
PASSWORD = os.getenv("PYTHONANYWHERE_PASSWORD", "")

def deploy():
    if not PASSWORD:
        print("❌ PYTHONANYWHERE_PASSWORD não configurada nas Secrets do GitHub.")
        return

    print("🚀 Iniciando deploy automatizado via Playwright no PythonAnywhere...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Login no PythonAnywhere
        print("🔑 1. Fazendo login...")
        page.goto("https://www.pythonanywhere.com/login/")
        page.fill("input[name='auth-username']", USERNAME)
        page.fill("input[name='auth-password']", PASSWORD)
        page.click("button#id_next")
        page.wait_for_load_state("networkidle")

        # 2. Acessa os consoles para rodar o git pull
        print("💻 2. Acessando console para rodar 'git pull origin main'...")
        page.goto(f"https://www.pythonanywhere.com/user/{USERNAME}/consoles/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        bash_link = page.query_selector("a[href*='/consoles/']:has-text('Bash')") or page.query_selector("a[href*='/consoles/']")
        if bash_link:
            bash_link.click()
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            page.keyboard.type("cd /home/datawashes/mysite && git pull origin main\n", delay=20)
            time.sleep(6)
            print("   ✅ Comando 'git pull' executado.")

        # 3. Dispara o Reload da aplicação Web
        print("🔄 3. Acessando aba Web para disparar o Reload...")
        page.goto(f"https://www.pythonanywhere.com/user/{USERNAME}/webapps/#tab_id_{USERNAME}_pythonanywhere_com")
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        reload_btn = page.query_selector("input[value*='Reload']") or page.query_selector("button:has-text('Reload')")
        if reload_btn:
            reload_btn.click()
            print("🎉 SUCESSO: datawashes.pythonanywhere.com atualizado e recarregado com sucesso!")
            time.sleep(3)
        else:
            print("❌ Botão de reload não encontrado.")

        browser.close()

if __name__ == "__main__":
    deploy()
