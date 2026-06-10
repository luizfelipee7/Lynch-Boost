import customtkinter as ctk
import os
import threading
from tkinter import filedialog

def abrir_modal_confirmacao(parent, titulo, mensagem, comando_confirmar, comando_cancelar=None, categoria=None):
    modal = ctk.CTkToplevel(parent)
    modal.title(titulo)
    modal.geometry("560x440")
    modal.resizable(False, False)
    modal.configure(fg_color="#282A36")
    
    # Prende o foco na janela do modal
    modal.transient(parent)
    modal.grab_set()

    # Centraliza o modal na tela
    modal.update_idletasks()
    x = (modal.winfo_screenwidth() - modal.winfo_reqwidth()) // 2
    y = (modal.winfo_screenheight() - modal.winfo_reqheight()) // 2
    modal.geometry(f"+{x}+{y}")

    # Obter tema com base na categoria (unificado para trazer confiança)
    THEMES = {
        cat: {"bg": "#1E2029", "border": "#0078FB", "text": "#e8e8f0"}
        for cat in [
            "config_windows", "debloat_servicos", "limpeza_armazenamento",
            "memory_tweaks", "cpu_energia", "gaming", "rede_latencia", "mouse_teclado",
            "instalacao"
        ]
    }
    
    t_cfg = THEMES.get(categoria, {"bg": "#1E2029", "border": "#0078FB", "text": "#e8e8f0"})

    # Título Principal do Modal
    lbl_titulo = ctk.CTkLabel(
        modal, text=f"⚠️ {titulo} ⚠️", 
        font=ctk.CTkFont(family="Arial", size=18, weight="bold"), 
        text_color=t_cfg["border"]
    )
    lbl_titulo.pack(pady=(20, 5))

    # Box Explicativo Premium
    frame_aviso = ctk.CTkFrame(
        modal, fg_color=t_cfg["bg"], border_width=1, border_color=t_cfg["border"],
        corner_radius=8
    )
    frame_aviso.pack(padx=25, pady=(10, 15), fill="both", expand=True)

    lbl_mensagem = ctk.CTkLabel(
        frame_aviso, text=mensagem, wraplength=460, justify="left",
        font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
        text_color=t_cfg["text"]
    )
    lbl_mensagem.pack(padx=15, pady=15, fill="both", expand=True)

    frame_botoes = ctk.CTkFrame(modal, fg_color="transparent")
    frame_botoes.pack(fill="x", padx=25, pady=(0, 20), side="bottom")

    def clicar_sim():
        modal.destroy() 
        comando_confirmar() 

    def clicar_nao():
        if comando_cancelar:
            comando_cancelar()
        modal.destroy() 

    btn_sim = ctk.CTkButton(
        frame_botoes, text="⚡ SIM, EXECUTAR", 
        fg_color="#27ae60", hover_color="#2ecc71", 
        font=ctk.CTkFont(weight="bold", size=12), height=40,
        command=clicar_sim
    )
    btn_sim.pack(side="left", padx=10, expand=True, fill="x")

    btn_nao = ctk.CTkButton(
        frame_botoes, text="❌ NÃO, CANCELAR", 
        fg_color="#c0392b", hover_color="#e74c3c", 
        font=ctk.CTkFont(weight="bold", size=12), height=40,
        command=clicar_nao
    )
    btn_nao.pack(side="right", padx=10, expand=True, fill="x")




def abrir_modal_menu_contexto(parent, btn_ref=None, categoria=None, item_id=None):
    import core.runner as runner
    modal = ctk.CTkToplevel(parent)
    modal.title("Estilo do Menu de Contexto")
    modal.geometry("560x440")
    modal.resizable(False, False)
    modal.configure(fg_color="#282A36")
    
    modal.transient(parent)
    modal.grab_set()
    
    # Configurar ícone para consistência visual na barra de tarefas
    try:
        if hasattr(parent, 'icon_path') and os.path.exists(parent.icon_path):
            modal.iconbitmap(parent.icon_path)
    except Exception:
        pass

    modal.update_idletasks()
    x = (modal.winfo_screenwidth() - modal.winfo_reqwidth()) // 2
    y = (modal.winfo_screenheight() - modal.winfo_reqheight()) // 2
    modal.geometry(f"+{x}+{y}")

    # Título Principal do Modal
    lbl_titulo = ctk.CTkLabel(
        modal, text="⚠️ Estilo do Menu de Contexto ⚠️", 
        font=ctk.CTkFont(family="Arial", size=18, weight="bold"), 
        text_color="#0078FB"
    )
    lbl_titulo.pack(pady=(20, 5))

    # Box Explicativo Premium
    frame_aviso = ctk.CTkFrame(
        modal, fg_color="#1E2029", border_width=1, border_color="#0078FB",
        corner_radius=8
    )
    frame_aviso.pack(padx=25, pady=(10, 15), fill="both", expand=True)

    lbl_mensagem = ctk.CTkLabel(
        frame_aviso, text="Qual formato de menu do botão direito você deseja utilizar no Windows?", wraplength=460, justify="left",
        font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
        text_color="#e8e8f0"
    )
    lbl_mensagem.pack(padx=15, pady=15, fill="both", expand=True)

    frame_botoes = ctk.CTkFrame(modal, fg_color="transparent")
    frame_botoes.pack(fill="x", padx=25, pady=(0, 20), side="bottom")

    def aplicar_win10():
        modal.destroy()
        parent.log_mensagem("Aplicando Menu Classico (Win 10)...")
        sucesso = runner.executar_arquivo("scripts/windows_tweaks/script_menu_contexto_classico.bat", logger=parent.log_mensagem)
        if sucesso:
            parent.log_mensagem("Menu Classico aplicado com sucesso!")
            if btn_ref:
                if categoria and item_id:
                    parent.marcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#4CAF50", hover_color="#388E3C")

    def aplicar_win11():
        modal.destroy()
        parent.log_mensagem("Restaurando Menu Original (Win 11)...")
        sucesso = runner.executar_arquivo("scripts/windows_tweaks/script_menu_contexto_moderno.bat", logger=parent.log_mensagem)
        if sucesso:
            parent.log_mensagem("Menu Original do Win 11 restaurado!")
            if btn_ref:
                if categoria and item_id:
                    parent.desmarcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#D32F2F", hover_color="#B71C1C")

    btn_win10 = ctk.CTkButton(
        frame_botoes, text="⚡ CLÁSSICO (WIN 10)", 
        fg_color="#27ae60", hover_color="#2ecc71", 
        font=ctk.CTkFont(weight="bold", size=12), height=40,
        command=aplicar_win10
    )
    btn_win10.pack(side="left", padx=10, expand=True, fill="x")

    btn_win11 = ctk.CTkButton(
        frame_botoes, text="❌ ORIGINAL (WIN 11)", 
        fg_color="#c0392b", hover_color="#e74c3c", 
        font=ctk.CTkFont(weight="bold", size=12), height=40,
        command=aplicar_win11
    )
    btn_win11.pack(side="right", padx=10, expand=True, fill="x")



