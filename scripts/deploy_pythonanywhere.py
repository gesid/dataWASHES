import os
import time
import requests

USERNAME = "datawashes"
DOMAIN = "datawashes.pythonanywhere.com"
TOKEN = os.getenv("PYTHONANYWHERE_API_TOKEN")

def deploy():
    if not TOKEN:
        print("❌ PYTHONANYWHERE_API_TOKEN não configurada nas Secrets do GitHub.")
        return

    headers = {"Authorization": f"Token {TOKEN}"}
    base_url = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}"

    print("🚀 1. Criando console no PythonAnywhere para executar git pull...")
    res = requests.post(f"{base_url}/consoles/", json={"executable": "bash"}, headers=headers)
    
    if res.status_code == 201:
        console_id = res.json()["id"]
        print(f"💻 Console #{console_id} aberto. Enviando 'git pull origin main'...")
        cmd = "cd /home/datawashes/mysite && git pull origin main\n"
        requests.post(f"{base_url}/consoles/{console_id}/send_input/", json={"input": cmd}, headers=headers)
        
        # Aguarda a conclusão do git pull
        time.sleep(8)
        
        # Fecha o console temporário
        requests.delete(f"{base_url}/consoles/{console_id}/", headers=headers)
    else:
        print(f"⚠️ Não foi possível abrir console ({res.status_code}). Tentando reload direto...")

    # 2. Dispara o Reload da aplicação Web
    print("🔄 2. Disparando Reload da aplicação Web...")
    reload_res = requests.post(f"{base_url}/webapps/{DOMAIN}/reload/", headers=headers)
    if reload_res.status_code == 200:
        print("🎉 SUCESSO: datawashes.pythonanywhere.com atualizado e recarregado com sucesso!")
    else:
        print(f"❌ Erro ao dar reload ({reload_res.status_code}): {reload_res.text}")

if __name__ == "__main__":
    deploy()
