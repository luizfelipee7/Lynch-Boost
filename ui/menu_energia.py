import customtkinter as ctk
import subprocess
import os
import threading
from core import atalhos

class MenuEnergia(ctk.CTkToplevel):
    def __init__(self, master=None, parent_btn=None):
        super().__init__(master)
        
        self.parent_btn = parent_btn
        self.modificou_algo = False
        
        self.title("Lynch Boost - Planos de Energia")
        self.geometry("480x420") 
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#282A36")

        # Caminho dinâmico para os scripts
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.script_ativar = os.path.abspath(os.path.join(base_dir, '..', 'scripts', 'windows_tweaks', 'script_importar_plano_energia.ps1'))
        
        # --- CABEÇALHO ---
        self.label_titulo = ctk.CTkLabel(self, text="Plano de Energia Lynch", font=("Segoe UI", 20, "bold"))
        self.label_titulo.pack(pady=(20, 5))
        
        self.label_sub = ctk.CTkLabel(
            self, 
            text="Ative o plano de energia customizado para garantir o máximo de desempenho, ignorando a economia de energia.", 
            font=("Segoe UI", 12), text_color="gray", wraplength=400
        )
        self.label_sub.pack(pady=(0, 20))

        # --- BOTÕES DE OPÇÕES ---
        self.btn_ativar = ctk.CTkButton(
            self, 
            text="Ativar Plano Lynch (Desempenho Extremo)",
            fg_color="#8B0000", hover_color="#FF0000", text_color="white", font=ctk.CTkFont(weight="bold"),
            height=45,
            command=lambda: self.executar_script(self.script_ativar, "Ativando Plano de Energia...")
        )
        self.btn_ativar.pack(pady=10, padx=40, fill="x")

        # --- ATALHO ---
        self.btn_verificar = ctk.CTkButton(
            self, 
            text="⚙️ Abrir Painel de Energia do Windows", 
            fg_color="#F6821F", hover_color="#D86B11", text_color="black", font=ctk.CTkFont(weight="bold"),
            height=35,
            command=lambda: atalhos.abrir_energia(None)
        )
        self.btn_verificar.pack(pady=(15, 0), padx=40, fill="x")

        # --- LABEL DE STATUS ---
        self.label_status = ctk.CTkLabel(self, text="", font=("Segoe UI", 12, "bold"))
        self.label_status.pack(pady=(15, 5))
        
        # --- BOTÃO FECHAR ---
        self.btn_fechar = ctk.CTkButton(
            self, text="Fechar Janela", width=120, height=35, fg_color="#333333", 
            hover_color="#555555", command=self.fechar_modal
        )
        self.btn_fechar.pack(pady=(5, 10))

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

    def executar_script(self, script_path, msg_inicial):
        if not os.path.exists(script_path):
            self.label_status.configure(text="Erro: Script executor não encontrado!", text_color="#FF0000")
            self._log(f"[ERRO ENERGIA] Script executor nao encontrado: {script_path}", tipo="red")
            return

        self._set_state_botoes("disabled")
        self.label_status.configure(text=msg_inicial, text_color="#E3B505")
        
        def run_thread():
            comando = [
                "powershell.exe", 
                "-ExecutionPolicy", "Bypass", 
                "-NoProfile", 
                "-WindowStyle", "Hidden", 
                "-File", script_path
            ]

            try:
                process = subprocess.run(comando, check=True, creationflags=0x08000000, capture_output=True, text=True)
                self.modificou_algo = True
                self.after(0, lambda: self.label_status.configure(text="Plano ativado com sucesso!", text_color="#00FF00"))
                self._log_saida("[SUCESSO ENERGIA] Plano ativado.", process.stdout)
            except subprocess.CalledProcessError as e:
                self.after(0, lambda: self.label_status.configure(text="Erro ao aplicar modificação.", text_color="#FF0000"))
                self._log_saida("[ERRO ENERGIA] Falha ao aplicar modificacao.", e.stdout, e.stderr, tipo="red")
            finally:
                self.after(0, lambda: self._set_state_botoes("normal"))

        threading.Thread(target=run_thread, daemon=True).start()

    def _set_state_botoes(self, estado):
        self.btn_ativar.configure(state=estado)
        self.btn_verificar.configure(state=estado)
        self.btn_fechar.configure(state=estado)