def abrir_modal_finalizar_tarefa(parent, btn_ref=None, categoria=None, item_id=None):
    import core.runner as runner
    modal = ctk.CTkToplevel(parent)
    modal.title("Finalizar Tarefa na Barra (Win 11)")
    modal.geometry("560x440")
    modal.resizable(False, False)
    modal.configure(fg_color="#282A36")
    
    modal.transient(parent)
    modal.grab_set()
    
    # Configurar ícone para consistência visual na barra de tarefas
    try:
        if hasattr(parent, 'icon_path') and os.path.exists(parent.icon_path):
            modal.iconbitmap(parent.icon_path)
    except Exception:
        pass

    modal.update_idletasks()
    x = (modal.winfo_screenwidth() - modal.winfo_reqwidth()) // 2
    y = (modal.winfo_screenheight() - modal.winfo_reqheight()) // 2
    modal.geometry(f"+{x}+{y}")

    # Título Principal do Modal
    lbl_titulo = ctk.CTkLabel(
        modal, text="⚠️ Finalizar Tarefa na Barra ⚠️", 
        font=ctk.CTkFont(family="Arial", size=18, weight="bold"), 
        text_color="#0078FB"
    )
    lbl_titulo.pack(pady=(20, 5))

    texto_explicativo = (
        "No Windows 11, você pode habilitar um botão secreto chamado "
        "'Finalizar Tarefa' direto no ícone dos aplicativos abertos.\n\n"
        "Se um jogo ou programa travar, basta clicar com o botão direito "
        "no ícone dele na barra de tarefas e escolher 'Finalizar Tarefa' para "
        "fechá-lo à força na hora, sem precisar abrir o Gerenciador de Tarefas!"
    )

    # Box Explicativo Premium
    frame_aviso = ctk.CTkFrame(
        modal, fg_color="#1E2029", border_width=1, border_color="#0078FB",
        corner_radius=8
    )
    frame_aviso.pack(padx=25, pady=(10, 15), fill="both", expand=True)

    lbl_mensagem = ctk.CTkLabel(
        frame_aviso, text=texto_explicativo, wraplength=460, justify="left",
        font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
        text_color="#e8e8f0"
    )
    lbl_mensagem.pack(padx=15, pady=15, fill="both", expand=True)

    def ativar():
        modal.destroy()
        parent.log_mensagem("Ativando opcao 'Finalizar Tarefa'...")
        sucesso = runner.executar_arquivo("scripts/windows_tweaks/script_finalizar_tarefa.ps1", logger=parent.log_mensagem, argumentos_extras="-Acao Ativar")
        if sucesso:
            parent.log_mensagem("Opcao ativada com sucesso! Reinicie o PC para aplicar.")
            if btn_ref:
                if categoria and item_id:
                    parent.marcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#4CAF50", hover_color="#388E3C")
        else:
            parent.log_mensagem("[ERRO] Falha ao ativar a opção.")

    def remover():
        modal.destroy()
        parent.log_mensagem("Removendo opcao 'Finalizar Tarefa'...")
        sucesso = runner.executar_arquivo("scripts/windows_tweaks/script_finalizar_tarefa.ps1", logger=parent.log_mensagem, argumentos_extras="-Acao Reverter")
        if sucesso:
            parent.log_mensagem("Opcao removida com sucesso! Reinicie o PC para aplicar.")
            if btn_ref:
                if categoria and item_id:
                    parent.desmarcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#D32F2F", hover_color="#B71C1C")
        else:
            parent.log_mensagem("[ERRO] Falha ao remover a opção.")

    frame_botoes = ctk.CTkFrame(modal, fg_color="transparent")
    frame_botoes.pack(fill="x", padx=25, pady=(0, 20), side="bottom")

    btn_ativar = ctk.CTkButton(
        frame_botoes, text="⚡ ATIVAR OPÇÃO", 
        fg_color="#27ae60", hover_color="#2ecc71", 
        font=ctk.CTkFont(weight="bold", size=12), height=40,
        command=ativar
    )
    btn_ativar.pack(side="left", padx=10, expand=True, fill="x")

    btn_remover = ctk.CTkButton(
        frame_botoes, text="❌ REMOVER", 
        fg_color="#c0392b", hover_color="#e74c3c", 
        font=ctk.CTkFont(weight="bold", size=12), height=40,
        command=remover
    )
    btn_remover.pack(side="right", padx=10, expand=True, fill="x")

def _criar_modal_generico(parent, titulo, explicacao, script_base, btn_ref=None, categoria=None, item_id=None, permitir_reverter=True):
    import core.runner as runner
    modal = ctk.CTkToplevel(parent)
    modal.title(titulo)
    modal.geometry("560x440")
    modal.resizable(False, False)
    modal.configure(fg_color="#282A36")
    
    modal.transient(parent)
    modal.grab_set()
    
    # Configurar ícone para consistência visual na barra de tarefas
    try:
        if hasattr(parent, 'icon_path') and os.path.exists(parent.icon_path):
            modal.iconbitmap(parent.icon_path)
    except Exception:
        pass

    modal.update_idletasks()
    x = (modal.winfo_screenwidth() - modal.winfo_reqwidth()) // 2
    y = (modal.winfo_screenheight() - modal.winfo_reqheight()) // 2
    modal.geometry(f"+{x}+{y}")

    # Título Principal do Modal
    lbl_titulo = ctk.CTkLabel(
        modal, text=f"⚠️ {titulo} ⚠️", 
        font=ctk.CTkFont(family="Arial", size=18, weight="bold"), 
        text_color="#0078FB"
    )
    lbl_titulo.pack(pady=(20, 5))

    # Box Explicativo Premium
    frame_aviso = ctk.CTkFrame(
        modal, fg_color="#1E2029", border_width=1, border_color="#0078FB",
        corner_radius=8
    )
    frame_aviso.pack(padx=25, pady=(10, 15), fill="both", expand=True)

    lbl_mensagem = ctk.CTkLabel(
        frame_aviso, text=explicacao, wraplength=460, justify="left",
        font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
        text_color="#e8e8f0"
    )
    lbl_mensagem.pack(padx=15, pady=15, fill="both", expand=True)

    def ativar():
        modal.destroy()
        parent.log_mensagem(f"Ativando: {titulo}...")
        argumentos = "-Acao Ativar" if permitir_reverter else ""
        
        def run_thread():
            sucesso = runner.executar_arquivo(script_base, logger=parent.log_mensagem, argumentos_extras=argumentos)
            if sucesso:
                parent.log_mensagem("Operacao concluida com sucesso! Reinicie o PC para aplicar.")
                if btn_ref:
                    if categoria and item_id:
                        parent.after(0, lambda: parent.marcar_completado(categoria, item_id, btn_ref))
                    else:
                        parent.after(0, lambda: btn_ref.configure(fg_color="#4CAF50", hover_color="#388E3C"))
            else:
                parent.log_mensagem("[ERRO] Falha ao executar.")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def reverter():
        modal.destroy()
        parent.log_mensagem(f"Revertendo: {titulo}...")
        
        def run_thread():
            sucesso = runner.executar_arquivo(script_base, logger=parent.log_mensagem, argumentos_extras="-Acao Reverter")
            if sucesso:
                parent.log_mensagem("Operacao revertida com sucesso! Reinicie o PC para aplicar.")
                if btn_ref:
                    if categoria and item_id:
                        parent.after(0, lambda: parent.desmarcar_completado(categoria, item_id, btn_ref))
                    else:
                        parent.after(0, lambda: btn_ref.configure(fg_color="#D32F2F", hover_color="#B71C1C"))
            else:
                parent.log_mensagem("[ERRO] Falha ao reverter.")

        threading.Thread(target=run_thread, daemon=True).start()

    frame_botoes = ctk.CTkFrame(modal, fg_color="transparent")
    frame_botoes.pack(fill="x", padx=25, pady=(0, 20), side="bottom")

    btn_ativar = ctk.CTkButton(
        frame_botoes, text="⚡ ATIVAR", 
        fg_color="#27ae60", hover_color="#2ecc71", 
        font=ctk.CTkFont(weight="bold", size=12), height=40, command=ativar
    )
    if permitir_reverter:
        btn_ativar.pack(side="left", padx=10, expand=True, fill="x")
        btn_reverter = ctk.CTkButton(
            frame_botoes, text="❌ REVERTER", 
            fg_color="#c0392b", hover_color="#e74c3c", 
            font=ctk.CTkFont(weight="bold", size=12), height=40, command=reverter
        )
        btn_reverter.pack(side="right", padx=10, expand=True, fill="x")
    else:
        btn_ativar.pack(padx=10, expand=True, fill="x")

def abrir_modal_sticky_keys(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Desativar Teclas de Aderência",
        "Quando você aperta 'Shift' 5 vezes seguidas muito rápido, o Windows trava a tela e emite um apito perguntando se você quer ligar as Teclas de Aderência.\n\nEssa é a principal causa de mortes em jogos FPS e travamentos para gamers. Ativar essa opção elimina esse pop-up irritante para sempre.",
        "scripts/windows_tweaks/script_sticky_keys.ps1",
        btn_ref,
        categoria,
        item_id
    )

def abrir_modal_forcar_abnt2(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Forçar Teclado ABNT2",
        "Esta opção desativa o layout de teclado ABNT (ABNT1) do Windows, mantendo apenas o layout ABNT2 ativo.\n\nIsso evita que o Windows alterne o layout do teclado acidentalmente durante digitação ou jogos. O layout ABNT2 (com Ç) continuará funcionando normalmente no seu sistema.",
        "scripts/windows_tweaks/script_forcar_abnt2.ps1",
        btn_ref,
        categoria,
        item_id
    )

def abrir_modal_teclado_eua(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Teclado Layout EUA (60%)",
        "Esta opção adiciona o layout de teclado 'Estados Unidos (Internacional)' ao seu sistema.\n\nEsse padrão é essencial para teclados no formato 60% ou importados que não possuem a tecla física Ç. Você poderá digitar acentuações normalmente (ex: '+c gera ç). O seu layout ABNT2 padrão continuará disponível no sistema.",
        "scripts/windows_tweaks/script_adicionar_teclado_eua.ps1",
        btn_ref,
        categoria,
        item_id
    )

def abrir_modal_explorer_this_pc(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Explorador no 'Meu Computador'",
        "Por padrão, quando você abre uma pasta no Windows 11, ele abre na aba de 'Início / Acesso Rápido' que costuma ser uma bagunça de arquivos recentes.\n\nAtivando isso, o Explorador de Arquivos abrirá diretamente no 'Este Computador' mostrando seus Discos C: e D:, muito mais organizado.",
        "scripts/windows_tweaks/script_explorer_this_pc.ps1",
        btn_ref,
        categoria,
        item_id
    )

def abrir_modal_show_extensions(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Mostrar Extensões (.exe, .pdf)",
        "O Windows esconde a extensão real dos arquivos por padrão. Isso permite que vírus disfarçados de 'documento.pdf.exe' enganem você facilmente.\n\nAtivar isso forçará o Windows a mostrar sempre a extensão de todos os arquivos, garantindo segurança máxima e controle sobre o que você está abrindo.",
        "scripts/windows_tweaks/script_show_extensions.ps1",
        btn_ref,
        categoria,
        item_id
    )

