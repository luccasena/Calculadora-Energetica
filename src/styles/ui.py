from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

from src.lib.calculations import gerar_calculo
from src.lib.config import LOGO_PATH, TARIFA_REFERENCIA, URL_TARIFA
from src.lib.state import (
    adicionar_aparelho,
    buscar_aparelho_em_edicao,
    invalidar_dashboard,
    limpar_aparelhos,
    remover_aparelho,
    resetar_simulacao,
)


def renderizar_cabecalho(aviso_csv):
    logo = Path(LOGO_PATH)
    if logo.exists():
        st.image(str(logo), width=400)

    st.title("Calculadora de Gasto Energético")
    st.caption(
        "Adicione os aparelhos da residência para estimar o consumo mensal e "
        "identificar quais possuem maior potencial de gasto."
    )
    st.info(
        "A simulação considera um mês de 30 dias e utiliza valores aproximados. "
        "O resultado não representa o valor final da conta de luz."
    )

    if aviso_csv:
        st.warning(aviso_csv)

    st.divider()


def renderizar_formulario_preset(presets):
    st.markdown("### Aparelhos pré-configurados")
    st.caption("Selecione um aparelho. A potência é preenchida automaticamente.")

    with st.form("form_preset", clear_on_submit=True):
        preset = st.selectbox("Aparelho", list(presets.keys()))
        st.caption(f"Potência de referência: {presets[preset]:.0f} W")

        col_qtd, col_horas = st.columns(2)
        with col_qtd:
            qtd_pre = st.number_input(
                "Quantidade", min_value=1, max_value=50, value=1, step=1
            )
        with col_horas:
            horas_pre = st.number_input(
                "Horas de uso por dia",
                min_value=0.1,
                max_value=24.0,
                value=1.0,
                step=0.5,
            )

        if st.form_submit_button("Adicionar", type="primary", use_container_width=True):
            adicionar_aparelho(preset, presets[preset], qtd_pre, horas_pre)
            st.success(f"{preset} adicionado.")

    st.divider()


def renderizar_formulario_personalizado():
    st.markdown("### Aparelho personalizado")
    st.caption("Cadastre um aparelho que não esteja na lista.")

    with st.form("form_personalizado", clear_on_submit=True):
        nome_c = st.text_input("Nome do aparelho", placeholder="Ex.: Cafeteira")

        col_potencia, col_qtd, col_horas = st.columns(3)
        with col_potencia:
            potencia_c = st.number_input(
                "Potência (W)",
                min_value=1.0,
                max_value=50000.0,
                value=100.0,
                step=10.0,
            )
        with col_qtd:
            qtd_c = st.number_input(
                "Quantidade", min_value=1, max_value=50, value=1, step=1, key="qtd_c"
            )
        with col_horas:
            horas_c = st.number_input(
                "Horas de uso por dia",
                min_value=0.1,
                max_value=24.0,
                value=1.0,
                step=0.5,
                key="horas_c",
            )

        if st.form_submit_button(
            "Adicionar personalizado", type="primary", use_container_width=True
        ):
            if not nome_c.strip():
                st.error("Informe o nome do aparelho.")
            else:
                adicionar_aparelho(nome_c, potencia_c, qtd_c, horas_c)
                st.success(f"{nome_c.strip()} adicionado.")


