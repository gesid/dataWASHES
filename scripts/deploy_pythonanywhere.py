"""Deploy automatizado do dataWASHES no PythonAnywhere via Playwright.

Fluxo: login -> console Bash -> `git pull` -> reload da aplicação web.

Este é o mesmo fluxo do procedimento manual documentado em
``docs/maintenance/deploy.md`` e da antiga automação por API oficial: buscar o
código no repositório e recarregar a aplicação. O deploy não instala
dependências; ver ``build_deploy_command`` para o porquê.

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
# O comando remoto passou a ser apenas `git pull` + sentinela, que resolve em
# segundos. O limite é mantido generoso para não introduzir um segundo modo de
# falha por timeout.
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
  const q = (s) => document.querySelectorAll(s);
  const join = (nodes) => {
    const lines = Array.from(nodes).map((el) => el.textContent || '');
    return lines.some((l) => l.trim()) ? lines.join('\\n') : '';
  };
  const xterm = join(q('.xterm-rows > div'));
  if (xterm) return xterm;
  const hterm = join(q('.hterm-row'));
  if (hterm) return hterm;
  for (const s of ['.hterm-scrollable', '.hterm-screen', '.xterm-rows',
                   '.xterm-screen', '.terminal']) {
    const el = document.querySelector(s);
    if (el) {
      const t = el.textContent || '';
      if (t.trim()) return t;
    }
  }
  return '';
}
"""

# Último recurso, separado de propósito: o hterm renderiza texto real no DOM,
# então o corpo do frame contém a saída do shell. Fica isolado porque o corpo da
# página *principal* também tem texto (títulos, menus) e não serve de prova de
# que o terminal foi lido.
READ_BODY_JS = """
() => (document.body ? (document.body.innerText || document.body.textContent || '') : '')
"""

# Descreve o terreno real do console, avaliado em cada frame. Usado em qualquer
# falha para responder "o que existe de fato" em vez de fazer outro chute.
FRAME_PROBE_JS = """
() => {
  let anywhere = false;
  try { anywhere = !!(window.Anywhere && window.Anywhere.terminal); } catch (e) {}
  const probes = ['.hterm', '.hterm-screen', '.hterm-row', '.hterm-scrollable',
                  '.xterm-rows', '.xterm-screen', '.xterm-helper-textarea',
                  'canvas', 'textarea'];
  const counts = probes.map((s) => {
    try { return s + '=' + document.querySelectorAll(s).length; } catch (e) { return s + '=err'; }
  });
  let body = '';
  try { body = (document.body ? (document.body.innerText || '') : '').slice(0, 100).replace(/\\n/g, ' / '); } catch (e) {}
  return 'anywhere.terminal=' + anywhere + ' | ' + counts.join(' ') + ' | body=' + body;
}
"""


def fail(step: str, detail: str = "") -> None:
    """Encerra o deploy com código 1. Nunca retorna."""
    print(f"❌ FALHA em '{step}': {detail}" if detail else f"❌ FALHA em '{step}'.")
    print("   O código NÃO foi atualizado em produção. Trate o deploy como falho.")
    sys.exit(1)


def build_deploy_command(app_dir: str) -> str:
    """Monta a linha de comando executada no console Bash.

    Comando reto e determinístico: ``git pull`` e nada mais. A versão anterior
    ativava um virtualenv (``source .../datawashes-virtualenv/bin/activate``) e
    rodava ``pip install -r requirements.txt``; esse caminho nunca foi confirmado
    no ambiente real e fazia o deploy morrer com ``No such file or directory``
    depois de o ``git pull`` já ter sucesso.

    Esse passo não é perdido, é removido por falta de evidência de que seja
    necessário: ``pip install`` nunca fez parte do procedimento manual
    documentado, nem da automação anterior por API oficial, e o app roda com
    APIs estáveis de Flask/flask-restx, sem depender de recurso removido em
    Flask 3. Instalação de dependências, se vier a ser necessária, deve ser um
    passo explícito e com caminho verificado -- não um palpite dentro do deploy.

    A sentinela vem após um ``;``, portanto ``$?`` carrega o código de saída da
    cadeia. Não há ``\\n`` aqui: quem digita no terminal acrescenta a quebra de
    linha.
    """
    return (
        f"cd {app_dir} && "
        "git pull origin main; "
        "echo '__DATAWASHES_EXIT_'$?'__'"
    )