def abrir_modal_home_galeria(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Desativar Home e Galeria",
        "Por padrão, o Windows 11 exibe as seções 'Início' e 'Galeria' no Explorador de Arquivos. Elas carregam arquivos e fotos recentes continuamente, consumindo processamento e criando poluição visual.\n\nAtivando isso, você remove essas seções e deixa a navegação de pastas mais rápida e limpa.",
        "scripts/windows_tweaks/script_desativar_home_galeria.ps1",
        btn_ref,
        categoria,
        item_id
    )

def abrir_modal_wsl_icon(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Ocultar Pasta Linux (WSL)",
        "O Windows exibe um ícone da pasta 'Linux' no painel 'Este Computador' do Explorador de Arquivos quando o WSL está ativado.\n\nAtivar esta opção oculta o atalho da pasta Linux para manter o seu Explorador limpo. Você ainda poderá acessar seus arquivos do WSL normalmente.",
        "scripts/windows_tweaks/script_wsl_icon.ps1",
        btn_ref,
        categoria,
        item_id
    )

def abrir_modal_fast_startup(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Desativar Inicialização Rápida",
        "A Inicialização Rápida (Fast Startup) não desliga o seu PC de verdade, ela apenas hiberna o kernel. Isso gera uma bola de neve de bugs com drivers de vídeo, áudio e atualizações falhas.\n\nDesativar isso fará seu PC ligar 1 segundo mais devagar, mas garantirá que seu sistema inicie 100% fresco e livre de travamentos crônicos.",
        "scripts/windows_tweaks/script_fast_startup.ps1",
        btn_ref,
        categoria,
        item_id
    )

def abrir_modal_repeticao_teclado(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Acelerar Taxa de Repetição do Teclado",
        "Esta opção diminui o atraso antes da repetição de teclas (Keyboard Delay) para o mínimo (0) e acelera a taxa de repetição do teclado (Keyboard Speed) ao máximo.\n\nIsso reduz sensivelmente o atraso de digitação e a latência de comandos de movimento em jogos (como o strafe rápido e corte de animação em jogos FPS).",
        "scripts/windows_tweaks/script_acelerar_repeticao_teclado.ps1",
        btn_ref,
        categoria,
        item_id
    )


class ModalInstalacaoCaminho(ctk.CTkToplevel):
    def __init__(self, master, app_name, is_first_app=False):
        super().__init__(master)
        
        self.app_name = app_name
        self.resultado_caminho = None
        self.ignorar = False
        self.cancelado = False
        self.cancelar_tudo = False
        
        self.title("Local de Instalação")
        largura_modal = 560
        altura_modal = 440
        self.geometry(f"{largura_modal}x{altura_modal}")
        self.resizable(False, False)
        self.configure(fg_color="#282A36")
        
        self.transient(master)
        self.grab_set()
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() - largura_modal) // 2
        y = (self.winfo_screenheight() - altura_modal) // 2
        self.geometry(f"{largura_modal}x{altura_modal}+{x}+{y}")
        
        self.protocol("WM_DELETE_WINDOW", self.on_fechar)
        
        lbl_titulo = ctk.CTkLabel(self, text=f"Instalando: {app_name}", font=ctk.CTkFont(size=18, weight="bold"))
        lbl_titulo.pack(pady=(20, 5))
        
        lbl_sub = ctk.CTkLabel(self, text="Selecione onde deseja instalar o aplicativo:", font=ctk.CTkFont(size=12))
        lbl_sub.pack(pady=(0, 15))
        
        frame_input = ctk.CTkFrame(self, fg_color="transparent")
        frame_input.pack(fill="x", padx=20)
        
        caminho_padrao = f"C:\\Program Files\\{app_name.replace(' ', '')}"
        
        self.entry_caminho = ctk.CTkEntry(frame_input, width=320)
        self.entry_caminho.pack(side="left", padx=(0, 10))
        self.entry_caminho.insert(0, caminho_padrao)
        
        btn_procurar = ctk.CTkButton(frame_input, text="Procurar...", width=90, command=self.procurar_pasta)
        btn_procurar.pack(side="right")
        
        lbl_aviso = ctk.CTkLabel(self, text="*Nota: Alguns apps (ex: Discord, Chrome) ignoram o caminho customizado.", 
                                 font=ctk.CTkFont(size=11, slant="italic"), text_color="#A0A0A0")
        lbl_aviso.pack(pady=(5, 0))
        
        if is_first_app:
            self.chk_todos_var = ctk.BooleanVar(value=False)
            chk_todos = ctk.CTkCheckBox(self, text="Aplicar este diretório base para os próximos apps", variable=self.chk_todos_var)
            chk_todos.pack(anchor="w", padx=20, pady=15)
        else:
            self.chk_todos_var = None
            ctk.CTkFrame(self, height=35, fg_color="transparent").pack()
            
        frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns.pack(fill="x", padx=20, pady=(10, 20), side="bottom")
        
        btn_ignorar = ctk.CTkButton(frame_btns, text="Padrão do Sistema", fg_color="#333333", hover_color="#555555", width=130, command=self.on_ignorar)
        btn_ignorar.pack(side="left")
        
        btn_cancelar = ctk.CTkButton(frame_btns, text="Cancelar (Pular)", fg_color="#c0392b", hover_color="#e74c3c", width=130, command=self.on_cancelar)
        btn_cancelar.pack(side="left", padx=10)
        
        btn_aceitar = ctk.CTkButton(frame_btns, text="Confirmar Caminho", fg_color="#27ae60", hover_color="#2ecc71", width=140, command=self.on_aceitar)
        btn_aceitar.pack(side="right")
        
    def procurar_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta de instalação")
        if pasta:
            pasta = os.path.normpath(pasta)
            self.entry_caminho.delete(0, "end")
            caminho_final = os.path.join(pasta, self.app_name.replace(' ', ''))
            self.entry_caminho.insert(0, caminho_final)
            
    def on_aceitar(self):
        self.resultado_caminho = self.entry_caminho.get()
        self.destroy()
        
    def on_ignorar(self):
        self.ignorar = True
        self.resultado_caminho = None
        self.destroy()
        
    def on_cancelar(self):
        self.cancelado = True
        self.destroy()
        
    def on_fechar(self):
        self.cancelar_tudo = True
        self.destroy()

def abrir_modal_desativar_sincronizacao(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Sincronizacao de Configuracoes",
        "Por padrao, o Windows fica utilizando sua internet e processamento em segundo plano para tentar sincronizar papel de parede, senhas, temas e configuracoes locais com a sua conta Microsoft nas nuvens.\n\nDesativar isso economiza trafego de rede e reduz processos inuteis de sincronizacao de telemetria rodando em segundo plano.",
        "scripts/windows_tweaks/script_desativar_sincronizacao.ps1",
        btn_ref,
        categoria,
        item_id
    )

def abrir_modal_desativar_experimentos(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Experimentos do Windows",
        "Por padrao, a Microsoft utiliza o seu PC para testar recursos em desenvolvimento e novas atualizacoes do Windows Insider sem o seu consentimento explicito.\n\nDesativar isso impede que o Windows baixe pacotes de experimentos inacabados e mude configuracoes do sistema de forma silenciosa, melhorando a estabilidade global.",
        "scripts/windows_tweaks/script_desativar_experimentos.ps1",
        btn_ref,
        categoria,
        item_id
    )

def abrir_modal_ativar_game_mode(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Ativar Game Mode",
        "O Game Mode prioriza os recursos de hardware para seus jogos, reduzindo a atividade de outros aplicativos em segundo plano para garantir o desempenho e FPS maximos.\n\nAtivar isso melhora a estabilidade dos quadros por segundo in jogos competitivos.",
        "scripts/windows_tweaks/script_ativar_game_mode.ps1",
        btn_ref,
        categoria,
        item_id,
        permitir_reverter=False
    )

def abrir_modal_desativar_popups(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Desativar Pop-ups e Dicas",
        "O Windows exibe frequentemente anúncios do OneDrive no Explorador, balões de sugestões e telas invasivas de 'Vamos terminar de configurar seu dispositivo' após atualizações.\n\nAtivar essa opção remove toda essa poluição visual e notificações irritantes, tornando o sistema mais limpo e ágil.",
        "scripts/windows_tweaks/script_desativar_popups.ps1",
        btn_ref,
        categoria,
        item_id
    )

def abrir_modal_desativar_activity_feed(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Desativar Feed e Atividades",
        "O Windows mantém um histórico secreto e contínuo de todos os aplicativos abertos, arquivos acessados e sites visitados (Linha do Tempo), além de rodar Widgets de notícias em segundo plano.\n\nAtivar isso desativa a Linha do Tempo e o painel de Notícias/Widgets, economizando muita memória RAM e tráfego de rede.",
        "scripts/windows_tweaks/script_desativar_activity_feed.ps1",
        btn_ref,
        categoria,
        item_id
    )

def abrir_modal_desativar_game_dvr(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Desativar Game DVR",
        "Esta ação desativa por completo o Game DVR e a gravação de clipes em segundo plano. Isso reduz drasticamente o uso de CPU, GPU e poupa o ciclo de leitura/escrita física no seu disco (SSD/HD), eliminando engasgos nos jogos.\n\nAVISO: O atalho 'Win + Alt + G' para gravar os últimos segundos de tela deixará de funcionar.",
        "scripts/windows_tweaks/script_game_dvr.ps1",
        btn_ref,
        categoria,
        item_id,
        permitir_reverter=True
    )

