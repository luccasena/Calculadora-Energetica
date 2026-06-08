import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora de Gasto Energético", page_icon="⚡", layout="wide")

st.markdown("""
<style>
/* Formulário com fundo escuro */
div[data-testid="stForm"] {
    background-color: rgb(8 31 100 / 20%);
    border-radius: 12px;
    padding: 24px;
}
div[data-testid="stForm"] label,
div[data-testid="stForm"] p,
div[data-testid="stForm"] span {
    color: #021047 !important;
}
div[data-testid="stForm"] input,
div[data-testid="stForm"] textarea,
div[data-testid="stForm"] [data-baseweb="select"] > div,
div[data-testid="stForm"] [data-baseweb="base-input"],
div[data-testid="stForm"] .stNumberInput > div > div {
    background-color: rgb(8 31 100 / 20%) !important;
    border-color: rgb(29 72 153 / 50%) !important;
    color: #021047 !important;
}

/* Cards de métrica com fundo escuro */
[data-testid="metric-container"] {
    background-color: #081F64;
    border: 1px solid #1D4899;
    border-radius: 10px;
    padding: 16px 20px;
    color: #FEFEFE !important;
}
[data-testid="metric-container"] * {
    color: #FEFEFE !important;
}

/* Tabela com fundo escuro */
[data-testid="stDataFrame"] {
    background-color: #081F64;
    border-radius: 10px;
    border: 1px solid #1D4899;
}

/* Título e textos gerais em azul escuro */
h1, h2, h3 { color: #021047 !important; }
</style>
""", unsafe_allow_html=True)

st.image(image="img/percursor-analysis.png",width=500)

st.title("Calculadora de Gasto Energético")
st.caption("Calcule o consumo e o custo de energia da sua residência")

@st.cache_data
def carregar_presets():
    df = pd.read_csv("aparelhos_potencia.csv")
    return dict(zip(df["aparelho"], df["kwh"]))

PRESETS = carregar_presets()
opcoes = ["Personalizado"] + list(PRESETS.keys())

if "eletrodomesticos" not in st.session_state:
    st.session_state.eletrodomesticos = []

# --- Formulário ---
st.subheader("Adicionar Eletrodoméstico")

with st.form("form_adicionar"):
    col1, col2 = st.columns([2, 2])

    with col1:
        preset = st.selectbox("Aparelho", opcoes)

    is_custom = preset == "Personalizado"

    with col2:
        nome_custom = st.text_input(
            "Nome do aparelho",
            placeholder="Informe o nome..." if is_custom else preset,
            disabled=not is_custom,
        )

    col3, col4, col5, col6 = st.columns(4)

    with col3:
        quantidade = st.number_input("Quantidade", min_value=1, max_value=20, value=1)
    with col4:
        marca = st.text_input("Marca", placeholder="Ex: LG, Brastemp...")
    with col5:
        # Sempre editável no modo personalizado; exibe o valor do preset nos demais
        kwh_value = 0.0 if is_custom else float(PRESETS[preset])
        kwh_input = st.number_input(
            "Potência (kWh)",
            min_value=0.0,
            value=kwh_value,
            step=0.001,
            format="%.3f",
            disabled=not is_custom,
            help="Preenchido automaticamente pelo preset. Editável apenas em 'Personalizado'.",
        )
    with col6:
        horas = st.number_input("Horas/dia", min_value=0.1, max_value=24.0, value=1.0, step=0.5)

    submitted = st.form_submit_button("Adicionar", use_container_width=True, type="primary")

    if submitted:
        nome_final = nome_custom.strip() if is_custom else preset
        kwh_final = kwh_input if is_custom else float(PRESETS[preset])

        if not nome_final:
            st.error("Informe o nome do aparelho.")
        elif kwh_final <= 0:
            st.error("A potência deve ser maior que zero.")
        else:
            consumo_diario = kwh_final * horas * quantidade
            st.session_state.eletrodomesticos.append({
                "Nome": nome_final,
                "Quantidade": quantidade,
                "Marca": marca or "—",
                "Potência (kWh)": round(kwh_final, 3),
                "Horas/dia": horas,
                "Consumo diário (kWh)": round(consumo_diario, 3),
                "Consumo mensal (kWh)": round(consumo_diario * 30, 2),
            })
            st.success(f"✅ {nome_final} adicionado com sucesso!")

# --- Lista ---
if st.session_state.eletrodomesticos:
    st.divider()
    st.subheader("📋 Eletrodomésticos cadastrados")

    df = pd.DataFrame(st.session_state.eletrodomesticos)
    st.dataframe(df, use_container_width=True, hide_index=True)

    if st.button("🗑️ Limpar tudo", type="secondary"):
        st.session_state.eletrodomesticos = []
        st.rerun()

    # --- Dashboard ---
    st.divider()
    st.subheader("Dashboard de Consumo")

    total_mensal_kwh = df["Consumo mensal (kWh)"].sum()
    media_kwh = df["Consumo mensal (kWh)"].mean()
    maior_gasto = df.loc[df["Consumo mensal (kWh)"].idxmax()]
    custo_min = total_mensal_kwh * 0.60
    custo_max = total_mensal_kwh * 0.85

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("⚠️ Maior consumidor", maior_gasto["Nome"],
                  f"{maior_gasto['Consumo mensal (kWh)']} kWh/mês")
    with col_b:
        st.metric("📈 Média por aparelho", f"{round(media_kwh, 2)} kWh/mês")
    with col_c:
        st.metric("💡 Conta de luz estimada",
                  f"R&#36; {custo_min:.2f} – R&#36; {custo_max:.2f}",
                  f"Total: {round(total_mensal_kwh, 2)} kWh/mês")

    st.caption("Tarifa da Paraíba: R&#36; 0,60 – R&#36; 0,85 por kWh · Fonte: ND-5.1 / CEMIG")

else:
    st.info("Nenhum eletrodoméstico adicionado ainda. Use o formulário acima para começar.")