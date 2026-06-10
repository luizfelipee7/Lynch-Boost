import customtkinter as ctk
import winreg
from datetime import datetime
from core.auditoria import anexar_auditoria

class AudioDeviceManagerFrame(ctk.CTkFrame):
    def __init__(self, master, parent_btn=None, categoria=None, item_id=None):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        
        self.master = master
        self.parent_btn = parent_btn
        self.categoria = categoria
        self.item_id = item_id
        self.modificou_algo = False
        
        self._criar_layout()
        self.atualizar_dispositivos()

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
            header, text="🔊  Gerenciador de Som",
            font=ctk.CTkFont(size=22, weight="bold"), text_color="white"
        ).pack(side="left", padx=(15, 0))

        # --- SEPARADOR ---
        ctk.CTkFrame(self, height=1, fg_color="#333333").pack(
            fill="x", padx=20, pady=(10, 5)
        )
        
        # --- ÁREA PRINCIPAL ---
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=(5, 5))
        
        main_content.columnconfigure(0, weight=1, uniform="col")
        main_content.columnconfigure(1, weight=1, uniform="col")
        main_content.rowconfigure(0, weight=1)
        
        # COLUNA 1: Reprodução
        playback_container = ctk.CTkFrame(
            main_content, fg_color="#1E2029",
            border_color="#3d4153", border_width=1,
            corner_radius=10
        )
        playback_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        
        playback_title = ctk.CTkLabel(
            playback_container, text="🔊 Reprodução (Playback)",
            font=("Segoe UI", 14, "bold"), text_color="#ffffff"
        )
        playback_title.pack(anchor="w", padx=16, pady=(12, 4))
        
        ctk.CTkFrame(playback_container, height=1, fg_color="#0078FB").pack(fill="x", padx=16, pady=(0, 8))
        
        self.playback_scroll = ctk.CTkScrollableFrame(playback_container, fg_color="transparent")
        self.playback_scroll.pack(fill="both", expand=True, padx=6, pady=(0, 10))
        
        # COLUNA 2: Gravação
        recording_container = ctk.CTkFrame(
            main_content, fg_color="#1E2029",
            border_color="#3d4153", border_width=1,
            corner_radius=10
        )
        recording_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        
        recording_title = ctk.CTkLabel(
            recording_container, text="🎙️ Gravação (Capture)",
            font=("Segoe UI", 14, "bold"), text_color="#ffffff"
        )
        recording_title.pack(anchor="w", padx=16, pady=(12, 4))
        
        ctk.CTkFrame(recording_container, height=1, fg_color="#0078FB").pack(fill="x", padx=16, pady=(0, 8))
        
        self.recording_scroll = ctk.CTkScrollableFrame(recording_container, fg_color="transparent")
        self.recording_scroll.pack(fill="both", expand=True, padx=6, pady=(0, 10))

    def obter_dispositivos(self):
        playback = []
        recording = []
        
        for tipo, path in [("Render", r"SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Render"),
                           ("Capture", r"SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Capture")]:
            try:
                hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                num_subkeys = winreg.QueryInfoKey(hkey)[0]
                for i in range(num_subkeys):
                    guid = winreg.EnumKey(hkey, i)
                    dev_key = winreg.OpenKey(hkey, guid)
                    
                    try:
                        state, _ = winreg.QueryValueEx(dev_key, "DeviceState")
                        state = int(state)
                    except Exception:
                        state = 1
                        
                    # Filtrar apenas Ativos (1), Desabilitados (2) e Desconectados (8)
                    if (state & 0xF) not in (1, 2, 8):
                        winreg.CloseKey(dev_key)
                        continue
                        
                    try:
                        prop_key = winreg.OpenKey(dev_key, "Properties")
                        try:
                            name, _ = winreg.QueryValueEx(prop_key, "{a45c254e-df1c-4efd-8020-67d146a850e0},2")
                        except Exception:
                            name = "Dispositivo de Áudio"
                        try:
                            desc, _ = winreg.QueryValueEx(prop_key, "{b3f8fa53-0004-438e-9003-51a46e139bfc},6")
                        except Exception:
                            desc = ""
                        winreg.CloseKey(prop_key)
                    except Exception:
                        name = "Dispositivo de Áudio"
                        desc = ""
                        
                    winreg.CloseKey(dev_key)
                    
                    info = {
                        "guid": guid,
                        "name": name,
                        "desc": desc,
                        "state": state
                    }
                    if tipo == "Render":
                        playback.append(info)
                    else:
                        recording.append(info)
                winreg.CloseKey(hkey)
            except Exception as e:
                self._log(f"[ERRO AUDIO] Falha ao ler registro para {tipo}: {e}", tipo="red")
                
        return playback, recording

    def atualizar_dispositivos(self):
        for widget in self.playback_scroll.winfo_children():
            widget.destroy()
        for widget in self.recording_scroll.winfo_children():
            widget.destroy()
            
        playback, recording = self.obter_dispositivos()
        
        if not playback:
            lbl = ctk.CTkLabel(self.playback_scroll, text="Nenhum dispositivo de reprodução encontrado.", font=("Segoe UI", 11), text_color="gray")
            lbl.pack(pady=20)
        else:
            for dev in playback:
                self._criar_card_dispositivo(self.playback_scroll, dev["guid"], "Render", dev["name"], dev["desc"], dev["state"])
                
        if not recording:
            lbl = ctk.CTkLabel(self.recording_scroll, text="Nenhum dispositivo de gravação encontrado.", font=("Segoe UI", 11), text_color="gray")
            lbl.pack(pady=20)
        else:
            for dev in recording:
                self._criar_card_dispositivo(self.recording_scroll, dev["guid"], "Capture", dev["name"], dev["desc"], dev["state"])

    def _criar_card_dispositivo(self, parent, guid, tipo, name, desc, state):
        n = (name + " " + desc).lower()
        if "fone" in n or "headphone" in n or "ear" in n:
            emoji = "🎧"
        elif "alto-falante" in n or "speaker" in n:
            emoji = "🔊"
        elif "digital" in n or "spdif" in n or "s/pdif" in n:
            emoji = "🔌"
        elif "hdmi" in n or "nvidia" in n or "display" in n or "zowie" in n or "monitor" in n:
            emoji = "📺"
        elif "mixagem" in n or "stereo mix" in n:
            emoji = "🎛️"
        elif "microfone" in n or "mic" in n:
            emoji = "🎙️"
        else:
            emoji = "🔊" if tipo == "Render" else "🎙️"
            
        actual_state = state & 0xF
        if actual_state == 2:
            status_text = "Desabilitado"
            status_color = "#FF5555"
            card_fg = "#1E2029"
            card_border = "#282A36"
            switch_initial = False
        elif actual_state == 8:
            status_text = "Desconectado"
            status_color = "#E3B505"
            card_fg = "#343746"
            card_border = "#3a3d52"
            switch_initial = True
        else:
            status_text = "Ativo"
            status_color = "#22c55e"
            card_fg = "#343746"
            card_border = "#3a3d52"
            switch_initial = True
            
        # Obter estado inicial do Som Espacial para dispositivos de saída
        spatial_initial = False
        if tipo == "Render":
            try:
                path_prop = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Render\{guid}\Properties"
                hkey_prop = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path_prop)
                try:
                    spatial_val, _ = winreg.QueryValueEx(hkey_prop, "{f8d2c69d-0989-4cc6-b197-a9e152f3b5d3},3")
                    if str(spatial_val) == "{b53b4c27-1c42-4148-8533-507b42b6a0f7}":
                        spatial_initial = True
                except FileNotFoundError:
                    pass
                winreg.CloseKey(hkey_prop)
            except Exception:
                pass

        card = ctk.CTkFrame(
            parent,
            fg_color=card_fg,
            border_color=card_border,
            border_width=1,
            corner_radius=8
        )
        card.pack(fill="x", pady=4, padx=4)
        
        card.grid_columnconfigure(0, weight=0)
        card.grid_columnconfigure(1, weight=1)
        card.grid_columnconfigure(2, weight=0)
        
        ctk.CTkLabel(
            card, text=emoji,
            font=("Segoe UI Emoji", 20),
            width=36
        ).grid(row=0, column=0, rowspan=2, padx=(10, 5), pady=8, sticky="nsew")
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, rowspan=2, padx=5, pady=8, sticky="w")
        
        name_lbl = ctk.CTkLabel(
            info_frame, text=name,
            font=("Segoe UI", 12, "bold"), text_color="#ffffff",
            anchor="w"
        )
        name_lbl.pack(anchor="w")
        
        desc_lbl = ctk.CTkLabel(
            info_frame, text=desc if desc else "Dispositivo de Áudio do Sistema",
            font=("Segoe UI", 10), text_color="#aaaaaa",
            anchor="w"
        )
        desc_lbl.pack(anchor="w")
        
        status_lbl = ctk.CTkLabel(
            info_frame, text=status_text,
            font=("Segoe UI", 9, "bold"), text_color=status_color,
            anchor="w"
        )
        status_lbl.pack(anchor="w", pady=(2, 0))
        
        # Switch de Som Espacial (apenas para Reprodução)
        spatial_switch = None
        if tipo == "Render":
            spatial_var = ctk.BooleanVar(value=spatial_initial)
            spatial_switch = ctk.CTkSwitch(
                info_frame, text="Som Espacial (Sonic)",
                font=("Segoe UI", 10), progress_color="#0078FB",
                variable=spatial_var, height=18, width=32
            )
            spatial_switch.pack(anchor="w", pady=(4, 0))
            spatial_switch.configure(command=lambda g=guid, n=name, sw=spatial_switch, sv=spatial_var: self.toggle_spatial(g, n, sw, sv))
            
            if actual_state == 2:
                spatial_switch.configure(state="disabled")

        switch_var = ctk.BooleanVar(value=switch_initial)
        switch = ctk.CTkSwitch(
            card, text="",
            progress_color="#0078FB",
            width=40, height=20,
            variable=switch_var
        )
        switch.grid(row=0, column=2, rowspan=2, padx=(5, 12), pady=8, sticky="e")
        
        switch.configure(command=lambda g=guid, t=tipo, n=name, sw=switch, sl=status_lbl, c=card, sv=switch_var, sp_sw=spatial_switch: self.toggle_device(g, t, n, sw, sl, c, sv, sp_sw))

    def obter_estado_atual(self, guid, tipo):
        path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\{tipo}\{guid}"
        try:
            hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
            state, _ = winreg.QueryValueEx(hkey, "DeviceState")
            winreg.CloseKey(hkey)
            return int(state)
        except Exception:
            return 1

    def alterar_estado_dispositivo(self, guid, tipo, novo_estado):
        path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\{tipo}\{guid}"
        try:
            hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(hkey, "DeviceState", 0, winreg.REG_DWORD, novo_estado)
            winreg.CloseKey(hkey)
            return True
        except Exception as e:
            self._log(f"[ERRO AUDIO] Erro ao alterar registro: {e}", tipo="red")
            return False

    def toggle_device(self, guid, tipo, name, switch_widget, status_label, card_frame, switch_var, spatial_switch=None):
        is_on = switch_widget.get()
        target_state = 1 if is_on else 2
        
        success = self.alterar_estado_dispositivo(guid, tipo, target_state)
        
        if success:
            self.modificou_algo = True
            if target_state == 1:
                actual_state = self.obter_estado_atual(guid, tipo)
                if (actual_state & 0xF) == 8:
                    status_text = "Desconectado"
                    status_color = "#E3B505"
                else:
                    status_text = "Ativo"
                    status_color = "#22c55e"
                status_label.configure(text=status_text, text_color=status_color)
                card_frame.configure(fg_color="#343746", border_color="#3a3d52")
                self.master.log_mensagem(f"Dispositivo '{name}' ativado com sucesso! Estado: {status_text}.")
                
                if spatial_switch:
                    spatial_switch.configure(state="normal")
            else:
                status_label.configure(text="Desabilitado", text_color="#FF5555")
                card_frame.configure(fg_color="#1E2029", border_color="#282A36")
                self.master.log_mensagem(f"Dispositivo '{name}' desativado com sucesso!")
                
                if spatial_switch:
                    spatial_switch.configure(state="disabled")
            
            self.adicionar_auditoria_dispositivo(name, guid, tipo, target_state)
        else:
            switch_var.set(not is_on)
            self.master.log_mensagem(f"Falha ao alterar estado do dispositivo '{name}'. Verifique permissões.", tipo="red")

    def toggle_spatial(self, guid, name, switch_widget, switch_var):
        is_on = switch_widget.get()
        path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Render\{guid}\Properties"
        try:
            hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_SET_VALUE)
            if is_on:
                winreg.SetValueEx(hkey, "{f8d2c69d-0989-4cc6-b197-a9e152f3b5d3},3", 0, winreg.REG_SZ, "{b53b4c27-1c42-4148-8533-507b42b6a0f7}")
                self.master.log_mensagem(f"Som Espacial (Windows Sonic) ativado para '{name}'.")
            else:
                try:
                    winreg.DeleteValue(hkey, "{f8d2c69d-0989-4cc6-b197-a9e152f3b5d3},3")
                except FileNotFoundError:
                    pass
                self.master.log_mensagem(f"Som Espacial desativado para '{name}'.")
            winreg.CloseKey(hkey)
            self.modificou_algo = True
            
            self.adicionar_auditoria_spatial(name, guid, is_on)
        except Exception as e:
            switch_var.set(not is_on)
            self.master.log_mensagem(f"Falha ao alterar Som Espacial para '{name}'. Verifique permissões.", tipo="red")
            self._log(f"[ERRO AUDIO] Falha ao alterar som espacial: {e}", tipo="red")

    def adicionar_auditoria_dispositivo(self, name, guid, tipo, state):
        data_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state_str = "Ativado (1)" if state == 1 else "Desativado (2)"
        
        entry = f"\n\n---\n\n# Plano de Verificação: Estado de Dispositivo de Som\n**Data da Alteração:** {data_str}\n\n## 1. Alteração Realizada\n* **Impacto:** O dispositivo de som '{name}' ({tipo}) com GUID `{guid}` foi configurado como {state_str}.\n\n## 2. Comando de Auditoria Manual\nExecute o comando abaixo no Prompt de Comando (CMD):\n```cmd\nreg query \"HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\MMDevices\\Audio\\{tipo}\\{guid}\" /v DeviceState\n```\n\n## 3. Resultado Esperado\nO terminal deve retornar exatamente a seguinte linha:\n```text\nDeviceState    REG_DWORD    0x{state}\n```\n"
        
        try:
            anexar_auditoria(entry)
        except Exception as e:
            self._log(f"[ERRO AUDITORIA] Falha ao gravar auditoria: {e}", tipo="red")

    def adicionar_auditoria_spatial(self, name, guid, enabled):
        data_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state_str = "Ativado (Windows Sonic)" if enabled else "Desativado"
        
        entry = f"\n\n---\n\n# Plano de Verificação: Som Espacial (Windows Sonic)\n**Data da Alteração:** {data_str}\n\n## 1. Alteração Realizada\n* **Impacto:** O Som Espacial para o dispositivo de reprodução '{name}' com GUID `{guid}` foi configurado como {state_str}.\n\n## 2. Comando de Auditoria Manual\nExecute o comando abaixo no Prompt de Comando (CMD):\n```cmd\nreg query \"HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\MMDevices\\Audio\\Render\\{guid}\\Properties\" /v \"{{f8d2c69d-0989-4cc6-b197-a9e152f3b5d3}},3\"\n```\n\n## 3. Resultado Esperado\n* Quando ativado (Windows Sonic): o terminal deve retornar exatamente a seguinte linha:\n```text\n{{f8d2c69d-0989-4cc6-b197-a9e152f3b5d3}},3    REG_SZ    {{b53b4c27-1c42-4148-8533-507b42b6a0f7}}\n```\n* Quando desativado: a chave não deve constar no registro (retorna erro de valor não encontrado).\n"
        
        try:
            anexar_auditoria(entry)
        except Exception as e:
            self._log(f"[ERRO AUDITORIA] Falha ao gravar auditoria de som espacial: {e}", tipo="red")

    def voltar(self):
        if self.modificou_algo and self.categoria and self.item_id and self.parent_btn:
            self.master.marcar_completado(self.categoria, self.item_id, self.parent_btn)
        self.master.abrir_categoria("mouse_teclado")