def abrir_modal_energia_amd(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Ajustes de Latência e CPU AMD",
        "Esta ação aplica ajustes avançados de energia e CPU específicos para processadores AMD.\n\nEla ativa a distribuição de cronômetros (timers) do kernel entre os núcleos (aliviando o Core 0 e reduzindo stutters), desativa o throttling de clock por software e acelera a transição de frequências (P-States).\n\n*Aviso: Setup com refrigeração muito deficiente pode sofrer leve elevação de temperatura, pois o processador priorizará desempenho absoluto em tempo real.*",
        "scripts/windows_tweaks/script_otimizar_energia_amd.ps1",
        btn_ref,
        categoria,
        item_id,
        permitir_reverter=True
    )

def abrir_modal_energia_intel(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Ajustes de Latência e CPU Intel",
        "Esta ação aplica ajustes avançados de energia e CPU específicos para processadores Intel.\n\nEla otimiza o isolamento de contexto no BCDEDIT (reduzindo impacto de mitigações de segurança), ativa a distribuição de cronômetros do kernel entre os núcleos (aliviando o Core 0), desativa o throttling de software e força o P-State máximo da CPU.\n\n*Aviso: Setup com refrigeração muito deficiente pode sofrer leve elevação de temperatura, pois o processador priorizará desempenho absoluto em tempo real.*",
        "scripts/windows_tweaks/script_otimizar_energia_intel.ps1",
        btn_ref,
        categoria,
        item_id,
        permitir_reverter=True
    )

def abrir_modal_otimizar_gpu(parent, btn_ref=None, categoria=None, item_id=None):
    import core.runner as runner
    
    modal = ctk.CTkToplevel(parent)
    modal.title("Otimização Profunda de GPU")
    modal.geometry("560x520")
    modal.resizable(False, False)
    modal.configure(fg_color="#282A36")
    
    # Prende o foco no modal
    modal.transient(parent)
    modal.grab_set()

    # Centraliza o modal na tela
    modal.update_idletasks()
    x = (modal.winfo_screenwidth() - modal.winfo_reqwidth()) // 2
    y = (modal.winfo_screenheight() - modal.winfo_reqheight()) // 2
    modal.geometry(f"+{x}+{y}")

    # Título Principal
    lbl_titulo = ctk.CTkLabel(modal, text="Otimização Profunda de GPU", font=ctk.CTkFont(size=20, weight="bold"))
    lbl_titulo.pack(pady=(20, 5))

    lbl_desc = ctk.CTkLabel(
        modal, 
        text="Selecione manualmente a fabricante do seu chip de vídeo para aplicar os tweaks do EXM. Se você possui um notebook gamer híbrido (Intel + NVIDIA/AMD), é altamente recomendado otimizar ambos!",
        wraplength=500,
        font=ctk.CTkFont(size=12),
        justify="center"
    )
    lbl_desc.pack(pady=(0, 20))

    # Funções de Ação
    def aplicar_gpu(fabricante, cor_marca):
        modal.destroy()
        parent.log_mensagem(f"Iniciando otimizações avançadas para GPU {fabricante}...")
        sucesso = runner.executar_arquivo(
            "scripts/windows_tweaks/script_otimizar_gpu.ps1",
            logger=parent.log_mensagem,
            argumentos_extras=f'-Acao Ativar -Fabricante "{fabricante}"'
        )
        if sucesso:
            parent.log_mensagem(f"[OK] Otimizações para GPU {fabricante} aplicadas com sucesso!")
            if btn_ref:
                if categoria and item_id:
                    parent.marcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color=cor_marca, hover_color=cor_marca)
        else:
            parent.log_mensagem(f"[ERRO] Falha ao aplicar otimizações da GPU {fabricante}.")

    def reverter_gpu(fabricante):
        modal.destroy()
        parent.log_mensagem(f"Revertendo otimizações da GPU {fabricante} para o padrão...")
        sucesso = runner.executar_arquivo(
            "scripts/windows_tweaks/script_otimizar_gpu.ps1",
            logger=parent.log_mensagem,
            argumentos_extras=f'-Acao Reverter -Fabricante "{fabricante}"'
        )
        if sucesso:
            parent.log_mensagem(f"[OK] GPU {fabricante} restaurada ao padrão original!")
            if btn_ref:
                if categoria and item_id:
                    parent.desmarcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#c0392b", hover_color="#e74c3c")
        else:
            parent.log_mensagem(f"[ERRO] Falha ao reverter otimizações da GPU {fabricante}.")

    # --- SEÇÃO NVIDIA ---
    frame_nvidia = ctk.CTkFrame(modal, fg_color="#1a251c", border_width=1, border_color="#27ae60")
    frame_nvidia.pack(fill="x", padx=25, pady=8, ipady=5)
    
    lbl_nv_title = ctk.CTkLabel(frame_nvidia, text="🟢 NVIDIA GeForce Tweaks", font=ctk.CTkFont(size=14, weight="bold"), text_color="#2ecc71")
    lbl_nv_title.pack(anchor="w", padx=15, pady=(5, 0))
    lbl_nv_desc = ctk.CTkLabel(frame_nvidia, text="MSI Mode Prioridade Alta, telemetria suspensa e latências ultrabaixas PCIe.", font=ctk.CTkFont(size=11), text_color="#aaaaaa")
    lbl_nv_desc.pack(anchor="w", padx=15, pady=(0, 2))
    
    lbl_nv_warning = ctk.CTkLabel(frame_nvidia, text="⚠️ IMPORTANTE: No Painel de Controle NVIDIA (Ajustar configs de imagem), deixe selecionada a 2ª opção: 'Use as configurações de imagens avançadas em 3D' para ativar os tweaks.", font=ctk.CTkFont(size=10, weight="bold"), text_color="#f1c40f", wraplength=480, justify="left")
    lbl_nv_warning.pack(anchor="w", padx=15, pady=(0, 5))
    
    frame_nv_btns = ctk.CTkFrame(frame_nvidia, fg_color="transparent")
    frame_nv_btns.pack(fill="x", padx=15, pady=5)
    
    btn_nv_ativar = ctk.CTkButton(frame_nv_btns, text="Otimizar NVIDIA", fg_color="#27ae60", hover_color="#2ecc71", width=120, height=26, font=ctk.CTkFont(size=11, weight="bold"), command=lambda: aplicar_gpu("NVIDIA", "#27ae60"))
    btn_nv_ativar.pack(side="left", padx=(0, 10))
    btn_nv_reverter = ctk.CTkButton(frame_nv_btns, text="Reverter Padrão", fg_color="#444444", hover_color="#555555", width=110, height=26, font=ctk.CTkFont(size=11), command=lambda: reverter_gpu("NVIDIA"))
    btn_nv_reverter.pack(side="left")

    # --- SEÇÃO AMD ---
    frame_amd = ctk.CTkFrame(modal, fg_color="#251a1a", border_width=1, border_color="#c0392b")
    frame_amd.pack(fill="x", padx=25, pady=8, ipady=5)
    
    lbl_amd_title = ctk.CTkLabel(frame_amd, text="🔴 AMD Radeon Tweaks", font=ctk.CTkFont(size=14, weight="bold"), text_color="#e74c3c")
    lbl_amd_title.pack(anchor="w", padx=15, pady=(5, 0))
    lbl_amd_desc = ctk.CTkLabel(frame_amd, text="Desativa ULPS/Overlays, desliga Clock/Power Gating e crava FlipQueueSize em 1.", font=ctk.CTkFont(size=11), text_color="#aaaaaa")
    lbl_amd_desc.pack(anchor="w", padx=15, pady=(0, 5))
    
    frame_amd_btns = ctk.CTkFrame(frame_amd, fg_color="transparent")
    frame_amd_btns.pack(fill="x", padx=15, pady=5)
    
    btn_amd_ativar = ctk.CTkButton(frame_amd_btns, text="Otimizar AMD", fg_color="#c0392b", hover_color="#e74c3c", width=120, height=26, font=ctk.CTkFont(size=11, weight="bold"), command=lambda: aplicar_gpu("AMD", "#c0392b"))
    btn_amd_ativar.pack(side="left", padx=(0, 10))
    btn_amd_reverter = ctk.CTkButton(frame_amd_btns, text="Reverter Padrão", fg_color="#444444", hover_color="#555555", width=110, height=26, font=ctk.CTkFont(size=11), command=lambda: reverter_gpu("AMD"))
    btn_amd_reverter.pack(side="left")

    # --- SEÇÃO INTEL ---
    frame_intel = ctk.CTkFrame(modal, fg_color="#1a2025", border_width=1, border_color="#2980b9")
    frame_intel.pack(fill="x", padx=25, pady=8, ipady=5)
    
    lbl_intel_title = ctk.CTkLabel(frame_intel, text="🔵 Intel Graphics Tweaks", font=ctk.CTkFont(size=14, weight="bold"), text_color="#3498db")
    lbl_intel_title.pack(anchor="w", padx=15, pady=(5, 0))
    lbl_intel_desc = ctk.CTkLabel(frame_intel, text="Fixa segmento de memória estática de vídeo em 512MB e desativa economias.", font=ctk.CTkFont(size=11), text_color="#aaaaaa")
    lbl_intel_desc.pack(anchor="w", padx=15, pady=(0, 5))
    
    frame_intel_btns = ctk.CTkFrame(frame_intel, fg_color="transparent")
    frame_intel_btns.pack(fill="x", padx=15, pady=5)
    
    btn_intel_ativar = ctk.CTkButton(frame_intel_btns, text="Otimizar Intel", fg_color="#2980b9", hover_color="#3498db", width=120, height=26, font=ctk.CTkFont(size=11, weight="bold"), command=lambda: aplicar_gpu("Intel", "#2980b9"))
    btn_intel_ativar.pack(side="left", padx=(0, 10))
    btn_intel_reverter = ctk.CTkButton(frame_intel_btns, text="Reverter Padrão", fg_color="#444444", hover_color="#555555", width=110, height=26, font=ctk.CTkFont(size=11), command=lambda: reverter_gpu("Intel"))
    btn_intel_reverter.pack(side="left")


