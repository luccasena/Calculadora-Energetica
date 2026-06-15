import streamlit as st

from src.data.data import carregar_presets
from src.lib.state import inicializar_estado
from src.styles.styles import aplicar_estilos
from src.styles.ui import (
    renderizar_cabecalho,
    renderizar_formulario_personalizado,
    renderizar_formulario_preset,
    renderizar_lista_aparelhos,
    renderizar_simulacao,
)


def main():
    st.set_page_config(
        page_title="Calculadora de Energia",
        page_icon="⚡",
        layout="wide",
    )

    aplicar_estilos()
    inicializar_estado()

    presets, aviso_csv = carregar_presets()

    renderizar_cabecalho(aviso_csv)
    renderizar_formulario_preset(presets)
    renderizar_formulario_personalizado()
    renderizar_lista_aparelhos()
    renderizar_simulacao()


if __name__ == "__main__":
    main()
