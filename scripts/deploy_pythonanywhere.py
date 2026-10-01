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

# Leitura do buffer do terminal xterm.js.
#
# `innerText` respeita o rendering CSS, e o xterm.js posiciona cada linha com
# `transform: translateY(...)` dentro de uma área de overflow. Quando isso
# acontece `innerText` devolve string vazia -- foi exatamente o que aconteceu no
# deploy que expirou em 420s com "(buffer do terminal vazio ou ilegível)".
#
# Por isso as estratégias são tentadas em ordem de robustez, e `textContent` vem
# antes de `innerText` porque independe de estilo. O console do PythonAnywhere
# expõe as linhas em `.xterm-rows > div`.
READ_TERMINAL_JS = """
() => {
  const docs = [document];
  for (const f of Array.from(document.querySelectorAll('iframe'))) {
    try { if (f.contentDocument) docs.push(f.contentDocument); } catch (e) {}
  }
  for (const d of docs) {
    const xtermRows = d.querySelectorAll('.xterm-rows > div');
    if (xtermRows.length) {
      const lines = Array.from(xtermRows).map((el) => el.textContent || '');
      if (lines.some((l) => l.trim())) return lines.join('\\n');
    }
    const htermRows = d.querySelectorAll('.hterm-row');
    if (htermRows.length) {
      const lines = Array.from(htermRows).map((el) => el.textContent || '');
      if (lines.some((l) => l.trim())) return lines.join('\\n');
    }
    const screen = d.querySelector('.hterm-screen, .xterm-rows, .xterm-screen');
    if (screen) {
      const viaText = screen.textContent || '';
      if (viaText.trim()) return viaText;
    }
  }
  return '';
}
"""

# Descreve o terreno real do console. Se o seletor estiver errado de novo, este
# mapa diz o que existe de fato -- encerrando o ciclo de tentativa e erro às
# custas de um deploy de ~7 minutos por tentativa.
PROBE_JS = """
() => {
  const docs = [['main', document]];
  for (const f of Array.from(document.querySelectorAll('iframe'))) {
    try {
      if (f.contentDocument) docs.push([f.id || f.name || '(sem id)', f.contentDocument]);
    } catch (e) {}
  }
  const probes = ['.xterm-helper-textarea', '.xterm-rows', '.xterm-screen', '.hterm',
                  '.hterm-screen', '.hterm-row', 'canvas', 'textarea'];
  const out = [];
  for (const [name, d] of docs) {
    let anywhere = false;
    try {
      anywhere = !!(d.defaultView && d.defaultView.Anywhere && d.defaultView.Anywhere.terminal);
    } catch (e) {}
    const counts = probes.map((s) => {
      try { return s + '=' + d.querySelectorAll(s).length; } catch (e) { return s + '=err'; }
    });
    out.push(name + ' | anywhere.terminal=' + anywhere + ' | ' + counts.join(' '));
  }
  return out.join('\\n      ');
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

    O ``echo "INICIANDO PIP"`` é um marco de progresso: se ele não aparecer no
    console, sabemos que o comando morreu antes do pip (``cd``, ``git pull`` ou
    ``source`` falhou) em vez de ficarmos sem saber em que ponto parou.
    """
    return (
        f"cd {app_dir} && "
        f"git pull origin main && "
        f"source {venv_dir}/bin/activate && "
        f'echo "INICIANDO PIP" && pip install -r requirements.txt; '
        f"echo '__DATAWASHES_EXIT_'$?'__'"
    )


def read_console(page) -> str:
    """Devolve o texto do buffer do terminal, ou string vazia se ilegível."""
    try:
        return page.evaluate(READ_TERMINAL_JS) or ""
    except Exception:
        return ""


# O console do PythonAnywhere NÃO é xterm.js por padrão: a documentação oficial
# diz que usam hterm na maioria das contas (xterm.js só em algumas). O terminal
# do hterm vive dentro de um <iframe id="id_console"> e é alcançado por
# `iframe.contentWindow.Anywhere.terminal`. Por isso a lista cobre as duas
# tecnologias, e a leitura percorre também os iframes.
READY_SELECTORS = (
    "iframe#id_console",
    ".xterm-helper-textarea",
    ".xterm-cursor",
    ".xterm-rows",
    ".xterm-screen",
    ".hterm-screen",
    ".hterm-row",
    ".hterm",
    ".terminal",
    ".CodeMirror",
)