def abrir_modal_seguranca_avancada(parent, btn_ref=None, categoria=None, item_id=None):
    import core.runner as runner
    modal = ctk.CTkToplevel(parent)
    modal.title("Mitigações de Kernel e Segurança (FPS Extremo)")
    modal.geometry("560x520")
    modal.resizable(False, False)
    modal.configure(fg_color="#282A36")
    
    # Prende o foco no modal
    modal.transient(parent)
    modal.grab_set()

    # Centraliza o modal na tela
    modal.update_idletasks()
    x = (modal.winfo_screenwidth() - modal.winfo_reqwidth()) // 2
    y = (modal.winfo_screenheight() - modal.winfo_reqheight()) // 2
    modal.geometry(f"+{x}+{y}")

    # Título Principal
    lbl_titulo = ctk.CTkLabel(modal, text="🛡️ Segurança do Kernel vs FPS ⚡", font=ctk.CTkFont(size=20, weight="bold"), text_color="#e74c3c")
    lbl_titulo.pack(pady=(20, 5))

    aviso_texto = (
        "⚠️ AVISO DE SEGURANÇA CRÍTICO E DE RISCO ⚠️\n\n"
        "Esta otimização desativa recursos fundamentais de segurança de hardware e isolamento do Windows:\n\n"
        "• Spectre & Meltdown (Mitigações de CPU): Desativa remendos de hardware. Aumenta o desempenho e resposta de clock geral da CPU.\n"
        "• Virtualization-Based Security (VBS / Core Isolation): Desativa a virtualização de segurança do Windows. Elimina stutters e engasgos de frames.\n"
        "• ASLR (Address Space Layout Randomization): Desativa o embaralhamento estático de endereços de DLLs na memória RAM. Acelera o tempo de carregamento de processos.\n\n"
        "Risco: O PC ficará exposto a explorações de memória se você executar arquivos suspeitos ou vírus. Recomendado apenas para computadores dedicados exclusivamente a JOGOS competitivos!"
    )

    frame_aviso = ctk.CTkFrame(
        modal, fg_color="#2c1a1a", border_width=1, border_color="#c0392b",
        corner_radius=8
    )
    frame_aviso.pack(padx=25, pady=(10, 15), fill="both", expand=True)

    lbl_aviso = ctk.CTkLabel(
        frame_aviso, text=aviso_texto, wraplength=480, justify="center",
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color="#e74c3c"
    )
    lbl_aviso.pack(padx=15, pady=15, fill="both", expand=True)

    def desativar_seguranca():
        modal.destroy()
        parent.log_mensagem("DESATIVANDO proteções de kernel e segurança (FPS Máximo)...")
        sucesso = runner.executar_arquivo(
            "scripts/windows_tweaks/script_seguranca_avancada.ps1",
            logger=parent.log_mensagem,
            argumentos_extras='-Acao Ativar'
        )
        if sucesso:
            parent.log_mensagem("[OK] Otimizações de segurança extrema aplicadas! REINICIE o PC.")
            if btn_ref:
                if categoria and item_id:
                    parent.marcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#27ae60", hover_color="#2ecc71")
        else:
            parent.log_mensagem("[ERRO] Falha ao desativar as proteções de segurança.")

    def reativar_seguranca():
        modal.destroy()
        parent.log_mensagem("REATIVANDO proteções padrão do Windows (Segurança Recomendada)...")
        sucesso = runner.executar_arquivo(
            "scripts/windows_tweaks/script_seguranca_avancada.ps1",
            logger=parent.log_mensagem,
            argumentos_extras='-Acao Reverter'
        )
        if sucesso:
            parent.log_mensagem("[OK] Proteções e mitigações restauradas ao padrão original!")
            if btn_ref:
                if categoria and item_id:
                    parent.desmarcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#D32F2F", hover_color="#B71C1C")
        else:
            parent.log_mensagem("[ERRO] Falha ao restaurar as proteções de segurança.")

    frame_botoes = ctk.CTkFrame(modal, fg_color="transparent")
    frame_botoes.pack(fill="x", padx=25, pady=(0, 25), side="bottom")

    btn_desativar = ctk.CTkButton(
        frame_botoes, text="⚡ FPS MÁXIMO (Desproteger)", 
        fg_color="#c0392b", hover_color="#e74c3c", 
        font=ctk.CTkFont(weight="bold", size=12), height=42, 
        command=desativar_seguranca
    )
    btn_desativar.pack(side="left", padx=(0, 10), expand=True, fill="x")

    btn_reativar = ctk.CTkButton(
        frame_botoes, text="🛡️ SEGURANÇA (Padrão Windows)", 
        fg_color="#27ae60", hover_color="#2ecc71", 
        font=ctk.CTkFont(weight="bold", size=12), height=42, 
        command=reativar_seguranca
    )
    btn_reativar.pack(side="right", expand=True, fill="x")


def abrir_modal_timer_coalescing(parent, btn_ref=None, categoria=None, item_id=None):
    import core.runner as runner
    modal = ctk.CTkToplevel(parent)
    modal.title("Timer Coalescing & Latência")
    modal.geometry("560x440")
    modal.resizable(False, False)
    modal.configure(fg_color="#282A36")
    
    # Prende o foco no modal
    modal.transient(parent)
    modal.grab_set()

    # Centraliza o modal na tela
    modal.update_idletasks()
    x = (modal.winfo_screenwidth() - modal.winfo_reqwidth()) // 2
    y = (modal.winfo_screenheight() - modal.winfo_reqheight()) // 2
    modal.geometry(f"+{x}+{y}")

    # Título Principal
    lbl_titulo = ctk.CTkLabel(modal, text="⚡ Timer Coalescing & Latência de CPU ⚡", font=ctk.CTkFont(family="Arial", size=18, weight="bold"), text_color="#3498db")
    lbl_titulo.pack(pady=(20, 5))

    texto_explicativo = (
        "Esta ação desativa recursos que forçam o seu processador a poupar energia à custa de latência:\n\n"
        "• Timer Coalescing: Impede que o Windows agrupe requisições de tempo, acelerando a resposta da CPU.\n"
        "• GPU Energy Driver: Desativa o driver de telemetria de consumo da placa de vídeo.\n"
        "• Telemetria de Energia: Bloqueia logs e limites artificiais da pilha TaggedEnergy no kernel.\n\n"
        "Vantagem: Resposta física imediata da CPU e GPU nos seus jogos!"
    )

    frame_aviso = ctk.CTkFrame(
        modal, fg_color="#1a2025", border_width=1, border_color="#2980b9",
        corner_radius=8
    )
    frame_aviso.pack(padx=25, pady=(10, 15), fill="both", expand=True)

    lbl_aviso = ctk.CTkLabel(
        frame_aviso, text=texto_explicativo, wraplength=480, justify="left",
        font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
        text_color="#3498db"
    )
    lbl_aviso.pack(padx=15, pady=15, fill="both", expand=True)

    def ativar():
        modal.destroy()
        parent.log_mensagem("Ativando Otimizações de Timer Coalescing (FPS Máximo)...")
        sucesso = runner.executar_arquivo(
            "scripts/windows_tweaks/script_desativar_timer_coalescing.ps1",
            logger=parent.log_mensagem,
            argumentos_extras='-Acao Ativar'
        )
        if sucesso:
            parent.log_mensagem("[OK] Otimizações de Timer Coalescing e Energia aplicadas!")
            if btn_ref:
                if categoria and item_id:
                    parent.marcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#27ae60", hover_color="#2ecc71")
        else:
            parent.log_mensagem("[ERRO] Falha ao desativar Timer Coalescing.")

    def reverter():
        modal.destroy()
        parent.log_mensagem("Revertendo Otimizações de Timer Coalescing para o padrão...")
        sucesso = runner.executar_arquivo(
            "scripts/windows_tweaks/script_desativar_timer_coalescing.ps1",
            logger=parent.log_mensagem,
            argumentos_extras='-Acao Reverter'
        )
        if sucesso:
            parent.log_mensagem("[OK] Agrupamento de timers e energia restaurados ao padrão!")
            if btn_ref:
                if categoria and item_id:
                    parent.desmarcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#D32F2F", hover_color="#B71C1C")
        else:
            parent.log_mensagem("[ERRO] Falha ao reverter Timer Coalescing.")

    frame_botoes = ctk.CTkFrame(modal, fg_color="transparent")
    frame_botoes.pack(fill="x", padx=25, pady=(0, 20), side="bottom")

    btn_ativar = ctk.CTkButton(
        frame_botoes, text="⚡ ATIVAR OTIMIZAÇÃO", 
        fg_color="#27ae60", hover_color="#2ecc71", 
        font=ctk.CTkFont(weight="bold", size=12), height=40, 
        command=ativar
    )
    btn_ativar.pack(side="left", padx=(0, 10), expand=True, fill="x")

    btn_reverter = ctk.CTkButton(
        frame_botoes, text="🛡️ REVERTER PADRÃO", 
        fg_color="#c0392b", hover_color="#e74c3c", 
        font=ctk.CTkFont(weight="bold", size=12), height=40, 
        command=reverter
    )
    btn_reverter.pack(side="right", expand=True, fill="x")