def renderizar_lista_aparelhos():
    if not st.session_state.aparelhos:
        return

    st.divider()
    st.markdown("### Aparelhos adicionados")

    for item in st.session_state.aparelhos:
        col_info, col_edit, col_del = st.columns([7, 1, 1])

        with col_info:
            st.markdown(
                (
                    "<div class='item-row'>"
                    f"<b>{escape(item['nome'])}</b> &nbsp;·&nbsp; "
                    f"{item['quantidade']} unidade(s) &nbsp;·&nbsp; "
                    f"{item['potencia_w']:.0f} W &nbsp;·&nbsp; "
                    f"{item['horas_dia']:.1f} h/dia"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

        with col_edit:
            if st.button("Editar", key=f"edit_{item['id']}"):
                st.session_state.edit_id = item["id"]
                st.rerun()

        with col_del:
            if st.button("Remover", key=f"del_{item['id']}"):
                remover_aparelho(item["id"])
                st.rerun()

    renderizar_formulario_edicao()

    tipos = len({item["nome"] for item in st.session_state.aparelhos})
    unidades = sum(item["quantidade"] for item in st.session_state.aparelhos)
    st.caption(f"{tipos} tipo(s) de aparelho e {unidades} unidade(s) adicionada(s).")

    if st.button("Limpar aparelhos", use_container_width=True):
        limpar_aparelhos()
        st.rerun()


def renderizar_formulario_edicao():
    item_editado = buscar_aparelho_em_edicao()

    if not item_editado:
        return

    st.markdown(f"**Editando:** {escape(item_editado['nome'])}")

    with st.form("form_edicao"):
        nome_e = st.text_input("Nome", value=item_editado["nome"])

        col_potencia, col_qtd, col_horas = st.columns(3)
        with col_potencia:
            potencia_e = st.number_input(
                "Potência (W)",
                min_value=1.0,
                max_value=50000.0,
                value=float(item_editado["potencia_w"]),
                step=10.0,
            )
        with col_qtd:
            qtd_e = st.number_input(
                "Quantidade",
                min_value=1,
                max_value=50,
                value=int(item_editado["quantidade"]),
                step=1,
            )
        with col_horas:
            horas_e = st.number_input(
                "Horas de uso por dia",
                min_value=0.1,
                max_value=24.0,
                value=float(item_editado["horas_dia"]),
                step=0.5,
            )

        col_salvar, col_cancelar = st.columns(2)
        with col_salvar:
            salvar = st.form_submit_button(
                "Salvar", type="primary", use_container_width=True
            )
        with col_cancelar:
            cancelar = st.form_submit_button("Cancelar", use_container_width=True)

        if salvar:
            if not nome_e.strip():
                st.error("Informe o nome do aparelho.")
            else:
                item_editado.update(
                    {
                        "nome": nome_e.strip(),
                        "potencia_w": float(potencia_e),
                        "quantidade": int(qtd_e),
                        "horas_dia": float(horas_e),
                    }
                )
                st.session_state.edit_id = None
                invalidar_dashboard()
                st.rerun()

        if cancelar:
            st.session_state.edit_id = None
            st.rerun()


def renderizar_simulacao():
    st.divider()

    if not st.session_state.aparelhos:
        st.info("Adicione ao menos um aparelho para gerar a simulação.")
    elif st.button("Gerar simulação", type="primary", use_container_width=True):
        st.session_state.dashboard = gerar_calculo(st.session_state.aparelhos)

    if st.session_state.dashboard:
        renderizar_dashboard()


def renderizar_dashboard():
    df = pd.DataFrame(st.session_state.dashboard)
    df = df.sort_values("Consumo mensal (kWh)", ascending=False).reset_index(drop=True)

    resumo = (
        df.groupby("Aparelho", as_index=False)["Consumo mensal (kWh)"]
        .sum()
        .sort_values("Consumo mensal (kWh)", ascending=False)
        .reset_index(drop=True)
    )

    total_kwh = resumo["Consumo mensal (kWh)"].sum()
    maior = resumo.iloc[0]
    percentual_maior = maior["Consumo mensal (kWh)"] / total_kwh * 100
    custo_aproximado = total_kwh * TARIFA_REFERENCIA

    st.markdown("### Resultado da simulação")

    col_total, col_maior, col_custo = st.columns(3)
    with col_total:
        st.metric("Consumo mensal aproximado", f"{total_kwh:.2f} kWh")
    with col_maior:
        st.metric(
            "Maior potencial de consumo",
            maior["Aparelho"],
            f"{maior['Consumo mensal (kWh)']:.2f} kWh/mês",
        )
    with col_custo:
        st.metric("Custo aproximado do consumo", f"R$ {custo_aproximado:.2f}")

    st.info(
        f"**{maior['Aparelho']}** apresentou o maior potencial de consumo, "
        f"representando aproximadamente **{percentual_maior:.1f}%** do total simulado."
    )

    st.markdown("#### Ranking de consumo mensal")

    fig = px.bar(
        resumo, 
        x="Aparelho", 
        y="Consumo mensal (kWh)",  
        text_auto=True,           
        title="Resumo por Aparelho"
    )

    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Detalhamento")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Potência (W)": st.column_config.NumberColumn(format="%.0f W"),
            "Horas/dia": st.column_config.NumberColumn(format="%.1f h"),
            "Consumo diário (kWh)": st.column_config.NumberColumn(format="%.3f kWh"),
            "Consumo mensal (kWh)": st.column_config.NumberColumn(format="%.2f kWh"),
        },
    )

    st.caption(
        f"O custo usa uma tarifa residencial de referência de "
        f"R$ {TARIFA_REFERENCIA:.5f}/kWh. Impostos, bandeiras e outras cobranças "
        "da fatura não estão incluídos."
    )

    col_link, col_reset = st.columns(2)
    with col_link:
        st.link_button(
            "Consultar tarifa de referência",
            URL_TARIFA,
            use_container_width=True,
        )
    with col_reset:
        if st.button("Resetar e começar novamente", use_container_width=True):
            resetar_simulacao()
            st.rerun()

