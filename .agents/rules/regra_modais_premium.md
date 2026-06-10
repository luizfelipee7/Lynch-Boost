---
trigger: always_on
---

# Regra de Sistema: Padrão de Modais Premium (UI Customizada)

## 📌 Objetivo
Garantir que todas as opções da interface do **Lynch FPS Boost** que exijam explicações técnicas detalhadas ou confirmações críticas utilizem modais premium customizados de alta legibilidade, seguindo um design harmônico, profissional e moderno, evitando truncamento de textos e interfaces genéricas de tamanho reduzido.

---

## 📐 Diretrizes de Design e Estrutura do Modal

Sempre que implementar ou refatorar modais de confirmação explicativos (como Timer Coalescing, Latência de Disco ou mitigações de segurança), siga rigorosamente a estrutura abaixo:

### 1. Proporções e Geometria
* **Dimensão Mínima Exigida:** `560x440` (ou superior se necessário, nunca inferior a isso para evitar o corte de explicações).
* **Centralização Dinâmica:** Sempre calcular o posicionamento na tela com `update_idletasks()` para garantir centralização perfeita independente da resolução do usuário.
* **Foco Estrito:** Usar `transient()` e `grab_set()` para travar o foco do usuário no modal ativo.

### 2. Cabeçalho e Títulos
* **Identidade Visual:** Usar emojis representativos e títulos com caixa alta estilizada (ex: `⚡ Timer Coalescing & Latência de CPU ⚡` ou `💾 Latência de Armazenamento (HIPM/DIPM) 💾`).
* **Tipografia:** Usar a fonte **Arial** com tamanho **18** em negrito (`ctk.CTkFont(family="Arial", size=18, weight="bold")`).

### 3. Box Explicativo Premium ("Div" de Texto)
* **Estrutura:** O texto explicativo deve obrigatoriamente ficar dentro de um container dedicado (`ctk.CTkFrame`) com bordas finas e cores harmonizadas com o tema específico da aba a qual pertence:
  * **Windows (azul escuro):** Fundo do box `#0f172a` com borda azul `#3b82f6` de espessura `1`.
  * **Debloat (azul claro):** Fundo do box `#082f49` com borda azul claro `#0ea5e9` de espessura `1`.
  * **Limpeza & Disco (laranja):** Fundo do box `#2c1a12` com borda laranja `#f97316` de espessura `1`.
  * **Memória RAM (preto):** Fundo do box `#0b0f12` com borda teal `#1abc9c` de espessura `1`.
  * **Energia & CPU (verde escuro):** Fundo do box `#064e3b` com borda verde `#10b981` de espessura `1`.
  * **Gaming & Rede (vermelho):** Fundo do box `#2c1010` com borda vermelha `#ef4444` de espessura `1`.
  * **Mouse & Teclado (rosa):** Fundo do box `#2d0f20` com borda rosa `#ec4899` de espessura `1`.
  * **Instalador (branco):** Fundo do box `#222225` com borda prateada `#e2e8f0` de espessura `1`.
  * **Ferramentas (cinza escuro):** Fundo do box `#1f2937` com borda cinza `#9ca3af` de espessura `1`.
* **Margens:** Usar `padx=25` e `pady=(10, 15)` no frame para manter o alinhamento impecável.

### 4. Texto Explicativo e Legibilidade (Arial 13)
* **Conteúdo Resumido:** Encurtar o texto focando em alto impacto, objetividade e leitura rápida.
* **Alinhamento:** Sempre alinhar o texto à esquerda (`justify="left"`) e usar marcadores/bullet points (`•`) para separar tópicos técnicos.
* **Tipografia:** Usar obrigatoriamente a fonte **Arial** com tamanho **13** em negrito (`ctk.CTkFont(family="Arial", size=13, weight="bold")`) para máxima legibilidade.
* **Quebra de Linha:** Fixar `wraplength=480` para garantir que o texto quebre linhas de forma harmônica sem encostar nas bordas do box.

### 5. Botões de Ação Dinâmicos
* O modal deve oferecer dois botões claros na parte inferior com tamanho e cores padronizados:
  * **Botão Ativar (Verde):** `fg_color="#27ae60"`, `hover_color="#2ecc71"`. Executa a ação passando o parâmetro `-Acao Ativar` e marca o progresso do card via `parent.marcar_completado()`.
  * **Botão Reverter (Vermelho):** `fg_color="#c0392b"`, `hover_color="#e74c3c"`. Executa a ação passando o parâmetro `-Acao Reverter` e atualiza o card via `parent.desmarcar_completado()`.

---

## ⚙️ Registro no Config e UI

* **config.json:** A ação nunca deve usar a execução direta de `"arquivo"`. Ela deve ser cadastrada obrigatoriamente como `"acao_especial"` associada ao abridor do modal.
  ```json
  {
    "nome": "Desativar Timer Coalescing",
    "acao_especial": "abrir_modal_timer_coalescing",
    "destrutivo": false
  }
  ```
* **janela_principal.py:** Mapear a ação especial no roteador central para efetuar o Lazy Import do módulo de modais e chamar a respectiva função de forma isolada.