def abrir_modal_latencia_disco(parent, btn_ref=None, categoria=None, item_id=None):
    import core.runner as runner
    modal = ctk.CTkToplevel(parent)
    modal.title("Otimizar Latência de Disco")
    modal.geometry("560x440")
    modal.resizable(False, False)
    modal.configure(fg_color="#282A36")
    
    # Prende o foco no modal
    modal.transient(parent)
    modal.grab_set()

    # Centraliza o modal na tela
    modal.update_idletasks()
    x = (modal.winfo_screenwidth() - modal.winfo_reqwidth()) // 2
    y = (modal.winfo_screenheight() - modal.winfo_reqheight()) // 2
    modal.geometry(f"+{x}+{y}")

    # Título Principal
    lbl_titulo = ctk.CTkLabel(modal, text="💾 Latência de Armazenamento (HIPM/DIPM) 💾", font=ctk.CTkFont(family="Arial", size=18, weight="bold"), text_color="#9b59b6")
    lbl_titulo.pack(pady=(20, 5))

    texto_explicativo = (
        "Esta ação desativa os modos de repouso físico e economia de link nas suas unidades de disco:\n\n"
        "• StorPort Idle Power: Impede que o controlador de armazenamento entre em repouso temporário ocioso.\n"
        "• HIPM / DIPM: Desativa as economias de energia de link da placa-mãe para o SSD/HDD.\n"
        "• HDD Parking: Evita o recolhimento repentino das cabeças de leitura física de HDDs.\n\n"
        "Vantagem: Discos sempre ativos, eliminando micro-travadas (stutters) nos jogos!"
    )

    frame_aviso = ctk.CTkFrame(
        modal, fg_color="#201a25", border_width=1, border_color="#8e44ad",
        corner_radius=8
    )
    frame_aviso.pack(padx=25, pady=(10, 15), fill="both", expand=True)

    lbl_aviso = ctk.CTkLabel(
        frame_aviso, text=texto_explicativo, wraplength=480, justify="left",
        font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
        text_color="#9b59b6"
    )
    lbl_aviso.pack(padx=15, pady=15, fill="both", expand=True)

    def ativar():
        modal.destroy()
        parent.log_mensagem("Ativando Otimizações de Latência de Disco (HIPM/DIPM)...")
        sucesso = runner.executar_arquivo(
            "scripts/windows_tweaks/script_otimizar_latencia_disco.ps1",
            logger=parent.log_mensagem,
            argumentos_extras='-Acao Ativar'
        )
        if sucesso:
            parent.log_mensagem("[OK] Otimizações de Latência de Disco aplicadas!")
            if btn_ref:
                if categoria and item_id:
                    parent.marcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#27ae60", hover_color="#2ecc71")
        else:
            parent.log_mensagem("[ERRO] Falha ao otimizar latência de disco.")

    def reverter():
        modal.destroy()
        parent.log_mensagem("Revertendo Otimizações de Latência de Disco para o padrão...")
        sucesso = runner.executar_arquivo(
            "scripts/windows_tweaks/script_otimizar_latencia_disco.ps1",
            logger=parent.log_mensagem,
            argumentos_extras='-Acao Reverter'
        )
        if sucesso:
            parent.log_mensagem("[OK] Latência de disco restaurada ao padrão de economia de energia!")
            if btn_ref:
                if categoria and item_id:
                    parent.desmarcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#D32F2F", hover_color="#B71C1C")
        else:
            parent.log_mensagem("[ERRO] Falha ao reverter latência de disco.")

    frame_botoes = ctk.CTkFrame(modal, fg_color="transparent")
    frame_botoes.pack(fill="x", padx=25, pady=(0, 20), side="bottom")

    btn_ativar = ctk.CTkButton(
        frame_botoes, text="💾 ATIVAR OTIMIZAÇÃO", 
        fg_color="#27ae60", hover_color="#2ecc71", 
        font=ctk.CTkFont(weight="bold", size=12), height=40, 
        command=ativar
    )
    btn_ativar.pack(side="left", padx=(0, 10), expand=True, fill="x")

    btn_reverter = ctk.CTkButton(
        frame_botoes, text="🛡️ REVERTER PADRÃO", 
        fg_color="#c0392b", hover_color="#e74c3c", 
        font=ctk.CTkFont(weight="bold", size=12), height=40, 
        command=reverter
    )
    btn_reverter.pack(side="right", expand=True, fill="x")


def abrir_modal_limpar_cache_ram(parent, btn_ref=None, categoria=None, item_id=None):
    _criar_modal_generico(
        parent,
        "Limpar Cache de Memória RAM (Standby)",
        "Esta opção limpa a lista de páginas em cache que o Windows mantém na RAM (Standby List), além de forçar a coleta de lixo e liberação de memória inativa.\n\nIsso pode liberar gigabytes de RAM instantaneamente sem fechar seus programas, melhorando a responsividade e reduzindo travamentos (stutters) em jogos pesados.",
        "scripts/windows_tweaks/script_limpar_cache_ram.ps1",
        btn_ref,
        categoria,
        item_id,
        permitir_reverter=False
    )


def abrir_modal_otimizar_memoria(parent, btn_ref=None, categoria=None, item_id=None):
    import core.runner as runner
    modal = ctk.CTkToplevel(parent)
    modal.title("Otimizar Memória RAM")
    modal.geometry("560x440")
    modal.resizable(False, False)
    modal.configure(fg_color="#282A36")
    
    # Prende o foco no modal
    modal.transient(parent)
    modal.grab_set()

    # Centraliza o modal na tela
    modal.update_idletasks()
    x = (modal.winfo_screenwidth() - modal.winfo_reqwidth()) // 2
    y = (modal.winfo_screenheight() - modal.winfo_reqheight()) // 2
    modal.geometry(f"+{x}+{y}")

    # Título Principal
    lbl_titulo = ctk.CTkLabel(modal, text="🧠 Otimização de Memória RAM & Pagefile 🧠", font=ctk.CTkFont(family="Arial", size=18, weight="bold"), text_color="#1abc9c")
    lbl_titulo.pack(pady=(20, 5))

    texto_explicativo = (
        "Esta ação otimiza o uso e velocidade da memória RAM instalada no computador:\n\n"
        "• Compressão de RAM: Desativa a compressão se o PC tiver >= 16GB de RAM, economizando ciclos de CPU.\n"
        "• Page Combining: Desativa a fusão de memória ociosa em segundo plano para poupar a CPU.\n"
        "• Paging Executive: Mantém o Kernel e drivers inteiramente na RAM física, eliminando latências.\n\n"
        "Vantagem: Menor uso de CPU e tempo de resposta extremamente rápido in-game!"
    )

    frame_aviso = ctk.CTkFrame(
        modal, fg_color="#112220", border_width=1, border_color="#1abc9c",
        corner_radius=8
    )
    frame_aviso.pack(padx=25, pady=(10, 15), fill="both", expand=True)

    lbl_aviso = ctk.CTkLabel(
        frame_aviso, text=texto_explicativo, wraplength=480, justify="left",
        font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
        text_color="#1abc9c"
    )
    lbl_aviso.pack(padx=15, pady=15, fill="both", expand=True)

    def ativar():
        modal.destroy()
        parent.log_mensagem("Ativando Otimizações de Memória RAM (FPS Máximo)...")
        sucesso = runner.executar_arquivo(
            "scripts/windows_tweaks/script_otimizar_memoria.ps1",
            logger=parent.log_mensagem,
            argumentos_extras='-Acao Ativar'
        )
        if sucesso:
            parent.log_mensagem("[OK] Otimizações de Memória RAM aplicadas com sucesso!")
            if btn_ref:
                if categoria and item_id:
                    parent.marcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#27ae60", hover_color="#2ecc71")
        else:
            parent.log_mensagem("[ERRO] Falha ao otimizar memória RAM.")

    def reverter():
        modal.destroy()
        parent.log_mensagem("Revertendo Otimizações de Memória RAM para o padrão...")
        sucesso = runner.executar_arquivo(
            "scripts/windows_tweaks/script_otimizar_memoria.ps1",
            logger=parent.log_mensagem,
            argumentos_extras='-Acao Reverter'
        )
        if sucesso:
            parent.log_mensagem("[OK] Configurações de memória RAM restauradas ao padrão original!")
            if btn_ref:
                if categoria and item_id:
                    parent.desmarcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#D32F2F", hover_color="#B71C1C")
        else:
            parent.log_mensagem("[ERRO] Falha ao reverter otimizações de memória RAM.")

    frame_botoes = ctk.CTkFrame(modal, fg_color="transparent")
    frame_botoes.pack(fill="x", padx=25, pady=(0, 20), side="bottom")

    btn_ativar = ctk.CTkButton(
        frame_botoes, text="🧠 ATIVAR OTIMIZAÇÃO", 
        fg_color="#27ae60", hover_color="#2ecc71", 
        font=ctk.CTkFont(weight="bold", size=12), height=40, 
        command=ativar
    )
    btn_ativar.pack(side="left", padx=(0, 10), expand=True, fill="x")

    btn_reverter = ctk.CTkButton(
        frame_botoes, text="🛡️ REVERTER PADRÃO", 
        fg_color="#c0392b", hover_color="#e74c3c", 
        font=ctk.CTkFont(weight="bold", size=12), height=40, 
        command=reverter
    )
    btn_reverter.pack(side="right", expand=True, fill="x")


