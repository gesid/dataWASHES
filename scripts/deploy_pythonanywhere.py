"""Deploy automatizado do dataWASHES no PythonAnywhere via Playwright.

Fluxo: login -> console Bash -> `git pull` + instalação das dependências no
virtualenv -> reload da aplicação web.

Princípio de robustez: **nenhuma falha pode passar silenciosa**. Um deploy que
printa "✅" e sai com código 0 depois de um `git pull` quebrado é pior que um
deploy que não roda, porque o workflow fica verde e ninguém percebe que a
produção está servindo código velho. Por isso toda etapa tem verificação
explícita e qualquer erro encerra o processo com ``sys.exit(1)``.

A verificação dos comandos de console não se baseia em "pareceu que rodou": cada
comando é encadeado com ``&&`` até um eco sentinela ``echo "__EXIT_<codigo>__"``
que só é impresso se toda a cadeia tiver sucesso. O código lido da sentinela é
o código de saída real da cadeia, lido do buffer do terminal (xterm.js).
"""

import os
import re
import sys
import time

# O console do runner do GitHub Actions nem sempre é UTF-8 (cp1252 no Windows,
# latin-1 em alguns runners Linux). Sem isto, o primeiro emoji do `print`
# estoura UnicodeEncodeError e o traceback esconde a mensagem de falha real --
# exatamente o oposto do que este script pretende.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

USERNAME = os.getenv("PYTHONANYWHERE_USERNAME", "datawashes")
PASSWORD = os.getenv("PYTHONANYWHERE_PASSWORD", "")

APP_DIR = os.getenv("PYTHONANYWHERE_APP_DIR", "~/mysite")
VENV_DIR = os.getenv(
    "PYTHONANYWHERE_VENV", "~/.virtualenvs/datawashes-virtualenv"
)
# 300s é apertado para `pip install` em máquina gratuita e foi a causa do
# timeout do último deploy. 420s dá folga para o build completo.
DEFAULT_TIMEOUT = int(os.getenv("PYTHONANYWHERE_TIMEOUT", "420"))

SENTINEL_RE = re.compile(r"__DATAWASHES_EXIT_(-?\d+)__")

# Quantas linhas do terminal anexar ao log quando algo dá errado.
TAIL_LINES = int(os.getenv("PYTHONANYWHERE_TAIL_LINES", "10"))

LOGIN_URL = "https://www.pythonanywhere.com/login/"
CONSOLES_URL = "https://www.pythonanywhere.com/user/{user}/consoles/"
WEBAPPS_URL = "https://www.pythonanywhere.com/user/{user}/webapps/#tab_id_{user}_pythonanywhere_com"

# Lê o buffer visível do terminal xterm.js usado pelo console do PythonAnywhere.
READ_TERMINAL_JS = """
() => {
  const rows = document.querySelector('.xterm-rows')
    || document.querySelector('.xterm-screen');
  return rows ? rows.innerText : '';
}
"""


def fail(step: str, detail: str = "") -> None:
    """Encerra o deploy com código 1. Nunca retorna."""
    print(f"❌ FALHA em '{step}': {detail}" if detail else f"❌ FALHA em '{step}'.")
    print("   O código NÃO foi atualizado em produção. Trate o deploy como falho.")
    sys.exit(1)


def build_deploy_command(app_dir: str, venv_dir: str) -> str:
    """Monta a linha de comando executada no console Bash.

    Comando reto e determinístico: sem fallback, sem glob, sem subshell. A
    versão anterior usava ``||`` com ``ls`` e ``$(...)`` para adivinhar o
    virtualenv; no console do PythonAnywhere isso travou o runner e o deploy
    died por timeout sem mensagem útil. Menos shell é mais shell confiável.

    ``&&`` garante que ``pip install`` só roda se o ``git pull`` passou. O
    ``echo`` da sentinela vem após um ``;``, portanto ``$?`` carrega o código de
    saída da cadeia inteira. Não há ``\\n`` aqui: quem digita no terminal
    acrescenta a quebra de linha.
    """
    return (
        f"cd {app_dir} && "
        f"git pull origin main && "
        f"source {venv_dir}/bin/activate && "
        f"pip install -r requirements.txt; "
        f"echo '__DATAWASHES_EXIT_'$?'__'"
    )


def read_console(page) -> str:
    """Devolve o texto do buffer do terminal, ou string vazia se ilegível."""
    try:
        return page.evaluate(READ_TERMINAL_JS) or ""
    except Exception:
        return ""


def console_tail(page, lines: int = 10) -> str:
    """Últimas ``lines`` linhas não vazias do console, para diagnóstico.

    Sem isso, um timeout de 300s chega ao log como "sentinela não apareceu" e
    não há como saber se o `pip install` estava instalando, compilando ou já
    tinha falhado.
    """
    raw = read_console(page)
    rows = [line.rstrip() for line in raw.replace("\r", "\n").split("\n")]
    tail = [line for line in rows if line.strip()][-lines:]
    if not tail:
        return "(buffer do terminal vazio ou ilegível)"
    return "\n".join(f"      | {line}" for line in tail)


