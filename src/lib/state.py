import streamlit as st


def inicializar_estado():
    if "aparelhos" not in st.session_state:
        st.session_state.aparelhos = []
    if "dashboard" not in st.session_state:
        st.session_state.dashboard = None
    if "edit_id" not in st.session_state:
        st.session_state.edit_id = None
    if "next_id" not in st.session_state:
        st.session_state.next_id = 1


def invalidar_dashboard():
    st.session_state.dashboard = None


def adicionar_aparelho(nome, potencia_w, quantidade, horas_dia):
    st.session_state.aparelhos.append(
        {
            "id": st.session_state.next_id,
            "nome": nome.strip(),
            "potencia_w": float(potencia_w),
            "quantidade": int(quantidade),
            "horas_dia": float(horas_dia),
        }
    )
    st.session_state.next_id += 1
    invalidar_dashboard()


def remover_aparelho(aparelho_id):
    st.session_state.aparelhos = [
        item for item in st.session_state.aparelhos if item["id"] != aparelho_id
    ]
    st.session_state.edit_id = None
    invalidar_dashboard()


def limpar_aparelhos():
    st.session_state.aparelhos = []
    st.session_state.edit_id = None
    invalidar_dashboard()


def resetar_simulacao():
    limpar_aparelhos()
    st.session_state.next_id = 1


def buscar_aparelho_em_edicao():
    return next(
        (
            item
            for item in st.session_state.aparelhos
            if item["id"] == st.session_state.edit_id
        ),
        None,
    )