def abrir_modal_latencia_usb(parent, btn_ref=None, categoria=None, item_id=None):
    import core.runner as runner
    modal = ctk.CTkToplevel(parent)
    modal.title("Otimizar Latência USB")
    modal.geometry("560x440")
    modal.resizable(False, False)
    modal.configure(fg_color="#282A36")
    
    # Prende o foco no modal
    modal.transient(parent)
    modal.grab_set()

    # Centraliza o modal na tela
    modal.update_idletasks()
    x = (modal.winfo_screenwidth() - modal.winfo_reqwidth()) // 2
    y = (modal.winfo_screenheight() - modal.winfo_reqheight()) // 2
    modal.geometry(f"+{x}+{y}")

    # Título Principal
    lbl_titulo = ctk.CTkLabel(modal, text="⚡ Latência USB & MSI Mode ⚡", font=ctk.CTkFont(family="Arial", size=18, weight="bold"), text_color="#f39c12")
    lbl_titulo.pack(pady=(20, 5))

    texto_explicativo = (
        "Esta ação desativa a suspensão seletiva e gerencia o tempo de resposta físico das suas portas USB:\n\n"
        "• USB Power Management: Impede que o Windows desligue portas USB para poupar energia.\n"
        "• Thread Priority: Força os drivers de barramento USB, Hubs e Rede a rodarem em tempo real (Prioridade 31).\n"
        "• MSI (Message Signaled Interrupts): Ativa interrupções sinalizadas para evitar jitter e atraso de polling.\n\n"
        "Vantagem: Inputs de mouse e teclado processados instantaneamente, sem atrasos ou stutters!"
    )

    frame_aviso = ctk.CTkFrame(
        modal, fg_color="#2c2415", border_width=1, border_color="#f39c12",
        corner_radius=8
    )
    frame_aviso.pack(padx=25, pady=(10, 15), fill="both", expand=True)

    lbl_aviso = ctk.CTkLabel(
        frame_aviso, text=texto_explicativo, wraplength=480, justify="left",
        font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
        text_color="#f39c12"
    )
    lbl_aviso.pack(padx=15, pady=15, fill="both", expand=True)

    def ativar():
        modal.destroy()
        parent.log_mensagem("Ativando Otimizações de Latência USB (MSI & PowerSavings)...")
        sucesso = runner.executar_arquivo(
            "scripts/windows_tweaks/script_otimizar_latencia_usb.ps1",
            logger=parent.log_mensagem,
            argumentos_extras='-Acao Ativar'
        )
        if sucesso:
            parent.log_mensagem("[OK] Otimizações de Latência USB aplicadas com sucesso!")
            if btn_ref:
                if categoria and item_id:
                    parent.marcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#27ae60", hover_color="#2ecc71")
        else:
            parent.log_mensagem("[ERRO] Falha ao otimizar latência USB.")

    def reverter():
        modal.destroy()
        parent.log_mensagem("Revertendo Otimizações de Latência USB para o padrão...")
        sucesso = runner.executar_arquivo(
            "scripts/windows_tweaks/script_otimizar_latencia_usb.ps1",
            logger=parent.log_mensagem,
            argumentos_extras='-Acao Reverter'
        )
        if sucesso:
            parent.log_mensagem("[OK] Otimizações de latência USB revertidas para o padrão original!")
            if btn_ref:
                if categoria and item_id:
                    parent.desmarcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#D32F2F", hover_color="#B71C1C")
        else:
            parent.log_mensagem("[ERRO] Falha ao reverter otimizações de latência USB.")

    frame_botoes = ctk.CTkFrame(modal, fg_color="transparent")
    frame_botoes.pack(fill="x", padx=25, pady=(0, 20), side="bottom")

    btn_ativar = ctk.CTkButton(
        frame_botoes, text="⚡ ATIVAR OTIMIZAÇÃO", 
        fg_color="#27ae60", hover_color="#2ecc71", 
        font=ctk.CTkFont(weight="bold", size=12), height=40, 
        command=ativar
    )
    btn_ativar.pack(side="left", padx=(0, 10), expand=True, fill="x")

    btn_reverter = ctk.CTkButton(
        frame_botoes, text="🛡️ REVERTER PADRÃO", 
        fg_color="#c0392b", hover_color="#e74c3c", 
        font=ctk.CTkFont(weight="bold", size=12), height=40, 
        command=reverter
    )
    btn_reverter.pack(side="right", expand=True, fill="x")


def abrir_modal_limpar_dispositivos(parent, btn_ref=None, categoria=None, item_id=None):
    import core.runner as runner
    modal = ctk.CTkToplevel(parent)
    modal.title("Limpar Dispositivos Fantasmas")
    modal.geometry("560x440")
    modal.resizable(False, False)
    modal.configure(fg_color="#282A36")
    
    # Prende o foco no modal
    modal.transient(parent)
    modal.grab_set()

    # Centraliza o modal na tela
    modal.update_idletasks()
    x = (modal.winfo_screenwidth() - modal.winfo_reqwidth()) // 2
    y = (modal.winfo_screenheight() - modal.winfo_reqheight()) // 2
    modal.geometry(f"+{x}+{y}")

    # Título Principal
    lbl_titulo = ctk.CTkLabel(modal, text="💾 Limpeza de Dispositivos Fantasmas (PnP) 💾", font=ctk.CTkFont(family="Arial", size=18, weight="bold"), text_color="#9b59b6")
    lbl_titulo.pack(pady=(20, 5))

    texto_explicativo = (
        "Esta ação limpa o histórico de dispositivos Plug & Play desconectados ou ausentes no seu registro:\n\n"
        "• Registro de Dispositivos Fantasmas: Remove vestígios inativos de antigos pendrives, mouses e teclados.\n"
        "• Despoluição do Subsistema PnP: Evita que o Windows gaste ciclos procurando hardwares ausentes.\n"
        "• Estabilidade de Periféricos: Diminui a latência de reconhecimento de dispositivos de entrada ativos.\n\n"
        "Vantagem: Um registro de hardware limpo e com tempo de resposta imediato para novos inputs!"
    )

    frame_aviso = ctk.CTkFrame(
        modal, fg_color="#201a25", border_width=1, border_color="#8e44ad",
        corner_radius=8
    )
    frame_aviso.pack(padx=25, pady=(10, 15), fill="both", expand=True)

    lbl_aviso = ctk.CTkLabel(
        frame_aviso, text=texto_explicativo, wraplength=480, justify="left",
        font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
        text_color="#9b59b6"
    )
    lbl_aviso.pack(padx=15, pady=15, fill="both", expand=True)

    def ativar():
        modal.destroy()
        parent.log_mensagem("Iniciando Limpeza de Dispositivos Fantasmas (PnP)...")
        sucesso = runner.executar_arquivo(
            "scripts/windows_tweaks/script_limpar_dispositivos_fantasmas.ps1",
            logger=parent.log_mensagem,
            argumentos_extras='-Acao Ativar'
        )
        if sucesso:
            parent.log_mensagem("[OK] Dispositivos fantasmas limpos do registro com sucesso!")
            if btn_ref:
                if categoria and item_id:
                    parent.marcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#27ae60", hover_color="#2ecc71")
        else:
            parent.log_mensagem("[ERRO] Falha ao limpar dispositivos fantasmas.")

    def reverter():
        modal.destroy()
        parent.log_mensagem("Revertendo Limpeza de Dispositivos Fantasmas...")
        sucesso = runner.executar_arquivo(
            "scripts/windows_tweaks/script_limpar_dispositivos_fantasmas.ps1",
            logger=parent.log_mensagem,
            argumentos_extras='-Acao Reverter'
        )
        if sucesso:
            parent.log_mensagem("[OK] Estado ideal do subsistema PnP restaurado!")
            if btn_ref:
                if categoria and item_id:
                    parent.desmarcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#D32F2F", hover_color="#B71C1C")
        else:
            parent.log_mensagem("[ERRO] Falha ao reverter limpeza de dispositivos.")

    frame_botoes = ctk.CTkFrame(modal, fg_color="transparent")
    frame_botoes.pack(fill="x", padx=25, pady=(0, 20), side="bottom")

    btn_ativar = ctk.CTkButton(
        frame_botoes, text="⚡ ATIVAR OTIMIZAÇÃO", 
        fg_color="#27ae60", hover_color="#2ecc71", 
        font=ctk.CTkFont(weight="bold", size=12), height=40, 
        command=ativar
    )
    btn_ativar.pack(side="left", padx=(0, 10), expand=True, fill="x")

    btn_reverter = ctk.CTkButton(
        frame_botoes, text="🛡️ REVERTER PADRÃO", 
        fg_color="#c0392b", hover_color="#e74c3c", 
        font=ctk.CTkFont(weight="bold", size=12), height=40, 
        command=reverter
    )
    btn_reverter.pack(side="right", expand=True, fill="x")


