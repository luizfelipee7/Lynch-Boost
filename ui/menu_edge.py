import customtkinter as ctk
import subprocess
import os
import threading

class MenuEdge(ctk.CTkToplevel):
    def __init__(self, master=None, parent_btn=None):
        super().__init__(master)
        
        self.parent_btn = parent_btn
        self.modificou_algo = False

        self.title("Lynch Boost - Gerenciador do Edge")
        self.geometry("560x500")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#282A36")

        # Caminho dinâmico e inteligente baseado na sua estrutura
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.script_path = os.path.abspath(os.path.join(base_dir, '..', 'scripts', 'windows_tweaks', 'script_remover_edge.ps1'))
        
        # Teste de Segurança: Verifica se o arquivo existe antes de montar a UI
        if not os.path.exists(self.script_path):
            self._log(f"[ERRO CRITICO] O script nao foi encontrado no caminho: {self.script_path}", tipo="red")

        # --- CABEÇALHO ---
        self.label_titulo = ctk.CTkLabel(self, text="Microsoft Edge & WebView", font=("Segoe UI", 20, "bold"))
        self.label_titulo.pack(pady=(20, 5))
        
        self.label_sub = ctk.CTkLabel(self, text="Selecione a ação desejada abaixo:", font=("Segoe UI", 12), text_color="gray")
        self.label_sub.pack(pady=(0, 20))

        # --- BOTÃO 1: MODO TRATOR (Desinstala + Apaga Dados) ---
        self.btn_desinstalar = ctk.CTkButton(
            self, 
            text="Desinstalar Edge e Limpar Dados", 
            fg_color="#8B0000",
            hover_color="#FF0000",
            height=40,
            command=lambda: self.executar_script(["-UninstallEdge", "-RemoveEdgeData", "-NonInteractive"])
        )
        self.btn_desinstalar.pack(pady=10, padx=40, fill="x")

        self.btn_reduzir_background = ctk.CTkButton(
            self,
            text="Reduzir Edge em Segundo Plano",
            fg_color="#1F6AA5",
            hover_color="#144870",
            height=40,
            command=lambda: self.executar_script(["-ReduceBackground", "-NonInteractive"])
        )
        self.btn_reduzir_background.pack(pady=10, padx=40, fill="x")

        # --- BOTÃO 2: INSTALAR APENAS EDGE ---
        self.btn_instalar_edge = ctk.CTkButton(
            self, 
            text="Instalar Microsoft Edge",
            height=40,
            command=lambda: self.executar_script(["-InstallEdge", "-NonInteractive"])
        )
        self.btn_instalar_edge.pack(pady=10, padx=40, fill="x")

        # --- BOTÃO 3: INSTALAR WEBVIEW ---
        self.btn_instalar_webview = ctk.CTkButton(
            self, 
            text="Instalar WebView2",
            height=40,
            command=lambda: self.executar_script(["-InstallWebView", "-NonInteractive"])
        )
        self.btn_instalar_webview.pack(pady=10, padx=40, fill="x")

        # --- LABEL DE STATUS ---
        self.label_status = ctk.CTkLabel(self, text="", font=("Segoe UI", 12, "bold"))
        self.label_status.pack(pady=(15, 5))
        
        # --- BOTÃO FECHAR ---
        self.btn_fechar = ctk.CTkButton(
            self, text="Fechar Janela", width=120, height=28, fg_color="#333333", 
            hover_color="#555555", command=self.fechar_modal
        )
        self.btn_fechar.pack(pady=(0, 10))

        # Interceptar o 'X' da janela
        self.protocol("WM_DELETE_WINDOW", self.fechar_modal)

    def fechar_modal(self):
        if self.modificou_algo and self.parent_btn:
            self.parent_btn.configure(fg_color="#4CAF50", hover_color="#388E3C")
        self.destroy()

    def _log(self, mensagem, tipo=None):
        logger = getattr(self.master, "log_mensagem", None)
        if not callable(logger):
            return

        def emitir():
            if tipo:
                logger(mensagem, tipo=tipo)
            else:
                logger(mensagem)

        self.after(0, emitir)

    def _log_saida(self, titulo, stdout="", stderr="", tipo=None):
        partes = [titulo]
        if stdout:
            partes.append(stdout.strip())
        if stderr:
            partes.append(stderr.strip())
        self._log("\n".join(parte for parte in partes if parte), tipo=tipo)

    def executar_script(self, argumentos):
        if not os.path.exists(self.script_path):
            self.label_status.configure(text="Erro: Script .ps1 não encontrado!", text_color="#FF0000")
            self._log(f"[ERRO EDGE] Caminho procurado: {self.script_path}", tipo="red")
            return

        self.btn_desinstalar.configure(state="disabled")
        self.btn_reduzir_background.configure(state="disabled")
        self.btn_instalar_edge.configure(state="disabled")
        self.btn_instalar_webview.configure(state="disabled")
        self.btn_fechar.configure(state="disabled")
        
        self.label_status.configure(text="Executando processo... Aguarde.", text_color="#E3B505")
        
        def run_thread():
            comando = [
                "powershell.exe", 
                "-ExecutionPolicy", "Bypass", 
                "-NoProfile", 
                "-WindowStyle", "Hidden", 
                "-File", self.script_path
            ] + argumentos

            try:
                process = subprocess.run(comando, check=True, creationflags=0x08000000, capture_output=True, text=True)
                self.modificou_algo = True
                self._log_saida("[SUCESSO EDGE] Processo concluido.", process.stdout)
                self.after(0, lambda: self.label_status.configure(text="Processo concluído com sucesso!", text_color="#00FF00"))
                
            except subprocess.CalledProcessError as e:
                # --- LÓGICA DE INTERPRETAÇÃO DE CÓDIGOS DE ERRO ---
                if e.returncode == 2:
                    # Código 2 = O motor de desinstalação não achou o Edge
                    self.modificou_algo = True
                    self.after(0, lambda: self.label_status.configure(text="O Microsoft Edge já está desinstalado!", text_color="#E3B505"))
                else:
                    # Outros erros (ex: falta de internet, erro de permissão)
                    self.after(0, lambda: self.label_status.configure(text="Erro ao executar o script. Veja o log.", text_color="#FF0000"))
                
                self._log_saida(
                    f"[ERRO EDGE] Codigo de saida: {e.returncode}",
                    e.stdout,
                    e.stderr,
                    tipo="red"
                )
                
            finally:
                self.after(0, lambda: self.btn_desinstalar.configure(state="normal"))
                self.after(0, lambda: self.btn_reduzir_background.configure(state="normal"))
                self.after(0, lambda: self.btn_instalar_edge.configure(state="normal"))
                self.after(0, lambda: self.btn_instalar_webview.configure(state="normal"))
                self.after(0, lambda: self.btn_fechar.configure(state="normal"))

        threading.Thread(target=run_thread, daemon=True).start()
