import customtkinter as ctk
import threading
from PIL import Image
import os
import subprocess
from core import runner, atalhos, gerenciador_json, diagnostico
from core.acoes_script import ACOES_SCRIPT
from core.riscos import risco_exige_confirmacao
from ui import modais

# Configuracao visual padrao
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ============================================================
# DEFINIÇÃO DAS CATEGORIAS DO CARDÁPIO
# ============================================================
CATEGORIAS = [
    {"key": "config_windows",       "emoji": "🪟", "titulo": "Windows",        "subtitulo": "Menu, Visuais e Interface"},
    {"key": "limpeza_armazenamento","emoji": "💾", "titulo": "Limpeza & Disco","subtitulo": "Liberar espaço e reparar"},
    {"key": "memory_tweaks",        "emoji": "📟", "titulo": "Memória RAM",     "subtitulo": "Otimizar RAM e Pagefile"},
    {"key": "cpu_energia",          "emoji": "⚡",  "titulo": "Energia & CPU",  "subtitulo": "Planos e desempenho max"},
    {"key": "gaming",               "emoji": "🎮", "titulo": "Gaming",         "subtitulo": "FPS, Game Mode e DVR"},
    {"key": "rede_latencia",        "emoji": "🌐", "titulo": "Rede / Latência",  "subtitulo": "Rede, CPU e GPU Latência"},
    {"key": "mouse_teclado",        "emoji": "🔌", "titulo": "Dispositivos",    "subtitulo": "Mouse, Teclado e Som"},
    {"key": "benchmark_info",       "emoji": "📊", "titulo": "Especificações",  "subtitulo": "Hardware e Diagnóstico"},
    {"key": "instalacao",           "emoji": "📦", "titulo": "Instalar",        "subtitulo": "Instale apps úteis"},
    {"key": "debloat_servicos",     "emoji": "🛡️", "titulo": "Desinstalar",     "subtitulo": "Remover apps e componentes"},
]

TEMAS_CATEGORIAS = {
    cat["key"]: {
        "fg": "#1E2029",            # Fundo escuro Dracula para os cards
        "border": "#3d4153",        # Borda sutil Dracula
        "hover_fg": "#282A36",      # Fundo padrão no hover (cor de fundo do app)
        "hover_border": "#0078FB",  # Borda azul da logo no hover
    }
    for cat in CATEGORIAS
}


# ============================================================
# GRUPOS DE SCRIPTS POR CATEGORIA (define o layout das abas)
# Scripts não listados aqui são exibidos em "Outros"
# automaticamente — garantindo espaço para scripts futuros.
# ============================================================
GRUPOS_DETALHE = {
    "config_windows": [
        {"titulo": "Interface Visual",       "emoji": "🎨",
         "scripts": ["Personalização (Visual e Cores)", "Efeitos Visuais de Desempenho"],
         "atalhos": []},
        {"titulo": "Menu e Explorador",      "emoji": "🗂️",
         "scripts": ["Alternar Menu de Contexto (Win 10/11)", "Explorador no Meu Computador", "Mostrar Extensões de Arquivo", "Desativar Home e Galeria", "Ocultar Pasta Linux (WSL)", "Desativar Linha do Tempo e Widgets"],
         "atalhos": []},
        {"titulo": "Performance do Sistema", "emoji": "⚡",
         "scripts": ["Inicialização Rápida (Fast Startup)", "Finalizar Tarefa (Barra de Tarefas)", "Bloquear Pop-ups, Dicas e Anúncios", "Restaurar Relógio para Hora Local (Padrão)", "Verificar Status do Antivírus (WMI)"],
         "atalhos": []},
    ],
    "debloat_servicos": [
        {"titulo": "Remoção de Aplicativos", "emoji": "🛡️",
         "scripts": ["Desinstalar Windows Apps", "OneDrive", "Microsoft Edge",
                     "Desinstalar somente Xbox Game Bar"],
         "atalhos": []},
        {"titulo": "Utilitários Nativos",    "emoji": "🔗",
         "scripts": [],
         "atalhos": [{"texto": "📋 Programas e Recursos", "cmd": "abrir_programas_recursos"}]},
    ],
    "limpeza_armazenamento": [
        {"titulo": "Limpeza Rápida",         "emoji": "🧹",
         "scripts": ["Limpar Cache de Apps e Browsers", "Limpar Arquivos Temporarios",
                     "Desativar Hibernacao", "Esvaziar Lixeira do PC"],
         "atalhos": []},
        {"titulo": "Manutenção e Reparo",    "emoji": "🔧",
         "scripts": ["Manutenção do Sistema (Disco e Rede)", "Reparar Integridade do Windows",
                     "Limpeza do Armazenamento de Componentes (WinSxS)", "Corrigir Windows Update",
                     "Apagar Pasta Windows.old", "BSOD Event Log"],
         "atalhos": []},
        {"titulo": "Otimização de Disco",    "emoji": "💽",
         "scripts": ["Ativar Cache de Gravação do Disco", "Otimização Inteligente de Unidades",
                     "Desativar Economia de Energia do Disco (HIPM/DIPM)", "Limpar Dispositivos Fantasmas (PnP)"],
         "atalhos": []},
        {"titulo": "Ferramentas de Disco",   "emoji": "🔗",
         "scripts": [],
         "atalhos": [
             {"texto": "💿 Limpeza de Disco (Nativo)",          "cmd": "abrir_limpeza_disco"},
             {"texto": "💿 Armazenamento (Configurações)",      "cmd": "abrir_armazenamento"},
             {"texto": "💿 Desfragmentar e Otimizar (Nativo)",  "cmd": "abrir_desfragmentador"},
         ]},
    ],
    "memory_tweaks": [
        {"titulo": "Otimização de RAM",      "emoji": "📟",
         "scripts": ["Otimizar Memória RAM (MMAgent & Paging)", "Limpar Cache de Memória RAM (Standby)"],
         "atalhos": []},
    ],
    "cpu_energia": [
        {"titulo": "Plano de Energia",       "emoji": "🔋",
         "scripts": ["Gerenciar Plano de Energia"],
         "atalhos": []},
    ],
    "gaming": [
        {"titulo": "Gaming",                 "emoji": "🎮",
         "scripts": ["Ativar Game Mode do Windows", "Desativar Gravação de Tela (Game DVR)",
                     "CS2 High CPU Priority", "Valorant High CPU Priority"],
         "atalhos": []},
    ],
    "rede_latencia": [
        {"titulo": "Rede e Ping",            "emoji": "🌐",
         "scripts": ["Otimizar DNS (Avançado)", "Redefinir Configurações de Rede"],
         "atalhos": []},
        {"titulo": "Privacidade e Telemetria", "emoji": "🔒",
         "scripts": ["Desativar Telemetria e Rastreadores", "Desativar Sincronizacao de Configuracoes",
                     "Desativar Experimentos do Windows"],
         "atalhos": []},
        {"titulo": "Serviços e Políticas",   "emoji": "🛡️",
         "scripts": ["Desativar Manutenção em Segundo Plano", "Otimizar Políticas de Grupo (GPO)",
                     "Otimizar Serviços do Windows"],
         "atalhos": []},
        {"titulo": "Latência",               "emoji": "⚡",
         "scripts": ["Redução Global de Latência (Ping/Hardware)", "Otimizar Latência USB (PowerSavings & MSI)", "Otimização de Registro (Avançado)"],
         "atalhos": []},
        {"titulo": "CPU",                    "emoji": "💻",
         "scripts": ["Ajustes de Latência e CPU AMD", "Ajustes de Latência e CPU Intel",
                     "Desativar Timer Coalescing"],
         "atalhos": []},
        {"titulo": "GPU",                    "emoji": "🎮",
         "scripts": ["Otimização de Placa de Vídeo (GPU)", "Otimização de GPU Global",
                     "Limpar Cache de Shaders de GPU", "Segurança do Kernel e Mitigações (FPS Extremo)",
                     "Importar Perfil NVIDIA (Lynch)"],
         "atalhos": []},
    ],
    "mouse_teclado": [
        {"titulo": "Mouse",                  "emoji": "🖱️",
         "scripts": ["Eliminar Input Lag (Competitivo)", "Otimização de Mouse (Aceleração)"],
         "atalhos": []},
        {"titulo": "Teclado e USB",          "emoji": "⌨️",
         "scripts": ["Acelerar Taxa de Repetição do Teclado", "Teclas de Aderência (Sticky Keys)", "Forçar Teclado ABNT2", "Teclado Layout EUA (60%)"],
         "atalhos": []},
        {"titulo": "Som e Áudio",            "emoji": "🔊",
         "scripts": ["Dispositivos de Som (Gerenciador)"],
         "atalhos": []},
    ],
}


class _NullBtn:
    """Widget fictício para compatibilidade com modais legados que chamam btn.configure()."""
    def configure(self, **kwargs):
        pass
    def cget(self, key):
        return None


