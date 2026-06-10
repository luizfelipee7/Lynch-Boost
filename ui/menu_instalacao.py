import json
import os
import subprocess
import threading
from tkinter import filedialog

import customtkinter as ctk

from ui import modais


CREATE_NO_WINDOW = 0x08000000


class MenuInstalacao(ctk.CTkFrame):
    def __init__(self, master, log_callback=None):
        super().__init__(master, fg_color="transparent")
        self.log_callback = log_callback
        self.selected_apps = {}
        self.app_checkboxes = []
        self.category_frames_apps = {}

        self.switch_foss = None
        self.lbl_contagem = None
        self.lbl_status = None
        self.progressbar = None
        self.btn_instalar = None

        self._popular_interface()

    def _popular_interface(self):
        apps_data = self._carregar_apps()

        top_bar = ctk.CTkFrame(
            self,
            fg_color="#1A1A2E",
            corner_radius=10,
            border_width=1,
            border_color="#333333",
        )
        top_bar.pack(fill="x", pady=(0, 15))

        row1 = ctk.CTkFrame(top_bar, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=10)

        self.switch_foss = ctk.CTkSwitch(
            row1,
            text="Destacar FOSS (Livres)",
            command=self.toggle_foss,
            progress_color="#4CAF50",
        )
        self.switch_foss.pack(side="left", padx=10)

        ctk.CTkButton(
            row1,
            text="Limpar Selecao",
            width=110,
            fg_color="#333333",
            hover_color="#555555",
            command=self.limpar_selecao,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            row1,
            text="Expandir Tudo",
            width=110,
            fg_color="#333333",
            hover_color="#555555",
            command=self.expandir_tudo,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            row1,
            text="Recolher Tudo",
            width=110,
            fg_color="#333333",
            hover_color="#555555",
            command=self.recolher_tudo,
        ).pack(side="left", padx=5)

        self.lbl_contagem = ctk.CTkLabel(
            row1,
            text="Selecionados: 0",
            font=ctk.CTkFont(weight="bold", size=14),
            text_color="#E3B505",
        )
        self.lbl_contagem.pack(side="right", padx=15)

        row_perfil = ctk.CTkFrame(top_bar, fg_color="transparent")
        row_perfil.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkButton(
            row_perfil,
            text="Exportar Perfil",
            width=140,
            fg_color="#1F4E79",
            hover_color="#296296",
            command=self.exportar_perfil,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            row_perfil,
            text="Importar Perfil",
            width=140,
            fg_color="#1F4E79",
            hover_color="#296296",
            command=self.importar_perfil,
        ).pack(side="left", padx=5)

        row2 = ctk.CTkFrame(top_bar, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(0, 10))

        self.btn_instalar = ctk.CTkButton(
            row2,
            text="INSTALAR SELECIONADOS",
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            width=200,
            height=45,
            font=ctk.CTkFont(weight="bold", size=14),
            command=self.iniciar_instalacao,
        )
        self.btn_instalar.pack(side="right", padx=5)

        progress_container = ctk.CTkFrame(row2, fg_color="transparent")
        progress_container.pack(side="left", fill="both", expand=True, padx=(10, 20))

        self.lbl_status = ctk.CTkLabel(
            progress_container,
            text="Aguardando selecao...",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.lbl_status.pack(anchor="w")

        self.progressbar = ctk.CTkProgressBar(
            progress_container,
            mode="determinate",
            fg_color="#11111A",
            progress_color="#4CAF50",
            height=15,
        )
        self.progressbar.pack(fill="x", pady=(2, 0))
        self.progressbar.set(0)

        if not apps_data:
            self.lbl_status.configure(
                text="Catalogo de apps nao encontrado ou vazio.",
                text_color="#FF0000",
            )
            return

        for categoria, apps in apps_data.items():
            self._criar_categoria_apps(categoria, apps)

    def _carregar_apps(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        apps_file = os.path.abspath(os.path.join(base_dir, "..", "dados", "apps.json"))
        if not os.path.exists(apps_file):
            self._log(f"Catalogo de apps nao encontrado: {apps_file}")
            return {}

        try:
            with open(apps_file, "r", encoding="utf-8") as file:
                apps_data = json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            self._log(f"Erro ao carregar catalogo de apps: {exc}")
            return {}

        if not isinstance(apps_data, dict):
            self._log("Catalogo de apps invalido: raiz JSON deve ser um objeto.")
            return {}
        return apps_data

    def _criar_categoria_apps(self, categoria, apps):
        if not isinstance(apps, list):
            self._log(f"Categoria ignorada no catalogo de apps: {categoria}")
            return

        cat_frame = ctk.CTkFrame(
            self,
            fg_color="#1A1A2E",
            corner_radius=8,
            border_width=1,
            border_color="#2A2A3E",
        )
        cat_frame.pack(fill="x", pady=5)

        header = ctk.CTkFrame(cat_frame, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=5)

        lbl_cat = ctk.CTkLabel(
            header,
            text=str(categoria),
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        lbl_cat.pack(side="left")

        apps_container = ctk.CTkFrame(cat_frame, fg_color="transparent")
        apps_container.pack(fill="x", padx=5, pady=(0, 5))

        def toggle_cat(container=apps_container):
            if container.winfo_ismapped():
                container.pack_forget()
            else:
                container.pack(fill="x", padx=5, pady=(0, 5))

        ctk.CTkButton(
            header,
            text="v",
            width=30,
            height=20,
            fg_color="transparent",
            hover_color="#333333",
            command=toggle_cat,
        ).pack(side="right")

        self.category_frames_apps[categoria] = apps_container

        for i in range(4):
            apps_container.grid_columnconfigure(i, weight=1, uniform="app")

        for i, app in enumerate(apps):
            if not isinstance(app, dict) or "id" not in app or "nome" not in app:
                self._log(f"App ignorado na categoria {categoria}: entrada invalida.")
                continue

            row = i // 4
            col = i % 4
            wrap = ctk.CTkFrame(apps_container, fg_color="transparent")
            wrap.grid(row=row, column=col, sticky="w", pady=2, padx=2)

            chk = ctk.CTkCheckBox(
                wrap,
                text=app["nome"],
                font=ctk.CTkFont(size=12),
                checkbox_height=18,
                checkbox_width=18,
                command=lambda a=app: self.on_check(a),
            )
            chk.pack(anchor="w")
            self.app_checkboxes.append({"widget": chk, "wrapper": wrap, "app": app})

    def on_check(self, app):
        app_id = app["id"]
        chk_widget = next(
            (item["widget"] for item in self.app_checkboxes if item["app"]["id"] == app_id),
            None,
        )
        if chk_widget and chk_widget.get() == 1:
            self.selected_apps[app_id] = app["nome"]
        else:
            self.selected_apps.pop(app_id, None)
        self.lbl_contagem.configure(text=f"Selecionados: {len(self.selected_apps)}")

    def toggle_foss(self):
        highlight = self.switch_foss.get() == 1
        for item in self.app_checkboxes:
            if item["app"].get("foss"):
                if highlight:
                    item["widget"].configure(
                        text_color="#4CAF50",
                        font=ctk.CTkFont(size=12, weight="bold"),
                    )
                else:
                    item["widget"].configure(
                        text_color=["gray10", "#DCE4EE"],
                        font=ctk.CTkFont(size=12, weight="normal"),
                    )

    def limpar_selecao(self):
        for item in self.app_checkboxes:
            item["widget"].deselect()
        self.selected_apps.clear()
        self.lbl_contagem.configure(text="Selecionados: 0")

    def expandir_tudo(self):
        for container in self.category_frames_apps.values():
            container.pack(fill="x", padx=5, pady=(0, 5))

    def recolher_tudo(self):
        for container in self.category_frames_apps.values():
            container.pack_forget()

    def exportar_perfil(self):
        if not self.selected_apps:
            self.lbl_status.configure(
                text="Erro: selecione pelo menos 1 app para exportar.",
                text_color="#FF0000",
            )
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Perfil Lynch", "*.json"), ("Todos os Arquivos", "*.*")],
            title="Salvar Perfil de Instalacao",
        )
        if not filepath:
            return

        try:
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(list(self.selected_apps.keys()), file, indent=4)
        except OSError as exc:
            self.lbl_status.configure(
                text="Erro ao salvar o arquivo de perfil.",
                text_color="#FF0000",
            )
            self._log(f"Erro ao salvar perfil de instalacao: {exc}")
            return

        self.lbl_status.configure(
            text=f"Perfil salvo em: {os.path.basename(filepath)}",
            text_color="#4CAF50",
        )

    def importar_perfil(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Perfil Lynch", "*.json"), ("Todos os Arquivos", "*.*")],
            title="Carregar Perfil de Instalacao",
        )
        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                apps_importados = json.load(file)
            if not isinstance(apps_importados, list):
                raise ValueError("Formato invalido")
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            self.lbl_status.configure(
                text="Erro ao carregar o arquivo de perfil.",
                text_color="#FF0000",
            )
            self._log(f"Erro ao importar perfil de instalacao: {exc}")
            return

        self.limpar_selecao()
        count = 0
        apps_importados = set(apps_importados)
        for item in self.app_checkboxes:
            app = item["app"]
            if app["id"] in apps_importados:
                item["widget"].select()
                self.selected_apps[app["id"]] = app["nome"]
                count += 1

        self.lbl_contagem.configure(text=f"Selecionados: {len(self.selected_apps)}")
        self.lbl_status.configure(
            text=f"Perfil importado. {count} apps selecionados.",
            text_color="#4CAF50",
        )

    def iniciar_instalacao(self):
        if not self.selected_apps:
            self.lbl_status.configure(
                text="Erro: selecione pelo menos 1 app.",
                text_color="#FF0000",
            )
            return

        self.btn_instalar.configure(state="disabled")
        self.lbl_status.configure(text="Configurando caminhos...", text_color="#E3B505")
        self.progressbar.set(0)

        apps_to_install = list(self.selected_apps.items())
        caminhos_customizados = {}
        base_path_global = None
        final_apps_to_install = []

        for i, (app_id, app_name) in enumerate(apps_to_install):
            if base_path_global:
                caminhos_customizados[app_id] = os.path.join(
                    base_path_global,
                    app_name.replace(" ", ""),
                )
                final_apps_to_install.append((app_id, app_name))
                continue

            modal = modais.ModalInstalacaoCaminho(
                self.winfo_toplevel(),
                app_name,
                is_first_app=(i == 0),
            )
            self.wait_window(modal)

            if getattr(modal, "cancelar_tudo", False):
                final_apps_to_install = []
                break

            if getattr(modal, "cancelado", False):
                continue

            final_apps_to_install.append((app_id, app_name))
            if not getattr(modal, "ignorar", False) and getattr(modal, "resultado_caminho", None):
                caminhos_customizados[app_id] = modal.resultado_caminho
                chk_todos_var = getattr(modal, "chk_todos_var", None)
                aplicar_todos = bool(chk_todos_var.get()) if chk_todos_var is not None else False
                if aplicar_todos:
                    base_path_global = os.path.dirname(modal.resultado_caminho)
            else:
                caminhos_customizados[app_id] = None

        if not final_apps_to_install:
            self.lbl_status.configure(
                text="Aguardando selecao...",
                text_color=["gray10", "#DCE4EE"],
            )
            self.btn_instalar.configure(state="normal")
            return

        self.lbl_status.configure(text="Iniciando instalacao...", text_color="#E3B505")
        threading.Thread(
            target=self._executar_instalacao,
            args=(final_apps_to_install, caminhos_customizados),
            daemon=True,
        ).start()

    def _executar_instalacao(self, final_apps_to_install, caminhos_customizados):
        total = len(final_apps_to_install)
        for index, (app_id, app_name) in enumerate(final_apps_to_install):
            progress = index / total
            percent = int(progress * 100)
            self.after(0, lambda p=progress: self.progressbar.set(p))
            self.after(
                0,
                lambda n=app_name, idx=index, t=total, pc=percent: self.lbl_status.configure(
                    text=f"Instalando {n} ({idx + 1}/{t}) - {pc}% concluido",
                    text_color="#E3B505",
                ),
            )

            comando = [
                "winget",
                "install",
                "--id",
                app_id,
                "--exact",
                "--silent",
                "--accept-source-agreements",
                "--accept-package-agreements",
            ]

            caminho = caminhos_customizados.get(app_id)
            if caminho:
                comando.extend(["--location", caminho])

            try:
                subprocess.run(
                    comando,
                    check=True,
                    creationflags=CREATE_NO_WINDOW,
                    capture_output=True,
                    text=True,
                )
                self._log(f"App instalado via Winget: {app_name}")
            except FileNotFoundError:
                self._log("Erro ao instalar apps: winget nao foi encontrado no sistema.")
                break
            except subprocess.CalledProcessError as exc:
                detalhe = (exc.stderr or exc.stdout or "").strip()
                if detalhe:
                    self._log(f"Erro ao instalar {app_name}: {detalhe}")
                else:
                    self._log(f"Erro ao instalar {app_name}: Winget retornou codigo {exc.returncode}.")

        self.after(0, lambda: self.progressbar.set(1.0))
        self.after(
            0,
            lambda: self.lbl_status.configure(
                text="Concluido. Todos os apps foram processados - 100%",
                text_color="#4CAF50",
            ),
        )
        self.after(0, lambda: self.btn_instalar.configure(state="normal"))
        self.after(0, self.limpar_selecao)

    def _log(self, mensagem):
        if self.log_callback:
            try:
                self.after(0, lambda msg=mensagem: self.log_callback(msg))
            except Exception:
                self.log_callback(mensagem)
