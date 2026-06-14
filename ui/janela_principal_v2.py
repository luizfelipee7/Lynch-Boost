import os
import customtkinter as ctk
from PIL import Image

from core import atalhos, gerenciador_json
from core.acoes_script import ACOES_SCRIPT
from core.riscos import risco_exige_confirmacao
from ui.janela_principal import (
    CATEGORIAS,
    GRUPOS_DETALHE,
    PCBoosterHub as LegacyHub,
    _NullBtn,
)


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


COLORS = {
    "root": "#101216",
    "sidebar": "#14171d",
    "surface": "#191d25",
    "surface_alt": "#202531",
    "surface_soft": "#252b38",
    "border": "#303747",
    "border_soft": "#252b34",
    "text": "#f4f7fb",
    "muted": "#9aa4b2",
    "subtle": "#697386",
    "blue": "#3b82f6",
    "blue_hover": "#2563eb",
    "green": "#22c55e",
    "amber": "#f59e0b",
    "red": "#ef4444",
    "purple": "#a855f7",
}

RISK_THEME = {
    "seguro": ("Seguro", COLORS["green"], "#11351f"),
    "reversivel": ("Reversivel", COLORS["blue"], "#10233d"),
    "painel": ("Painel", COLORS["purple"], "#2b1742"),
    "confirmacao": ("Confirmacao", COLORS["amber"], "#3a2609"),
    "requer_reinicio": ("Requer reinicio", COLORS["amber"], "#3a2609"),
    "destrutivo": ("Destrutivo", COLORS["red"], "#3d1414"),
    "atalho": ("Atalho", "#9ca3af", "#232833"),
}


def font(size, weight=None):
    return ctk.CTkFont(family="Segoe UI", size=size, weight=weight)


def is_admin():
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def pending_reboot():
    try:
        import winreg
        checks = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired"),
        ]
        for hive, path in checks:
            try:
                key = winreg.OpenKey(hive, path)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                continue
    except Exception:
        return False
    return False


