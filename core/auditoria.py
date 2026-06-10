from pathlib import Path


AUDITORIA_PATH = Path.home() / (
    ".gemini/antigravity-ide/brain/"
    "ebfd0c78-c013-49cb-b349-da134efb3ffd/auditoria_verificacao.md"
)


def anexar_auditoria(conteudo):
    AUDITORIA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDITORIA_PATH.open("a", encoding="utf-8") as arquivo:
        arquivo.write(conteudo)