def abrir_modal_limpar_lixeira(parent, btn_ref=None, categoria=None, item_id=None):
    import core.runner as runner
    modal = ctk.CTkToplevel(parent)
    modal.title("Esvaziar Lixeira do PC")
    modal.geometry("560x440")
    modal.resizable(False, False)
    modal.configure(fg_color="#282A36")
    
    # Prende o foco no modal
    modal.transient(parent)
    modal.grab_set()

    # Centraliza o modal na tela
    modal.update_idletasks()
    x = (modal.winfo_screenwidth() - modal.winfo_reqwidth()) // 2
    y = (modal.winfo_screenheight() - modal.winfo_reqheight()) // 2
    modal.geometry(f"+{x}+{y}")

    # Título Principal
    lbl_titulo = ctk.CTkLabel(modal, text="💾 Esvaziar Lixeira do PC 💾", font=ctk.CTkFont(family="Arial", size=18, weight="bold"), text_color="#9b59b6")
    lbl_titulo.pack(pady=(20, 5))

    texto_explicativo = (
        "Esta ação calcula o espaço atual e apaga permanentemente todos os itens da Lixeira do Windows:\n\n"
        "• Esvaziamento Geral: Exclui permanentemente arquivos e pastas deletadas em todos os discos.\n"
        "• Liberação Imediata: Recupera megabytes ou gigabytes de armazenamento desperdiçado na lixeira.\n"
        "• Nota de Segurança: A remoção de arquivos é definitiva e não poderá ser desfeita posteriormente.\n\n"
        "Vantagem: Liberação imediata de espaço e limpeza definitiva de arquivos inativos no disco!"
    )

    frame_aviso = ctk.CTkFrame(
        modal, fg_color="#201a25", border_width=1, border_color="#8e44ad",
        corner_radius=8
    )
    frame_aviso.pack(padx=25, pady=(10, 15), fill="both", expand=True)

    lbl_aviso = ctk.CTkLabel(
        frame_aviso, text=texto_explicativo, wraplength=480, justify="left",
        font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
        text_color="#9b59b6"
    )
    lbl_aviso.pack(padx=15, pady=15, fill="both", expand=True)

    def ativar():
        modal.destroy()
        parent.log_mensagem("Iniciando Limpeza e Esvaziamento da Lixeira...")
        sucesso = runner.executar_arquivo(
            "scripts/windows_tweaks/script_limpar_lixeira.ps1",
            logger=parent.log_mensagem,
            argumentos_extras='-Acao Ativar'
        )
        if sucesso:
            parent.log_mensagem("[OK] Lixeira esvaziada com sucesso!")
            if btn_ref:
                if categoria and item_id:
                    parent.marcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#27ae60", hover_color="#2ecc71")
        else:
            parent.log_mensagem("[ERRO] Falha ao esvaziar lixeira.")

    def reverter():
        modal.destroy()
        parent.log_mensagem("Revertendo Limpeza da Lixeira...")
        sucesso = runner.executar_arquivo(
            "scripts/windows_tweaks/script_limpar_lixeira.ps1",
            logger=parent.log_mensagem,
            argumentos_extras='-Acao Reverter'
        )
        if sucesso:
            parent.log_mensagem("[OK] Estado ideal de armazenamento mantido!")
            if btn_ref:
                if categoria and item_id:
                    parent.desmarcar_completado(categoria, item_id, btn_ref)
                else:
                    btn_ref.configure(fg_color="#D32F2F", hover_color="#B71C1C")
        else:
            parent.log_mensagem("[ERRO] Falha ao reverter limpeza de lixeira.")

    frame_botoes = ctk.CTkFrame(modal, fg_color="transparent")
    frame_botoes.pack(fill="x", padx=25, pady=(0, 20), side="bottom")

    btn_ativar = ctk.CTkButton(
        frame_botoes, text="⚡ ATIVAR OTIMIZAÇÃO", 
        fg_color="#27ae60", hover_color="#2ecc71", 
        font=ctk.CTkFont(weight="bold", size=12), height=40, 
        command=ativar
    )
    btn_ativar.pack(side="left", padx=(0, 10), expand=True, fill="x")

    btn_reverter = ctk.CTkButton(
        frame_botoes, text="🛡️ REVERTER PADRÃO", 
        fg_color="#c0392b", hover_color="#e74c3c", 
        font=ctk.CTkFont(weight="bold", size=12), height=40, 
        command=reverter
    )
    btn_reverter.pack(side="right", expand=True, fill="x")


def abrir_modal_leiame_windows(parent):
    modal = ctk.CTkToplevel(parent)
    modal.title("⚠️ LEIA-ME: Como aplicar otimizações ⚠️")
    modal.geometry("700x530")
    modal.resizable(False, False)
    modal.configure(fg_color="#282A36")
    
    modal.transient(parent)
    modal.grab_set()

    modal.update_idletasks()
    x = (modal.winfo_screenwidth() - modal.winfo_reqwidth()) // 2
    y = (modal.winfo_screenheight() - modal.winfo_reqheight()) // 2
    modal.geometry(f"+{x}+{y}")

    # Cores do tema unificado (foco na confiança e clareza)
    bg_color = "#1E2029"
    accent_color = "#0078FB"
    warning_color = "#E3B505"
    text_color = "#e8e8f0"

    # Título explicativo com cor de aviso
    lbl_aviso = ctk.CTkLabel(
        modal, text="⚠️ LEITURA MANDATÓRIA: AJUSTES DO WINDOWS ⚠️",
        font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
        text_color=warning_color
    )
    lbl_aviso.pack(pady=(20, 5))

    # Box Explicativo Premium
    frame_aviso = ctk.CTkFrame(
        modal, fg_color=bg_color, border_width=1, border_color=accent_color,
        corner_radius=8
    )
    frame_aviso.pack(padx=25, pady=(10, 15), fill="both", expand=True)

    text_msg = (
        "Para que as modificações visuais e de interface desta aba funcionem corretamente, "
        "leia atentamente as instruções abaixo:\n\n"
        "1. Por que é necessário Reiniciar?\n"
        "Ajustes como Tema Escuro, Menu de Contexto Clássico, ocultar/mostrar extensões de arquivo "
        "e configurações de Efeitos Visuais alteram registros que ficam armazenados em cache pelo "
        "Windows Explorer (explorer.exe). O Windows precisa recarregar esse processo ou reiniciar "
        "a máquina para que essas alterações entrem em vigor na interface.\n\n"
        "2. Qual opção escolher?\n"
        "• 📂 Reiniciar Explorer: Ação rápida e instantânea (a barra de tarefas piscará por 1 segundo). "
        "Ideal para aplicar imediatamente a maioria dos efeitos visuais de janelas e menus de contexto.\n"
        "• 🔄 Reiniciar PC (Recomendado): É a opção mais segura e definitiva. Garante que todas as "
        "novas diretivas de grupo (GPOs) e prioridades do kernel sejam carregadas de forma limpa pelo Windows.\n\n"
        "3. Dica de Produtividade:\n"
        "Você não precisa reiniciar a cada script aplicado! Sinta-se totalmente à vontade para "
        "rodar e ativar todos os ajustes visuais e de menu que desejar nesta aba do Windows e, somente após concluir "
        "todas as modificações, utilize uma das opções de reinício no topo para aplicar tudo de uma única vez."
    )

    lbl_mensagem = ctk.CTkLabel(
        frame_aviso, text=text_msg, wraplength=600, justify="left",
        font=ctk.CTkFont(family="Segoe UI", size=14),
        text_color=text_color
    )
    lbl_mensagem.pack(padx=15, pady=15, fill="both", expand=True)

    frame_botoes = ctk.CTkFrame(modal, fg_color="transparent")
    frame_botoes.pack(fill="x", padx=25, pady=(0, 20), side="bottom")

    btn_entendido = ctk.CTkButton(
        frame_botoes, text="ENTENDIDO, PROSSEGUIR", 
        fg_color=accent_color, hover_color="#005bc4", 
        font=ctk.CTkFont(weight="bold", size=12), height=40,
        command=modal.destroy
    )
    btn_entendido.pack(expand=True, fill="x")
