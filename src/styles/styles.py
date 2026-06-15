import streamlit as st


def aplicar_estilos():
    st.markdown(
        """
        <style>
        h1, h2, h3, h4 { color: #021047 !important; }

        div[data-testid="stForm"] {
            background-color: rgb(8 31 100 / 12%);
            border: 1px solid rgb(29 72 153 / 30%);
            border-radius: 12px;
            padding: 20px 24px;
        }

        div[data-testid="stForm"] label,
        div[data-testid="stForm"] p { color: #021047 !important; }

        div[data-testid="stForm"] input,
        div[data-testid="stForm"] [data-baseweb="select"] > div {
            background-color: rgb(8 31 100 / 20%) !important;
            border-color: rgb(29 72 153 / 50%) !important;
            color: #021047 !important;
        }

        [data-testid="metric-container"] {
            background-color: #081F64;
            border: 1px solid #1D4899;
            border-radius: 10px;
            padding: 16px 20px;
        }

        [data-testid="metric-container"] * { color: #FEFEFE !important; }

        .item-row {
            background: rgb(8 31 100 / 8%);
            border: 1px solid rgb(29 72 153 / 25%);
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 6px;
        }

        div[data-testid="stHorizontalBlock"] { align-items: center; }
        </style>
        """,
        unsafe_allow_html=True,
    )