def read_console(page) -> str:
    """Texto do terminal, varrendo todos os frames via API do Playwright.

    Avaliar em cada frame (e não via ``contentDocument``) funciona mesmo quando
    o iframe é de outra origem, e cobre o console do PythonAnywhere, que é
    quase sempre o hterm dentro de um iframe.
    """
    try:
        frames = page.frames
    except Exception:
        frames = []
    # Primeiro, só seletores de terminal, em todos os frames. Só se nenhum
    # responder é que se recorre ao texto do corpo.
    strict = []
    for frame in frames:
        try:
            text = frame.evaluate(READ_TERMINAL_JS) or ""
        except Exception:
            continue
        if text.strip():
            strict.append(text)
    if strict:
        return "\n".join(strict)
    loose = []
    for frame in frames:
        try:
            text = frame.evaluate(READ_BODY_JS) or ""
        except Exception:
            continue
        if text.strip():
            loose.append(text)
    return "\n".join(loose)


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
        probe = []
        for frame in page.frames:
            try:
                probe.append(f"{frame.name or '(frame)'} :: {frame.evaluate(FRAME_PROBE_JS)}")
            except Exception as exc:
                probe.append(f"{frame.name or '(frame)'} :: (probe falhou: {exc})")
        probe_text = "\n      ".join(probe)
    except Exception as exc:
        probe_text = f"(probe falhou: {exc})"
    return (
        f"url={url}\n"
        f"      título={title}\n"
        f"      abas no contexto={len(page.context.pages)}\n"
        f"      frames={frames}\n"
        f"      links na página={links}\n"
        f"      terminal por frame:\n      {probe_text}"
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


SEND_VIA_API_JS = """
(cmd) => {
  let term = null;
  try { term = (window.Anywhere && window.Anywhere.terminal) || null; } catch (e) {}
  if (!term) return false;
  const io = term.io || term;
  try {
    if (typeof io.sendString === 'function') {
      io.sendString(cmd);
      if (typeof io.sendKey === 'function') io.sendKey(13);        // Enter
      else if (typeof io.sendCR === 'function') io.sendCR();
      else io.sendString('\\r');
      return true;
    }
  } catch (e) {}
  return false;
}
"""


def send_command_via_api(page, command: str) -> bool:
    """Envia o comando pela API do hterm (Anywhere.terminal.io), se existir.

    Preferível a simular teclado: a API entrega a string ao shell sem depender
    de foco, de coordenadas ou da posição do cursor -- as três coisas que quebram
    com terminal embarcado em iframe. Devolve False se a API não estiver
    disponível, para o chamador cair na digitação por teclado.
    """
    try:
        frames = page.frames
    except Exception:
        frames = []
    for frame in frames:
        try:
            if frame.evaluate(SEND_VIA_API_JS, command):
                return True
        except Exception:
            continue
    return False


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
    não há como saber em que ponto o comando parou ou se já tinha falhado.
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
    last_buffer = ""
    while time.monotonic() < deadline:
        last_buffer = read_console(page)
        match = SENTINEL_RE.search(last_buffer)
        if match:
            return int(match.group(1))
        time.sleep(1.0)
    # Anexar o estado da página aqui é essencial: foi justamente neste caminho
    # que a causa raiz (hterm em iframe) ficou invisível por vários deploys.
    raise TimeoutError(
        f"o console não devolveu o código de saída em {timeout}s. "
        f"Buffer lido: {len(last_buffer)} chars.\n"
        f"Últimas {TAIL_LINES} linhas do terminal:\n{console_tail(page, TAIL_LINES)}\n"
        f"Estado da página:\n      {describe_page(page)}"
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


def run_deploy_commands(page, app_dir: str, timeout: int) -> None:
    """Executa git pull no console e valida o código de saída."""
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

    command = build_deploy_command(app_dir)
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
            f"'git pull' retornou código {code}. "
            f"Últimas {TAIL_LINES} linhas do terminal:\n{console_tail(target, TAIL_LINES)}",
        )
    print("   ✅ git pull concluído.")


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
                run_deploy_commands(page, APP_DIR, timeout)
                reload_web_app(page)
            finally:
                browser.close()
    except Exception as exc:
        fail("execução do Playwright", f"{type(exc).__name__}: {exc}")

    print("🎉 SUCESSO: datawashes.pythonanywhere.com atualizado e recarregado.")


if __name__ == "__main__":
    deploy()