def open_console_tab(page, link, timeout: int = 45):
    """Clica no link do console e devolve a página onde o terminal realmente está.

    O PythonAnywhere não navega a aba atual: ele abre o console em outra aba
    (evento ``popup``) e, em algumas versões, dentro de um ``iframe``. Se
    ignorado, o código continua inspecionando a listagem de consoles e conclui
    que o xterm.js nunca apareceu.
    """
    context = page.context
    before = set(context.pages)

    try:
        with context.expect_page(timeout=timeout) as popup_info:
            link.click()
    except Exception:
        # Sem popup: talvez tenha navegado na própria aba.
        pass

    # Dá um instante para o Playwright registrar a nova aba.
    deadline = time.monotonic() + timeout
    new_pages = []
    while time.monotonic() < deadline:
        new_pages = [p for p in context.pages if p not in before and not p.is_closed()]
        if new_pages:
            break
        page.wait_for_timeout(300)

    console_page = new_pages[0] if new_pages else page
    if new_pages:
        print(f"   Console abriu em nova aba ({len(new_pages)}).")
    else:
        print("   Nenhuma aba nova; o console reutilizou a aba atual.")
    try:
        console_page.wait_for_load_state("networkidle")
    except Exception:
        pass
    console_page.wait_for_timeout(2000)
    return console_page


def describe_page(page) -> str:
    """Resumo do que existe na página, para diagnóstico de falha.

    Sem isto, um "terminal não encontrado" não diz se faltou o popup, se o
    link Levou à página errada ou se o seletor ficou obsoleto -- e cada tentativa
    custa um deploy de 420s.
    """
    try:
        url = page.url
    except Exception:
        url = "?"
    try:
        title = page.title()
    except Exception:
        title = "?"
    try:
        links = page.locator("a").count()
    except Exception:
        links = -1
    try:
        frames = len(page.frames)
    except Exception:
        frames = -1
    try:
        probe = page.evaluate(PROBE_JS)
    except Exception as exc:
        probe = f"(probe falhou: {exc})"
    return (
        f"url={url}\n"
        f"      título={title}\n"
        f"      abas no contexto={len(page.context.pages)}\n"
        f"      frames={frames}\n"
        f"      links na página={links}\n"
        f"      terminal por documento:\n      {probe}"
    )


def find_terminal_frame(page):
    """Se o terminal estiver em iframe, devolve o frame que contém o xterm."""
    for frame in page.frames:
        for selector in READY_SELECTORS:
            try:
                if frame.locator(selector).count() > 0:
                    return frame
            except Exception:
                continue
    return None


def send_command_via_api(page, command: str) -> bool:
    """Envia o comando pela API do hterm (Anywhere.terminal.io), se existir.

    Preferível a simular teclado: a API entrega a string ao shell sem depender
    de foco, de coordenadas ou da posição do cursor -- as três coisas que
    quebram com terminal embarcado em iframe. Devolve False se a API não
    estiver disponível, para o chamador cair na digitação por teclado.
    """
    sent = page.evaluate(
        """
        (cmd) => {
          const docs = [document];
          for (const f of Array.from(document.querySelectorAll('iframe'))) {
            try { if (f.contentDocument) docs.push(f.contentDocument); } catch (e) {}
          }
          for (const d of docs) {
            let term = null;
            try { term = d.defaultView && d.defaultView.Anywhere && d.defaultView.Anywhere.terminal; } catch (e) {}
            if (!term) continue;
            const io = term.io || term;
            try {
              if (typeof io.sendString === 'function') {
                io.sendString(cmd);
                if (typeof io.sendKey === 'function') io.sendKey(13);       // Enter
                else if (typeof io.sendCR === 'function') io.sendCR();
                else io.sendString('\\r');
                return true;
              }
            } catch (e) {}
          }
          return false;
        }
        """,
        command,
    )
    return bool(sent)


