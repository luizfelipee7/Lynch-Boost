# Build do Executavel

O executavel final deve ser gerado com o manifesto `packaging/LynchBoost.exe.manifest` embutido, exigindo administrador no startup:

```xml
<requestedExecutionLevel level="requireAdministrator" uiAccess="false" />
```

## Gerar ambiente

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Gerar EXE

```powershell
.\.venv\Scripts\pyinstaller.exe LynchBoost.spec --clean --noconfirm
```

Saida esperada:

```text
dist\LynchBoost.exe
```

Ao abrir o executavel, o Windows deve exibir o UAC antes da interface carregar. Depois da autorizacao, o Hub e os scripts executados por ele rodam no mesmo contexto administrativo.

## Escopo empacotado

Incluido no executavel:

- `assets`
- `dados`
- `config.json`
- `scripts/windows_tweaks`
- `scripts/games`
- `scripts/app.exe`

Excluido do executavel:

- `scripts/otimizadores`

Essa pasta contem scripts e executaveis de terceiros e deve continuar isolada ate uma extracao seletiva para `scripts/windows_tweaks`.
