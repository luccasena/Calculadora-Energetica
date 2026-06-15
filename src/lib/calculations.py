from src.lib.config import DIAS_MES


def gerar_calculo(aparelhos):
    linhas = []

    for item in aparelhos:
        potencia_kw = item["potencia_w"] / 1000
        consumo_diario = potencia_kw * item["horas_dia"] * item["quantidade"]
        consumo_mensal = consumo_diario * DIAS_MES

        linhas.append(
            {
                "Aparelho": item["nome"],
                "Quantidade": item["quantidade"],
                "Potência (W)": round(item["potencia_w"]),
                "Horas/dia": item["horas_dia"],
                "Consumo diário (kWh)": round(consumo_diario, 3),
                "Consumo mensal (kWh)": round(consumo_mensal, 2),
            }
        )

    total = sum(linha["Consumo mensal (kWh)"] for linha in linhas)

    for linha in linhas:
        percentual = linha["Consumo mensal (kWh)"] / total * 100 if total else 0
        linha["Participação"] = f"{percentual:.1f}%"

    return linhas

