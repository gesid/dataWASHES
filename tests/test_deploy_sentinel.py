"""Testes do protocolo de sentinela do console persistente do PythonAnywhere.

Regressão coberta: o console é reutilizado entre execuções, então o scrollback
contém sentinelas de runs anteriores. Com marcador fixo, o run #32 casou com o
``__DATAWASHES_EXIT_1__`` do run #31 e reportou falha indevida.
"""

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from deploy_pythonanywhere import (  # noqa: E402
    SENTINEL_PREFIX,
    build_deploy_command,
    cut_point,
    new_run_token,
    sentinel_re,
)


def test_token_is_unique_per_call():
    tokens = {new_run_token() for _ in range(200)}
    assert len(tokens) == 200


def test_command_embeds_this_run_token():
    token = new_run_token()
    command = build_deploy_command("~/mysite", token)
    assert command == (
        f"cd ~/mysite && git pull origin main; "
        f"echo '{SENTINEL_PREFIX}{token}_EXIT_'$?'__'"
    )


def test_command_has_no_venv_nor_pip():
    command = build_deploy_command("~/mysite", new_run_token())
    assert "activate" not in command
    assert "pip install" not in command
    assert "virtualenv" not in command


def test_regex_accepts_own_sentinel():
    token = new_run_token()
    regex = sentinel_re(token)
    assert regex.search(f"__DATAWASHES_{token}_EXIT_0__").group(1) == "0"
    assert regex.search(f"__DATAWASHES_{token}_EXIT_1__").group(1) == "1"


def test_regex_rejects_residual_sentinel_from_previous_run():
    """O bug do run #32: sentinela antiga não pode casar com o token atual."""
    old_token = new_run_token()
    residual = f"__DATAWASHES_{old_token}_EXIT_1__"
    current_token = new_run_token()

    assert sentinel_re(old_token).search(residual)
    assert sentinel_re(current_token).search(residual) is None


def test_echoed_command_line_is_not_a_false_positive():
    """O eco do comando digitado contém o token, mas não é uma sentinela."""
    token = new_run_token()
    echoed = f"echo '{SENTINEL_PREFIX}{token}_EXIT_'$?'__'"
    assert sentinel_re(token).search(echoed) is None


def test_cut_point_discards_exact_previous_buffer():
    baseline = "linha1\nlinha2\n__DATAWASHES_antigo_EXIT_1__"
    buffer = baseline + "\nnova saida\n__DATAWASHES_atual_EXIT_0__"
    assert cut_point(buffer, baseline) == len(baseline)


def test_cut_point_degrades_safely_when_scrolled():
    """Se o terminal rolou, o corte não pode rejeitar a sentinela atual."""
    baseline = "velho1\nvelho2\nvelho3"
    scrolled = "velho3\nnovo\n__DATAWASHES_atual_EXIT_0__"
    pos = cut_point(scrolled, baseline)
    assert 0 <= pos < len(scrolled)
    assert scrolled.find("__DATAWASHES_atual_EXIT_0__", pos) != -1


def test_cut_point_without_baseline_is_zero():
    assert cut_point("qualquer coisa", "") == 0


@pytest.mark.parametrize("code", ["0", "1", "2", "128", "255"])
def test_exit_codes_are_preserved(code):
    """Cobre 0, falha e os códigos de erro típicos de shell."""
    token = new_run_token()
    buffer = (
        "20:00 ~/mysite (master)$ cd ~/mysite && git pull origin main\n"
        f"Already up to date.\n__DATAWASHES_{token}_EXIT_{code}__\n"
    )
    match = sentinel_re(token).search(buffer)
    assert match is not None
    assert int(match.group(1)) == int(code)


def test_end_to_end_residual_buffer_then_current_result():
    """Reproduz o cenário real: buffer velho + saída da execução atual."""
    residual = (
        "eb6f36a..be96f0a  main -> origin/main\n"
        "bash: /home/datawashes/.virtualenvs/datawashes-virtualenv/bin/activate:"
        " No such file or directory\n"
    )
    previous_token = new_run_token()
    old_sentinel = f"{SENTINEL_PREFIX}{previous_token}_EXIT_1__"
    baseline = residual + old_sentinel

    current_token = new_run_token()
    after = (
        baseline
        + f"\n20:00 ~/mysite (master)$ {build_deploy_command('~/mysite', current_token)}\n"
        + f"{SENTINEL_PREFIX}{current_token}_EXIT_0__\n"
    )

    pos = cut_point(after, baseline)
    match = sentinel_re(current_token).search(after, pos)

    assert match is not None, "a sentinela atual deve ser encontrada"
    assert int(match.group(1)) == 0
    # E o valor antigo, que está antes do corte, é numericamente diferente.
    assert int(re.search(r"_EXIT_(-?\d+)__", old_sentinel).group(1)) == 1
