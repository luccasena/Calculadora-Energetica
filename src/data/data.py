from pathlib import Path

import pandas as pd
import streamlit as st

from src.lib.config import PRESETS_CSV_PATH


PRESETS_PADRAO = {
    "Ar-condicionado": 1200.0,
    "Chuveiro elétrico": 5500.0,
    "Computador": 300.0,
    "Ferro de passar": 1000.0,
    "Geladeira": 150.0,
    "Lâmpada LED": 10.0,
    "Micro-ondas": 1400.0,
    "Televisão": 100.0,
    "Ventilador": 80.0,
}


@st.cache_data
def carregar_presets(caminho_csv=PRESETS_CSV_PATH):
    """Carrega o CSV antigo e converte a potência para watts."""
    caminho = Path(caminho_csv)

    if not caminho.exists():
        return PRESETS_PADRAO, "Arquivo de aparelhos não encontrado; usando lista básica."

    try:
        df = pd.read_csv(caminho)

        if "aparelho" not in df.columns:
            raise ValueError("coluna 'aparelho' ausente")

        if "potencia_w" in df.columns:
            potencia = pd.to_numeric(df["potencia_w"], errors="coerce")
        elif "w" in df.columns:
            potencia = pd.to_numeric(df["w"], errors="coerce")
        elif "kw" in df.columns:
            potencia = pd.to_numeric(df["kw"], errors="coerce") * 1000
        elif "kwh" in df.columns:
            potencia = pd.to_numeric(df["kwh"], errors="coerce") * 1000
        else:
            raise ValueError("coluna de potência ausente")

        dados = pd.DataFrame(
            {
                "aparelho": df["aparelho"].astype(str).str.strip(),
                "potencia_w": potencia,
            }
        ).dropna()

        dados = dados[(dados["aparelho"] != "") & (dados["potencia_w"] > 0)]

        if dados.empty:
            raise ValueError("nenhum aparelho válido")

        return dict(zip(dados["aparelho"], dados["potencia_w"])), None

    except Exception as erro:
        return PRESETS_PADRAO, f"Não foi possível ler o CSV ({erro}); usando lista básica."

