import json
import os
import threading
from tkinter import filedialog

import customtkinter as ctk

from core import runner
from ui import modais


class MenuDesinstalarAppsWindows(ctk.CTkFrame):
    def __init__(self, master, log_callback=None, back_callback=None):
        super().__init__(master, fg_color="transparent")
        self.log_callback = log_callback
        self.back_callback = back_callback
        self.selected_apps = {}
        self.app_checkboxes = []
        self.category_frames_apps = {}

        self.lbl_contagem = None
        self.lbl_status = None
        self.progressbar = None
        self.btn_remover = None

        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.catalog_path = os.path.join(self.base_dir, "dados", "apps_windows_remocao.json")
        self.executor_path = "scripts/windows_tweaks/script_remover_apps_windows.ps1"

        self._popular_interface()

    def _popular_interface(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(12, 0))

        ctk.CTkButton(
            header,
            text="< Voltar",
            width=100,
            height=32,
            fg_color="#333333",
            hover_color="#555555",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._voltar,
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text="Desinstalar Windows Apps",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white",
        ).pack(side="left", padx=(15, 0))

        ctk.CTkButton(
            header,
            text="Exportar Perfil",
            width=125,
            height=32,
            fg_color="#1F4E79",
            hover_color="#296296",
            command=self.exportar_perfil,
        ).pack(side="right", padx=(5, 0))

        ctk.CTkButton(
            header,
            text="Importar Perfil",
            width=125,
            height=32,
            fg_color="#1F4E79",
            hover_color="#296296",
            command=self.importar_perfil,
        ).pack(side="right", padx=5)

        ctk.CTkFrame(self, height=1, fg_color="#333333").pack(
            fill="x", padx=20, pady=(10, 5)
        )

        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(5, 5))

        apps_data = self._carregar_apps()

        top_bar = ctk.CTkFrame(
            content,
            fg_color="#1A1A2E",
            corner_radius=10,
            border_width=1,
            border_color="#333333",
        )
        top_bar.pack(fill="x", pady=(0, 15))

        row1 = ctk.CTkFrame(top_bar, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            row1,
            text="Selecionar Tudo",
            width=125,
            fg_color="#333333",
            hover_color="#555555",
            command=self.selecionar_tudo,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            row1,
            text="Limpar Selecao",
            width=125,
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

        row2 = ctk.CTkFrame(top_bar, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(0, 10))

        self.btn_remover = ctk.CTkButton(
            row2,
            text="DESINSTALAR SELECIONADOS",
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            width=240,
            height=45,
            font=ctk.CTkFont(weight="bold", size=14),
            command=self.confirmar_remocao,
        )
        self.btn_remover.pack(side="right", padx=5)

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
            progress_color="#D32F2F",
            height=15,
        )
        self.progressbar.pack(fill="x", pady=(2, 0))
        self.progressbar.set(0)

        if not apps_data:
            self.lbl_status.configure(
                text="Catalogo de remocao nao encontrado ou vazio.",
                text_color="#FF0000",
            )
            return

        for categoria, apps in apps_data.items():
            self._criar_categoria_apps(content, categoria, apps)

    def _carregar_apps(self):
        if not os.path.exists(self.catalog_path):
            self._log(f"Catalogo de remocao nao encontrado: {self.catalog_path}")
            return {}

        try:
            with open(self.catalog_path, "r", encoding="utf-8") as file:
                apps_data = json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            self._log(f"Erro ao carregar catalogo de remocao: {exc}")
            return {}

        if not isinstance(apps_data, dict):
            self._log("Catalogo de remocao invalido: raiz JSON deve ser um objeto.")
            return {}
        return apps_data

    def _criar_categoria_apps(self, parent, categoria, apps):
        if not isinstance(apps, list):
            self._log(f"Categoria ignorada no catalogo de remocao: {categoria}")
            return

        cat_frame = ctk.CTkFrame(
            parent,
            fg_color="#1A1A2E",
            corner_radius=8,
            border_width=1,
            border_color="#2A2A3E",
        )
        cat_frame.pack(fill="x", pady=5)

        header = ctk.CTkFrame(cat_frame, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            header,
            text=str(categoria),
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left")

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

        for i in range(3):
            apps_container.grid_columnconfigure(i, weight=1, uniform="app_removal")

        for index, app in enumerate(apps):
            if not isinstance(app, dict) or "id" not in app or "nome" not in app:
                self._log(f"App ignorado na categoria {categoria}: entrada invalida.")
                continue

            row = index // 3
            col = index % 3
            wrap = ctk.CTkFrame(apps_container, fg_color="transparent")
            wrap.grid(row=row, column=col, sticky="w", pady=3, padx=2)

            chk = ctk.CTkCheckBox(
                wrap,
                text=app["nome"],
                font=ctk.CTkFont(size=12),
                checkbox_height=18,
                checkbox_width=18,
                command=lambda a=app: self.on_check(a),
            )
            chk.pack(anchor="w")

            if app.get("risco") in ("destrutivo", "requer_reinicio"):
                chk.configure(text_color="#F2C94C")

            self.app_checkboxes.append({"widget": chk, "wrapper": wrap, "app": app})

    def on_check(self, app):
        app_id = app["id"]
        checkbox = self._checkbox_por_id(app_id)
        if checkbox and checkbox.get() == 1:
            self.selected_apps[app_id] = app
        else:
            self.selected_apps.pop(app_id, None)
        self._atualizar_contagem()

    def selecionar_recomendados(self):
        self.limpar_selecao()
        for item in self.app_checkboxes:
            app = item["app"]
            if app.get("recomendado"):
                item["widget"].select()
                self.selected_apps[app["id"]] = app
        self._atualizar_contagem()
        self.lbl_status.configure(text="Preset recomendado selecionado.", text_color="#E3B505")

    def selecionar_tudo(self):
        for item in self.app_checkboxes:
            app = item["app"]
            item["widget"].select()
            self.selected_apps[app["id"]] = app
        self._atualizar_contagem()

    def limpar_selecao(self):
        for item in self.app_checkboxes:
            item["widget"].deselect()
        self.selected_apps.clear()
        self._atualizar_contagem()

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
            title="Salvar Perfil de Remocao de Apps",
        )
        if not filepath:
            return

        payload = {
            "tipo": "lynch_windows_apps_removal_profile",
            "versao": 1,
            "apps": sorted(self.selected_apps.keys()),
        }

        try:
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)
        except OSError as exc:
            self.lbl_status.configure(
                text="Erro ao salvar o perfil.",
                text_color="#FF0000",
            )
            self._log(f"Erro ao exportar perfil de remocao: {exc}")
            return

        self.lbl_status.configure(
            text=f"Perfil exportado: {os.path.basename(filepath)}",
            text_color="#4CAF50",
        )

    def importar_perfil(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Perfil Lynch", "*.json"), ("Todos os Arquivos", "*.*")],
            title="Carregar Perfil de Remocao de Apps",
        )
        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                payload = json.load(file)
            if isinstance(payload, dict):
                app_ids = payload.get("apps", [])
            else:
                app_ids = payload
            if not isinstance(app_ids, list):
                raise ValueError("Formato invalido")
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            self.lbl_status.configure(
                text="Erro ao carregar o perfil.",
                text_color="#FF0000",
            )
            self._log(f"Erro ao importar perfil de remocao: {exc}")
            return

        valid_ids = {item["app"]["id"] for item in self.app_checkboxes}
        imported_ids = {str(app_id) for app_id in app_ids}
        unknown_ids = sorted(imported_ids - valid_ids)

        self.limpar_selecao()
        for item in self.app_checkboxes:
            app = item["app"]
            if app["id"] in imported_ids:
                item["widget"].select()
                self.selected_apps[app["id"]] = app

        self._atualizar_contagem()
        if unknown_ids:
            self.lbl_status.configure(
                text=f"Perfil importado com {len(unknown_ids)} ID(s) ignorado(s).",
                text_color="#E3B505",
            )
            self._log(f"IDs ignorados no perfil de remocao: {', '.join(unknown_ids)}")
        else:
            self.lbl_status.configure(
                text=f"Perfil importado. {len(self.selected_apps)} app(s) selecionado(s).",
                text_color="#4CAF50",
            )

    def expandir_tudo(self):
        for container in self.category_frames_apps.values():
            container.pack(fill="x", padx=5, pady=(0, 5))

    def recolher_tudo(self):
        for container in self.category_frames_apps.values():
            container.pack_forget()

    def confirmar_remocao(self):
        if not self.selected_apps:
            self.lbl_status.configure(
                text="Erro: selecione pelo menos 1 app.",
                text_color="#FF0000",
            )
            return

        total = len(self.selected_apps)
        mensagem = (
            f"Esta acao vai remover {total} item(ns) selecionado(s) do Windows. "
            "Apps comuns serao removidos tambem da lista de provisionamento do sistema. "
            "Recursos do sistema podem exigir reinicializacao para concluir. Deseja continuar?"
        )

        modais.abrir_modal_confirmacao(
            self.winfo_toplevel(),
            "Confirmar desinstalacao de apps",
            mensagem,
            self.iniciar_remocao,
            lambda: self._log("Remocao de apps cancelada pelo usuario."),
            categoria="debloat_servicos",
        )

    def iniciar_remocao(self):
        self.btn_remover.configure(state="disabled")
        self.lbl_status.configure(text="Iniciando remocao...", text_color="#E3B505")
        self.progressbar.set(0)

        selected = list(self.selected_apps.values())
        threading.Thread(target=self._executar_remocao, args=(selected,), daemon=True).start()

    def _executar_remocao(self, selected):
        ids = ",".join(app["id"] for app in selected)
        self._set_status("Removendo apps e recursos selecionados...", "#E3B505")
        sucesso = runner.executar_arquivo(
            self.executor_path,
            self._log,
            ["-CatalogPath", self.catalog_path, "-Ids", ids],
        )
        self._finalizar_remocao(sucesso)

    def _finalizar_remocao(self, sucesso):
        if sucesso:
            self._set_progress(1, 1)
            self._set_status("Concluido. Apps selecionados foram processados.", "#4CAF50")
            self.after(0, self.limpar_selecao)
        else:
            self._set_status("Falha ao processar remocao. Veja o log.", "#FF0000")
        self.after(0, lambda: self.btn_remover.configure(state="normal"))

    def _checkbox_por_id(self, app_id):
        for item in self.app_checkboxes:
            if item["app"]["id"] == app_id:
                return item["widget"]
        return None

    def _atualizar_contagem(self):
        if self.lbl_contagem:
            self.lbl_contagem.configure(text=f"Selecionados: {len(self.selected_apps)}")

    def _set_status(self, text, color):
        self.after(0, lambda: self.lbl_status.configure(text=text, text_color=color))

    def _set_progress(self, completed, total):
        if total <= 0:
            value = 0
        else:
            value = completed / total
        self.after(0, lambda: self.progressbar.set(value))

    def _voltar(self):
        if callable(self.back_callback):
            self.back_callback()

    def _log(self, mensagem):
        if self.log_callback:
            try:
                self.after(0, lambda msg=mensagem: self.log_callback(msg))
            except Exception:
                self.log_callback(mensagem)
