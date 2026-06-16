# Lynch Boost

Painel operacional para aplicar ajustes, diagnósticos e rotinas de manutenção no Windows com foco em desempenho, jogos, latência, limpeza, instalação de aplicativos e remoção seletiva de componentes.

O projeto é uma aplicação desktop em Python com interface `customtkinter`. A execução final esperada é via `LynchBoost.exe`, gerado com PyInstaller e manifesto de administrador embutido.

## Status do Repositório

Este repositório deve permanecer privado enquanto o projeto estiver em desenvolvimento interno. O objetivo atual é permitir versionamento, backup, clonagem e geração controlada de builds pelo autor.

Não publicar releases públicas antes de revisar:

- segurança dos scripts;
- impacto destrutivo de cada ação;
- assinatura digital do executável;
- documentação de suporte;
- política de restauração/reversão;
- testes em máquinas limpas.

## Como o Projeto Funciona

O Hub lê `config.json`, monta as categorias da interface e roteia cada ação para uma função registrada em `core/acoes_script.py`.

Fluxo principal:

1. `main.py` inicia a interface.
2. `ui/janela_principal_v2.py` monta dashboard, sidebar, categorias, console e execução rápida.
3. A ação selecionada chama uma entrada de `core/acoes_script.py`.
4. `core/runner.py` executa scripts `.ps1`, `.bat`, `.cmd` ou `.reg` com tratamento de permissões.
5. Logs retornam para o console da interface.

O executável final carrega arquivos internos empacotados pelo PyInstaller. Em tempo de execução, o PyInstaller extrai conteúdo temporário em `%TEMP%\_MEIxxxxx`.

## Estrutura Principal

```text
main.py
ui/
core/
assets/
dados/
scripts/
packaging/
config.json
LynchBoost.spec
requirements.txt
BUILD.md
```

## Pastas Empacotadas no EXE

Entram no `LynchBoost.exe`:

- `main.py`
- `ui/`
- `core/`
- `config.json`
- `assets/`
- `dados/`
- `scripts/windows_tweaks/`
- `scripts/games/`
- `scripts/app.exe/`

Usados no build, mas não distribuídos como pastas externas:

- `LynchBoost.spec`
- `requirements.txt`
- `packaging/LynchBoost.exe.manifest`

## Pastas Fora do EXE

Ficam fora do executável:

- `scripts/otimizadores/`
- `.agents/`
- `.git/`
- `.vscode/`
- `tests/`
- `build/`
- `dist/`
- `__pycache__/`
- `.tmp/`
- logs locais;
- arquivos `.env`;
- credenciais, tokens e chaves privadas.

`scripts/otimizadores/` contém scripts e executáveis de terceiros. Essa pasta deve continuar isolada. Qualquer uso futuro deve ser feito por extração seletiva, revisão manual e integração controlada em `scripts/windows_tweaks/`.

## Níveis de Risco

### Baixo Risco

Ações que consultam informação, abrem painéis do Windows ou ajustam preferências reversíveis.

Exemplos:

- visualizar especificações;
- abrir ferramentas nativas;
- limpar console;
- abrir painel de DNS;
- abrir instalador de aplicativos;
- abrir desinstalador de apps;
- consultar status de antivírus;
- ler logs/diagnósticos.

### Médio Risco

Ações que alteram preferências do usuário, rede, energia, interface, mouse, teclado ou caches.

Exemplos:

- otimizar DNS;
- limpar arquivos temporários;
- esvaziar lixeira;
- limpar cache de RAM;
- alterar plano de energia;
- ajustar repetição do teclado;
- ativar/desativar aceleração do mouse;
- alterar opções do Explorer;
- aplicar tweaks visuais.

Impacto esperado: reversível, mas pode exigir ajuste manual se o usuário não gostar do resultado.

### Alto Risco

Ações que alteram serviços, políticas, registro, componentes do Windows, rede ou recursos do sistema.

Exemplos:

- desativar telemetria;
- otimizar políticas de grupo;
- otimizar serviços do Windows;
- resetar rede;
- reparar Windows;
- limpar componentes do Windows;
- alterar Game DVR/Game Mode;
- aplicar arquivos `.reg`;
- alterar prioridade de jogos;
- desativar manutenção em segundo plano.

