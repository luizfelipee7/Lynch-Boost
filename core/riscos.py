RISCO_SEGURO = "seguro"
RISCO_REVERSIVEL = "reversivel"
RISCO_DESTRUTIVO = "destrutivo"
RISCO_REQUER_REINICIO = "requer_reinicio"

RISCOS_VALIDOS = frozenset({
    RISCO_SEGURO,
    RISCO_REVERSIVEL,
    RISCO_DESTRUTIVO,
    RISCO_REQUER_REINICIO,
})

RISCOS_CONFIRMACAO_OBRIGATORIA = frozenset({
    RISCO_DESTRUTIVO,
    RISCO_REQUER_REINICIO,
})

RISCOS_ACOES = {
    "abrir_menu_desempenho": RISCO_REVERSIVEL,
    "abrir_modal_menu_contexto": RISCO_REVERSIVEL,
    "abrir_modal_explorer_this_pc": RISCO_REVERSIVEL,
    "abrir_modal_show_extensions": RISCO_REVERSIVEL,
    "abrir_modal_home_galeria": RISCO_REVERSIVEL,
    "abrir_modal_wsl_icon": RISCO_REVERSIVEL,
    "abrir_modal_fast_startup": RISCO_REVERSIVEL,
    "abrir_modal_finalizar_tarefa": RISCO_REVERSIVEL,
    "abrir_modal_desativar_popups": RISCO_REVERSIVEL,
    "executar_restaurar_relogio_para_hora_local_padrao": RISCO_REVERSIVEL,
    "executar_verificar_status_do_antivirus_wmi": RISCO_SEGURO,
    "abrir_menu_personalizacao": RISCO_REVERSIVEL,
    "abrir_modal_desativar_activity_feed": RISCO_REVERSIVEL,
    "executar_desativar_telemetria_e_rastreadores": RISCO_REVERSIVEL,
    "executar_desativar_manutencao_em_segundo_plano": RISCO_REVERSIVEL,
    "executar_otimizar_politicas_de_grupo_gpo": RISCO_REVERSIVEL,
    "executar_otimizar_servicos_do_windows": RISCO_REVERSIVEL,
    "executar_debloat_do_windows_11_moderno": RISCO_DESTRUTIVO,
    "executar_onedrive": RISCO_DESTRUTIVO,
    "abrir_modal_desativar_sincronizacao": RISCO_REVERSIVEL,
    "abrir_modal_desativar_experimentos": RISCO_REVERSIVEL,
    "executar_desinstalar_somente_xbox_game_bar": RISCO_DESTRUTIVO,
    "executar_limpar_cache_de_apps_e_browsers": RISCO_DESTRUTIVO,
    "executar_limpar_arquivos_temporarios": RISCO_DESTRUTIVO,
    "executar_desativar_hibernacao": RISCO_REVERSIVEL,
    "executar_manutencao_do_sistema_disco_e_rede": RISCO_REQUER_REINICIO,
    "executar_reparar_integridade_do_windows": RISCO_SEGURO,
    "executar_limpeza_do_armazenamento_de_componentes_winsxs": RISCO_DESTRUTIVO,
    "executar_corrigir_windows_update": RISCO_REVERSIVEL,
    "executar_apagar_pasta_windows_old": RISCO_DESTRUTIVO,
    "executar_bsod_event_log": RISCO_SEGURO,
    "executar_ativar_cache_de_gravacao_do_disco": RISCO_REVERSIVEL,
    "executar_otimizacao_inteligente_de_unidades": RISCO_SEGURO,
    "abrir_modal_latencia_disco": RISCO_REVERSIVEL,
    "abrir_modal_limpar_dispositivos": RISCO_REVERSIVEL,
    "abrir_modal_limpar_lixeira": RISCO_DESTRUTIVO,
    "abrir_modal_otimizar_memoria": RISCO_REVERSIVEL,
    "abrir_modal_limpar_cache_ram": RISCO_SEGURO,
    "abrir_menu_energia": RISCO_REVERSIVEL,
    "executar_cs2_high_cpu_priority": RISCO_REVERSIVEL,
    "executar_valorant_high_cpu_priority": RISCO_REVERSIVEL,
    "abrir_modal_ativar_game_mode": RISCO_REVERSIVEL,
    "abrir_modal_desativar_game_dvr": RISCO_REVERSIVEL,
    "abrir_menu_dns": RISCO_REVERSIVEL,
    "executar_reducao_global_de_latencia_ping_hardware": RISCO_REQUER_REINICIO,
    "executar_redefinir_configuracoes_de_rede": RISCO_REQUER_REINICIO,
    "abrir_modal_energia_amd": RISCO_REVERSIVEL,
    "abrir_modal_energia_intel": RISCO_REVERSIVEL,
    "abrir_modal_timer_coalescing": RISCO_REVERSIVEL,
    "abrir_modal_otimizar_gpu": RISCO_REVERSIVEL,
    "executar_otimizacao_de_gpu_global": RISCO_REVERSIVEL,
    "executar_limpar_cache_de_shaders_de_gpu": RISCO_DESTRUTIVO,
    "abrir_modal_seguranca_avancada": RISCO_REQUER_REINICIO,
    "abrir_menu_otimizacao": RISCO_REVERSIVEL,
    "abrir_modal_latencia_usb": RISCO_REVERSIVEL,
    "executar_importar_perfil_nvidia_lynch": RISCO_REVERSIVEL,
    "executar_eliminar_input_lag_competitivo": RISCO_REVERSIVEL,
    "abrir_modal_repeticao_teclado": RISCO_REVERSIVEL,
    "abrir_menu_mouse": RISCO_REVERSIVEL,
    "abrir_modal_sticky_keys": RISCO_REVERSIVEL,
    "abrir_modal_forcar_abnt2": RISCO_REVERSIVEL,
    "abrir_modal_teclado_eua": RISCO_REVERSIVEL,
    "abrir_menu_audio": RISCO_SEGURO,
    "abrir_menu_instalacao": RISCO_REVERSIVEL,
}


def risco_da_acao(acao_especial):
    return RISCOS_ACOES[acao_especial]


def risco_exige_confirmacao(risco):
    return risco in RISCOS_CONFIRMACAO_OBRIGATORIA
