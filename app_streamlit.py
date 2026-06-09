import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora de Energia", page_icon="⚡", layout="wide")

st.markdown("""
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
div[data-testid="stForm"] textarea,
div[data-testid="stForm"] [data-baseweb="select"] > div,
div[data-testid="stForm"] [data-baseweb="base-input"],
div[data-testid="stForm"] .stNumberInput > div > div {
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

[data-testid="stDataFrame"] {
    background-color: rgb(8 31 100 / 20%);
    border-radius: 10px;
    border: 1px solid rgb(29 72 153 / 40%);
}
[data-testid="stDataFrame"] * { color: #021047 !important; }

/* Linha de item da lista */
.item-row {
    background: rgb(8 31 100 / 8%);
    border: 1px solid rgb(29 72 153 / 25%);
    border-radius: 8px;
    padding: 8px 14px;
    margin-bottom: 6px;
}

div[data-testid="stHorizontalBlock"] { align-items: center; }
</style>
""", unsafe_allow_html=True)

# ── Dados e estado ────────────────────────────────────────────────────────────
@st.cache_data
def carregar_presets():
    df = pd.read_csv("aparelhos_potencia.csv")
    return dict(zip(df["aparelho"], df["kwh"]))

PRESETS = carregar_presets()

def _init():
    defaults = {
        "pre_lista":  [],
        "cust_lista": [],
        "dashboard":  None,
        "edit_pre_idx":  None,
        "edit_cust_idx": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

st.image("img/percursor-analysis.png", width=400)
st.title("Calculadora de Gasto Energético")
st.caption("Preencha os aparelhos da sua residência e clique em **Gerar Cálculo** para ver os resultados. Os cálculos de tarifas são baseados na tabela oficial da **Energisa Paraíba** (Res. ANEEL nº 3.518/2025) e aplicam-se a consumidores residenciais da Paraíba.")
st.divider()

st.markdown("### Aparelhos Pré-configurados")
st.caption("Use a pesquisa para encontrar um aparelho. A potência é preenchida automaticamente.")

with st.form("form_pre"):
    preset = st.selectbox("Nome do aparelho", PRESETS, filter_mode="contains", )

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        marca_pre = st.text_input("Marca", placeholder="Ex: LG, Brastemp...")
    with c2:
        qtd_pre = st.number_input("Qtd.", min_value=1, max_value=20, value=1)
    with c3:
        horas_pre = st.number_input("Horas/dia", min_value=0.1, max_value=24.0, value=1.0, step=0.5)

    if add_pre := st.form_submit_button("Adicionar", type="primary", use_container_width=True):
        st.session_state.pre_lista.append({
            "Nome": preset,
            "Marca": marca_pre or "—",
            "Qtd.": qtd_pre,
            "Potência (kWh)": round(float(PRESETS[preset]), 3),
            "Horas/dia": horas_pre,
        })
        st.session_state.dashboard = None
        st.success(f"{preset} adicionado.")


if st.session_state.pre_lista:
    st.markdown("**Itens adicionados:**")
    for i, item in enumerate(st.session_state.pre_lista):
        col_info, col_edit, col_del = st.columns([7, 1, 1])
        with col_info:
            st.markdown(
                f"<div class='item-row'><b>{item['Nome']}</b> &nbsp;·&nbsp; {item['Marca']} "
                f"&nbsp;·&nbsp; {item['Qtd.']}× &nbsp;·&nbsp; "
                f"{item['Potência (kWh)']} kWh &nbsp;·&nbsp; {item['Horas/dia']}h/dia</div>",
                unsafe_allow_html=True,
            )
        with col_edit:
            if st.button("Editar", key=f"ep_{i}", help="Editar"):
                st.session_state.edit_pre_idx = i
                st.rerun()
        with col_del:
            if st.button("Remover", key=f"dp_{i}", help="Remover"):
                st.session_state.pre_lista.pop(i)
                st.session_state.dashboard = None
                if st.session_state.edit_pre_idx == i:
                    st.session_state.edit_pre_idx = None
                st.rerun()

    # Edição inline pré-configurado
    ei = st.session_state.edit_pre_idx
    if ei is not None and ei < len(st.session_state.pre_lista):
        item = st.session_state.pre_lista[ei]
        st.markdown(f"**Editando:** {item['Nome']}")
        with st.form("form_edit_pre"):
            # Pesquisa também disponível na edição
            busca_e = st.text_input("Alterar aparelho (opcional)", placeholder="Deixe em branco para manter")
            nomes_e = [n for n in PRESETS if busca_e.lower() in n.lower()] if busca_e else [item["Nome"]]
            nome_e = st.selectbox("Aparelho", nomes_e, index=0)

            ec1, ec2, ec3 = st.columns([2, 1, 1])
            with ec1:
                em = st.text_input("Marca", value=item["Marca"])
            with ec2:
                eq = st.number_input("Qtd.", min_value=1, max_value=20, value=int(item["Qtd."]))
            with ec3:
                eh = st.number_input("Horas/dia", min_value=0.1, max_value=24.0,
                                     value=float(item["Horas/dia"]), step=0.5)

            sc1, sc2 = st.columns(2)
            with sc1:
                if st.form_submit_button("Salvar", type="primary", use_container_width=True):
                    st.session_state.pre_lista[ei] = {
                        "Nome": nome_e,
                        "Marca": em or "—",
                        "Qtd.": eq,
                        "Potência (kWh)": round(float(PRESETS[nome_e]), 3),
                        "Horas/dia": eh,
                    }
                    st.session_state.edit_pre_idx = None
                    st.session_state.dashboard = None
                    st.rerun()
            with sc2:
                if st.form_submit_button("Cancelar", use_container_width=True):
                    st.session_state.edit_pre_idx = None
                    st.rerun()

    if st.button("Limpar pré-configurados", key="clear_pre"):
        st.session_state.pre_lista = []
        st.session_state.edit_pre_idx = None
        st.session_state.dashboard = None
        st.rerun()

st.divider()

st.markdown("### Aparelhos Personalizados")
st.caption("Cadastre aparelhos que não estão na lista ou com valores específicos do seu modelo.")

with st.form("form_custom"):
    c1, c2 = st.columns([3, 2])
    with c1:
        nome_c = st.text_input("Nome do aparelho", placeholder="Ex: Ar-condicionado portátil")
    with c2:
        marca_c = st.text_input("Marca", placeholder="Ex: Midea")

    c3, c4, c5 = st.columns(3)
    with c3:
        kwh_c = st.number_input("Potência (kWh)", min_value=0.001, value=0.100, step=0.001, format="%.3f")
    with c4:
        qtd_c = st.number_input("Qtd.", min_value=1, max_value=20, value=1)
    with c5:
        horas_c = st.number_input("Horas/dia", min_value=0.1, max_value=24.0, value=1.0, step=0.5)

    if add_c := st.form_submit_button("Adicionar personalizado", type="primary", use_container_width=True):
        if not nome_c.strip():
            st.error("Informe o nome do aparelho.")
        else:
            st.session_state.cust_lista.append({
                "Nome": nome_c.strip(),
                "Marca": marca_c or "—",
                "Qtd.": qtd_c,
                "Potência (kWh)": round(kwh_c, 3),
                "Horas/dia": horas_c,
            })
            st.session_state.dashboard = None
            st.success(f"{nome_c.strip()} adicionado.")

if st.session_state.cust_lista:
    st.markdown("**Itens adicionados:**")
    for i, item in enumerate(st.session_state.cust_lista):
        col_info, col_edit, col_del = st.columns([7, 1, 1])
        with col_info:
            st.markdown(
                f"<div class='item-row'><b>{item['Nome']}</b> &nbsp;·&nbsp; {item['Marca']} "
                f"&nbsp;·&nbsp; {item['Qtd.']}× &nbsp;·&nbsp; "
                f"{item['Potência (kWh)']} kWh &nbsp;·&nbsp; {item['Horas/dia']}h/dia</div>",
                unsafe_allow_html=True,
            )
        with col_edit:
            if st.button("Editar", key=f"ec_{i}", help="Editar"):
                st.session_state.edit_cust_idx = i
                st.rerun()
        with col_del:
            if st.button("Deletar", key=f"dc_{i}", help="Remover"):
                st.session_state.cust_lista.pop(i)
                st.session_state.dashboard = None
                if st.session_state.edit_cust_idx == i:
                    st.session_state.edit_cust_idx = None
                st.rerun()

    # Edição inline personalizado
    ci = st.session_state.edit_cust_idx
    if ci is not None and ci < len(st.session_state.cust_lista):
        item = st.session_state.cust_lista[ci]
        st.markdown(f"**Editando:** {item['Nome']}")
        with st.form("form_edit_cust"):
            cc1, cc2 = st.columns([3, 2])
            with cc1:
                cn = st.text_input("Nome", value=item["Nome"])
            with cc2:
                cm = st.text_input("Marca", value=item["Marca"])

            cc3, cc4, cc5 = st.columns(3)
            with cc3:
                ck = st.number_input("Potência (kWh)", min_value=0.001,
                                     value=float(item["Potência (kWh)"]), step=0.001, format="%.3f")
            with cc4:
                cq = st.number_input("Qtd.", min_value=1, max_value=20, value=int(item["Qtd."]))
            with cc5:
                ch = st.number_input("Horas/dia", min_value=0.1, max_value=24.0,
                                     value=float(item["Horas/dia"]), step=0.5)

            sc1, sc2 = st.columns(2)
            with sc1:
                if st.form_submit_button("Salvar", type="primary", use_container_width=True):
                    st.session_state.cust_lista[ci] = {
                        "Nome": cn.strip() or item["Nome"],
                        "Marca": cm or "—",
                        "Qtd.": cq,
                        "Potência (kWh)": round(ck, 3),
                        "Horas/dia": ch,
                    }
                    st.session_state.edit_cust_idx = None
                    st.session_state.dashboard = None
                    st.rerun()
            with sc2:
                if st.form_submit_button("✖️ Cancelar", use_container_width=True):
                    st.session_state.edit_cust_idx = None
                    st.rerun()

    if st.button("Limpar personalizados", key="clear_cust"):
        st.session_state.cust_lista = []
        st.session_state.edit_cust_idx = None
        st.session_state.dashboard = None
        st.rerun()

st.divider()

total_itens = len(st.session_state.pre_lista) + len(st.session_state.cust_lista)

if total_itens == 0:
    st.info("Adicione ao menos um aparelho para gerar o cálculo.")
else:
    st.markdown(f"**{total_itens} aparelho(s) cadastrado(s).** Pronto para calcular?")
    if st.button("Gerar Cálculo", type="primary", use_container_width=True):
        todos = []
        for item in st.session_state.pre_lista + st.session_state.cust_lista:
            consumo_d = item["Potência (kWh)"] * item["Horas/dia"] * item["Qtd."]
            todos.append({
                "Nome": item["Nome"],
                "Marca": item["Marca"],
                "Qtd.": item["Qtd."],
                "Potência (kWh)": item["Potência (kWh)"],
                "Horas/dia": item["Horas/dia"],
                "Consumo diário (kWh)": round(consumo_d, 3),
                "Consumo mensal (kWh)": round(consumo_d * 30, 2),
            })
        st.session_state.dashboard = todos


if st.session_state.dashboard:
    df = pd.DataFrame(st.session_state.dashboard)

    st.markdown("### Dashboard de Consumo")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.divider()

    total_kwh = df["Consumo mensal (kWh)"].sum()
    media_kwh = df["Consumo mensal (kWh)"].mean()
    maior     = df.loc[df["Consumo mensal (kWh)"].idxmax()]
    custo_min = total_kwh * 0.57492  # Residencial Baixa Renda acima de 80 kWh (Energisa PB)
    custo_max = total_kwh * 0.67565  # Residencial sem benefício (Energisa PB)

    ca, cb, cc = st.columns(3)
    with ca:
        st.metric("Maior consumidor", maior["Nome"],
                  f"{maior['Consumo mensal (kWh)']} kWh/mês")
    with cb:
        st.metric("Média por aparelho", f"{round(media_kwh, 2)} kWh/mês")
    with cc:
        st.metric("Conta de luz estimada",
                  f"R&#36; {custo_min:.2f} – R&#36; {custo_max:.2f}")

    st.divider()
    col_link, col_reset = st.columns(2)
    with col_link:
        st.link_button(
            "📄 Consultar tabela oficial de tarifas (Energisa PB)",
            url="https://www.energisa.com.br/sites/energisa/files/media/documents/2025-07/Quadro%20de%20Tarifas%20EPB-ATUAL.pdf",
            use_container_width=True,
        )
    with col_reset:
        if st.button("🔄 Resetar tudo e começar novamente", use_container_width=True, type="secondary"):
            for key in ["pre_lista", "cust_lista", "dashboard", "edit_pre_idx", "edit_cust_idx"]:
                st.session_state[key] = [] if key in ("pre_lista", "cust_lista") else None
            st.rerun()