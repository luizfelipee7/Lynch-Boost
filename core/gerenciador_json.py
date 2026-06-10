import json
import os

def ler_config_json(logger=None):
    # Como este arquivo esta dentro de 'core', precisamos voltar uma pasta (..)
    diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho_json = os.path.join(diretorio_base, "config.json")
    
    if not os.path.exists(caminho_json):
        if logger:
            logger(f"[ERRO] Arquivo config.json nao encontrado na rota:\n{caminho_json}")
        return None

    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        if logger:
            logger(f"[ERRO] Falha ao ler config.json: {e}")
        return None