Impacto esperado: pode mudar comportamento do Windows, afetar updates, serviços, rede ou compatibilidade.

### Destrutivo ou Irreversível sem Reinstalação/Recuperação

Ações que removem aplicativos, componentes ou dados.

Exemplos:

- desinstalar apps do Windows;
- remover Microsoft Edge;
- remover OneDrive;
- remover Xbox Game Bar;
- remover apps Xbox;
- remover apps provisionados para novos usuários;
- limpar `Windows.old`;
- limpar arquivos temporários sem recuperação;
- remover caches de aplicativos/navegadores.

Impacto esperado: pode remover componentes usados pelo usuário. Algumas ações exigem reinstalação manual, Microsoft Store, PowerShell, Winget ou restauração do sistema.

## Regras de Segurança Operacional

- O usuário não deve executar scripts diretamente fora do Hub.
- O EXE deve exigir administrador no início.
- A interface deve explicar ações de maior risco antes da execução.
- Scripts de terceiros não entram no fluxo ativo sem revisão.
- Ações destrutivas devem ser tratadas como decisão consciente do usuário.
- O projeto deve evitar caminhos absolutos pessoais em código versionado.
- Credenciais, tokens, `.env` e chaves privadas nunca devem ser commitados.

## Build do Executável

Build recomendado por versão:

```powershell
$Version = "v1.1"
$Project = "C:\Users\Usuario\Documento\teste\pjt-Lynch-boost"
$ReleaseRoot = "C:\Users\Usuario\Downloads\$Version"
$BuildRoot = Join-Path $ReleaseRoot "lynchboost-build"
$VenvPath = Join-Path $BuildRoot ".venv"
$WorkPath = Join-Path $BuildRoot "work"

Remove-Item -LiteralPath $BuildRoot -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $ReleaseRoot -Force | Out-Null

& "C:\Users\Usuario\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m venv $VenvPath
& "$VenvPath\Scripts\python.exe" -m pip install --upgrade pip
& "$VenvPath\Scripts\python.exe" -m pip install -r "$Project\requirements.txt"

& "$VenvPath\Scripts\pyinstaller.exe" "$Project\LynchBoost.spec" `
  --clean `
  --noconfirm `
  --distpath $ReleaseRoot `
  --workpath $WorkPath
```

Saída esperada:

```text
C:\Users\Usuario\Downloads\v1.1\LynchBoost.exe
```

## Manifesto de Administrador

O build usa:

```text
packaging/LynchBoost.exe.manifest
```

O manifesto define:

```xml
<requestedExecutionLevel level="requireAdministrator" uiAccess="false" />
```

Resultado esperado: ao abrir `LynchBoost.exe`, o Windows exibe UAC antes de carregar a interface.

## Processo de Release

Checklist mínimo antes de gerar uma nova versão:

1. Confirmar worktree limpo.
2. Rodar testes estáticos.
3. Rodar `compileall`.
4. Gerar build limpo em pasta versionada.
5. Confirmar que `scripts/otimizadores/` não entrou no EXE.
6. Confirmar manifest admin embutido.
7. Abrir o EXE em máquina de teste.
8. Validar fluxos principais sem executar ações destrutivas desnecessárias.
9. Registrar tamanho, data e versão.
10. Criar tag/release apenas depois da validação manual.

Exemplo de pasta de release:

```text
C:\Users\Usuario\Downloads\v1.1\
├── LynchBoost.exe
└── lynchboost-build\
```

`lynchboost-build/` pode ser apagada depois. Ela serve só para gerar o executável.

## Desenvolvimento

Instalação local:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Execução:

```powershell
.\.venv\Scripts\python.exe main.py
```

Testes:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Observações

Este projeto altera configurações sensíveis do Windows. Não deve ser usado em máquinas de produção sem backup, ponto de restauração ou validação prévia.

O objetivo do Hub é centralizar ações e reduzir execução manual de scripts soltos, mantendo maior rastreabilidade e previsibilidade operacional.
