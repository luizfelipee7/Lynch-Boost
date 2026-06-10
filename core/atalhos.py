import os
import subprocess

def abrir_inicializacao(logger=None):
    if logger: logger("Abrindo Gerenciador de Tarefas (Aba Inicializacao)...")
    subprocess.Popen(["taskmgr", "/0", "/startup"])

def abrir_energia(logger=None):
    if logger: logger("Abrindo Opcoes de Energia...")
    subprocess.Popen(["control.exe", "powercfg.cpl"])

def abrir_desempenho(logger=None):
    if logger: logger("Abrindo Opcoes de Desempenho (Memoria Virtual)...")
    subprocess.Popen(["SystemPropertiesPerformance.exe"])

def abrir_limpeza_disco(logger=None):
    if logger: logger("Abrindo Limpeza de Disco nativa...")
    subprocess.Popen(["cleanmgr.exe"])

def abrir_uac(logger=None):
    if logger: logger("Abrindo Controle de Conta (UAC)...")
    subprocess.Popen(["UserAccountControlSettings.exe"])

def abrir_armazenamento(logger=None):
    if logger: logger("Abrindo painel de Armazenamento do Windows...")
    os.startfile("ms-settings:storagesense")

def abrir_mouse(logger=None):
    if logger: logger("Abrindo Propriedades de Mouse (Opções de Ponteiro)...")
    subprocess.Popen(["control.exe", "main.cpl,,2"])

def abrir_programas_recursos(logger=None):
    if logger: logger("Abrindo Programas e Recursos (appwiz.cpl)...")
    subprocess.Popen(["control.exe", "appwiz.cpl"])

def abrir_desfragmentador(logger=None):
    if logger: logger("Abrindo Otimizador de Unidades nativo (Defrag/Trim)...")
    subprocess.Popen(["dfrgui.exe"])
