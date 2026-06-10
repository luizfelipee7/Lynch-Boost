---
trigger: always_on
---

# Contexto do Projeto: Lynch FPS Boost

**1. Arquitetura da Interface (UI)**
* O software é construído em Python utilizando a biblioteca `CustomTkinter` com o tema Dark e a cor azul.
* O coração do sistema é o arquivo `config.json`. A tela `janela_principal.py` é apenas uma "vitrine" que lê esse JSON dinamicamente para gerar os botões da interface. 
* NÓS NÃO MUDAMOS o arquivo principal de Python para adicionar scripts normais; nós apenas adicionamos os caminhos no arquivo `config.json`.

**2. Estrutura de Menus e Lazy Import**
* O software é dividido em abas modulares: Windows Tweaks, Remover Aplicativos, Planos de Energia, Gaming & FPS.
* Telas complexas e separadas (como a do Gerenciador do Edge) usam a técnica de "Lazy Import" (importando o módulo apenas dentro da função do botão) para evitar o erro de *Circular Import*.

**3. Módulos Ativos e Lógica de Otimização**
* **Microsoft Edge:** Possui uma interface gráfica independente. O script `.ps1` foi "hackeado" para pular a verificação de internet defeituosa do PowerShell, evitando o bloqueio por firewalls e o travamento do motor fantasma do Internet Explorer antigo.
* **Plano de Energia:** O script `Importar-Plano.ps1` lê dinamicamente um arquivo binário `.pow` (plano-lynch.pow), extrai o código GUID gerado pelo Windows via Regex e injeta o modo de Desempenho Extremo (Core Unparking) automaticamente.
* **Jogos e Bloatware:** Removemos serviços pesados (como a Xbox Game Bar via script) e apagamos o OneDrive pela raiz.

**4. Regras Absolutas de Código para o Agente**
* Todos os scripts `.ps1` ou `.bat` que o agente criar DEVEM possuir requisições de privilégio de Administrador para que as modificações no Registro e no Sistema (SysMain, Telemetria) funcionem.
* É estritamente proibido utilizar "Aliases" (como `?` ou `%`) nos scripts de PowerShell. Para seguir as regras de linting profissional, use sempre os nomes por extenso (ex: `Where-Object`, `ForEach-Object`).
* O tratamento de erros de PowerShell rodando em sub-threads no Python deve sempre usar `capture_output=True` no `subprocess.run` para capturar os erros nativos da máquina e mostrar logs reais na interface, não avisos genéricos.

**5. Análise de Contexto, Leitura e Estrutura**
* Antes de aplicar qualquer nova modificação, criar scripts ou fornecer informações, o agente DEVE revisar a organização de todos os arquivos do projeto informados, os padrões de indentação e ler os arquivos base (como o `config.json` e a UI).
* O agente deve utilizar esse contexto de leitura para evitar redundâncias, não sugerir implementações que já existam no programa e garantir que o novo código se integre exatamente nos padrões arquiteturais estabelecidos.