def wait_for_exit_code(page, timeout: int = DEFAULT_TIMEOUT) -> int:
    """Aguarda a sentinela da cadeia de comandos e devolve o código de saída.

    Levanta ``TimeoutError`` se a sentinela não aparecer no tempo limite, o que
    na prática significa console travado, login perdido ou comando que nunca
    terminou.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        match = SENTINEL_RE.search(read_console(page))
        if match:
            return int(match.group(1))
        time.sleep(1.0)
    raise TimeoutError(
        f"o console não devolveu o código de saída em {timeout}s. "
        f"Últimas {TAIL_LINES} linhas do terminal:\n{console_tail(page, TAIL_LINES)}"
    )


def login_form_visible(page) -> bool:
    """True se a página atual ainda mostra o formulário de login."""
    return page.locator("input[name='auth-username']").count() > 0


def login(page) -> None:
    """Autentica no painel. Encerra o processo se o login falhar."""
    print("🔑 1. Fazendo login...")
    page.goto(LOGIN_URL)
    page.wait_for_load_state("networkidle")
    page.fill("input[name='auth-username']", USERNAME)
    page.fill("input[name='auth-password']", PASSWORD)
    page.click("button#id_next")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    if login_form_visible(page):
        fail(
            "login",
            "o formulário de login continua visível após submeter "
            "(credencial expirada, bloqueada ou 2FA pendente)",
        )

    try:
        page.goto(CONSOLES_URL.format(user=USERNAME))
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
    except Exception as exc:
        fail("login", f"não foi possível abrir a área de consoles após o login: {exc}")

    if login_form_visible(page):
        fail("login", f"sessão expirada ao abrir {CONSOLES_URL.format(user=USERNAME)}")

    print("   ✅ Login confirmado.")


def run_deploy_commands(page, app_dir: str, venv_dir: str, timeout: int) -> None:
    """Executa git pull + pip install no console e valida o código de saída."""
    print("💻 2. Abrindo console Bash...")
    page.wait_for_timeout(1000)

    bash_link = (
        page.query_selector("a[href*='/consoles/']:has-text('Bash')")
        or page.query_selector("a[href*='/consoles/']")
    )
    if not bash_link:
        fail("console", "nenhum link de console Bash encontrado na página de consoles")

    bash_link.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    command = build_deploy_command(app_dir, venv_dir)
    print(f"   $ {command}")
    page.keyboard.type(command + "\n", delay=20)

    try:
        code = wait_for_exit_code(page, timeout=timeout)
    except TimeoutError as exc:
        fail("deploy no console", str(exc))

    if code != 0:
        fail(
            "deploy no console",
            f"'git pull' ou 'pip install' retornou código {code}. "
            f"Últimas {TAIL_LINES} linhas do terminal:\n{console_tail(page, TAIL_LINES)}",
        )
    print("   ✅ git pull e instalação das dependências concluídos.")


def reload_web_app(page) -> None:
    """Dispara o reload da aplicação web e confirma que o botão respondeu."""
    print("🔄 3. Acessando aba Web para disparar o Reload...")
    page.goto(WEBAPPS_URL.format(user=USERNAME))
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    if login_form_visible(page):
        fail("reload", f"sessão expirada ao abrir {WEBAPPS_URL.format(user=USERNAME)}")

    reload_btn = (
        page.query_selector("input[value*='Reload']")
        or page.query_selector("button:has-text('Reload')")
    )
    if not reload_btn:
        fail(
            "reload",
            "botão de Reload não encontrado na página de webapps; "
            "confirme se a aplicação continua cadastrada no PythonAnywhere",
        )

    try:
        reload_btn.click()
    except Exception as exc:
        fail("reload", f"falha ao clicar no botão de Reload: {exc}")

    page.wait_for_timeout(4000)
    print("   ✅ Reload disparado.")


def deploy() -> None:
    """Executa o deploy completo; encerra com código 1 em qualquer falha."""
    if not PASSWORD:
        fail(
            "pré-requisito",
            "PYTHONANYWHERE_PASSWORD não configurada. "
            "Defina a secret no repositório antes de acionar o deploy.",
        )

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        fail("dependência", f"Playwright não instalado no runner: {exc}")

    print("🚀 Iniciando deploy automatizado via Playwright no PythonAnywhere...")
    timeout = DEFAULT_TIMEOUT

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                login(page)
                run_deploy_commands(page, APP_DIR, VENV_DIR, timeout)
                reload_web_app(page)
            finally:
                browser.close()
    except Exception as exc:
        fail("execução do Playwright", f"{type(exc).__name__}: {exc}")

    print("🎉 SUCESSO: datawashes.pythonanywhere.com atualizado e recarregado.")


if __name__ == "__main__":
    deploy()