def wait_for_terminal_ready(page, timeout: int = 60):
    """Aguarda o xterm.js montar e ficar interativo; foca o terminal.

    Sem esta espera, o comando é digitado enquanto a página ainda exibe
    "Loading console..." e a teclas vão para o vazio: o shell nunca recebe nada,
    a sentinela nunca aparece e o deploy só pode expirar. Clicar no terminal
    também é necessário -- o `keyboard.type` envia eventos para o elemento em
    foco, que após um `page.goto` raramente é o terminal.

    Devolve ``(alvo_de_leitura, page_de_digitacao)``: o alvo é a própria page
    ou o frame que contém o terminal; a page de digitação é sempre um objeto
    ``Page``, pois ``Frame`` não possui ``.keyboard``.
    """
    deadline = time.monotonic() + timeout
    target = page
    last = ""
    while time.monotonic() < deadline:
        for selector in READY_SELECTORS:
            try:
                if page.locator(selector).count() > 0:
                    last, target = selector, page
                    break
            except Exception:
                continue
        if last:
            break
        # O terminal pode estar dentro de um iframe do console.
        frame = find_terminal_frame(page)
        if frame is not None:
            last, target = "iframe", frame
            break
        page.wait_for_timeout(500)

    # Achar a tag <iframe id="id_console"> não prova que o terminal já
    # renderizou: o iframe existe antes do conteúdo carregar. Por isso, quando
    # o alvo é o próprio iframe, só consideramos pronto quando o buffer
    # devolver texto de verdade.
    if last and read_console(target).strip() == "":
        probe_deadline = time.monotonic() + min(timeout, 30)
        while time.monotonic() < probe_deadline:
            if read_console(target).strip():
                break
            page.wait_for_timeout(500)

    if not last:
        fail(
            "console",
            f"o terminal xterm.js não ficou pronto em {timeout}s "
            f"(nenhum de {', '.join(READY_SELECTORS)} encontrado). "
            f"Estado da página:\n      {describe_page(page)}",
        )

    print(f"   Terminal pronto ({last}).")
    # `Frame` não expõe `.keyboard`; o foco e a digitação vão pela Page, enquanto
    # a leitura do buffer usa o frame. Por isso devolvemos os dois.
    keyboard_page = page
    try:
        target.locator(READY_SELECTORS[0]).first.click(timeout=5000)
    except Exception:
        for selector in READY_SELECTORS:
            try:
                target.locator(selector).first.click(timeout=2000)
                break
            except Exception:
                continue
    page.wait_for_timeout(500)
    return target, keyboard_page


def console_is_readable(page, attempts: int = 10, delay: float = 1.0) -> bool:
    """True se o buffer do terminal devolver algum texto.

    Usado como diagnóstico: um buffer ilegível impede qualquer verificação da
    sentinela, então é melhor detectá-lo logo e falhar com mensagem clara do que
    esperar o timeout inteiro para descobrir que nada era observável.

    A checagem é repetida algumas vezes porque o xterm.js pode existir no DOM
    antes de pintar o prompt: uma única leitura às cegas produziria falso
    negativo e abortaria um deploy que estava prestes a funcionar.
    """
    for attempt in range(attempts):
        if read_console(page).strip():
            if attempt:
                print(f"   Buffer ficou legível após {attempt}s.")
            return True
        if attempt < attempts - 1:
            time.sleep(delay)
    return False


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
        fail(
            "console",
            "nenhum link de console Bash encontrado na página de consoles. "
            f"Estado da página:\n      {describe_page(page)}",
        )

# O PythonAnywhere abre o console em uma NOVA ABA (ou iframe). Sem tratar
    # isso, `page` continua apontando para a listagem de consoles, onde não
    # existe nenhum xterm.js -- foi exatamente o que produziu
    # "o terminal xterm.js não ficou pronto em 60s".
    console_page = open_console_tab(page, bash_link)
    target, keyboard_page = wait_for_terminal_ready(console_page)

    if not console_is_readable(target):
        # Aviso, não falha: o xterm.js pode existir no DOM antes de pintar o
        # prompt, e um falso negativo aqui abortaria um deploy que funcionaria.
        # A verificação autoritativa é a sentinela; se o buffer estiver realmente
        # ilegível, o fluxo falhará no timeout com `describe_page` anexado.
        print(
            "   ⚠️  Buffer do terminal ainda vazio; seguindo. "
            "Se o deploy expirar, o log terá o estado da página."
        )

    command = build_deploy_command(app_dir, venv_dir)
    print(f"   $ {command}")
    if send_command_via_api(console_page, command):
        print("   Comando enviado pela API do terminal (hterm).")
    else:
        print("   API do terminal indisponível; digitando pelo teclado.")
        keyboard_page.keyboard.type(command, delay=20)
        keyboard_page.keyboard.press("Enter")

    try:
        code = wait_for_exit_code(target, timeout=timeout)
    except TimeoutError as exc:
        fail("deploy no console", str(exc))

    if code != 0:
        fail(
            "deploy no console",
            f"'git pull' ou 'pip install' retornou código {code}. "
            f"Últimas {TAIL_LINES} linhas do terminal:\n{console_tail(target, TAIL_LINES)}",
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
