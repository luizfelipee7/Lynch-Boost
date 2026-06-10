---
trigger: always_on
---

# Regra de Sistema: Geração de Plano de Auditoria Manual (.md)

## 📌 Objetivo
Garantir total transparência, segurança e controle sobre todas as modificações críticas feitas no sistema operacional pelo Lynch FPS Boost. O usuário receberá um plano de implementação e verificação detalhado em formato Markdown para auditoria manual nativa.

## ⚠️ Diretriz Absoluta (Gatilho)
Toda vez que você (o agente) criar, modificar ou refatorar um script (PowerShell, Batch, Python) que altere configurações profundas do sistema, você **DEVERÁ** gerar ou atualizar um arquivo Markdown de verificação.

Configurações profundas incluem:
* Modificações no Registro do Windows (Regedit)
* Alteração de estado de Serviços (`services.msc`)
* Mudanças de adaptadores de Rede, DNS e tabelas IP
* Tarefas Agendadas e Políticas de Grupo (GPO)
* Planos de Energia e Core Unparking

## 📂 Caminho do Arquivo de Saída
O arquivo de auditoria DEVE ser salvo obrigatoriamente no seguinte caminho local derivado do perfil do usuário atual:
`%USERPROFILE%\.gemini\antigravity-ide\brain\ebfd0c78-c013-49cb-b349-da134efb3ffd\auditoria_verificacao.md`

No código Python, o caminho deve ser montado com `Path.home()` para evitar exposição de caminhos absolutos do ambiente de desenvolvimento.

## 📐 Estrutura Exigida para o Arquivo `auditoria_verificacao.md`
O arquivo gerado deve seguir o padrão de um *Implementation & Verification Plan*, contendo:

1. **Cabeçalho:** Título da modificação e data/hora da alteração.
2. **Impacto:** O que foi alterado no Windows (chaves de registro, serviços, etc.).
3. **Comando de Verificação (Nativo):** O comando exato de leitura (`reg query`, `Get-Service`, `ipconfig`) para o usuário rodar no terminal.
4. **Resultado Esperado:** O valor ou estado exato que o terminal deve retornar se o script tiver funcionado.

### Exemplo de Conteúdo que o Agente deve gravar no arquivo:
```markdown
# Plano de Verificação: Prioridade de CPU (CS2)

## 1. Alteração Realizada
* **Caminho:** `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\cs2.exe\PerfOptions`
* **Valor modificado:** `CpuPriorityClass` definido como `3` (Alta Prioridade).

## 2. Comando de Auditoria Manual
Execute o comando abaixo no Prompt de Comando (CMD) como Administrador:
\`\`\`cmd
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\cs2.exe\PerfOptions" /v CpuPriorityClass
\`\`\`

## 3. Resultado Esperado
O terminal deve retornar exatamente a seguinte linha:
\`\`\`text
CpuPriorityClass    REG_DWORD    0x3
\`\`\`
