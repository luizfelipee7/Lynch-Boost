import customtkinter as ctk
import subprocess
import os
import threading

class MenuDNS(ctk.CTkToplevel):
    def __init__(self, master=None, parent_btn=None):
        super().__init__(master)
        
        self.parent_btn = parent_btn
        self.modificou_algo = False
        
        self.title("Lynch Boost - Configurador de DNS")
        self.geometry("480x700") 
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#282A36")

        # Caminho dinâmico e inteligente baseado na estrutura
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.script_path = os.path.abspath(os.path.join(base_dir, '..', 'scripts', 'windows_tweaks', 'script_otimizar_dns.ps1'))
        
        if not os.path.exists(self.script_path):
            self._log(f"[ERRO CRITICO] O script nao foi encontrado no caminho: {self.script_path}", tipo="red")

        # --- CABEÇALHO ---
        self.label_titulo = ctk.CTkLabel(self, text="Otimização de DNS", font=("Segoe UI", 20, "bold"))
        self.label_titulo.pack(pady=(15, 5))
        
        self.label_sub = ctk.CTkLabel(self, text="Selecione o servidor DNS para aplicar na sua conexão:", font=("Segoe UI", 12), text_color="gray")
        self.label_sub.pack(pady=(0, 15))

        # --- BOTÕES DE DNS ---
        self.btn_cloudflare = ctk.CTkButton(
            self, 
            text="1. Usar Cloudflare (Foco em Velocidade)", 
            fg_color="#F6821F", hover_color="#D86B11", text_color="black", font=ctk.CTkFont(weight="bold"),
            height=36,
            command=lambda: self.executar_script("Cloudflare")
        )
        self.btn_cloudflare.pack(pady=5, padx=40, fill="x")

        self.btn_google = ctk.CTkButton(
            self, 
            text="2. Usar Google DNS (Foco em Estabilidade)",
            fg_color="#4285F4", hover_color="#2B6BCE", font=ctk.CTkFont(weight="bold"),
            height=36,
            command=lambda: self.executar_script("Google")
        )
        self.btn_google.pack(pady=5, padx=40, fill="x")

        self.btn_quad9 = ctk.CTkButton(
            self, 
            text="3. Usar Quad9 (Foco em Segurança)",
            fg_color="#0066CC", hover_color="#004C99", font=ctk.CTkFont(weight="bold"),
            height=36,
            command=lambda: self.executar_script("Quad9")
        )
        self.btn_quad9.pack(pady=5, padx=40, fill="x")

        self.btn_opendns = ctk.CTkButton(
            self, 
            text="4. Usar OpenDNS (Foco em Desempenho)",
            fg_color="#0072C6", hover_color="#005A9E", font=ctk.CTkFont(weight="bold"),
            height=36,
            command=lambda: self.executar_script("OpenDNS")
        )
        self.btn_opendns.pack(pady=5, padx=40, fill="x")

        self.btn_adguard = ctk.CTkButton(
            self, 
            text="5. Usar AdGuard DNS (Bloqueio de Anúncios)",
            fg_color="#107C41", hover_color="#0B592E", font=ctk.CTkFont(weight="bold"),
            height=36,
            command=lambda: self.executar_script("AdGuard")
        )
        self.btn_adguard.pack(pady=5, padx=40, fill="x")

        self.btn_padrao = ctk.CTkButton(
            self, 
            text="6. Restaurar Padrão (DHCP Automático)",
            fg_color="#27ae60", hover_color="#1e8449", font=ctk.CTkFont(weight="bold"),
            height=36,
            command=lambda: self.executar_script("Reset")
        )
        self.btn_padrao.pack(pady=5, padx=40, fill="x")

        self.btn_flush = ctk.CTkButton(
            self, 
            text="7. Apenas Limpar Cache DNS (Flush)",
            fg_color="#8B0000", hover_color="#FF0000", font=ctk.CTkFont(weight="bold"),
            height=36,
            command=lambda: self.executar_script("Flush")
        )
        self.btn_flush.pack(pady=5, padx=40, fill="x")

        # --- SEÇÃO DNS PERSONALIZADO ---
        self.frame_custom = ctk.CTkFrame(self, fg_color="#1E2029", border_color="#3d4153", border_width=1)
        self.frame_custom.pack(pady=(12, 5), padx=40, fill="x")
        
        self.label_custom_title = ctk.CTkLabel(self.frame_custom, text="DNS Personalizado (IPv4)", font=("Segoe UI", 12, "bold"), text_color="#0078FB")
        self.label_custom_title.pack(pady=(6, 2))
        
        self.grid_inputs = ctk.CTkFrame(self.frame_custom, fg_color="transparent")
        self.grid_inputs.pack(pady=4, padx=10, fill="x")
        self.grid_inputs.grid_columnconfigure(0, weight=1)
        self.grid_inputs.grid_columnconfigure(1, weight=1)
        
        self.entry_primario = ctk.CTkEntry(self.grid_inputs, placeholder_text="DNS Primário (Ex: 1.1.1.1)", font=("Segoe UI", 11), height=30, fg_color="#282A36", border_color="#3d4153")
        self.entry_primario.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.entry_secundario = ctk.CTkEntry(self.grid_inputs, placeholder_text="DNS Secundário (Ex: 1.0.0.1)", font=("Segoe UI", 11), height=30, fg_color="#282A36", border_color="#3d4153")
        self.entry_secundario.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        self.btn_aplicar_custom = ctk.CTkButton(
            self.frame_custom,
            text="Aplicar DNS Personalizado",
            fg_color="#343A40", hover_color="#495057", font=ctk.CTkFont(weight="bold"),
            height=32,
            command=self.aplicar_dns_customizado
        )
        self.btn_aplicar_custom.pack(pady=(8, 8), padx=20, fill="x")

        # --- LABEL DE STATUS ---
        self.label_status = ctk.CTkLabel(self, text="", font=("Segoe UI", 12, "bold"))
        self.label_status.pack(pady=(10, 5))
        
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

    def aplicar_dns_customizado(self):
        ip_primario = self.entry_primario.get().strip()
        ip_secundario = self.entry_secundario.get().strip()
        
        if not ip_primario or not ip_secundario:
            self.label_status.configure(text="Erro: Preencha ambos os campos de DNS!", text_color="#FF0000")
            return
            
        def validar_ipv4(ip):
            partes = ip.split('.')
            if len(partes) != 4:
                return False
            for parte in partes:
                if not parte.isdigit() or not (0 <= int(parte) <= 255):
                    return False
            return True
            
        if not validar_ipv4(ip_primario) or not validar_ipv4(ip_secundario):
            self.label_status.configure(text="Erro: Formato de IP IPv4 inválido!", text_color="#FF0000")
            return
            
        self.executar_script("Custom", ip_primario, ip_secundario)

    def executar_script(self, modo, ip_primario=None, ip_secundario=None):
        if not os.path.exists(self.script_path):
            self.label_status.configure(text="Erro: Script .ps1 não encontrado!", text_color="#FF0000")
            return

        # Desabilitar botões durante execução
        self._set_state_botoes("disabled")
        self.label_status.configure(text=f"Aplicando configuração '{modo}'... Aguarde.", text_color="#E3B505")
        
        def run_thread():
            comando = [
                "powershell.exe", 
                "-ExecutionPolicy", "Bypass", 
                "-NoProfile", 
                "-WindowStyle", "Hidden", 
                "-File", self.script_path,
                "-DNS_Mode", modo
            ]
            
            if modo == "Custom" and ip_primario and ip_secundario:
                comando.extend(["-Primary", ip_primario, "-Secondary", ip_secundario])

            try:
                process = subprocess.run(comando, check=True, creationflags=0x08000000, capture_output=True, text=True)
                self.modificou_algo = True
                self._log_saida(f"[SUCESSO DNS] Configuracao aplicada: {modo}", process.stdout)
                self.after(0, lambda: self.label_status.configure(text="Configuração aplicada com sucesso!", text_color="#00FF00"))
            except subprocess.CalledProcessError as e:
                self.after(0, lambda: self.label_status.configure(text="Erro ao aplicar configuração.", text_color="#FF0000"))
                self._log_saida(f"[ERRO DNS] Falha ao aplicar configuracao: {modo}", e.stdout, e.stderr, tipo="red")
            finally:
                self.after(0, lambda: self._set_state_botoes("normal"))

        threading.Thread(target=run_thread, daemon=True).start()

    def _set_state_botoes(self, estado):
        self.btn_cloudflare.configure(state=estado)
        self.btn_google.configure(state=estado)
        self.btn_quad9.configure(state=estado)
        self.btn_opendns.configure(state=estado)
        self.btn_adguard.configure(state=estado)
        self.btn_padrao.configure(state=estado)
        self.btn_flush.configure(state=estado)
        self.btn_aplicar_custom.configure(state=estado)
        self.entry_primario.configure(state=estado)
        self.entry_secundario.configure(state=estado)
        self.btn_fechar.configure(state=estado)
