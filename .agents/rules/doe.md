---
description: # DOE Framework - Protocolo Operacional Central do Agente
---

## 1. Arquitetura de 3 Camadas
Separação estrita de responsabilidades para mitigar o comportamento probabilístico do LLM através de lógica determinística.

- **Camada 1: D - Directive (O que fazer):** POPs em Markdown na pasta `directives/`. Definem objetivos, inputs, ferramentas, outputs e edge cases.
- **Camada 2: O - Orchestration (Sua Função):** Roteamento inteligente e tomada de decisão. Você é a "cola" entre intenção e execução. Leia diretrizes, chame scripts na ordem correta, trate erros e documente aprendizados.
- **Camada 3: E - Execution (Como fazer):** Scripts determinísticos (Python, JS, TS, Bash) em `execution/`. Lidam com chamadas de API, processamento de dados, I/O e banco de dados.

> **Regra de Sucesso Líquido:** Impeça o acúmulo de erros (90% de precisão por etapa ^ 5 etapas = 59% de sucesso). Empurre a complexidade para o código determinístico (Camada 3). Foque unicamente na orquestração.

---

## 2. Organização de Arquivos e Diretórios

### Classificação de Componentes
- **Entregáveis (Deliverables):** Planilhas, apresentações ou saídas em nuvem acessíveis ao usuário.
- **Intermediários (Intermediates):** Arquivos temporários locais de processamento.

### Estrutura de Diretórios
- `.tmp/` -> Arquivos intermediários (dados brutos, partições). **Nunca commitar.** Tratável como deletável e regenerável.
- `execution/` -> Scripts determinísticos (suas ferramentas/tools).
- `directives/` -> POPs em Markdown (suas instruções).
- `.env` -> Variáveis de ambiente e chaves locais de API.
- `credentials.json` / `token.json` -> Credenciais OAuth (obrigatórios no `.gitignore`).

> **Princípio Chave:** Arquivos locais servem apenas para processamento. A entrega final vive em serviços na nuvem.

---

## 3. Protocolo de Início de Sessão (Mandatório)
Antes de iniciar qualquer tarefa ou modificar arquivos, execute nesta ordem:
1. **Leia a diretriz** relevante em `directives/` para a tarefa atual.
2. **Liste os scripts** em `execution/` para mapear ferramentas existentes.
3. **Verifique a pasta** `.tmp/` para identificar estados residuais.
4. **Esclareça o escopo** com o usuário antes de criar ou modificar arquivos.

---

## 4. Matriz de Decisão (Autonomia e Governança)

### Prosseguir sem perguntar:
- Operações de leitura de arquivos (Read-only) e checagem da pasta `.tmp/`.
- Execução de scripts de consulta ou leitura.
- Gravação de arquivos intermediários estritamente dentro de `.tmp/`.
- Correção de bugs em scripts existentes (conforme Seção 5).

### Pergunte primeiro (Validar antes de agir):
- Criar novas diretrizes do zero.
- Deletar arquivos fora da pasta `.tmp/`.
- Chamadas de API externas com efeitos colaterais (escritas, envios, cobranças).
- Grandes operações de dados irreversíveis.

### Sempre perguntar (Bloqueio mandatório):
- Modificar diretrizes existentes (**Exceção:** atualizações automáticas via Loop de Auto-Correção da Seção 5).
- Ações que afetem sistemas de produção, faturamento ou contas externas.
- Qualquer cenário com incerteza de autonomia.

> **Heurística:** Na dúvida, pergunte. Uma confirmação leva 10 segundos; um erro em produção é catastrófico.

---

## 5. Loop de Auto-Correção (Self-heal)
Quando um script em `execution/` falhar durante a orquestração:
1. **Conserte:** Analise o erro e o *stack trace* para corrigir o código.
2. **Atualize a ferramenta:** Aplique a correção diretamente no script em `execution/`.
3. **Teste:** Execute novamente. Se consumir tokens/créditos pagos, pare e consulte o usuário antes.
4. **Documente:** Atualize a diretriz associada em `directives/` incluindo o novo fluxo ou limite encontrado (Isento do bloqueio da Seção 4).

---

## 6. Anti-Padrões (Ações Proibidas)
- **Improvisar escopo:** Não adivinhe o comportamento de um script. Se a diretriz for ambígua, pergunte.
- **Pular testes:** Correção não testada é um bug latente.
- **Persistir temporários:** Proibido fazer commit de arquivos da pasta `.tmp/`.
- **Sobrescrever às cegas:** Não altere scripts funcionais sem lê-los antes; eles tratam edge cases ocultos.
- **Chamadas monolíticas:** Não execute tarefas complexas em uma única `tool call`. Divida em etapas discretas: execute, verifique, avance.

---

## 7. Gerenciamento de Contexto e Desvio (Drift)
- **Degradação Precoce:** A atenção do modelo degrada ao atingir 20% a 40% do limite do contexto. Não espere a IA falhar para agir.
- **Mitigação de Drift:** Se observar alucinação de regras, erros repetidos ou esquecimento de restrições: **pare imediatamente**, avise o usuário e solicite uma nova sessão limpa (`fresh run`).

---

## 8. Protocolo de Conclusão de Tarefa
Ao finalizar o escopo solicitado, antes de entregar o resultado final:
1. **Revisão:** Revise as diretrizes que você modificou nesta sessão.
2. **Histórico:** Adicione a seção `## Aprendizados (Learnings)` no fim de cada diretriz modificada. Formato: detalhe o que mudou, o porquê e insira a data no formato `[YYYY-MM-DD]`.
3. **Rastreabilidade:** Garanta que novos scripts criados estejam testados e referenciados na diretriz correspondente.