class PCBoosterHub(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurar identificador do Windows para forçar exibição do ícone personalizado na barra de tarefas
        try:
            import ctypes
            myappid = 'lynch.fpsboost.hub.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        self.title("Lynch Boost - Hub")
        self.geometry("1100x800")
        self.resizable(False, False)
        self.configure(fg_color="#282A36")

        # Definir o ícone padrão para todas as janelas (incluindo modais secundários)
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.icon_path = os.path.abspath(os.path.join(base_dir, "..", "assets", "logo-ico.ico"))
            if os.path.exists(self.icon_path):
                self.iconbitmap(default=self.icon_path)
        except Exception:
            pass

        # Carregar imagens de logo globalmente para evitar Garbage Collection
        self._startup_warnings = []
        self.logo_img_splash = None
        self.logo_img_dash = None
        try:
            logo_png_path = os.path.abspath(os.path.join(base_dir, "..", "assets", "logo.png"))
            if os.path.exists(logo_png_path):
                img = Image.open(logo_png_path)
                self.logo_img_splash = ctk.CTkImage(light_image=img, dark_image=img, size=(160, 160))
                self.logo_img_dash = ctk.CTkImage(light_image=img, dark_image=img, size=(50, 50))
        except Exception as e:
            self._startup_warnings.append(f"[AVISO] Erro ao pre-carregar logo.png: {e}")

        # Estado de rastreamento dos cards
        self.card_status = {}           # {key: {"total": N, "completados": set()}}
        self.card_widgets = {}          # {key: card_frame}
        self.card_progress_labels = {}  # {key: progress_label}
        self.detail_frames = {}         # {key: detail_frame}
        self.item_status_labels = {}    # {item_id: CTkLabel} — indicadores ✅ do design premium
        self.item_text_labels = {}      # {item_id: CTkLabel} — nome do script
        self.item_row_frames = {}       # {item_id: CTkFrame} — container/botão do script

        # Layout principal — uma unica celula expansiva
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Console de log (criado primeiro para ser referenciado, gridado sob demanda)
        self._criar_console()
        for aviso in self._startup_warnings:
            self.log_mensagem(aviso)

        # Carregar dados do config.json
        self.dados_config = gerenciador_json.ler_config_json(self.log_mensagem) or {}

        # Inicializar contagem de status por categoria
        self._inicializar_status()

        # Construir as interfaces
        self.criar_dashboard()
        self._criar_telas_detalhe()
        self.criar_tela_inicial()  # Splash por cima de tudo

    # ============================================================
    # CONSOLE DE LOG
    # ============================================================
    # ============================================================
    # PAINEL DE LOG PREMIUM
    # ============================================================
    def _criar_console(self):
        self.console_frame = ctk.CTkFrame(
            self, fg_color="#1E2029",
            border_color="#3d4153", border_width=1,
            corner_radius=0
        )

        # Cabeçalho do log
        _hdr = ctk.CTkFrame(self.console_frame, fg_color="#282A36", corner_radius=0, height=32)
        _hdr.pack(fill="x")
        _hdr.pack_propagate(False)

        ctk.CTkLabel(
            _hdr, text="◉  Lynch Activity Log",
            font=("Segoe UI", 10, "bold"), text_color="#6366f1"
        ).pack(side="left", padx=(12, 0))

        ctk.CTkLabel(
            _hdr, text="● Sistema Online",
            font=("Segoe UI", 9), text_color="#22c55e"
        ).pack(side="left", padx=(10, 0))

        self.btn_limpar = ctk.CTkButton(
            _hdr, text="⌫ Limpar", width=65, height=22,
            fg_color="#343746", hover_color="#44475a",
            border_width=1, border_color="#44475a",
            text_color="#6366f1",
            font=ctk.CTkFont(size=9, weight="bold"),
            command=self.limpar_console
        )
        self.btn_limpar.pack(side="right", padx=8, pady=5)

        # Divisor
        ctk.CTkFrame(self.console_frame, height=1, fg_color="#3d4153").pack(fill="x")

        # Área de log
        self.console_box = ctk.CTkTextbox(
            self.console_frame,
            fg_color="#1E2029",
            text_color="#f8f8f2",
            font=("Segoe UI", 14),
            scrollbar_button_color="#343746",
            scrollbar_button_hover_color="#44475a",
        )
        self.console_box.pack(fill="both", expand=True, padx=6, pady=(4, 6))
        self.console_box.insert("0.0", "◉  Lynch Boost — Motor Online\n›  Aguardando comandos...")
        self.console_box.configure(state="disabled")

    # ============================================================
    # SPLASH SCREEN
    # ============================================================
    def criar_tela_inicial(self):
        self.splash_frame = ctk.CTkFrame(self, fg_color="black", corner_radius=0)
        self.splash_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")

        if self.logo_img_splash:
            self.splash_frame.grid_rowconfigure(0, weight=1)
            self.splash_frame.grid_rowconfigure(5, weight=1)
            self.splash_frame.grid_columnconfigure(0, weight=1)

            logo_lbl = ctk.CTkLabel(self.splash_frame, image=self.logo_img_splash, text="")
            logo_lbl.grid(row=1, column=0, pady=(0, 15))

            titulo = ctk.CTkLabel(
                self.splash_frame, text="LYNCH BOOST",
                font=ctk.CTkFont(size=56, weight="bold"), text_color="#0078FB"
            )
            titulo.grid(row=2, column=0, pady=(0, 10))

            sub = ctk.CTkLabel(
                self.splash_frame, text="Ultimate Windows Optimization Engine  ",
                font=ctk.CTkFont(size=20, slant="italic"), text_color="#AAAAAA"
            )
            sub.grid(row=3, column=0, pady=(0, 40))

            btn_iniciar = ctk.CTkButton(
                self.splash_frame, text="INICIAR MOTOR",
                width=300, height=60, font=ctk.CTkFont(size=24, weight="bold"),
                fg_color="#0078FB", hover_color="#005bc4", text_color="white",
                command=self.fechar_tela_inicial
            )
            btn_iniciar.grid(row=4, column=0)
        else:
            self.splash_frame.grid_rowconfigure(0, weight=1)
            self.splash_frame.grid_rowconfigure(4, weight=1)
            self.splash_frame.grid_columnconfigure(0, weight=1)

            titulo = ctk.CTkLabel(
                self.splash_frame, text="LYNCH BOOST",
                font=ctk.CTkFont(size=56, weight="bold"), text_color="#0078FB"
            )
            titulo.grid(row=1, column=0, pady=(0, 10))

            sub = ctk.CTkLabel(
                self.splash_frame, text="Ultimate Windows Optimization Engine  ",
                font=ctk.CTkFont(size=20, slant="italic"), text_color="#AAAAAA"
            )
            sub.grid(row=2, column=0, pady=(0, 50))

            btn_iniciar = ctk.CTkButton(
                self.splash_frame, text="INICIAR MOTOR",
                width=300, height=60, font=ctk.CTkFont(size=24, weight="bold"),
                fg_color="#0078FB", hover_color="#005bc4", text_color="white",
                command=self.fechar_tela_inicial
            )
            btn_iniciar.grid(row=3, column=0)

    def fechar_tela_inicial(self):
        self.splash_frame.grid_forget()
        self.mostrar_dashboard()

    # ============================================================
    # DASHBOARD — GRADE DE CARDS 3×2
    # ============================================================
    def criar_dashboard(self):
        self.dashboard_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)

        # --- Header ---
        header = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 0))

        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(anchor="center")

        if self.logo_img_dash:
            logo_lbl_dash = ctk.CTkLabel(header_content, image=self.logo_img_dash, text="")
            logo_lbl_dash.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            header_content, text="LYNCH HUB",
            font=ctk.CTkFont(size=28, weight="bold"), text_color="#0078FB"
        ).pack(side="left")

        # --- Separador azul ---
        ctk.CTkFrame(self.dashboard_frame, height=2, fg_color="#0078FB").pack(
            fill="x", padx=30, pady=(12, 5)
        )

        # --- Grade de Cards ---
        grid_box = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        grid_box.pack(expand=True, fill="both", padx=20, pady=(5, 5))

        for i in range(3):
            grid_box.grid_columnconfigure(i, weight=1, uniform="card")
        num_rows = (len(CATEGORIAS) + 2) // 3
        for i in range(num_rows):
            grid_box.grid_rowconfigure(i, weight=1, uniform="card")

        for idx, cat in enumerate(CATEGORIAS):
            self._criar_card(grid_box, idx // 3, idx % 3, cat)

        # --- Footer ---
        ctk.CTkLabel(
            self.dashboard_frame, text="Lynch Boost v1.0",
            font=ctk.CTkFont(size=10), text_color="#444444"
        ).pack(side="bottom", pady=(0, 8))

    def _criar_card(self, parent, row, col, cat_info):
        key = cat_info["key"]
        tema = TEMAS_CATEGORIAS.get(key, {"fg": "#1A1A2E", "border": "#2A2A3E", "hover_fg": "#22223A", "hover_border": "#0078FB"})

        card = ctk.CTkFrame(
            parent, corner_radius=15, fg_color=tema["fg"],
            border_width=2, border_color=tema["border"], cursor="hand2"
        )
        card.grid(row=row, column=col, padx=12, pady=7, sticky="nsew")
        card._completed = False

        # Layout interno do card
        card.grid_rowconfigure(0, weight=2)
        card.grid_rowconfigure(1, weight=0)
        card.grid_rowconfigure(2, weight=0)
        card.grid_rowconfigure(3, weight=1)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text=cat_info["emoji"],
            font=ctk.CTkFont(family="Segoe UI Emoji", size=36),
            height=0,
            cursor="hand2"
        ).grid(row=0, column=0, sticky="s", pady=(8, 2))

        ctk.CTkLabel(
            card, text=cat_info["titulo"],
            font=ctk.CTkFont(size=15, weight="bold"), text_color="white",
            height=20,
            cursor="hand2"
        ).grid(row=1, column=0, pady=(2, 0))

        ctk.CTkLabel(
            card, text=cat_info["subtitulo"],
            font=ctk.CTkFont(size=10), text_color="#888888",
            height=14,
            cursor="hand2"
        ).grid(row=2, column=0, pady=(2, 0))

        # Indicador de progresso ou label utilitária
        total = self.card_status.get(key, {}).get("total", 0)

        if total > 0:
            lbl_prog = ctk.CTkLabel(
                card, text=f"0/{total} ✔", font=ctk.CTkFont(size=10),
                text_color="#555555", height=14, cursor="hand2"
            )
            lbl_prog.grid(row=3, column=0, sticky="s", pady=(0, 6))
            self.card_progress_labels[key] = lbl_prog
        else:
            txt_footer = "Diagnóstico" if key == "benchmark_info" else "Utilitários"
            ctk.CTkLabel(
                card, text=txt_footer, font=ctk.CTkFont(size=10),
                text_color="#555555", height=14, cursor="hand2"
            ).grid(row=3, column=0, sticky="s", pady=(0, 6))

        self.card_widgets[key] = card

        # --- Hover Effect (seguro para widgets filhos) ---
        def update_hover():
            if getattr(card, "_completed", False):
                return
            try:
                x = card.winfo_pointerx() - card.winfo_rootx()
                y = card.winfo_pointery() - card.winfo_rooty()
                if 0 <= x <= card.winfo_width() and 0 <= y <= card.winfo_height():
                    card.configure(border_color=tema["hover_border"], fg_color=tema["hover_fg"])
                else:
                    card.configure(border_color=tema["border"], fg_color=tema["fg"])
            except Exception:
                pass

        def on_enter(e):
            update_hover()

        def on_leave(e):
            card.after(20, update_hover)

        def on_click(e, k=key):
            self.abrir_categoria(k)

        for w in [card] + list(card.winfo_children()):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

    # ============================================================
    # TELAS DE DETALHE (uma por categoria)
    # ============================================================
    def _criar_telas_detalhe(self):
        for cat in CATEGORIAS:
            key = cat["key"]
            frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)

            # --- Header com botão Voltar ---
            header = ctk.CTkFrame(frame, fg_color="transparent")
            header.pack(fill="x", padx=20, pady=(12, 0))

            ctk.CTkButton(
                header, text="← Voltar", width=100, height=32,
                fg_color="#333333", hover_color="#555555",
                font=ctk.CTkFont(size=13, weight="bold"),
                command=self.voltar_ao_menu
            ).pack(side="left")

            ctk.CTkLabel(
                header, text=f"{cat['emoji']}  {cat['titulo']}",
                font=ctk.CTkFont(size=22, weight="bold"), text_color="white"
            ).pack(side="left", padx=(15, 0))

            if key == "config_windows":
                # Botão para Reiniciar o PC
                btn_reboot = ctk.CTkButton(
                    header, text="🔄 Reiniciar PC", width=110, height=32,
                    fg_color="#A30000", hover_color="#D10000",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    command=self.confirmar_reiniciar_pc
                )
                btn_reboot.pack(side="right", padx=(5, 0))

                # Botão para Reiniciar o Explorer
                btn_explorer = ctk.CTkButton(
                    header, text="📂 Reiniciar Explorer", width=140, height=32,
                    fg_color="#3A3D52", hover_color="#4D516B",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    command=self.confirmar_reiniciar_explorer
                )
                btn_explorer.pack(side="right", padx=5)

                # Botão explicativo LEIA-ME
                btn_leiame = ctk.CTkButton(
                    header, text="⚠️ LEIA-ME!", width=100, height=32,
                    fg_color="#E3B505", hover_color="#C29B04", text_color="black",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    command=self.abrir_leiame_windows
                )
                btn_leiame.pack(side="right", padx=5)

            # --- Separador ---
            ctk.CTkFrame(frame, height=1, fg_color="#333333").pack(
                fill="x", padx=20, pady=(10, 5)
            )

            # --- Conteúdo scrollável (ou frame normal para especificações) ---
            if key == "benchmark_info":
                content = ctk.CTkFrame(frame, fg_color="transparent")
                content.pack(fill="both", expand=True, padx=20, pady=(5, 5))
                self._preparar_tela_hardware(content)
            else:
                content = ctk.CTkScrollableFrame(frame, fg_color="transparent")
                content.pack(fill="both", expand=True, padx=20, pady=(5, 5))
                if key == "instalacao":
                    from ui.menu_instalacao import MenuInstalacao
                    self.menu_instalacao = MenuInstalacao(content, log_callback=self.log_mensagem)
                    self.menu_instalacao.pack(fill="both", expand=True)
                else:
                    self._popular_detalhe(content, cat)
            self.detail_frames[key] = frame

    def _popular_detalhe(self, content, cat_info):
        """Popula a aba de detalhe com scripts agrupados no design premium."""
        key = cat_info["key"]

        # Mapa de scripts por nome → (dados_script, item_id)
        scripts_por_nome = {}
        if key in self.dados_config:
            for idx, script in enumerate(self.dados_config[key]):
                item_id = f"{key}_{idx}"
                scripts_por_nome[script["nome"]] = (script, item_id)

        # Botões fixos que não vêm do config.json
        fixed_buttons = {}
        if key == "debloat_servicos":
            fixed_buttons["Microsoft Edge"] = {"nome": "Microsoft Edge", "_fixed": "edge"}

        grupos = GRUPOS_DETALHE.get(key, [])
        scripts_colocados = set()

        for grupo in grupos:
            items_do_grupo = []

            for nome in grupo.get("scripts", []):
                if nome in scripts_por_nome:
                    items_do_grupo.append(("script", nome, scripts_por_nome[nome]))
                    scripts_colocados.add(nome)
                elif nome in fixed_buttons:
                    items_do_grupo.append(("fixed", nome, (fixed_buttons[nome], f"{key}_edge")))
                    scripts_colocados.add(nome)

            for atalho_def in grupo.get("atalhos", []):
                items_do_grupo.append(("atalho", atalho_def.get("texto", ""), atalho_def))

            if items_do_grupo:
                self._criar_grupo_scripts(content, grupo, key, items_do_grupo)

        # Scripts NÃO colocados em nenhum grupo → grupo "Outros"
        # Garante espaço automático para scripts futuros adicionados ao config.json
        nao_colocados = []
        for nome, dados in scripts_por_nome.items():
            if nome not in scripts_colocados:
                nao_colocados.append(("script", nome, dados))
        for nome, fixed_data in fixed_buttons.items():
            if nome not in scripts_colocados:
                nao_colocados.append(("fixed", nome, (fixed_data, f"{key}_edge")))

        if nao_colocados:
            grupo_outros = {"titulo": "Outros", "emoji": "⚙️"}
            self._criar_grupo_scripts(content, grupo_outros, key, nao_colocados)

    def _criar_grupo_scripts(self, parent, grupo_info, categoria, items):
        """Cria um card de grupo de scripts com itens de texto clicáveis."""
        tema = TEMAS_CATEGORIAS.get(categoria, {})
        accent = tema.get("hover_border", "#a855f7")

        # Card do grupo — fundo levemente escuro, sem azul forte
        group_card = ctk.CTkFrame(
            parent, fg_color="#1E2029",
            border_color="#3d4153", border_width=1,
            corner_radius=10
        )
        group_card.pack(fill="x", pady=(0, 10))

        # Cabeçalho do grupo
        _hdr = ctk.CTkFrame(group_card, fg_color="transparent")
        _hdr.pack(fill="x", padx=16, pady=(12, 8))

        ctk.CTkLabel(
            _hdr,
            text=f"{grupo_info.get('emoji', '⚙️')}  {grupo_info['titulo']}",
            font=("Segoe UI", 13, "bold"),
            text_color="#ffffff", anchor="w"
        ).pack(side="left")

        # Linha colorida com a cor accent da aba (em vez do divisor cinza)
        ctk.CTkFrame(group_card, height=1, fg_color=accent).pack(fill="x", padx=16, pady=(0, 4))

        # Container de itens
        items_outer = ctk.CTkFrame(group_card, fg_color="transparent")
        items_outer.pack(fill="x", padx=6, pady=(2, 10))

        # Sempre usa layout em grade de 2 colunas para manter tamanhos consistentes
        items_outer.grid_columnconfigure(0, weight=1, uniform="gcol")
        items_outer.grid_columnconfigure(1, weight=1, uniform="gcol")
        row_g, col_g = 0, 0

        for tipo, nome, dados in items:
            if tipo in ("script", "fixed"):
                script_data, item_id = dados
                widget = self._criar_item_script(items_outer, script_data, categoria, item_id)
            else:
                widget = self._criar_item_atalho(items_outer, dados, categoria)

            widget.grid(row=row_g, column=col_g, sticky="ew", padx=4, pady=3)
            col_g += 1
            if col_g >= 2:
                col_g = 0
                row_g += 1

        # Se o número de itens for ímpar, adiciona um frame invisível/dummy na coluna vazia
        # para garantir que as duas colunas tenham o mesmo tamanho (50% da largura).
        if len(items) % 2 != 0:
            dummy = ctk.CTkFrame(items_outer, fg_color="transparent", height=1, border_width=0)
            dummy.grid(row=row_g, column=col_g, sticky="ew", padx=4, pady=3)

    def _criar_item_script(self, parent, script_data, categoria, item_id):
        """Cria um item de script como botão arredondado com indicador de status ✅."""
        fonte_padrao = "Segoe UI"
        row = ctk.CTkFrame(
            parent,
            fg_color="#343746",
            border_color="#3a3d52",
            border_width=1,
            corner_radius=6,
            cursor="hand2"
        )

        # Indicador de status — ⏳ (ampulheta/esperando) antes, ✅ após execução
        status_lbl = ctk.CTkLabel(
            row, text="⏳", width=28,
            font=("Segoe UI Emoji", 14),
            text_color="#0078FB"
        )
        status_lbl.pack(side="left", padx=(8, 0), pady=6)

        # Nome do script (texto clicável) — fonte SF branca
        text_lbl = ctk.CTkLabel(
            row,
            text=script_data["nome"],
            font=(fonte_padrao, 13),
            text_color="#e8e8f0",
            anchor="w", cursor="hand2"
        )
        text_lbl.pack(side="left", fill="x", expand=True, padx=(6, 10), pady=6)

        # Registrar indicador, text label e row frame para atualização futura via marcar_completado
        self.item_status_labels[item_id] = status_lbl
        self.item_text_labels[item_id] = text_lbl
        self.item_row_frames[item_id] = row

        # Efeitos de hover
        def on_enter(e):
            if status_lbl.cget("text") == "✅":
                row.configure(fg_color="#234a31", border_color="#22c55e")
            else:
                row.configure(fg_color="#44475a", border_color="#3a3d52")
            text_lbl.configure(font=(fonte_padrao, 13, "bold"), text_color="#ffffff")

        def on_leave(e):
            # Se já estiver concluído, mantém o fundo forest green e a borda verde
            if status_lbl.cget("text") == "✅":
                row.configure(fg_color="#1b3a24", border_color="#22c55e")
                text_lbl.configure(font=(fonte_padrao, 13, "bold"), text_color="#ffffff")
            else:
                row.configure(fg_color="#343746", border_color="#3a3d52")
                text_lbl.configure(font=(fonte_padrao, 13), text_color="#e8e8f0")

        # Clique — usa _NullBtn para compatibilidade com modais que chamam btn.configure()
        _nb = _NullBtn()

        def on_click(e, sd=script_data, cat=categoria, iid=item_id, nb=_nb):
            self.limpar_console_silencioso()
            if sd.get("_fixed") == "edge":
                self.abrir_menu_edge(nb, cat, iid)
            else:
                self._executar_acao(sd, nb, cat, iid)

        for w in (row, text_lbl, status_lbl):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

        return row

    def _criar_item_atalho(self, parent, atalho_info, categoria):
        """Cria um item de atalho nativo como chip/botão estilizado com badge 'ATALHO'."""
        ATALHO_CMDS = {
            "abrir_programas_recursos": lambda: atalhos.abrir_programas_recursos(self.log_mensagem),
            "abrir_limpeza_disco":      lambda: atalhos.abrir_limpeza_disco(self.log_mensagem),
            "abrir_armazenamento":      lambda: atalhos.abrir_armazenamento(self.log_mensagem),
            "abrir_desfragmentador":    lambda: atalhos.abrir_desfragmentador(self.log_mensagem),
            "abrir_inicializacao":      lambda: atalhos.abrir_inicializacao(self.log_mensagem),
            "abrir_energia":            lambda: atalhos.abrir_energia(self.log_mensagem),
            "abrir_uac":                lambda: atalhos.abrir_uac(self.log_mensagem),
        }

        tema = TEMAS_CATEGORIAS.get(categoria, {})
        accent = tema.get("hover_border", "#6366f1")
        fonte_padrao = "Segoe UI"

        # Container da linha como botão
        row = ctk.CTkFrame(
            parent,
            fg_color="#343746",
            border_color="#3a3d52",
            border_width=1,
            corner_radius=6,
            cursor="hand2"
        )

        # Badge "ATALHO" — chip com borda colorida (accent da aba)
        badge = ctk.CTkFrame(
            row,
            fg_color="transparent",
            border_color=accent,
            border_width=1,
            corner_radius=4
        )
        badge.pack(side="left", padx=(10, 8), pady=7)

        badge_lbl = ctk.CTkLabel(
            badge, text="ATALHO",
            font=("Segoe UI", 8, "bold"),
            text_color=accent
        )
        badge_lbl.pack(padx=5, pady=1)

        # Texto do atalho
        text_lbl = ctk.CTkLabel(
            row,
            text=atalho_info.get("texto", ""),
            font=(fonte_padrao, 13),
            text_color="#7878a0",
            anchor="w", cursor="hand2"
        )
        text_lbl.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=7)

        cmd_key = atalho_info.get("cmd", "")
        cmd_fn = ATALHO_CMDS.get(cmd_key, lambda: None)

        def on_enter(e):
            row.configure(fg_color="#44475a")
            badge.configure(fg_color=accent)
            badge_lbl.configure(text_color="#ffffff")
            text_lbl.configure(font=(fonte_padrao, 13, "bold"), text_color="#ffffff")

        def on_leave(e):
            row.configure(fg_color="#343746")
            badge.configure(fg_color="transparent")
            badge_lbl.configure(text_color=accent)
            text_lbl.configure(font=(fonte_padrao, 13), text_color="#7878a0")

        def on_click(e, fn=cmd_fn):
            self.limpar_console_silencioso()
            fn()

        for w in (row, text_lbl, badge, badge_lbl):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

        return row


    # ============================================================
    # INICIALIZAÇÃO DE STATUS
    # ============================================================
    def _inicializar_status(self):
        for cat in CATEGORIAS:
            key = cat["key"]
            if key in ("instalacao", "benchmark_info"):
                total = 0
            else:
                total = len(self.dados_config.get(key, []))
            # Botões fixos rastreáveis
            if key == "debloat_servicos":
                total += 1  # Edge
            self.card_status[key] = {"total": total, "completados": set()}

    # ============================================================
    # SISTEMA DE ESTADO DOS CARDS
    # ============================================================
    def marcar_completado(self, categoria, item_id, btn_instance):
        """Registra conclusão: exibe ✅ no indicador de status (design premium) ou pinta botão (legado)."""
        # Novo design premium: atualizar indicador de status visual
        status_lbl = self.item_status_labels.get(item_id)
        if status_lbl:
            try:
                status_lbl.configure(text="✅", text_color="#22c55e")
            except Exception:
                pass
            
            # Mantém o texto em negrito fixo e branco
            text_lbl = getattr(self, "item_text_labels", {}).get(item_id)
            if text_lbl:
                try:
                    text_lbl.configure(font=("Segoe UI", 13, "bold"), text_color="#ffffff")
                except Exception:
                    pass

            # Mantém a caixinha com a cor forest green (#1b3a24) e borda verde (#22c55e)
            row_frame = getattr(self, "item_row_frames", {}).get(item_id)
            if row_frame:
                try:
                    row_frame.configure(fg_color="#1b3a24", border_color="#22c55e")
                except Exception:
                    pass
        else:
            # Fallback legado (CTkButton antigo)
            try:
                btn_instance.configure(fg_color="#4CAF50", hover_color="#388E3C")
            except Exception:
                pass

        status = self.card_status.get(categoria)
        if not status:
            return

        status["completados"].add(item_id)
        completados = len(status["completados"])
        total = status["total"]

        # Atualizar label de progresso no card do dashboard
        if categoria in self.card_progress_labels:
            self.card_progress_labels[categoria].configure(
                text=f"{completados}/{total} ✔",
                text_color="#4CAF50" if completados > 0 else "#555555"
            )

        # Todos completados → pintar card de verde no dashboard
        if completados >= total > 0:
            card = self.card_widgets.get(categoria)
            if card:
                card._completed = True
                card.configure(fg_color="#1E2029", border_color="#22C55E")

    def desmarcar_completado(self, categoria, item_id, btn_instance):
        """Remove conclusão: limpa indicador de status (design premium) ou restaura botão (legado)."""
        # Novo design premium: limpar indicador de status visual
        status_lbl = self.item_status_labels.get(item_id)
        if status_lbl:
            try:
                status_lbl.configure(text="⏳", text_color="#0078FB")
            except Exception:
                pass
            
            # Restaura o estilo de fonte normal
            text_lbl = getattr(self, "item_text_labels", {}).get(item_id)
            if text_lbl:
                try:
                    text_lbl.configure(font=("Segoe UI", 13), text_color="#e8e8f0")
                except Exception:
                    pass

            # Restaura o fundo padrão do botão (#343746) e a borda padrão (#3a3d52)
            row_frame = getattr(self, "item_row_frames", {}).get(item_id)
            if row_frame:
                try:
                    row_frame.configure(fg_color="#343746", border_color="#3a3d52")
                except Exception:
                    pass
        else:
            # Fallback legado
            try:
                btn_instance.configure(fg_color="#D32F2F", hover_color="#B71C1C")
            except Exception:
                pass

        status = self.card_status.get(categoria)
        if not status:
            return

        if item_id in status["completados"]:
            status["completados"].remove(item_id)
        completados = len(status["completados"])
        total = status["total"]

        # Atualizar label de progresso no card do dashboard
        if categoria in self.card_progress_labels:
            self.card_progress_labels[categoria].configure(
                text=f"{completados}/{total} ✔" if completados > 0 else f"0/{total}",
                text_color="#4CAF50" if completados > 0 else "#555555"
            )

        # Restaurar cor padrão do card se não estiver mais 100%
        if completados < total:
            card = self.card_widgets.get(categoria)
            if card:
                card._completed = False
                tema = TEMAS_CATEGORIAS.get(categoria, {"fg": "#1E2029", "border": "#3d4153"})
                card.configure(fg_color=tema["fg"], border_color=tema["border"])

    # ============================================================
    # EXECUÇÃO DE AÇÕES (scripts e modais)
    # ============================================================

    def _executar_acao(self, dados_script, btn_instance, categoria, item_id):
        """Roteador central: decide se abre modal, executa script direto ou com confirmação."""
        especial = dados_script.get("acao_especial")

        if especial in ACOES_SCRIPT:
            self._executar_acao_script_registrada(especial, dados_script, btn_instance, categoria, item_id)
            return

        # Ações especiais que abrem modais
        if especial == "abrir_menu_dns":
            self.abrir_menu_dns(btn_instance, categoria, item_id)
            return
        if especial == "abrir_menu_instalacao":
            self.abrir_menu_instalacao(btn_instance, categoria, item_id)
            return
        if especial == "abrir_menu_desinstalar_apps_windows":
            self.abrir_menu_desinstalar_apps_windows(btn_instance, categoria, item_id)
            return
        if especial == "abrir_menu_otimizacao":
            self.abrir_menu_otimizacao(btn_instance, categoria, item_id)
            return
        if especial == "abrir_menu_mouse":
            self.abrir_menu_mouse(btn_instance, categoria, item_id)
            return
        if especial == "abrir_menu_audio":
            self.abrir_menu_audio(btn_instance, categoria, item_id)
            return
        if especial == "abrir_menu_personalizacao":
            self.abrir_menu_personalizacao(btn_instance, categoria, item_id)
            return
        if especial == "abrir_menu_energia":
            self.abrir_menu_energia(btn_instance, categoria, item_id)
            return
        if especial == "abrir_menu_desempenho":
            self.abrir_menu_desempenho(btn_instance, categoria, item_id)
            return
        if especial == "abrir_mouse":
            atalhos.abrir_mouse(self.log_mensagem)
            return

        if especial == "abrir_modal_menu_contexto":
            modais.abrir_modal_menu_contexto(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_sticky_keys":
            modais.abrir_modal_sticky_keys(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_repeticao_teclado":
            modais.abrir_modal_repeticao_teclado(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_forcar_abnt2":
            modais.abrir_modal_forcar_abnt2(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_teclado_eua":
            modais.abrir_modal_teclado_eua(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_explorer_this_pc":
            modais.abrir_modal_explorer_this_pc(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_show_extensions":
            modais.abrir_modal_show_extensions(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_home_galeria":
            modais.abrir_modal_home_galeria(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_wsl_icon":
            modais.abrir_modal_wsl_icon(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_fast_startup":
            modais.abrir_modal_fast_startup(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_finalizar_tarefa":
            modais.abrir_modal_finalizar_tarefa(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_desativar_sincronizacao":
            modais.abrir_modal_desativar_sincronizacao(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_desativar_experimentos":
            modais.abrir_modal_desativar_experimentos(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_ativar_game_mode":
            modais.abrir_modal_ativar_game_mode(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_desativar_popups":
            modais.abrir_modal_desativar_popups(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_desativar_activity_feed":
            modais.abrir_modal_desativar_activity_feed(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_desativar_game_dvr":
            modais.abrir_modal_desativar_game_dvr(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_energia_amd":
            modais.abrir_modal_energia_amd(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_energia_intel":
            modais.abrir_modal_energia_intel(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_timer_coalescing":
            modais.abrir_modal_timer_coalescing(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_latencia_disco":
            modais.abrir_modal_latencia_disco(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_limpar_cache_ram":
            modais.abrir_modal_limpar_cache_ram(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_otimizar_memoria":
            modais.abrir_modal_otimizar_memoria(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_latencia_usb":
            modais.abrir_modal_latencia_usb(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_limpar_dispositivos":
            modais.abrir_modal_limpar_dispositivos(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_limpar_lixeira":
            modais.abrir_modal_limpar_lixeira(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_otimizar_gpu":
            modais.abrir_modal_otimizar_gpu(self, btn_instance, categoria, item_id)
            return

        if especial == "abrir_modal_seguranca_avancada":
            modais.abrir_modal_seguranca_avancada(self, btn_instance, categoria, item_id)
            return

        self.log_mensagem(f"[ERRO] Acao especial nao registrada: {especial}", tipo="red")

    def _executar_acao_script_registrada(self, especial, dados_script, btn_instance, categoria, item_id):
        acao = ACOES_SCRIPT[especial]
        nome = acao.get("nome", dados_script.get("nome", especial))
        arquivo = acao["arquivo"]

        def executar_script():
            self.log_mensagem(f"Executando via Hub: {nome}")

            def run_thread():
                sucesso = runner.executar_arquivo(arquivo, self.log_mensagem)
                self.log_mensagem(f"Executou {nome}. Sucesso: {sucesso}. Categoria: {categoria}, ItemID: {item_id}")
                if sucesso:
                    self.after(0, lambda: self.marcar_completado(categoria, item_id, btn_instance))

            threading.Thread(target=run_thread, daemon=True).start()

        if acao.get("destrutivo") or risco_exige_confirmacao(acao["risco"]):
            titulo = acao.get("modal_titulo", "Aviso: Ação Destrutiva")
            mensagem = acao.get("modal_mensagem", "Deseja executar esta ação?")

            def comando_cancelado():
                self.log_mensagem("Operação cancelada pelo usuário.")

            modais.abrir_modal_confirmacao(self, titulo, mensagem, executar_script, comando_cancelado, categoria=categoria)
            return

        executar_script()

    
    def _abrir_modal_com_callback(self, modal_class, btn_instance, categoria, item_id):
        """Abre um modal e intercepta o fechamento para registrar conclusão no card."""
        modal = modal_class(self, parent_btn=btn_instance)
        modal.grab_set()

        # Configurar ícone para consistência visual na barra de tarefas e título
        try:
            if hasattr(self, 'icon_path') and os.path.exists(self.icon_path):
                modal.iconbitmap(self.icon_path)
        except Exception:
            pass

        if categoria and item_id:
            _original = modal.fechar_modal

            def _wrapped():
                modificou = modal.modificou_algo
                _original()  # Pinta botão verde + destroy
                if modificou:
                    self.marcar_completado(categoria, item_id, btn_instance)

            modal.fechar_modal = _wrapped
            modal.protocol("WM_DELETE_WINDOW", _wrapped)
            # Atualizar o botão "Fechar Janela" do modal também
            if hasattr(modal, "btn_fechar"):
                modal.btn_fechar.configure(command=_wrapped)

    def abrir_menu_edge(self, parent_btn=None, categoria=None, item_id=None):
        self.log_mensagem("Iniciando interface do Gerenciador do Edge...")
        from ui.menu_edge import MenuEdge
        self._abrir_modal_com_callback(MenuEdge, parent_btn, categoria, item_id)

    def abrir_menu_dns(self, parent_btn=None, categoria=None, item_id=None):
        self.log_mensagem("Iniciando interface de Otimização de DNS...")
        from ui.menu_dns import MenuDNS
        self._abrir_modal_com_callback(MenuDNS, parent_btn, categoria, item_id)

    def abrir_menu_instalacao(self, parent_btn=None, categoria=None, item_id=None):
        self.log_mensagem("Abrindo interface do Instalador de Programas...")
        self.abrir_categoria("instalacao")

    def abrir_menu_desinstalar_apps_windows(self, parent_btn=None, categoria=None, item_id=None):
        self.log_mensagem("Abrindo interface do Desinstalador de Apps do Windows...")
        self._esconder_tudo()
        if not hasattr(self, "desinstalar_apps_windows_frame"):
            from ui.menu_desinstalar_apps_windows import MenuDesinstalarAppsWindows
            self.desinstalar_apps_windows_frame = MenuDesinstalarAppsWindows(
                self,
                log_callback=self.log_mensagem,
                back_callback=lambda: self.abrir_categoria("debloat_servicos"),
            )
            self.desinstalar_apps_windows_frame.grid(row=0, column=0, sticky="nsew")
        else:
            self.desinstalar_apps_windows_frame.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=8)
        self.grid_rowconfigure(1, weight=1)
        self.console_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

    def abrir_menu_otimizacao(self, parent_btn=None, categoria=None, item_id=None):
        self.log_mensagem("Iniciando interface de Otimização de Registro...")
        from ui.menu_otimizacao import MenuOtimizacaoReg
        self._abrir_modal_com_callback(MenuOtimizacaoReg, parent_btn, categoria, item_id)

    def abrir_menu_mouse(self, parent_btn=None, categoria=None, item_id=None):
        self.log_mensagem("Iniciando interface de Otimização do Mouse...")
        from ui.menu_mouse import MenuOtimizacaoMouse
        self._abrir_modal_com_callback(MenuOtimizacaoMouse, parent_btn, categoria, item_id)

    def abrir_menu_personalizacao(self, parent_btn=None, categoria=None, item_id=None):
        self.log_mensagem("Iniciando interface de Personalização...")
        self._esconder_tudo()
        if not hasattr(self, "personalizacao_frame"):
            from ui.menu_personalizacao import PersonalizacaoFrame
            self.personalizacao_frame = PersonalizacaoFrame(self, parent_btn, categoria, item_id)
            self.personalizacao_frame.grid(row=0, column=0, sticky="nsew")
        else:
            self.personalizacao_frame.carregar_configuracoes_atuais()
            self.personalizacao_frame.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

    def abrir_menu_audio(self, parent_btn=None, categoria=None, item_id=None):
        self.log_mensagem("Iniciando interface do Gerenciador de Áudio...")
        self._esconder_tudo()
        if not hasattr(self, "audio_frame"):
            from ui.menu_audio import AudioDeviceManagerFrame
            self.audio_frame = AudioDeviceManagerFrame(self, parent_btn, categoria, item_id)
            self.audio_frame.grid(row=0, column=0, sticky="nsew")
        else:
            self.audio_frame.atualizar_dispositivos()
            self.audio_frame.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=8)
        self.grid_rowconfigure(1, weight=1)
        self.console_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

    def abrir_menu_energia(self, parent_btn=None, categoria=None, item_id=None):
        self.log_mensagem("Iniciando interface de Planos de Energia...")
        from ui.menu_energia import MenuEnergia
        self._abrir_modal_com_callback(MenuEnergia, parent_btn, categoria, item_id)

    def abrir_menu_desempenho(self, parent_btn=None, categoria=None, item_id=None):
        self.log_mensagem("Iniciando interface de Efeitos Visuais...")
        from ui.menu_desempenho import MenuDesempenho
        self._abrir_modal_com_callback(MenuDesempenho, parent_btn, categoria, item_id)

    # ============================================================
    # NAVEGAÇÃO
    # ============================================================
    def mostrar_dashboard(self):
        """Exibe o dashboard de cards (sem console)."""
        self._esconder_tudo()
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")

    def abrir_categoria(self, key):
        """Exibe a tela de detalhe de uma categoria + console (exceto instalador)."""
        self._esconder_tudo()

        detail = self.detail_frames.get(key)
        if detail:
            detail.grid(row=0, column=0, sticky="nsew")

        if key in ("instalacao", "benchmark_info"):
            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=0)
            if key == "benchmark_info":
                self.recarregar_hardware_info()
        else:
            self.grid_rowconfigure(0, weight=8)
            self.grid_rowconfigure(1, weight=1)
            self.console_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

    def confirmar_reiniciar_pc(self):
        """Abre modal de confirmação para reiniciar o computador."""
        def executar():
            self.log_mensagem("Reiniciando o computador...")
            subprocess.run(["shutdown", "/r", "/t", "0"], shell=False)
            
        modais.abrir_modal_confirmacao(
            self, 
            titulo="Reiniciar Computador",
            mensagem="Tem certeza de que deseja reiniciar o computador agora? Certifique-se de salvar todos os seus trabalhos pendentes antes de prosseguir.",
            comando_confirmar=executar,
            categoria="config_windows"
        )

    def confirmar_reiniciar_explorer(self):
        """Abre modal de confirmação para reiniciar o Windows Explorer."""
        def executar():
            self.log_mensagem("Reiniciando o Windows Explorer...")
            subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.Popen(["explorer.exe"], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.log_mensagem("Windows Explorer reiniciado com sucesso.")

        modais.abrir_modal_confirmacao(
            self, 
            titulo="Reiniciar Explorer",
            mensagem="Tem certeza de que deseja reiniciar o Windows Explorer? A barra de tarefas e a área de trabalho sumirão por alguns segundos e depois retornarão.",
            comando_confirmar=executar,
            categoria="config_windows"
        )

    def abrir_leiame_windows(self):
        """Abre o modal explicativo 'LEIA-ME' da aba Windows."""
        modais.abrir_modal_leiame_windows(self)

    def voltar_ao_menu(self):
        """Volta para o dashboard de cards."""
        self.mostrar_dashboard()

    def _esconder_tudo(self):
        """Esconde todos os frames de conteúdo."""
        self.dashboard_frame.grid_forget()
        self.console_frame.grid_forget()
        for f in self.detail_frames.values():
            f.grid_forget()
        if hasattr(self, "audio_frame"):
            self.audio_frame.grid_forget()
        if hasattr(self, "personalizacao_frame"):
            self.personalizacao_frame.grid_forget()
        if hasattr(self, "desinstalar_apps_windows_frame"):
            self.desinstalar_apps_windows_frame.grid_forget()

    # ============================================================
    # LOG E UTILITÁRIOS
    # ============================================================
    def log_mensagem(self, mensagem, tipo="info"):
        """Registra uma mensagem formatada no painel de log premium."""
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")

        m = mensagem.lower()
        if tipo == "red" or "❌" in mensagem or "[erro]" in m or "falha" in m or "not found" in m or "não encontrad" in m:
            icone = "✗"
        elif "✔" in mensagem or "[ok]" in m or "sucesso" in m or "concluíd" in m or "aplicad" in m or "ativad" in m or "restaurad" in m or "inciado" in m:
            icone = "✓"
        elif "iniciando" in m or "executando" in m or "iniciado" in m or "abrindo" in m or "executar" in m:
            icone = "⚡"
        else:
            icone = "›"

        # Remover prefixos de ícone já existentes
        texto = (mensagem
                 .replace("❌ ", "").replace("✔️ ", "")
                 .replace("[OK] ", "").replace("[ERRO] ", "")
                 .replace("⚡ ", ""))

        self.console_box.configure(state="normal")
        self.console_box.insert("end", f"\n[{ts}] {icone}  {texto}")
        self.console_box.see("end")
        self.console_box.configure(state="disabled")

    def limpar_console(self):
        self.console_box.configure(state="normal")
        self.console_box.delete("0.0", "end")
        self.console_box.insert("0.0", "◉  Lynch Boost — Motor Online\n›  Log limpo. Aguardando comandos...")
        self.console_box.configure(state="disabled")

    def limpar_console_silencioso(self):
        self.console_box.configure(state="normal")
        self.console_box.delete("0.0", "end")
        self.console_box.insert("0.0", "◉  Lynch Boost — Motor Online")
        self.console_box.configure(state="disabled")

    # ============================================================
    # TELA DE ESPECIFICAÇÕES (HARDWARE INFO & DIAGNÓSTICO)
    # ============================================================
    def _preparar_tela_hardware(self, content):
        self.hardware_scroll_frame = content
        self.lbl_loading = ctk.CTkLabel(
            content, 
            text="⏳ Analisando componentes de hardware...\nPor favor, aguarde.",
            font=("Segoe UI", 16, "italic"),
            text_color="#a855f7"
        )
        self.lbl_loading.pack(expand=True, pady=150)

    def recarregar_hardware_info(self):
        # Limpar widgets anteriores
        for child in self.hardware_scroll_frame.winfo_children():
            child.pack_forget()
            child.destroy()
            
        self.lbl_loading = ctk.CTkLabel(
            self.hardware_scroll_frame, 
            text="⏳ Buscando especificações do sistema...\nPor favor, aguarde.",
            font=("Segoe UI", 16, "italic"),
            text_color="#a855f7"
        )
        self.lbl_loading.pack(expand=True, pady=150)
        
        def run_info():
            dados = diagnostico.obter_dados_hardware()
            self.after(0, lambda: self._renderizar_hardware_info(dados))
            
        threading.Thread(target=run_info, daemon=True).start()

    def _renderizar_hardware_info(self, dados):
        # Limpar loading
        if hasattr(self, "lbl_loading") and self.lbl_loading:
            try:
                self.lbl_loading.pack_forget()
                self.lbl_loading.destroy()
            except Exception:
                pass
            
        for child in self.hardware_scroll_frame.winfo_children():
            try:
                child.pack_forget()
                child.destroy()
            except Exception:
                pass

        # Estilo de cores - Lynch Art & Design
        card_bg = "#0B0914"       # Roxo profundo quase preto
        card_border = "#2A2147"   # Roxo médio para a borda
        text_accent = "#c084fc"   # Roxo neon pastel para títulos secundários
        highlight_color = "#38bdf8" # Cyan elegante para nomes de hardware

        # Criar CTkTabview moderno para dividir as abas de hardware
        tabview = ctk.CTkTabview(
            self.hardware_scroll_frame,
            fg_color=card_bg,
            segmented_button_fg_color="#18142c",
            segmented_button_selected_color="#a855f7",
            segmented_button_selected_hover_color="#c084fc",
            segmented_button_unselected_color="#0B0914",
            segmented_button_unselected_hover_color="#2A2147",
            text_color="white"
        )
        tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tenta aplicar fonte bold, maior altura e esticar o segmented button por toda a largura
        try:
            tabview._segmented_button.configure(
                font=("Segoe UI", 13, "bold"),
                height=40
            )
            tabview._segmented_button.grid(sticky="ew")
        except Exception:
            pass

        # Adicionar abas
        tab_sistema = tabview.add("Sistema")
        tab_motherboard = tabview.add("Placa Mãe")
        tab_cpu = tabview.add("Processador")
        tab_gpu = tabview.add("Placa de Vídeo")
        tab_ram = tabview.add("Memória RAM")
        tab_armazenamento = tabview.add("Armazenamento")
        tab_ferramentas = tabview.add("Ferramentas")

        def criar_card_tab(parent, emoji, titulo):
            card = ctk.CTkFrame(
                parent,
                fg_color=card_bg,
                border_color=card_border,
                border_width=1.5,
                corner_radius=12
            )
            # Reserva espaço para a scrollbar interna do CTkScrollableFrame (~18px) no lado direito
            # Garante que a borda roxa do card nunca seja cortada pela scrollbar
            right_pad = 28 if isinstance(parent, ctk.CTkScrollableFrame) else 10
            card.pack(fill="x", pady=10, padx=(10, right_pad))

            # Cabeçalho da seção
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=(12, 5))

            icon_lbl = ctk.CTkLabel(header, text=emoji, font=("Segoe UI Emoji", 20))
            icon_lbl.pack(side="left", padx=(0, 10))

            title_lbl = ctk.CTkLabel(header, text=titulo, font=("Segoe UI", 16, "bold"), text_color=text_accent)
            title_lbl.pack(side="left")

            # Linha divisória fina
            divider = ctk.CTkFrame(card, height=1, fg_color="#1d1633")
            divider.pack(fill="x", padx=15, pady=(2, 10))

            return card

        # Função auxiliar para criar linhas de dados nos cartões (Chave esquerda, Valor direita)
        def adicionar_linha_dado_card(parent, chave, valor, val_color="white"):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=4)

            lbl_key = ctk.CTkLabel(row, text=f"• {chave}", font=("Segoe UI", 12, "bold"), text_color="#9ca3af")
            lbl_key.pack(side="left")

            lbl_val = ctk.CTkLabel(row, text=str(valor), font=("Segoe UI", 12), text_color=val_color)
            lbl_val.pack(side="right")
            return lbl_val

        # Função auxiliar para criar linhas de detalhes simples à esquerda (estilo imagem Motherboard)
        def adicionar_linha_detalhe_esquerda(parent, label, value):
            line_text = f"{label}: {value}"
            lbl = ctk.CTkLabel(
                parent, 
                text=line_text, 
                font=("Segoe UI", 12), 
                text_color="white", 
                anchor="w",
                justify="left"
            )
            lbl.pack(fill="x", pady=3)

        # ------------------------------------------------------------
        # 1. ABA SISTEMA
        # ------------------------------------------------------------
        tab_sys_scroll = ctk.CTkScrollableFrame(tab_sistema, fg_color="transparent")
        tab_sys_scroll.pack(fill="both", expand=True, padx=0, pady=10)

        card_sys = criar_card_tab(tab_sys_scroll, "🖥️", "Sistema")

        # Fabricante do SO
        lbl_os_header = ctk.CTkLabel(
            card_sys, 
            text="Microsoft Windows", 
            font=("Segoe UI", 14, "bold"), 
            text_color="#60a5fa", 
            anchor="w"
        )
        lbl_os_header.pack(fill="x", padx=(30, 15), pady=(5, 10))

        # Detalhes do SO
        sys_details_frame = ctk.CTkFrame(card_sys, fg_color="transparent")
        sys_details_frame.pack(fill="x", padx=(50, 15), pady=(0, 15))

        adicionar_linha_detalhe_esquerda(sys_details_frame, "Sistema Operacional", dados["os"]["nome"])
        adicionar_linha_detalhe_esquerda(sys_details_frame, "Arquitetura", dados["os"]["arquitetura"])
        adicionar_linha_detalhe_esquerda(sys_details_frame, "Build do Windows", dados["os"]["build"])
        adicionar_linha_detalhe_esquerda(sys_details_frame, "Versão do DirectX", dados["os"]["directx"])
        adicionar_linha_detalhe_esquerda(sys_details_frame, "Tempo de Atividade", dados["os"]["uptime"])
        adicionar_linha_detalhe_esquerda(sys_details_frame, "Data de Instalação", dados["os"]["install_date"])
        adicionar_linha_detalhe_esquerda(sys_details_frame, "Secure Boot", dados["os"]["secure_boot"])
        adicionar_linha_detalhe_esquerda(sys_details_frame, "Compatibilidade CSM", dados["os"]["csm"])
        adicionar_linha_detalhe_esquerda(sys_details_frame, "Fast Startup (Fast Boot)", dados["os"]["fast_startup"])

        # ------------------------------------------------------------
        # 2. ABA PLACA MÃE (MOTHERBOARD)
        # ------------------------------------------------------------
        tab_mobo_scroll = ctk.CTkScrollableFrame(tab_motherboard, fg_color="transparent")
        tab_mobo_scroll.pack(fill="both", expand=True, padx=0, pady=10)

        card_mobo = criar_card_tab(tab_mobo_scroll, "🎛️", "Motherboard")

        mobo = dados["motherboard"]
        mfg_color = "#3b82f6"  # Cor azul idêntica à da imagem

        # Fabricante da Placa Mãe
        lbl_mobo_mfg = ctk.CTkLabel(
            card_mobo, 
            text=mobo["fabricante"], 
            font=("Segoe UI", 14, "bold"), 
            text_color=mfg_color, 
            anchor="w"
        )
        lbl_mobo_mfg.pack(fill="x", padx=(30, 15), pady=(5, 10))

        # Detalhes da Placa Mãe Indentados
        mobo_details_frame = ctk.CTkFrame(card_mobo, fg_color="transparent")
        mobo_details_frame.pack(fill="x", padx=(50, 15), pady=(0, 20))

        adicionar_linha_detalhe_esquerda(mobo_details_frame, "System", mobo["system"])
        adicionar_linha_detalhe_esquerda(mobo_details_frame, "Chipset", mobo["chipset"])
        adicionar_linha_detalhe_esquerda(mobo_details_frame, "Product", mobo["product"])
        adicionar_linha_detalhe_esquerda(mobo_details_frame, "Model", mobo["model"])
        adicionar_linha_detalhe_esquerda(mobo_details_frame, "Version", mobo["version"])
        adicionar_linha_detalhe_esquerda(mobo_details_frame, "Revision", mobo["revision"])

        # Cabeçalho da BIOS
        lbl_bios = ctk.CTkLabel(
            card_mobo, 
            text="BIOS", 
            font=("Segoe UI", 14, "bold"), 
            text_color=mfg_color, 
            anchor="w"
        )
        lbl_bios.pack(fill="x", padx=(30, 15), pady=(0, 10))

        # Detalhes da BIOS Indentados
        bios_details_frame = ctk.CTkFrame(card_mobo, fg_color="transparent")
        bios_details_frame.pack(fill="x", padx=(50, 15), pady=(0, 15))

        adicionar_linha_detalhe_esquerda(bios_details_frame, "Manufacturer", mobo["bios_manufacturer"])
        adicionar_linha_detalhe_esquerda(bios_details_frame, "Manufacturer", mobo["bios_name"])
        adicionar_linha_detalhe_esquerda(bios_details_frame, "Version", mobo["bios_version"])
        adicionar_linha_detalhe_esquerda(bios_details_frame, "Build Number", mobo["bios_build"])

        # ------------------------------------------------------------
        # 3. ABA PROCESSADOR (CPU)
        # ------------------------------------------------------------
        tab_cpu_scroll = ctk.CTkScrollableFrame(tab_cpu, fg_color="transparent")
        tab_cpu_scroll.pack(fill="both", expand=True, padx=0, pady=10)

        for idx, cpu in enumerate(dados["cpu"]):
            card_cpu = criar_card_tab(tab_cpu_scroll, "⚙️", f"Processador (CPU) #{idx+1}" if len(dados["cpu"]) > 1 else "Processador (CPU)")
            
            # Nome da CPU destacado em fonte maior
            lbl_nome = ctk.CTkLabel(card_cpu, text=cpu["nome"], font=("Segoe UI", 14, "bold"), text_color="#60a5fa", anchor="w")
            lbl_nome.pack(fill="x", padx=20, pady=(0, 6))

            adicionar_linha_dado_card(card_cpu, "Cores Físicos", cpu["cores_fisicos"])
            adicionar_linha_dado_card(card_cpu, "Threads (Processadores Lógicos)", cpu["threads"])
            adicionar_linha_dado_card(card_cpu, "Cache L2", cpu["cache_l2"])
            adicionar_linha_dado_card(card_cpu, "Cache L3", cpu["cache_l3"])
            adicionar_linha_dado_card(card_cpu, "Virtualização Habilitada", cpu["virtualizacao"], val_color="#4CAF50" if cpu["virtualizacao"] == "Sim" else "#f87171")
            adicionar_linha_dado_card(card_cpu, "Prevenção de Execução de Dados (DEP)", cpu.get("dep", "N/A"), val_color="#4CAF50" if cpu.get("dep") == "Sim" else "#f87171")
            adicionar_linha_dado_card(card_cpu, "Stepping", cpu.get("stepping", "N/A"))
            adicionar_linha_dado_card(card_cpu, "Revisão", cpu.get("revision", "N/A"))

        # ------------------------------------------------------------
        # 4. ABA PLACA DE VÍDEO (GPU)
        # ------------------------------------------------------------
        tab_gpu_scroll = ctk.CTkScrollableFrame(tab_gpu, fg_color="transparent")
        tab_gpu_scroll.pack(fill="both", expand=True, padx=0, pady=10)

        if not dados["gpu"]:
            lbl_no_gpu = ctk.CTkLabel(tab_gpu_scroll, text="Nenhuma placa de vídeo dedicada detectada.", font=("Segoe UI", 12, "italic"), text_color="gray", anchor="w")
            lbl_no_gpu.pack(fill="x", padx=20, pady=5)
        else:
            for idx, gpu in enumerate(dados["gpu"]):
                card_gpu = criar_card_tab(tab_gpu_scroll, "🎮", f"Placa de Vídeo (GPU) #{idx+1}" if len(dados["gpu"]) > 1 else "Placa de Vídeo (GPU)")
                
                # Identifica fabricante
                gpu_nome = gpu["nome"].upper()
                gpu_color = "#2ecc71" if "NVIDIA" in gpu_nome else "#f87171" if "AMD" in gpu_nome or "RADEON" in gpu_nome else "#60a5fa"
                
                lbl_nome = ctk.CTkLabel(card_gpu, text=gpu["nome"], font=("Segoe UI", 14, "bold"), text_color=gpu_color, anchor="w")
                lbl_nome.pack(fill="x", padx=20, pady=(0, 6))

                adicionar_linha_dado_card(card_gpu, "Video Memory", gpu.get("vram", "N/A"))
                adicionar_linha_dado_card(card_gpu, "Video Memory Type", gpu.get("vram_type", "Unknown"))
                adicionar_linha_dado_card(card_gpu, "DAC Type", gpu.get("dac_type", "Desconhecido"))
                adicionar_linha_dado_card(card_gpu, "Current Resolution", gpu.get("resolucao", "N/A"))
                adicionar_linha_dado_card(card_gpu, "Current Refresh Rate", gpu.get("taxa_atualizacao", "N/A"))

        # ------------------------------------------------------------
        # 5. ABA MEMÓRIA RAM
        # ------------------------------------------------------------
        tab_ram_scroll = ctk.CTkScrollableFrame(tab_ram, fg_color="transparent")
        tab_ram_scroll.pack(fill="both", expand=True, padx=0, pady=10)

        card_ram = criar_card_tab(tab_ram_scroll, "📟", "Módulos de Memória RAM Físicos")
        if not dados["ram_slots"]:
            lbl_no_ram = ctk.CTkLabel(card_ram, text="Nenhuma informação de slots de memória disponível via WMI.", font=("Segoe UI", 12, "italic"), text_color="gray", anchor="w")
            lbl_no_ram.pack(fill="x", padx=20, pady=5)
        else:
            # Container horizontal para módulos de memória (organizados em cards menores lado a lado)
            slots_container = ctk.CTkFrame(card_ram, fg_color="transparent")
            slots_container.pack(fill="x", padx=15, pady=(0, 10))
            
            # Configura colunas dinâmicas para organizar os pentes
            num_slots = len(dados["ram_slots"])
            cols_count = min(num_slots, 2)
            for c in range(cols_count):
                slots_container.grid_columnconfigure(c, weight=1, uniform="slot")
                
            for idx, slot in enumerate(dados["ram_slots"]):
                row = idx // cols_count
                col = idx % cols_count
                
                m_card = ctk.CTkFrame(
                    slots_container,
                    fg_color="#141029",
                    border_color="#2b2054",
                    border_width=1,
                    corner_radius=8
                )
                m_card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                
                lbl_slot_title = ctk.CTkLabel(m_card, text=f"📍 {slot['canal']}", font=("Segoe UI", 12, "bold"), text_color=text_accent, anchor="w")
                lbl_slot_title.pack(fill="x", padx=10, pady=(8, 2))
                
                ctk.CTkFrame(m_card, height=1, fg_color="#221942").pack(fill="x", padx=10, pady=2)
                
                def add_mini_linha(m_parent, ch, vl):
                    m_row = ctk.CTkFrame(m_parent, fg_color="transparent")
                    m_row.pack(fill="x", padx=10, pady=2)
                    ctk.CTkLabel(m_row, text=ch, font=("Segoe UI", 11), text_color="#9ca3af").pack(side="left")
                    ctk.CTkLabel(m_row, text=vl, font=("Segoe UI", 11, "bold"), text_color="white").pack(side="right")
                
                add_mini_linha(m_card, "Tamanho:", slot["tamanho"])
                add_mini_linha(m_card, "Velocidade:", slot["velocidade"])
                add_mini_linha(m_card, "Fabricante:", slot["fabricante"])
                add_mini_linha(m_card, "Form Factor:", slot["form_factor"])

        # ------------------------------------------------------------
        # 6. ABA ARMAZENAMENTO (DISCOS)
        # ------------------------------------------------------------
        tab_storage_scroll = ctk.CTkScrollableFrame(tab_armazenamento, fg_color="transparent")
        tab_storage_scroll.pack(fill="both", expand=True, padx=0, pady=10)

        if not dados.get("disks"):
            lbl_no_disks = ctk.CTkLabel(tab_storage_scroll, text="Nenhum dispositivo de armazenamento detectado.", font=("Segoe UI", 12, "italic"), text_color="gray", anchor="w")
            lbl_no_disks.pack(fill="x", padx=20, pady=5)
        else:
            for idx, disk in enumerate(dados["disks"]):
                card_disk = criar_card_tab(tab_storage_scroll, "💾", f"Disco de Armazenamento #{idx+1}" if len(dados["disks"]) > 1 else "Disco de Armazenamento")
                
                # Nome/Modelo do disco destacado
                lbl_model = ctk.CTkLabel(
                    card_disk,
                    text=disk["model"],
                    font=("Segoe UI", 14, "bold"),
                    text_color="#3b82f6", # Cor azul idêntica à da imagem da placa mãe
                    anchor="w"
                )
                lbl_model.pack(fill="x", padx=(30, 15), pady=(5, 10))

                # Detalhes do Disco
                disk_details_frame = ctk.CTkFrame(card_disk, fg_color="transparent")
                disk_details_frame.pack(fill="x", padx=(50, 15), pady=(0, 15))

                adicionar_linha_detalhe_esquerda(disk_details_frame, "Size", disk["size"])
                adicionar_linha_detalhe_esquerda(disk_details_frame, "Disk Type", disk["disk_type"])
                adicionar_linha_detalhe_esquerda(disk_details_frame, "Firmware Revision", disk["firmware"])
                adicionar_linha_detalhe_esquerda(disk_details_frame, "Media Type", disk["media_type"])
                adicionar_linha_detalhe_esquerda(disk_details_frame, "Bytes/Sector", disk["bytes_sector"])

        # ------------------------------------------------------------
        # 7. ABA FERRAMENTAS
        # ------------------------------------------------------------
        tab_tools_frame = ctk.CTkFrame(tab_ferramentas, fg_color="transparent")
        tab_tools_frame.pack(fill="both", expand=True, padx=10, pady=10)

        card_tools = criar_card_tab(tab_tools_frame, "🛠️", "Ferramentas de Diagnóstico Adicionais")
        
        lbl_intro_tools = ctk.CTkLabel(
            card_tools, 
            text="Centralize e execute atalhos para os utilitários de hardware mais famosos do mercado diretamente por aqui.", 
            font=("Segoe UI", 12), text_color="#9ca3af", wraplength=700, anchor="w", justify="left"
        )
        lbl_intro_tools.pack(fill="x", padx=20, pady=(0, 5))

        lbl_obs_tools = ctk.CTkLabel(
            card_tools,
            text="⚠️ Obs: Não é necessário ter estes programas instalados em seu computador. Ao clicar, eles serão executados em modo portátil diretamente do diretório local do otimizador.",
            font=("Segoe UI", 11, "italic"),
            text_color="#a78bfa",
            wraplength=700,
            anchor="w",
            justify="left"
        )
        lbl_obs_tools.pack(fill="x", padx=20, pady=(0, 10))

        btn_box = ctk.CTkFrame(card_tools, fg_color="transparent")
        btn_box.pack(fill="x", padx=15, pady=(5, 12))
        btn_box.grid_columnconfigure(0, weight=1, uniform="tool_btn")
        btn_box.grid_columnconfigure(1, weight=1, uniform="tool_btn")
        
        # Função para abrir os executáveis locais
        def abrir_ferramenta(caminho_relativo):
            try:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                caminho_completo = os.path.normpath(os.path.join(base_dir, caminho_relativo))
                
                # Se o arquivo exato não existir (ex: o usuário atualizou o app e mudou o nome da versão)
                # tenta procurar qualquer arquivo .exe no mesmo diretório
                if not os.path.exists(caminho_completo):
                    dir_name = os.path.dirname(caminho_completo)
                    if os.path.exists(dir_name) and os.path.isdir(dir_name):
                        exes = [f for f in os.listdir(dir_name) if f.lower().endswith(".exe")]
                        if exes:
                            caminho_completo = os.path.join(dir_name, exes[0])

                # Se for GPU-Z, configura o registro do Windows para não mostrar a tela de instalação
                if "GPU-Z" in caminho_completo:
                    try:
                        import winreg
                        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\techPowerUp\GPU-Z")
                        winreg.SetValueEx(key, "Install_Dir", 0, winreg.REG_SZ, "no")
                        winreg.CloseKey(key)
                    except Exception:
                        pass

                if os.path.exists(caminho_completo) and os.path.isfile(caminho_completo):
                    subprocess.Popen([caminho_completo])
                    self.log_mensagem(f"✔️ Iniciado: {os.path.basename(caminho_completo)}")
                else:
                    self.log_mensagem(f"❌ Erro: Ferramenta não encontrada em {os.path.dirname(caminho_completo)}", "red")
            except Exception as e:
                self.log_mensagem(f"❌ Falha ao iniciar ferramenta: {e}", "red")

        btn_cpuz = ctk.CTkButton(
            btn_box, text="⚙️ Abrir CPU-Z", 
            fg_color="#a855f7", hover_color="#c084fc", text_color="white",
            command=lambda: abrir_ferramenta(r"scripts\app.exe\CPU-Z\cpuz_x64.exe"),
            font=ctk.CTkFont(weight="bold"), height=35
        )
        btn_cpuz.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        btn_gpuz = ctk.CTkButton(
            btn_box, text="🎥 Abrir GPU-Z", 
            fg_color="#a855f7", hover_color="#c084fc", text_color="white",
            command=lambda: abrir_ferramenta(r"scripts\app.exe\GPU-Z\GPU-Z.2.55.0.exe"),
            font=ctk.CTkFont(weight="bold"), height=35
        )
        btn_gpuz.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        btn_hwinfo = ctk.CTkButton(
            btn_box, text="🔍 Abrir HWiNFO", 
            fg_color="#a855f7", hover_color="#c084fc", text_color="white",
            command=lambda: abrir_ferramenta(r"scripts\app.exe\HWiNFO\HWiNFO64.exe"),
            font=ctk.CTkFont(weight="bold"), height=35
        )
        btn_hwinfo.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        btn_hwmonitor = ctk.CTkButton(
            btn_box, text="🌡️ Abrir HWMonitor", 
            fg_color="#a855f7", hover_color="#c084fc", text_color="white",
            command=lambda: abrir_ferramenta(r"scripts\app.exe\HWMonitor\HWMonitor_x64.exe"),
            font=ctk.CTkFont(weight="bold"), height=35
        )
        btn_hwmonitor.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
