import customtkinter as ctk
import winreg
import os
import ctypes
from tkinter import filedialog, colorchooser
from PIL import Image, ImageTk
from datetime import datetime
from core.auditoria import anexar_auditoria

# Cores pré-definidas do Windows (hex)
PALETA_CORES = [
    "#ff8c00", "#e81123", "#d13438", "#c30052", "#e3008c", "#bf00ff",
    "#8e8cd8", "#6b69d6", "#008a00", "#107c10", "#00b7c3", "#0078d7",
    "#0063b1", "#8764b8", "#b4a0ff", "#7a7574", "#5b5f62", "#486860",
    "#847545", "#515c6b", "#4a5459", "#000000"
]

class PersonalizacaoFrame(ctk.CTkFrame):
    def __init__(self, master, parent_btn=None, categoria=None, item_id=None):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        
        self.master = master
        self.parent_btn = parent_btn
        self.categoria = categoria
        self.item_id = item_id
        
        self.wallpaper_atual = ""
        self.cor_atual = "#000000"
        self.tema_escuro_ativo = True
        self.transparencia_ativa = True
        self.taskview_ativo = True
        self.imagem_selecionada = ""
        self.modificou_algo = False
        
        self.preview_image_ctk = None
        self.monitor_bg_image_ctk = None
        self.color_buttons = {}
        
        self._criar_layout()
        self.carregar_configuracoes_atuais()

    def _log(self, mensagem, tipo=None):
        logger = getattr(self.master, "log_mensagem", None)
        if not callable(logger):
            return
        if tipo:
            logger(mensagem, tipo=tipo)
        else:
            logger(mensagem)

    def _criar_layout(self):
        # --- HEADER ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(12, 0))
        
        ctk.CTkButton(
            header, text="← Voltar", width=100, height=32,
            fg_color="#333333", hover_color="#555555",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.voltar
        ).pack(side="left")
        
        ctk.CTkLabel(
            header, text="🎨  Personalização do Windows",
            font=ctk.CTkFont(size=22, weight="bold"), text_color="white"
        ).pack(side="left", padx=(15, 0))

        # --- SEPARADOR ---
        ctk.CTkFrame(self, height=1, fg_color="#333333").pack(
            fill="x", padx=20, pady=(10, 5)
        )
        
        # --- CONTEÚDO PRINCIPAL ---
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=(5, 5))
        
        main_content.columnconfigure(0, weight=1, uniform="layout")
        main_content.columnconfigure(1, weight=1, uniform="layout")
        main_content.rowconfigure(0, weight=1, uniform="layout")
        main_content.rowconfigure(1, weight=1, uniform="layout")
        
        # 1. Monitor Mockup (Visualização da Área de Trabalho)
        monitor_container = ctk.CTkFrame(main_content, fg_color="#1E2029", border_color="#3d4153", border_width=1, corner_radius=10)
        monitor_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(monitor_container, text="Visualização da Área de Trabalho", font=("Segoe UI", 12, "bold"), text_color="gray").pack(pady=(8, 4))
        
        # O Monitor em si (300x168 para proporção 16:9 aprox)
        self.monitor_screen = ctk.CTkFrame(monitor_container, width=300, height=168, corner_radius=8, fg_color="#000000")
        self.monitor_screen.pack(pady=(0, 12), padx=20, expand=True)
        self.monitor_screen.pack_propagate(False)
        
        # Label para renderizar imagem de fundo no monitor
        self.lbl_monitor_bg = ctk.CTkLabel(self.monitor_screen, text="", bg_color="transparent")
        self.lbl_monitor_bg.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Barra de tarefas simulada no monitor
        self.sim_taskbar = ctk.CTkFrame(self.monitor_screen, height=16, fg_color="#181a21", corner_radius=0)
        self.sim_taskbar.pack(side="bottom", fill="x")
        
        # Container interno para os ícones da barra de tarefas
        self.sim_items_container = ctk.CTkFrame(self.sim_taskbar, height=16, fg_color="transparent")
        # Será empacotado/posicionado em atualizar_barra_tarefas_mockup()

        # 2. Switches de Tema e Efeitos (Ajustes Visuais do Windows)
        controls_card = ctk.CTkFrame(main_content, fg_color="#1E2029", border_color="#3d4153", border_width=1, corner_radius=10)
        controls_card.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(controls_card, text="Ajustes Visuais do Windows", font=("Segoe UI", 12, "bold"), text_color="white").pack(anchor="w", padx=16, pady=(12, 10))
        
        ctk.CTkLabel(controls_card, text="Tema do Windows:", font=("Segoe UI", 12), text_color="#aaaaaa").pack(anchor="w", padx=20, pady=(10, 4))
        
        tema_grid = ctk.CTkFrame(controls_card, fg_color="transparent")
        tema_grid.pack(fill="x", padx=20, pady=4)
        
        self.btn_tema_escuro = ctk.CTkButton(
            tema_grid, text="Escuro 🌙", width=110, height=35, corner_radius=6,
            fg_color="#181a21", hover_color="#282a36", text_color="white",
            border_width=0, border_color="#0078FB",
            font=("Segoe UI", 12, "bold"),
            command=lambda: self.selecionar_tema_com_confirmacao(True)
        )
        self.btn_tema_escuro.pack(side="left", padx=(0, 10))
        
        self.btn_tema_claro = ctk.CTkButton(
            tema_grid, text="Claro ☀️", width=110, height=35, corner_radius=6,
            fg_color="#e8e8f0", hover_color="#c8c8d0", text_color="#181a21",
            border_width=0, border_color="#0078FB",
            font=("Segoe UI", 12, "bold"),
            command=lambda: self.selecionar_tema_com_confirmacao(False)
        )
        self.btn_tema_claro.pack(side="left")
        
        self.switch_transparencia = ctk.CTkSwitch(
            controls_card, text="Efeitos de Transparência (Recomendado desativar)",
            font=("Segoe UI", 12), progress_color="#0078FB",
            command=self.toggle_transparencia
        )
        self.switch_transparencia.pack(anchor="w", padx=25, pady=(15, 10))

        # 3. Configurações da Barra de Tarefas
        taskbar_card = ctk.CTkFrame(main_content, fg_color="#1E2029", border_color="#3d4153", border_width=1, corner_radius=10)
        taskbar_card.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(taskbar_card, text="Configurações da Barra de Tarefas", font=("Segoe UI", 12, "bold"), text_color="white").pack(anchor="w", padx=16, pady=(12, 10))
        
        # Alinhamento
        align_row = ctk.CTkFrame(taskbar_card, fg_color="transparent")
        align_row.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(align_row, text="Alinhamento (Windows 11):", font=("Segoe UI", 12), text_color="#aaaaaa").pack(side="left")
        
        self.align_var = ctk.StringVar(value="Centro")
        self.option_align = ctk.CTkOptionMenu(
            align_row, values=["Centro", "Esquerda"],
            variable=self.align_var,
            fg_color="#343746", button_color="#343746", button_hover_color="#44475a",
            dropdown_fg_color="#1E2029", dropdown_hover_color="#343746",
            width=110, height=26,
            command=lambda v: self.alterar_alinhamento_taskbar()
        )
        self.option_align.pack(side="right")
        
        # Pesquisa
        search_row = ctk.CTkFrame(taskbar_card, fg_color="transparent")
        search_row.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(search_row, text="Pesquisa na Barra:", font=("Segoe UI", 12), text_color="#aaaaaa").pack(side="left")
        
        self.search_var = ctk.StringVar(value="Caixa de Pesquisa")
        self.option_search = ctk.CTkOptionMenu(
            search_row, values=["Caixa de Pesquisa", "Apenas Ícone", "Ocultar"],
            variable=self.search_var,
            fg_color="#343746", button_color="#343746", button_hover_color="#44475a",
            dropdown_fg_color="#1E2029", dropdown_hover_color="#343746",
            width=150, height=26,
            command=lambda v: self.alterar_pesquisa_taskbar()
        )
        self.option_search.pack(side="right")
        
        # Switch Visão de Tarefas
        self.switch_taskview = ctk.CTkSwitch(
            taskbar_card, text="Mostrar botão Visão de Tarefas",
            font=("Segoe UI", 12), progress_color="#0078FB",
            command=self.toggle_taskview
        )
        self.switch_taskview.pack(anchor="w", padx=25, pady=(8, 15))
        
        # 4. Plano de Fundo
        right_column = ctk.CTkFrame(main_content, fg_color="#1E2029", border_color="#3d4153", border_width=1, corner_radius=10)
        right_column.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Título da seção
        ctk.CTkLabel(right_column, text="Plano de Fundo", font=("Segoe UI", 14, "bold"), text_color="white").pack(anchor="w", padx=16, pady=(12, 4))
        ctk.CTkFrame(right_column, height=1, fg_color="#0078FB").pack(fill="x", padx=16, pady=(0, 10))
        
        # Dropdown Tipo de Fundo
        dropdown_frame = ctk.CTkFrame(right_column, fg_color="transparent")
        dropdown_frame.pack(fill="x", padx=16, pady=6)
        
        ctk.CTkLabel(dropdown_frame, text="Personalize seu plano de fundo:", font=("Segoe UI", 12, "bold"), text_color="#ffffff").pack(side="left")
        
        self.tipo_fundo_var = ctk.StringVar(value="Cor sólida")
        self.option_tipo = ctk.CTkOptionMenu(
            dropdown_frame, values=["Imagem", "Cor sólida"],
            variable=self.tipo_fundo_var,
            fg_color="#343746", button_color="#343746", button_hover_color="#44475a",
            dropdown_fg_color="#1E2029", dropdown_hover_color="#343746",
            width=120, height=28,
            command=lambda v: self.atualizar_visualizacao_tipo()
        )
        self.option_tipo.pack(side="right")
        
        # --- PAINÉIS DINÂMICOS DE FUNDO ---
        self.dynamic_content_frame = ctk.CTkFrame(right_column, fg_color="transparent")
        self.dynamic_content_frame.pack(fill="both", expand=True, padx=16, pady=10)
        
        # Criar painel de Cor Sólida
        self._criar_painel_cor_solida()
        # Criar painel de Imagem
        self._criar_painel_imagem()

    def _criar_painel_cor_solida(self):
        self.panel_cor = ctk.CTkFrame(self.dynamic_content_frame, fg_color="transparent")
        
        ctk.CTkLabel(self.panel_cor, text="Escolher a cor da tela de fundo:", font=("Segoe UI", 12), text_color="#aaaaaa").pack(anchor="w", pady=(0, 8))
        
        # Grade de Cores (8 colunas)
        colors_grid = ctk.CTkFrame(self.panel_cor, fg_color="transparent")
        colors_grid.pack(fill="x", pady=5)
        for i in range(8):
            colors_grid.grid_columnconfigure(i, weight=1)
            
        row, col = 0, 0
        for hex_color in PALETA_CORES:
            # Botão colorido como swatch
            btn = ctk.CTkButton(
                colors_grid, text="", width=32, height=32, corner_radius=4,
                fg_color=hex_color, hover_color=hex_color,
                border_width=0, border_color="#ffffff",
                command=lambda c=hex_color: self.selecionar_cor_paleta(c)
            )
            btn.grid(row=row, column=col, padx=4, pady=4)
            self.color_buttons[hex_color] = btn
            
            col += 1
            if col >= 8:
                col = 0
                row += 1
                
        # Botão Seletor de Cores Customizadas
        self.btn_picker = ctk.CTkButton(
            self.panel_cor, text="Mostrar as cores (Seletor)", width=180, height=32,
            fg_color="#343746", hover_color="#44475a", font=ctk.CTkFont(size=12, weight="bold"),
            command=self.abrir_seletor_cores
        )
        self.btn_picker.pack(anchor="w", pady=(15, 0))

    def _criar_painel_imagem(self):
        self.panel_imagem = ctk.CTkFrame(self.dynamic_content_frame, fg_color="transparent")
        
        ctk.CTkLabel(self.panel_imagem, text="Escolher uma imagem:", font=("Segoe UI", 12), text_color="#aaaaaa").pack(anchor="w", pady=(0, 6))
        
        input_row = ctk.CTkFrame(self.panel_imagem, fg_color="transparent")
        input_row.pack(fill="x", pady=4)
        
        self.btn_procurar = ctk.CTkButton(
            input_row, text="Procurar...", width=90, height=30,
            fg_color="#343746", hover_color="#44475a", font=ctk.CTkFont(size=12, weight="bold"),
            command=self.procurar_imagem
        )
        self.btn_procurar.pack(side="left")
        
        self.lbl_imagem_nome = ctk.CTkLabel(input_row, text="Nenhuma imagem selecionada", font=("Segoe UI", 11), text_color="gray", anchor="w")
        self.lbl_imagem_nome.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Preview da imagem selecionada
        self.img_preview_container = ctk.CTkFrame(self.panel_imagem, width=150, height=84, fg_color="#282A36", border_color="#3d4153", border_width=1)
        self.img_preview_container.pack(anchor="w", pady=(10, 15))
        self.img_preview_container.pack_propagate(False)
        
        self.lbl_img_preview = ctk.CTkLabel(self.img_preview_container, text="Sem Imagem", font=("Segoe UI", 10), text_color="gray")
        self.lbl_img_preview.pack(fill="both", expand=True)
        
        # Botão Aplicar Fundo de Imagem
        self.btn_aplicar_imagem = ctk.CTkButton(
            self.panel_imagem, text="Aplicar Imagem como Fundo", width=220, height=38,
            fg_color="#0078FB", hover_color="#005bc4", text_color="white", font=ctk.CTkFont(weight="bold"),
            command=self.aplicar_fundo_imagem
        )
        self.btn_aplicar_imagem.pack(anchor="w")

    def carregar_configuracoes_atuais(self):
        # 1. Wallpaper Atual
        try:
            hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop")
            wp, _ = winreg.QueryValueEx(hkey, "Wallpaper")
            winreg.CloseKey(hkey)
            self.wallpaper_atual = wp
        except Exception:
            self.wallpaper_atual = ""
            
        # 2. Cor Sólida Atual
        try:
            hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Colors")
            bg, _ = winreg.QueryValueEx(hkey, "Background")
            winreg.CloseKey(hkey)
            parts = bg.split()
            if len(parts) == 3:
                r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
                self.cor_atual = f"#{r:02x}{g:02x}{b:02x}"
            else:
                self.cor_atual = "#000000"
        except Exception:
            self.cor_atual = "#000000"
            
        # 3. Tema Escuro Ativo
        try:
            hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            apps_light, _ = winreg.QueryValueEx(hkey, "AppsUseLightTheme")
            self.tema_escuro_ativo = (apps_light == 0)
            winreg.CloseKey(hkey)
        except Exception:
            self.tema_escuro_ativo = True
            
        # 4. Transparência Ativa
        try:
            hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            trans, _ = winreg.QueryValueEx(hkey, "EnableTransparency")
            self.transparencia_ativa = (trans == 1)
            winreg.CloseKey(hkey)
        except Exception:
            self.transparencia_ativa = True

        # 5. Alinhamento da Barra de Tarefas
        try:
            hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced")
            align, _ = winreg.QueryValueEx(hkey, "TaskbarAl")
            winreg.CloseKey(hkey)
            self.align_var.set("Centro" if align == 1 else "Esquerda")
        except Exception:
            self.align_var.set("Centro")

        # 6. Modo de Pesquisa na Barra de Tarefas
        try:
            hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Search")
            mode, _ = winreg.QueryValueEx(hkey, "SearchboxTaskbarMode")
            winreg.CloseKey(hkey)
            if mode == 0:
                self.search_var.set("Ocultar")
            elif mode == 1:
                self.search_var.set("Apenas Ícone")
            else:
                self.search_var.set("Caixa de Pesquisa")
        except Exception:
            self.search_var.set("Caixa de Pesquisa")

        # 7. Botão Visão de Tarefas
        try:
            hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced")
            tv, _ = winreg.QueryValueEx(hkey, "ShowTaskViewButton")
            winreg.CloseKey(hkey)
            self.taskview_ativo = (tv == 1)
        except Exception:
            self.taskview_ativo = True
            
        # Determinar visualização inicial
        if not self.wallpaper_atual or not os.path.exists(self.wallpaper_atual):
            self.tipo_fundo_var.set("Cor sólida")
        else:
            self.tipo_fundo_var.set("Imagem")
            self.imagem_selecionada = self.wallpaper_atual
            self.lbl_imagem_nome.configure(text=os.path.basename(self.wallpaper_atual))
            self.atualizar_preview_imagem_selecionada()
            
        self.atualizar_visualizacao_tipo()
        self.atualizar_preview_monitor()
        self.atualizar_switches_ui()
        self.atualizar_barra_tarefas_mockup()
        self.destacar_cor_selecionada()

    def atualizar_visualizacao_tipo(self):
        tipo = self.tipo_fundo_var.get()
        if tipo == "Cor sólida":
            self.panel_imagem.pack_forget()
            self.panel_cor.pack(fill="both", expand=True)
        else:
            self.panel_cor.pack_forget()
            self.panel_imagem.pack(fill="both", expand=True)
        self.atualizar_preview_monitor()

    def atualizar_switches_ui(self):
        if self.tema_escuro_ativo:
            self.btn_tema_escuro.configure(border_width=2, border_color="#0078FB")
            self.btn_tema_claro.configure(border_width=0)
        else:
            self.btn_tema_escuro.configure(border_width=0)
            self.btn_tema_claro.configure(border_width=2, border_color="#0078FB")
            
        if self.transparencia_ativa:
            self.switch_transparencia.select()
        else:
            self.switch_transparencia.deselect()

        if self.taskview_ativo:
            self.switch_taskview.select()
        else:
            self.switch_taskview.deselect()

    def atualizar_preview_monitor(self):
        tipo = self.tipo_fundo_var.get()
        if tipo == "Cor sólida":
            self.lbl_monitor_bg.place_forget()
            self.monitor_screen.configure(fg_color=self.cor_atual)
        else:
            self.monitor_screen.configure(fg_color="#000000")
            path = self.imagem_selecionada if self.imagem_selecionada else self.wallpaper_atual
            if path and os.path.exists(path):
                try:
                    img = Image.open(path)
                    try:
                        resample = Image.Resampling.LANCZOS
                    except AttributeError:
                        resample = Image.LANCZOS
                    img_resized = img.resize((300, 168), resample)
                    self.monitor_bg_image_ctk = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, size=(300, 168))
                    
                    self.lbl_monitor_bg.configure(image=self.monitor_bg_image_ctk, fg_color="transparent")
                    self.lbl_monitor_bg.place(x=0, y=0, relwidth=1, relheight=1)
                    self.sim_taskbar.lift()
                except Exception as e:
                    self._log(f"[ERRO PREVIEW] Falha ao renderizar preview no monitor: {e}", tipo="red")
                    self.lbl_monitor_bg.place_forget()
            else:
                self.lbl_monitor_bg.place_forget()

    def destacar_cor_selecionada(self):
        # Limpar bordas
        for hex_color, btn in self.color_buttons.items():
            btn.configure(border_width=0)
            
        # Destacar cor selecionada se estiver na paleta
        current = self.cor_atual.lower()
        if current in self.color_buttons:
            self.color_buttons[current].configure(border_width=2)

    def selecionar_cor_paleta(self, hex_color):
        self.cor_atual = hex_color
        self.destacar_cor_selecionada()
        self.atualizar_preview_monitor()
        self.aplicar_cor_solida_sistema(hex_color)

    def abrir_seletor_cores(self):
        # Abre o seletor nativo do Tkinter
        cor = colorchooser.askcolor(initialcolor=self.cor_atual, title="Escolher Cor Sólida")
        if cor and cor[1]:
            hex_color = cor[1].lower()
            self.cor_atual = hex_color
            self.destacar_cor_selecionada()
            self.atualizar_preview_monitor()
            self.aplicar_cor_solida_sistema(hex_color)

    def aplicar_cor_solida_sistema(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # 1. Gravar chaves no Registro
        try:
            hkey_colors = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Colors", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(hkey_colors, "Background", 0, winreg.REG_SZ, f"{r} {g} {b}")
            winreg.CloseKey(hkey_colors)
            
            hkey_desktop = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(hkey_desktop, "Wallpaper", 0, winreg.REG_SZ, "")
            winreg.CloseKey(hkey_desktop)
            self.modificou_algo = True
        except Exception as e:
            self.master.log_mensagem(f"Erro ao salvar cor de fundo no Registro: {e}", tipo="red")
            return
            
        # 2. Aplicar cor na sessão atual imediatamente
        try:
            COLOR_BACKGROUND = 1
            colorref = r | (g << 8) | (b << 16)
            ctypes.windll.user32.SetSysColors(1, ctypes.byref(ctypes.c_int(COLOR_BACKGROUND)), ctypes.byref(ctypes.c_uint(colorref)))
            
            # Forçar Windows a limpar o papel de parede
            SPI_SETDESKWALLPAPER = 20
            SPIF_UPDATEINIFILE = 1
            SPIF_SENDCHANGE = 2
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, "", SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            
            self.master.log_mensagem(f"Plano de fundo definido para Cor Sólida ({hex_color.upper()}) com sucesso!")
            self.gravar_auditoria("Cor Sólida", cor_hex=hex_color)
        except Exception as e:
            self.master.log_mensagem(f"Erro ao aplicar cor de fundo na sessão: {e}", tipo="red")

    def procurar_imagem(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar Imagem de Plano de Fundo",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp"), ("Todos os arquivos", "*.*")]
        )
        if caminho:
            self.imagem_selecionada = caminho
            self.lbl_imagem_nome.configure(text=os.path.basename(caminho))
            self.atualizar_preview_imagem_selecionada()
            self.atualizar_preview_monitor()

    def atualizar_preview_imagem_selecionada(self):
        if not self.imagem_selecionada or not os.path.exists(self.imagem_selecionada):
            return
            
        try:
            for widget in self.img_preview_container.winfo_children():
                widget.destroy()
                
            img = Image.open(self.imagem_selecionada)
            try:
                resample = Image.Resampling.LANCZOS
            except AttributeError:
                resample = Image.LANCZOS
            img_resized = img.resize((150, 84), resample)
            self.preview_image_ctk = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, size=(150, 84))
            
            lbl = ctk.CTkLabel(self.img_preview_container, image=self.preview_image_ctk, text="")
            lbl.pack(fill="both", expand=True)
        except Exception as e:
            self._log(f"[ERRO PREVIEW] Falha ao renderizar miniatura da imagem selecionada: {e}", tipo="red")

    def aplicar_fundo_imagem(self):
        path = self.imagem_selecionada
        if not path or not os.path.exists(path):
            self.master.log_mensagem("Nenhuma imagem válida selecionada para aplicar.", tipo="red")
            return
            
        # 1. Gravar chaves no Registro
        try:
            hkey_desktop = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(hkey_desktop, "Wallpaper", 0, winreg.REG_SZ, path)
            winreg.SetValueEx(hkey_desktop, "WallpaperStyle", 0, winreg.REG_SZ, "10") # Ajuste preenchido (Fill)
            winreg.SetValueEx(hkey_desktop, "TileWallpaper", 0, winreg.REG_SZ, "0")
            winreg.CloseKey(hkey_desktop)
            self.modificou_algo = True
        except Exception as e:
            self.master.log_mensagem(f"Erro ao gravar caminho do papel de parede no Registro: {e}", tipo="red")
            return
            
        # 2. Aplicar papel de parede na sessão atual imediatamente
        try:
            SPI_SETDESKWALLPAPER = 20
            SPIF_UPDATEINIFILE = 1
            SPIF_SENDCHANGE = 2
            success = ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            if success:
                self.master.log_mensagem(f"Papel de parede de imagem aplicado com sucesso: {os.path.basename(path)}!")
                self.gravar_auditoria("Imagem", wallpaper_path=path)
            else:
                self.master.log_mensagem("O Windows falhou ao aceitar o novo papel de parede através da API.", tipo="red")
        except Exception as e:
            self.master.log_mensagem(f"Erro de chamada da API do Windows: {e}", tipo="red")

    def definir_tema_escuro(self, is_dark):
        val = 0 if is_dark else 1
        try:
            hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(hkey, "AppsUseLightTheme", 0, winreg.REG_DWORD, val)
            winreg.SetValueEx(hkey, "SystemUsesLightTheme", 0, winreg.REG_DWORD, val)
            winreg.CloseKey(hkey)
            self.tema_escuro_ativo = is_dark
            self.modificou_algo = True
            
            if is_dark:
                self.btn_tema_escuro.configure(border_width=2, border_color="#0078FB")
                self.btn_tema_claro.configure(border_width=0)
                status_txt = "Tema Escuro ativado!"
            else:
                self.btn_tema_escuro.configure(border_width=0)
                self.btn_tema_claro.configure(border_width=2, border_color="#0078FB")
                status_txt = "Tema Claro ativado!"
                
            self.master.log_mensagem(status_txt)
            self.gravar_auditoria("Tema Escuro" if is_dark else "Tema Claro")
            self.atualizar_barra_tarefas_mockup()
        except Exception as e:
            self.master.log_mensagem(f"Erro ao alterar Tema no Registro: {e}", tipo="red")

    def selecionar_tema_com_confirmacao(self, is_dark):
        if is_dark == self.tema_escuro_ativo:
            return
            
        from ui import modais
        tema_nome = "Escuro" if is_dark else "Claro"
        
        def confirmar_acao():
            self.definir_tema_escuro(is_dark)
            self.aplicar_alteracoes_globais()
            
        modais.abrir_modal_confirmacao(
            self.master,
            titulo=f"Alterar para Tema {tema_nome}",
            mensagem=(
                f"Você deseja alterar o tema do Windows para {tema_nome}?\n\n"
                "Para aplicar esta alteração visual e recarregar a barra de tarefas do Windows, "
                "o processo do Explorer será reiniciado e a barra de tarefas sumirá por alguns segundos "
                "(podendo variar de 5 a 15 segundos) antes de retornar ao normal.\n\n"
                "ADENDO: Para evitar quaisquer bugs visuais no sistema, o recomendado é reiniciar o "
                "computador, porém você pode fazer isso quando terminar todas as alterações no programa."
            ),
            comando_confirmar=confirmar_acao,
            categoria=self.categoria or "config_windows"
        )

    def toggle_transparencia(self):
        is_transparent = self.switch_transparencia.get()
        val = 1 if is_transparent else 0
        
        try:
            hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(hkey, "EnableTransparency", 0, winreg.REG_DWORD, val)
            winreg.CloseKey(hkey)
            self.modificou_algo = True
            
            status_txt = "Transparência reativada!" if is_transparent else "Transparência desativada (Visual)!"
            self.master.log_mensagem(status_txt)
            self.gravar_auditoria("Transparência Ativada" if is_transparent else "Transparência Desativada")
        except Exception as e:
            # Reverter switch se falhar
            self.switch_transparencia.toggle()
            self.master.log_mensagem(f"Erro ao alterar Transparência no Registro: {e}", tipo="red")

    def alterar_alinhamento_taskbar(self):
        val = 1 if self.align_var.get() == "Centro" else 0
        try:
            hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(hkey, "TaskbarAl", 0, winreg.REG_DWORD, val)
            winreg.CloseKey(hkey)
            self.modificou_algo = True
            self.master.log_mensagem(f"Alinhamento da Barra de Tarefas definido para: {self.align_var.get()} (Aplicar necessário)")
            self.atualizar_barra_tarefas_mockup()
        except Exception as e:
            self.master.log_mensagem(f"Erro ao alterar Alinhamento no Registro: {e}", tipo="red")

    def alterar_pesquisa_taskbar(self):
        mode_str = self.search_var.get()
        val = 3
        if mode_str == "Ocultar":
            val = 0
        elif mode_str == "Apenas Ícone":
            val = 1
        try:
            hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Search", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(hkey, "SearchboxTaskbarMode", 0, winreg.REG_DWORD, val)
            
            # Tentar gravar também o legacy SearchMode do Windows 10 para compatibilidade
            try:
                val_w10 = 2 if val == 3 else val
                winreg.SetValueEx(hkey, "SearchMode", 0, winreg.REG_DWORD, val_w10)
            except Exception:
                pass
                
            winreg.CloseKey(hkey)
            self.modificou_algo = True
            self.master.log_mensagem(f"Modo de Pesquisa na Barra definido para: {mode_str} (Aplicar necessário)")
            self.atualizar_barra_tarefas_mockup()
        except Exception as e:
            self.master.log_mensagem(f"Erro ao alterar Pesquisa no Registro: {e}", tipo="red")

    def toggle_taskview(self):
        is_on = self.switch_taskview.get()
        val = 1 if is_on else 0
        try:
            hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(hkey, "ShowTaskViewButton", 0, winreg.REG_DWORD, val)
            winreg.CloseKey(hkey)
            self.modificou_algo = True
            status = "exibido" if is_on else "ocultado"
            self.master.log_mensagem(f"Botão Visão de Tarefas {status} (Aplicar necessário)")
            self.atualizar_barra_tarefas_mockup()
        except Exception as e:
            self.switch_taskview.toggle()
            self.master.log_mensagem(f"Erro ao alterar Visão de Tarefas no Registro: {e}", tipo="red")

    def atualizar_barra_tarefas_mockup(self):
        try:
            align = self.align_var.get()
            search_mode = self.search_var.get()
            show_taskview = self.switch_taskview.get()
            
            # Atualizar cor da barra de tarefas de acordo com o tema ativo
            cor_barra = "#181a21" if self.tema_escuro_ativo else "#ffffff"
            self.sim_taskbar.configure(fg_color=cor_barra)
            
            for widget in self.sim_items_container.winfo_children():
                widget.destroy()
                
            self.sim_start = ctk.CTkFrame(self.sim_items_container, width=8, height=8, fg_color="#0078d7", corner_radius=1)
            self.sim_start.pack(side="left", padx=2, pady=4)
            
            if search_mode == "Caixa de Pesquisa":
                self.sim_search = ctk.CTkFrame(self.sim_items_container, width=35, height=8, fg_color="#343746", corner_radius=1)
                self.sim_search.pack(side="left", padx=2, pady=4)
                lupa = ctk.CTkFrame(self.sim_search, width=4, height=4, fg_color="gray", corner_radius=2)
                lupa.pack(side="left", padx=2, pady=2)
            elif search_mode == "Apenas Ícone":
                self.sim_search = ctk.CTkFrame(self.sim_items_container, width=8, height=8, fg_color="#343746", corner_radius=1)
                self.sim_search.pack(side="left", padx=2, pady=4)
                
            if show_taskview:
                self.sim_taskview = ctk.CTkFrame(self.sim_items_container, width=8, height=8, fg_color="#44475a", corner_radius=1)
                self.sim_taskview.pack(side="left", padx=2, pady=4)
                
            explorer_icon = ctk.CTkFrame(self.sim_items_container, width=8, height=8, fg_color="#ffb86c", corner_radius=1)
            explorer_icon.pack(side="left", padx=2, pady=4)
            
            browser_icon = ctk.CTkFrame(self.sim_items_container, width=8, height=8, fg_color="#8be9fd", corner_radius=1)
            browser_icon.pack(side="left", padx=2, pady=4)
            
            if align == "Centro":
                self.sim_items_container.place_forget()
                self.sim_items_container.place(relx=0.5, rely=0.5, anchor="center")
            else:
                self.sim_items_container.place_forget()
                self.sim_items_container.place(x=4, y=0, anchor="nw")
        except Exception as e:
            self._log(f"[ERRO MOCKUP BARRA] Falha ao atualizar mockup da barra de tarefas: {e}", tipo="red")

    def aplicar_alteracoes_globais(self):
        self.master.log_mensagem("Iniciando reinicialização do File Explorer para aplicar chaves da Barra de Tarefas...")
        try:
            import subprocess
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            # Finaliza o explorer de forma silenciosa
            subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], startupinfo=startupinfo, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Inicia o explorer novamente sem travar a thread da UI
            subprocess.Popen(["explorer.exe"], startupinfo=startupinfo)
            self.master.log_mensagem("File Explorer reiniciado com sucesso! Barra de tarefas atualizada.", tipo="green")
            self.gravar_auditoria("Reinicialização do Explorer")
        except Exception as e:
            self.master.log_mensagem(f"Erro ao reiniciar o File Explorer: {e}", tipo="red")

    def gravar_auditoria(self, tipo_alteracao, cor_hex="", wallpaper_path=""):
        data_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if tipo_alteracao == "Cor Sólida":
            desc = f"* **Tipo de Alteração:** Plano de fundo definido para Cor Sólida ({cor_hex.upper()}).\n"
            res = (f"HKCU\\Control Panel\\Colors -> Background: R G B correspondente a {cor_hex.upper()}\n"
                   f"HKCU\\Control Panel\\Desktop -> Wallpaper: (vazio)")
        elif tipo_alteracao == "Imagem":
            desc = f"* **Tipo de Alteração:** Papel de parede definido para Imagem: {wallpaper_path}.\n"
            res = f"HKCU\\Control Panel\\Desktop -> Wallpaper: {wallpaper_path}"
        elif tipo_alteracao == "Reinicialização do Explorer":
            desc = "* **Tipo de Alteração:** Reinicialização do processo explorer.exe para forçar recarregamento das chaves da Barra de Tarefas.\n"
            res = " explorer.exe reiniciado e chaves recarregadas."
        else:
            desc = f"* **Tipo de Alteração:** {tipo_alteracao} (Switches de tema/transparência/barra de tarefas).\n"
            res = r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize ou Explorer\Advanced modificado."

        entry = f"\n\n---\n\n# Plano de Verificação: Personalização Visual ({tipo_alteracao})\n**Data da Alteração:** {data_str}\n\n## 1. Alteração Realizada\n{desc}\n## 2. Comando de Auditoria Manual\nExecute os comandos abaixo no Prompt de Comando (CMD):\n```cmd\nreg query \"HKEY_CURRENT_USER\\Control Panel\\Colors\" /v Background\nreg query \"HKEY_CURRENT_USER\\Control Panel\\Desktop\" /v Wallpaper\nreg query \"HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize\"\nreg query \"HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced\"\nreg query \"HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Search\"\n```\n\n## 3. Resultado Esperado\nO terminal deve retornar chaves consistentes:\n```text\n{res}\n```\n"
        
        try:
            anexar_auditoria(entry)
        except Exception as e:
            self._log(f"[ERRO AUDITORIA] Falha ao gravar auditoria de personalizacao: {e}", tipo="red")

    def voltar(self):
        if self.modificou_algo and self.categoria and self.item_id and self.parent_btn:
            self.master.marcar_completado(self.categoria, self.item_id, self.parent_btn)
        self.master.abrir_categoria("config_windows")
