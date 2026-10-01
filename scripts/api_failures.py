"""Falhas fatais de APIs externas usadas pelo pipeline de sincronização.

Distingue duas condições que não devem passar silenciosas:

``ApiAuthError``
    HTTP 401/403 — credencial inválida, expirada ou bloqueada.

``ApiQuotaError``
    HTTP 429 — cota de requisições esgotada, ainda que após retentativas.

Ambas indicam que o dataset NÃO foi atualizado. Deixar o script terminar com
código 0 faria o GitHub Actions marcar o job como verde e abrir um PR vazio,
ou pior: gravar placeholder ``#`` na planilha e difundir a ideia de que o
acervo foi verificado quando na verdade não foi.
"""


class ApiAuthError(RuntimeError):
    """Credencial da API externa recusada (401/403)."""


class ApiQuotaError(RuntimeError):
    """Cota de requisições esgotada (429) mesmo após retentativas."""


def exit_with_error(message, code=1):
    """Registra a falha em log e encerra o processo com código != 0."""
    print(f"\n❌ ERRO FATAL: {message}")
    print("   O dataset NÃO foi atualizado. Corrija a credencial/cota e rode novamente.")
    raise SystemExit(code)