class PCBoosterHub(LegacyHub):
    def __init__(self):
        ctk.CTk.__init__(self)

        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("lynch.fpsboost.hub.2.0")
        except Exception:
            pass

        self.title("Lynch Boost - Painel Operacional")
        self.geometry("1280x820")
        self.minsize(1160, 740)
        self.resizable(True, True)
        self.configure(fg_color=COLORS["root"])

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.abspath(os.path.join(base_dir, "..", "assets", "logo-ico.ico"))
        self.logo_img_splash = None
        self.logo_img_dash = None
        self._startup_warnings = []

        try:
            if os.path.exists(self.icon_path):
                self.iconbitmap(default=self.icon_path)
        except Exception:
            pass

        try:
            logo_png_path = os.path.abspath(os.path.join(base_dir, "..", "assets", "logo.png"))
            if os.path.exists(logo_png_path):
                img = Image.open(logo_png_path)
                self.logo_img_splash = ctk.CTkImage(light_image=img, dark_image=img, size=(138, 138))
                self.logo_img_dash = ctk.CTkImage(light_image=img, dark_image=img, size=(42, 42))
        except Exception as exc:
            self._startup_warnings.append(f"[AVISO] Erro ao pre-carregar logo.png: {exc}")

        self.card_status = {}
        self.card_widgets = {}
        self.card_progress_labels = {}
        self.detail_frames = {}
        self.item_status_labels = {}
        self.item_text_labels = {}
        self.item_row_frames = {}
        self.sidebar_buttons = {}
        self.action_catalog = []
        self.action_records = {}
        self.selected_item_by_category = {}
        self.detail_panel_widgets = {}
        self.dashboard_stat_labels = {}
        self.recent_events = []
        self.active_nav_key = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._create_shell()
        self._create_console()

        for warning in self._startup_warnings:
            self.log_mensagem(warning)

        self.dados_config = gerenciador_json.ler_config_json(self.log_mensagem) or {}
        self._inicializar_status()
        self.action_catalog = self._build_action_catalog()
        self.action_records = {record["item_id"]: record for record in self.action_catalog}

        self._create_sidebar()
        self.criar_dashboard()
        self._criar_telas_detalhe()
        self.criar_tela_inicial()

    def _create_shell(self):
        self.app_shell = ctk.CTkFrame(self, fg_color=COLORS["root"], corner_radius=0)
        self.app_shell.grid(row=0, column=0, sticky="nsew")
        self.app_shell.grid_rowconfigure(0, weight=1)
        self.app_shell.grid_columnconfigure(0, weight=0)
        self.app_shell.grid_columnconfigure(1, weight=1)

        self.sidebar_frame = ctk.CTkFrame(
            self.app_shell,
            fg_color=COLORS["sidebar"],
            border_color=COLORS["border_soft"],
            border_width=1,
            corner_radius=0,
            width=235,
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        self.workspace_frame = ctk.CTkFrame(self.app_shell, fg_color=COLORS["root"], corner_radius=0)
        self.workspace_frame.grid(row=0, column=1, sticky="nsew")
        self.workspace_frame.grid_rowconfigure(0, weight=7)
        self.workspace_frame.grid_rowconfigure(1, weight=2)
        self.workspace_frame.grid_columnconfigure(0, weight=1)

        self.content_host = ctk.CTkFrame(self.workspace_frame, fg_color=COLORS["root"], corner_radius=0)
        self.content_host.grid(row=0, column=0, sticky="nsew", padx=12, pady=(12, 8))
        self.content_host.grid_rowconfigure(0, weight=1)
        self.content_host.grid_columnconfigure(0, weight=1)

        self.console_slot = ctk.CTkFrame(self.workspace_frame, fg_color=COLORS["root"], corner_radius=0)
        self.console_slot.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.console_slot.grid_rowconfigure(0, weight=1)
        self.console_slot.grid_columnconfigure(0, weight=1)

        self.content_host.log_mensagem = self.log_mensagem
        self.content_host.abrir_categoria = self.abrir_categoria
        self.content_host.marcar_completado = self.marcar_completado
        self.content_host.desmarcar_completado = self.desmarcar_completado

    def _create_console(self):
        self.console_frame = ctk.CTkFrame(
            self.console_slot,
            fg_color=COLORS["surface"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
        )
        self.console_frame.grid(row=0, column=0, sticky="nsew")
        self.console_frame.grid_rowconfigure(1, weight=1)
        self.console_frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self.console_frame, fg_color=COLORS["surface_alt"], corner_radius=8, height=34)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Activity Log", font=font(11, "bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, padx=(12, 6), pady=7, sticky="w"
        )
        ctk.CTkLabel(header, text="Motor online", font=font(10), text_color=COLORS["green"]).grid(
            row=0, column=1, padx=6, pady=7, sticky="w"
        )
        ctk.CTkButton(
            header,
            text="Limpar",
            width=74,
            height=24,
            fg_color=COLORS["surface_soft"],
            hover_color=COLORS["border"],
            border_width=1,
            border_color=COLORS["border"],
            font=font(10, "bold"),
            command=self.limpar_console,
        ).grid(row=0, column=2, padx=8, pady=5, sticky="e")

        self.console_box = ctk.CTkTextbox(
            self.console_frame,
            fg_color="#0d0f13",
            text_color="#e5e7eb",
            font=("Consolas", 12),
            border_width=0,
            scrollbar_button_color=COLORS["surface_soft"],
            scrollbar_button_hover_color=COLORS["border"],
        )
        self.console_box.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))
        self.console_box.insert("0.0", "Lynch Boost - Motor Online\nAguardando comandos...")
        self.console_box.configure(state="disabled")

    def _create_sidebar(self):
        brand = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        brand.pack(fill="x", padx=14, pady=(16, 12))

        if self.logo_img_dash:
            ctk.CTkLabel(brand, image=self.logo_img_dash, text="").pack(side="left", padx=(0, 10))

        title_box = ctk.CTkFrame(brand, fg_color="transparent")
        title_box.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(title_box, text="LYNCH BOOST", font=font(15, "bold"), text_color=COLORS["text"], anchor="w").pack(fill="x")
        ctk.CTkLabel(title_box, text="Painel Operacional", font=font(10), text_color=COLORS["muted"], anchor="w").pack(fill="x")

        ctk.CTkFrame(self.sidebar_frame, height=1, fg_color=COLORS["border_soft"]).pack(fill="x", padx=14, pady=(0, 10))
        self._create_sidebar_button("dashboard", "Inicio", "Visao geral e alertas", self.mostrar_dashboard)
        for category in CATEGORIAS:
            self._create_sidebar_button(
                category["key"],
                category["titulo"],
                category["subtitulo"],
                lambda key=category["key"]: self.abrir_categoria(key),
            )

        footer = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=14, pady=14)
        ctk.CTkLabel(
            footer,
            text="Sessao elevada" if is_admin() else "Sem elevacao",
            font=font(10, "bold"),
            text_color=COLORS["green"] if is_admin() else COLORS["amber"],
            anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(footer, text="interface v2", font=font(9), text_color=COLORS["subtle"], anchor="w").pack(fill="x", pady=(2, 0))

    def _create_sidebar_button(self, key, title, subtitle, command):
        row = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent", border_color=COLORS["sidebar"], border_width=1, corner_radius=8, cursor="hand2")
        row.pack(fill="x", padx=10, pady=3)
        row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(row, text=title, font=font(12, "bold"), text_color=COLORS["text"], anchor="w").grid(
            row=0, column=0, sticky="ew", padx=12, pady=(8, 0)
        )
        ctk.CTkLabel(row, text=subtitle, font=font(9), text_color=COLORS["muted"], anchor="w").grid(
            row=1, column=0, sticky="ew", padx=12, pady=(0, 8)
        )

        progress = ctk.CTkLabel(row, text="", font=font(9, "bold"), text_color=COLORS["subtle"], anchor="e")
        progress.grid(row=0, column=1, rowspan=2, padx=(4, 12), sticky="e")
        if key in self.card_status and self.card_status[key]["total"] > 0:
            progress.configure(text=f"0/{self.card_status[key]['total']}")
            self.card_progress_labels[key] = progress

        def on_enter(_event):
            if self.active_nav_key != key:
                row.configure(fg_color=COLORS["surface"], border_color=COLORS["border_soft"])

        def on_leave(_event):
            if self.active_nav_key != key:
                row.configure(fg_color="transparent", border_color=COLORS["sidebar"])

        def on_click(_event):
            command()

        for widget in (row, *row.winfo_children()):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

        self.sidebar_buttons[key] = row

    def _set_active_nav(self, key):
        self.active_nav_key = key
        for nav_key, row in self.sidebar_buttons.items():
            if nav_key == key:
                row.configure(fg_color=COLORS["surface_alt"], border_color=COLORS["blue"])
            else:
                row.configure(fg_color="transparent", border_color=COLORS["sidebar"])

    def _inicializar_status(self):
        for category in CATEGORIAS:
            key = category["key"]
            total = 0 if key in ("instalacao", "benchmark_info") else len(self.dados_config.get(key, []))
            if key == "debloat_servicos":
                total += 1
            self.card_status[key] = {"total": total, "completados": set()}

    def _action_risk(self, data):
        if data.get("_type") == "shortcut":
            return "atalho"
        if data.get("_fixed") or str(data.get("acao_especial", "")).startswith("abrir_menu"):
            return "painel"

        action = data.get("acao_especial")
        if action in ACOES_SCRIPT:
            metadata = ACOES_SCRIPT[action]
            risk = metadata.get("risco", "seguro")
            if metadata.get("destrutivo") or data.get("destrutivo"):
                return "destrutivo"
            if risco_exige_confirmacao(risk):
                return "confirmacao"
            return risk if risk in RISK_THEME else "reversivel"

        if data.get("destrutivo"):
            return "destrutivo"
        if str(action).startswith("abrir_modal"):
            return "confirmacao"
        return "reversivel"

    def _build_action_catalog(self):
        catalog = []
        for category in CATEGORIAS:
            key = category["key"]
            if key in ("benchmark_info", "instalacao"):
                continue

            scripts = self.dados_config.get(key, [])
            scripts_by_name = {script["nome"]: (index, script) for index, script in enumerate(scripts)}
            used_names = set()
            fixed = {}
            if key == "debloat_servicos":
                fixed["Microsoft Edge"] = {"nome": "Microsoft Edge", "_fixed": "edge"}

            shortcut_count = 0
            for group in GRUPOS_DETALHE.get(key, []):
                group_title = group.get("titulo", "Acoes")
                for name in group.get("scripts", []):
                    if name in scripts_by_name:
                        index, script = scripts_by_name[name]
                        catalog.append(self._make_record("script", key, category["titulo"], group_title, f"{key}_{index}", script["nome"], script))
                        used_names.add(name)
                    elif name in fixed:
                        data = fixed[name]
                        catalog.append(self._make_record("fixed", key, category["titulo"], group_title, f"{key}_edge", data["nome"], data))
                        used_names.add(name)

                for shortcut in group.get("atalhos", []):
                    shortcut_count += 1
                    data = dict(shortcut)
                    data["nome"] = data.get("texto", "Atalho")
                    data["_type"] = "shortcut"
                    catalog.append(self._make_record("shortcut", key, category["titulo"], group_title, f"{key}_atalho_{shortcut_count}", data["nome"], data))

            for name, (index, script) in scripts_by_name.items():
                if name not in used_names:
                    catalog.append(self._make_record("script", key, category["titulo"], "Outros", f"{key}_{index}", script["nome"], script))

            for name, data in fixed.items():
                if name not in used_names:
                    catalog.append(self._make_record("fixed", key, category["titulo"], "Outros", f"{key}_edge", data["nome"], data))

        return catalog

    def _make_record(self, action_type, category, category_title, group, item_id, name, data):
        record = {
            "type": action_type,
            "category": category,
            "category_title": category_title,
            "group": group,
            "item_id": item_id,
            "name": name,
            "data": data,
        }
        record["risk"] = self._action_risk(data)
        return record

    def criar_tela_inicial(self):
        self.splash_frame = ctk.CTkFrame(self, fg_color="#050609", corner_radius=0)
        self.splash_frame.grid(row=0, column=0, sticky="nsew")
        self.splash_frame.grid_rowconfigure(0, weight=1)
        self.splash_frame.grid_rowconfigure(5, weight=1)
        self.splash_frame.grid_columnconfigure(0, weight=1)

        if self.logo_img_splash:
            ctk.CTkLabel(self.splash_frame, image=self.logo_img_splash, text="").grid(row=1, column=0, pady=(0, 18))

        ctk.CTkLabel(self.splash_frame, text="LYNCH BOOST", font=font(48, "bold"), text_color=COLORS["text"]).grid(row=2, column=0, pady=(0, 6))
        ctk.CTkLabel(
            self.splash_frame,
            text="Painel operacional para Windows performance",
            font=font(16),
            text_color=COLORS["muted"],
        ).grid(row=3, column=0, pady=(0, 28))
        ctk.CTkButton(
            self.splash_frame,
            text="Abrir Painel",
            width=240,
            height=46,
            fg_color=COLORS["blue"],
            hover_color=COLORS["blue_hover"],
            font=font(16, "bold"),
            command=self.fechar_tela_inicial,
        ).grid(row=4, column=0)

    def fechar_tela_inicial(self):
        self.splash_frame.grid_forget()
        self.mostrar_dashboard()

    def criar_dashboard(self):
        self.dashboard_frame = ctk.CTkFrame(self.content_host, fg_color=COLORS["root"], corner_radius=0)
        self.dashboard_frame.grid_rowconfigure(2, weight=1)
        self.dashboard_frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="Painel Operacional", font=font(28, "bold"), text_color=COLORS["text"], anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header,
            text="Controle central de acoes, riscos, execucao e historico.",
            font=font(12),
            text_color=COLORS["muted"],
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        stats = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        stats.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        for index in range(4):
            stats.grid_columnconfigure(index, weight=1, uniform="stats")
        self._create_stat_card(stats, 0, "Administrador", "admin")
        self._create_stat_card(stats, 1, "Acoes no Hub", "actions")
        self._create_stat_card(stats, 2, "Pendencia", "reboot")
        self._create_stat_card(stats, 3, "Execucao", "execution")

        body = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        body.grid(row=2, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        left = ctk.CTkScrollableFrame(body, fg_color=COLORS["surface"], border_color=COLORS["border"], border_width=1, corner_radius=8)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(left, text="Areas operacionais", font=font(14, "bold"), text_color=COLORS["text"], anchor="w").pack(fill="x", padx=14, pady=(12, 8))
        for category in CATEGORIAS:
            self._create_dashboard_category_row(left, category)

        right = ctk.CTkFrame(body, fg_color=COLORS["surface"], border_color=COLORS["border"], border_width=1, corner_radius=8)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(4, weight=1)
        right.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(right, text="Execucao rapida", font=font(14, "bold"), text_color=COLORS["text"], anchor="w").grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))

        quick_box = ctk.CTkFrame(right, fg_color="transparent")
        quick_box.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
        for selector in [
            {"name": "Limpar Arquivos Temporarios", "category": "limpeza_armazenamento"},
            {"name": "Esvaziar Lixeira do PC", "category": "limpeza_armazenamento"},
            {"name": "Desfragmentar Disco", "category": "limpeza_armazenamento"},
            {"action": "abrir_menu_dns", "category": "rede_latencia"},
        ]:
            record = self._find_catalog_record(selector)
            if record:
                self._create_quick_button(quick_box, record)

        ctk.CTkFrame(right, height=1, fg_color=COLORS["border"]).grid(row=2, column=0, sticky="ew", padx=14, pady=8)
        ctk.CTkLabel(right, text="Historico recente", font=font(13, "bold"), text_color=COLORS["text"], anchor="w").grid(row=3, column=0, sticky="ew", padx=14)
        self.recent_events_frame = ctk.CTkFrame(right, fg_color="transparent")
        self.recent_events_frame.grid(row=4, column=0, sticky="nsew", padx=14, pady=(8, 12))
        self._update_dashboard_summary()
        self._render_recent_events()

    def _create_stat_card(self, parent, column, title, key):
        card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], border_color=COLORS["border"], border_width=1, corner_radius=8)
        card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 6, 0 if column == 3 else 6))
        ctk.CTkLabel(card, text=title, font=font(10, "bold"), text_color=COLORS["muted"], anchor="w").pack(fill="x", padx=12, pady=(10, 0))
        value = ctk.CTkLabel(card, text="-", font=font(20, "bold"), text_color=COLORS["text"], anchor="w")
        value.pack(fill="x", padx=12, pady=(2, 10))
        self.dashboard_stat_labels[key] = value

    def _create_dashboard_category_row(self, parent, category):
        key = category["key"]
        row = ctk.CTkFrame(parent, fg_color=COLORS["surface_alt"], border_color=COLORS["border_soft"], border_width=1, corner_radius=8, cursor="hand2")
        row.pack(fill="x", padx=10, pady=4)
        row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(row, text=category["titulo"], font=font(13, "bold"), text_color=COLORS["text"], anchor="w").grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 0))
        ctk.CTkLabel(row, text=category["subtitulo"], font=font(10), text_color=COLORS["muted"], anchor="w").grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        total = self.card_status.get(key, {}).get("total", 0)
        completed = len(self.card_status.get(key, {}).get("completados", set()))
        progress = f"{completed}/{total}" if total else ("Painel" if key in ("instalacao", "benchmark_info") else "Sem acoes")
        ctk.CTkLabel(row, text=progress, font=font(11, "bold"), text_color=COLORS["blue"] if total else COLORS["subtle"]).grid(
            row=0, column=1, rowspan=2, sticky="e", padx=12, pady=8
        )

        def open_category(_event):
            self.abrir_categoria(key)

        for widget in (row, *row.winfo_children()):
            widget.bind("<Button-1>", open_category)

    def _create_quick_button(self, parent, record):
        ctk.CTkButton(
            parent,
            text=record["name"],
            height=32,
            fg_color=COLORS["surface_soft"],
            hover_color=COLORS["border"],
            border_color=COLORS["border"],
            border_width=1,
            font=font(11, "bold"),
            command=lambda rec=record: self._execute_catalog_action(rec),
        ).pack(fill="x", padx=4, pady=3)

    def _find_catalog_record(self, selector):
        for record in self.action_catalog:
            if record["category"] != selector.get("category"):
                continue
            if selector.get("name") and record["name"] == selector["name"]:
                return record
            if selector.get("action") and record["data"].get("acao_especial") == selector["action"]:
                return record
            if selector.get("command") and record["data"].get("cmd") == selector["command"]:
                return record
        return None

    def _criar_telas_detalhe(self):
        for category in CATEGORIAS:
            key = category["key"]
            if key == "instalacao":
                self.detail_frames[key] = self._create_install_screen(category)
            elif key == "benchmark_info":
                self.detail_frames[key] = self._create_hardware_screen(category)
            else:
                self.detail_frames[key] = self._create_operational_screen(category)

    def _create_category_header(self, parent, category):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text=category["titulo"], font=font(24, "bold"), text_color=COLORS["text"], anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text=category["subtitulo"], font=font(11), text_color=COLORS["muted"], anchor="w").grid(row=1, column=0, sticky="w", pady=(2, 0))

        if category["key"] == "config_windows":
            actions = ctk.CTkFrame(header, fg_color="transparent")
            actions.grid(row=0, column=1, rowspan=2, sticky="e")
            ctk.CTkButton(actions, text="LEIA-ME", width=88, height=30, fg_color=COLORS["amber"], hover_color="#d97706", text_color="#111827", font=font(11, "bold"), command=self.abrir_leiame_windows).pack(side="left", padx=4)
            ctk.CTkButton(actions, text="Explorer", width=88, height=30, fg_color=COLORS["surface_soft"], hover_color=COLORS["border"], font=font(11, "bold"), command=self.confirmar_reiniciar_explorer).pack(side="left", padx=4)
            ctk.CTkButton(actions, text="Reiniciar PC", width=100, height=30, fg_color=COLORS["red"], hover_color="#dc2626", font=font(11, "bold"), command=self.confirmar_reiniciar_pc).pack(side="left", padx=4)

    def _create_operational_screen(self, category):
        frame = ctk.CTkFrame(self.content_host, fg_color=COLORS["root"], corner_radius=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=3)
        frame.grid_columnconfigure(1, weight=2)
        self._create_category_header(frame, category)

        action_list = ctk.CTkScrollableFrame(frame, fg_color=COLORS["surface"], border_color=COLORS["border"], border_width=1, corner_radius=8)
        action_list.grid(row=1, column=0, sticky="nsew", padx=(0, 8))

        records = [record for record in self.action_catalog if record["category"] == category["key"]]
        current_group = None
        for record in records:
            if record["group"] != current_group:
                current_group = record["group"]
                ctk.CTkLabel(action_list, text=current_group, font=font(12, "bold"), text_color=COLORS["muted"], anchor="w").pack(fill="x", padx=12, pady=(12, 4))
            self._create_action_row(action_list, record)

        panel = self._create_detail_panel(frame, category["key"])
        panel.grid(row=1, column=1, sticky="nsew")
        if records:
            self.selected_item_by_category[category["key"]] = records[0]["item_id"]
        return frame

    def _create_action_row(self, parent, record):
        row = ctk.CTkFrame(parent, fg_color=COLORS["surface_alt"], border_color=COLORS["border_soft"], border_width=1, corner_radius=8, cursor="hand2")
        row.pack(fill="x", padx=10, pady=4)
        row.grid_columnconfigure(1, weight=1)

        status = ctk.CTkLabel(row, text="Pendente", width=64, font=font(9, "bold"), text_color=COLORS["subtle"])
        status.grid(row=0, column=0, rowspan=2, sticky="w", padx=(10, 6), pady=9)
        title = ctk.CTkLabel(row, text=record["name"], font=font(12, "bold"), text_color=COLORS["text"], anchor="w")
        title.grid(row=0, column=1, sticky="ew", pady=(8, 0))

        row_hint = f"{record['category_title']} / {record['group']}"
        hint = ctk.CTkLabel(row, text=row_hint, font=font(9), text_color=COLORS["muted"], anchor="w", cursor="hand2")
        hint.grid(row=1, column=1, sticky="ew", pady=(0, 8))

        badge = None
        if record["type"] == "shortcut":
            risk_label, risk_color, risk_bg = RISK_THEME["atalho"]
            badge = ctk.CTkLabel(row, text=risk_label, width=96, height=22, fg_color=risk_bg, corner_radius=5, font=font(9, "bold"), text_color=risk_color)
            badge.grid(row=0, column=2, rowspan=2, padx=8, pady=8)
        ctk.CTkButton(
            row,
            text="Executar",
            width=78,
            height=26,
            fg_color=COLORS["blue"],
            hover_color=COLORS["blue_hover"],
            font=font(10, "bold"),
            command=lambda rec=record: self._execute_catalog_action(rec),
        ).grid(row=0, column=3, rowspan=2, padx=(0, 10), pady=8)

        self.item_status_labels[record["item_id"]] = status
        self.item_text_labels[record["item_id"]] = title
        self.item_row_frames[record["item_id"]] = row

        def select(_event):
            self._select_action(record["item_id"])

        clickable_widgets = [row, status, title, hint]
        if badge is not None:
            clickable_widgets.append(badge)
        for widget in clickable_widgets:
            widget.bind("<Button-1>", select)

    def _create_detail_panel(self, parent, category):
        panel = ctk.CTkFrame(parent, fg_color=COLORS["surface"], border_color=COLORS["border"], border_width=1, corner_radius=8)
        panel.grid_rowconfigure(8, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(panel, text="Selecione uma acao", font=font(18, "bold"), text_color=COLORS["text"], anchor="w", wraplength=390)
        title.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 4))
        meta = ctk.CTkLabel(panel, text="-", font=font(10, "bold"), text_color=COLORS["muted"], anchor="w")
        meta.grid(row=1, column=0, sticky="ew", padx=16)

        risk = ctk.CTkLabel(panel, text="-", height=26, fg_color=COLORS["surface_soft"], corner_radius=5, font=font(10, "bold"))
        risk.grid(row=2, column=0, sticky="w", padx=16, pady=(12, 8))

        summary_box, summary = self._create_detail_field(panel, 3, "Resumo operacional", "")
        mode_box, mode = self._create_detail_field(
            panel,
            4,
            "Modo de execucao",
            "Execucao individual. Nenhuma fila sera montada.",
        )

        run_btn = ctk.CTkButton(
            panel,
            text="Executar Agora",
            height=38,
            fg_color=COLORS["blue"],
            hover_color=COLORS["blue_hover"],
            font=font(12, "bold"),
        )
        run_btn.grid(row=5, column=0, sticky="ew", padx=16, pady=(10, 8))

        note = ctk.CTkLabel(
            panel,
            text="A acao selecionada e executada isoladamente para evitar conflito entre scripts sensiveis.",
            font=font(10),
            text_color=COLORS["subtle"],
            anchor="nw",
            justify="left",
            wraplength=390,
        )
        note.grid(row=6, column=0, sticky="ew", padx=16, pady=(0, 10))

        self.detail_panel_widgets[category] = {
            "title": title,
            "meta": meta,
            "risk": risk,
            "summary_box": summary_box,
            "summary": summary,
            "mode_box": mode_box,
            "mode": mode,
            "run_btn": run_btn,
        }
        return panel

    def _create_detail_field(self, parent, row, label, value, monospace=False):
        box = ctk.CTkFrame(parent, fg_color="#11141a", border_color=COLORS["border_soft"], border_width=1, corner_radius=7)
        box.grid(row=row, column=0, sticky="ew", padx=16, pady=(0, 8))
        box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            box,
            text=label,
            font=font(10, "bold"),
            text_color=COLORS["muted"],
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 1))

        value_label = ctk.CTkLabel(
            box,
            text=value,
            font=("Consolas", 10) if monospace else font(11),
            text_color=COLORS["text"] if value else COLORS["subtle"],
            anchor="nw",
            justify="left",
            wraplength=390,
        )
        value_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 9))
        return box, value_label

    def _create_install_screen(self, category):
        frame = ctk.CTkFrame(self.content_host, fg_color=COLORS["root"], corner_radius=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        self._create_category_header(frame, category)
        body = ctk.CTkFrame(frame, fg_color=COLORS["surface"], border_color=COLORS["border"], border_width=1, corner_radius=8)
        body.grid(row=1, column=0, sticky="nsew")
        from ui.menu_instalacao import MenuInstalacao
        self.menu_instalacao = MenuInstalacao(body, log_callback=self.log_mensagem)
        self.menu_instalacao.pack(fill="both", expand=True, padx=8, pady=8)
        return frame

    def _create_hardware_screen(self, category):
        frame = ctk.CTkFrame(self.content_host, fg_color=COLORS["root"], corner_radius=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        self._create_category_header(frame, category)
        content = ctk.CTkFrame(frame, fg_color=COLORS["surface"], border_color=COLORS["border"], border_width=1, corner_radius=8)
        content.grid(row=1, column=0, sticky="nsew")
        self._preparar_tela_hardware(content)
        return frame

    def _select_action(self, item_id):
        record = self.action_records.get(item_id)
        if not record:
            return

        category = record["category"]
        previous_item_id = self.selected_item_by_category.get(category)
        if previous_item_id and previous_item_id != item_id:
            self._style_action_row(previous_item_id, selected=False)

        self.selected_item_by_category[category] = item_id
        self._style_action_row(item_id, selected=True)

        widgets = self.detail_panel_widgets.get(category)
        if not widgets:
            return

        risk_label, risk_color, risk_bg = RISK_THEME.get(record["risk"], RISK_THEME["reversivel"])
        widgets["title"].configure(text=record["name"])
        widgets["meta"].configure(text=f"{record['category_title']} / {record['group']}")
        widgets["risk"].configure(text=risk_label, text_color=risk_color, fg_color=risk_bg)
        widgets["summary"].configure(text=self._action_summary(record))
        widgets["mode"].configure(text="Execucao individual. O Hub nao executa esta acao em lote.")
        widgets["run_btn"].configure(command=lambda rec=record: self._execute_catalog_action(rec))

    def _style_action_row(self, item_id, selected=False):
        row = self.item_row_frames.get(item_id)
        if not row:
            return

        status_label = self.item_status_labels.get(item_id)
        completed = False
        if status_label:
            try:
                completed = status_label.cget("text") == "OK"
            except Exception:
                completed = False

        try:
            if selected:
                row.configure(border_color=COLORS["blue"], fg_color="#1b2638")
            elif completed:
                row.configure(border_color=COLORS["green"], fg_color="#13281c")
            else:
                row.configure(border_color=COLORS["border_soft"], fg_color=COLORS["surface_alt"])
        except Exception:
            pass

    def _action_summary(self, record):
        data = record["data"]
        action = data.get("acao_especial", "")
        if data.get("_type") == "shortcut":
            return "Atalho nativo do Windows. Abre uma ferramenta do sistema sem executar script de otimizacao."
        if data.get("_fixed") == "edge":
            return "Abre o painel dedicado ao Microsoft Edge, com remocao e reducao de execucao em segundo plano."
        if action in ACOES_SCRIPT:
            return "Executa uma acao registrada no Hub com roteamento, permissao e confirmacao conforme o risco."
        if str(action).startswith("abrir_menu"):
            return "Abre uma interface especializada para configurar varias opcoes relacionadas a esta area."
        if str(action).startswith("abrir_modal"):
            return "Abre um modal premium com explicacao tecnica, confirmacao e controle de aplicacao."
        return "Acao operacional registrada no config.json."

    def _execute_catalog_action(self, record, clear_log=True):
        if clear_log:
            self.limpar_console_silencioso()
        self._record_recent_event(f"Executando: {record['name']}")

        if record["type"] == "shortcut":
            self._execute_shortcut(record["data"])
            return

        data = record["data"]
        button = _NullBtn()
        if data.get("_fixed") == "edge":
            self.abrir_menu_edge(button, record["category"], record["item_id"])
            return
        self._executar_acao(data, button, record["category"], record["item_id"])

    def _execute_shortcut(self, shortcut):
        command_key = shortcut.get("cmd", "")
        commands = {
            "abrir_programas_recursos": lambda: atalhos.abrir_programas_recursos(self.log_mensagem),
            "abrir_limpeza_disco": lambda: atalhos.abrir_limpeza_disco(self.log_mensagem),
            "abrir_armazenamento": lambda: atalhos.abrir_armazenamento(self.log_mensagem),
            "abrir_desfragmentador": lambda: atalhos.abrir_desfragmentador(self.log_mensagem),
            "abrir_inicializacao": lambda: atalhos.abrir_inicializacao(self.log_mensagem),
            "abrir_energia": lambda: atalhos.abrir_energia(self.log_mensagem),
            "abrir_uac": lambda: atalhos.abrir_uac(self.log_mensagem),
        }
        commands.get(command_key, lambda: self.log_mensagem(f"Atalho nao registrado: {command_key}", "red"))()

    def mostrar_dashboard(self):
        self._esconder_tudo()
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
        self._set_active_nav("dashboard")
        self._update_dashboard_summary()
        self._render_recent_events()

    def abrir_categoria(self, key):
        self._esconder_tudo()
        frame = self.detail_frames.get(key)
        if frame:
            frame.grid(row=0, column=0, sticky="nsew")
        self._set_active_nav(key)
        if key == "benchmark_info":
            self.recarregar_hardware_info()
        selected = self.selected_item_by_category.get(key)
        if selected:
            self._select_action(selected)

    def voltar_ao_menu(self):
        self.mostrar_dashboard()

    def _esconder_tudo(self):
        if hasattr(self, "dashboard_frame"):
            self.dashboard_frame.grid_forget()
        for frame in self.detail_frames.values():
            frame.grid_forget()
        for attr in ("audio_frame", "personalizacao_frame", "desinstalar_apps_windows_frame"):
            if hasattr(self, attr):
                getattr(self, attr).grid_forget()

    def abrir_menu_instalacao(self, parent_btn=None, categoria=None, item_id=None):
        self.log_mensagem("Abrindo interface do Instalador de Programas...")
        self.abrir_categoria("instalacao")

    def abrir_menu_desinstalar_apps_windows(self, parent_btn=None, categoria=None, item_id=None):
        self.log_mensagem("Abrindo interface do Desinstalador de Apps do Windows...")
        self._esconder_tudo()
        if not hasattr(self, "desinstalar_apps_windows_frame"):
            from ui.menu_desinstalar_apps_windows import MenuDesinstalarAppsWindows
            self.desinstalar_apps_windows_frame = MenuDesinstalarAppsWindows(
                self.content_host,
                log_callback=self.log_mensagem,
                back_callback=lambda: self.abrir_categoria("debloat_servicos"),
            )
        self.desinstalar_apps_windows_frame.grid(row=0, column=0, sticky="nsew")
        self._set_active_nav("debloat_servicos")

    def abrir_menu_personalizacao(self, parent_btn=None, categoria=None, item_id=None):
        self.log_mensagem("Iniciando interface de Personalizacao...")
        self._esconder_tudo()
        if not hasattr(self, "personalizacao_frame"):
            from ui.menu_personalizacao import PersonalizacaoFrame
            self.personalizacao_frame = PersonalizacaoFrame(self.content_host, parent_btn, categoria, item_id)
        else:
            self.personalizacao_frame.carregar_configuracoes_atuais()
        self.personalizacao_frame.grid(row=0, column=0, sticky="nsew")
        self._set_active_nav("config_windows")

    def abrir_menu_audio(self, parent_btn=None, categoria=None, item_id=None):
        self.log_mensagem("Iniciando interface do Gerenciador de Audio...")
        self._esconder_tudo()
        if not hasattr(self, "audio_frame"):
            from ui.menu_audio import AudioDeviceManagerFrame
            self.audio_frame = AudioDeviceManagerFrame(self.content_host, parent_btn, categoria, item_id)
        else:
            self.audio_frame.atualizar_dispositivos()
        self.audio_frame.grid(row=0, column=0, sticky="nsew")
        self._set_active_nav("mouse_teclado")

    def marcar_completado(self, categoria, item_id, btn_instance):
        status_label = self.item_status_labels.get(item_id)
        if status_label:
            status_label.configure(text="OK", text_color=COLORS["green"])
        row = self.item_row_frames.get(item_id)
        if row:
            row.configure(fg_color="#13281c", border_color=COLORS["green"])

        status = self.card_status.get(categoria)
        if not status:
            return
        status["completados"].add(item_id)
        self._update_category_progress(categoria)
        self._update_dashboard_summary()

    def desmarcar_completado(self, categoria, item_id, btn_instance):
        status_label = self.item_status_labels.get(item_id)
        if status_label:
            status_label.configure(text="Pendente", text_color=COLORS["subtle"])
        row = self.item_row_frames.get(item_id)
        if row:
            row.configure(fg_color=COLORS["surface_alt"], border_color=COLORS["border_soft"])

        status = self.card_status.get(categoria)
        if not status:
            return
        status["completados"].discard(item_id)
        self._update_category_progress(categoria)
        self._update_dashboard_summary()

    def _update_category_progress(self, category):
        status = self.card_status.get(category)
        if not status:
            return
        total = status["total"]
        completed = len(status["completados"])
        label = self.card_progress_labels.get(category)
        if label and total > 0:
            label.configure(text=f"{completed}/{total}", text_color=COLORS["green"] if completed else COLORS["subtle"])

    def log_mensagem(self, mensagem, tipo="info"):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        text = str(mensagem).strip()
        lower = text.lower()
        if tipo == "red" or "[erro]" in lower or "falha" in lower or "negado" in lower:
            prefix = "ERRO"
        elif tipo == "green" or "sucesso" in lower or "conclu" in lower or "[ok]" in lower:
            prefix = "OK"
        elif "executando" in lower or "abrindo" in lower or "iniciando" in lower:
            prefix = "RUN"
        else:
            prefix = "INFO"

        if hasattr(self, "console_box"):
            self.console_box.configure(state="normal")
            self.console_box.insert("end", f"\n[{timestamp}] {prefix}  {text}")
            self.console_box.see("end")
            self.console_box.configure(state="disabled")
        self._record_recent_event(text)

    def limpar_console(self):
        self.console_box.configure(state="normal")
        self.console_box.delete("0.0", "end")
        self.console_box.insert("0.0", "Lynch Boost - Motor Online\nLog limpo. Aguardando comandos...")
        self.console_box.configure(state="disabled")

    def limpar_console_silencioso(self):
        self.console_box.configure(state="normal")
        self.console_box.delete("0.0", "end")
        self.console_box.insert("0.0", "Lynch Boost - Motor Online")
        self.console_box.configure(state="disabled")

    def _record_recent_event(self, message):
        text = str(message).strip()
        if not text:
            return
        if len(text) > 90:
            text = text[:87] + "..."
        from datetime import datetime
        entry = f"{datetime.now().strftime('%H:%M:%S')}  {text}"
        if not self.recent_events or self.recent_events[0] != entry:
            self.recent_events.insert(0, entry)
            self.recent_events = self.recent_events[:8]
        self._render_recent_events()

    def _render_recent_events(self):
        frame = getattr(self, "recent_events_frame", None)
        if not frame:
            return
        for child in frame.winfo_children():
            child.destroy()
        if not self.recent_events:
            ctk.CTkLabel(frame, text="Nenhuma acao registrada nesta sessao.", font=font(10), text_color=COLORS["subtle"], anchor="w").pack(fill="x", pady=4)
            return
        for event in self.recent_events[:6]:
            ctk.CTkLabel(frame, text=event, font=font(10), text_color=COLORS["muted"], anchor="w", wraplength=390).pack(fill="x", pady=3)

    def _update_dashboard_summary(self):
        if not self.dashboard_stat_labels:
            return
        admin = is_admin()
        self.dashboard_stat_labels["admin"].configure(
            text="Ativo" if admin else "Pendente",
            text_color=COLORS["green"] if admin else COLORS["amber"],
        )
        self.dashboard_stat_labels["actions"].configure(
            text=str(len([record for record in self.action_catalog if record["type"] != "shortcut"]))
        )
        reboot = pending_reboot()
        self.dashboard_stat_labels["reboot"].configure(
            text="Reiniciar" if reboot else "Normal",
            text_color=COLORS["amber"] if reboot else COLORS["green"],
        )
        self.dashboard_stat_labels["execution"].configure(
            text="Individual",
            text_color=COLORS["blue"],
        )
