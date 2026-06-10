# Governanca da Pasta otimizadores

Esta pasta contem ferramentas e scripts de terceiros mantidos apenas como referencia tecnica.

Regras operacionais:

- Nao integrar arquivos desta pasta diretamente no Hub.
- Nao chamar arquivos desta pasta por `config.json`, UI, `core/acoes_script.py` ou `core/runner.py`.
- Nao executar binarios, `.ps1`, `.cmd` ou `.bat` desta pasta pelo fluxo do produto.
- Qualquer uso futuro deve ser feito por extracao seletiva, revisao manual e reimplementacao em `scripts/windows_tweaks`.
- Scripts migrados para `windows_tweaks` devem seguir as regras `.agents`: admin check, sem aliases PowerShell, logs compativeis com a UI e auditoria quando houver impacto no sistema operacional.
- Arquivos desta pasta nao fazem parte do comportamento ativo do aplicativo.

Barreira tecnica:

- `core/runner.py` bloqueia execucao de caminhos dentro de `scripts/otimizadores`.

Estado atual:

- Pasta isolada.
- Zero referencias ativas esperadas no Hub.
- Uso permitido somente para consulta e comparacao tecnica.
