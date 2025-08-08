import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador de Saldo Devedor", layout="wide")

st.title("📉 Calculadora de Saldo Devedor — Empréstimo Consignado")

# Alternar entre modo leigo e avançado
modo_leigo = st.sidebar.toggle("🔁 Modo Cliente Leigo", value=True)

if modo_leigo:
    st.markdown("""
    Simule **quanto ainda falta pagar** e o **juros por mês** do seu empréstimo com base na parcela e prazo.

    Indicamos de forma simples o quanto da dívida ainda existe a pagar e os juros embutidos.
    """)
else:
    st.markdown("""
    Esta calculadora estima o **saldo devedor atual** e a **taxa de juros mensal estimada** de um empréstimo consignado, com base no valor da parcela, prazo total e número de parcelas pagas.

    Você pode escolher entre os sistemas de amortização **PRICE** ou **SAC**.
    """)

# Inputs com textos diferentes conforme o modo
st.sidebar.header("🔧 Parâmetros")

modelo = st.sidebar.selectbox(
    "📊 Tipo de Empréstimo",
    ["PRICE", "SAC"],
    help="PRICE: parcelas fixas. SAC: parcelas decrescentes."
)

parcela = st.sidebar.number_input(
    "💰 Valor da Parcela (R$)" if modo_leigo else "💰 Parcela Mensal (R$)",
    min_value=100.0, step=10.0, value=1000.0,
    help="Valor que você paga mensalmente pelo empréstimo."
)

prazo_total = st.sidebar.number_input(
    "📆 Quantidade total de parcelas" if modo_leigo else "📆 Prazo total do contrato (meses)",
    min_value=1, step=1, value=60,
    help="Duração do empréstimo, em meses."
)

parcelas_pagas = st.sidebar.number_input(
    "✔️ Parcelas que já foram pagas" if modo_leigo else "✔️ Número de parcelas quitadas",
    min_value=0, max_value=prazo_total, step=1, value=12,
    help="Quantas parcelas você já pagou até hoje."
)

# Função para estimar taxa de juros (PRICE)
def estimar_taxa_price(parcela, prazo, chute_inicial=0.01, max_iter=1000, tol=1e-6):
    taxa = chute_inicial
    for _ in range(max_iter):
        PV_estimado = parcela * (1 - (1 + taxa) ** -prazo) / taxa
        dPV_dtaxa = (
            parcela * ((1 + taxa) ** -prazo * (prazo / (1 + taxa)) - (1 - (1 + taxa) ** -prazo)) / (taxa ** 2)
        )
        erro = parcela * (1 - (1 + taxa) ** -prazo) / taxa - PV_estimado
        if abs(erro) < tol:
            break
        taxa = taxa - erro / dPV_dtaxa
    return taxa

# Cálculos
if modelo == "PRICE":
    cor_modelo = "#1f77b4"  # azul
    taxa_aproximada = estimar_taxa_price(parcela, prazo_total)
    PV = parcela * (1 - (1 + taxa_aproximada) ** -prazo_total) / taxa_aproximada
    saldo_devedor = PV * (1 + taxa_aproximada) ** parcelas_pagas - parcela * ((1 + taxa_aproximada) ** parcelas_pagas - 1) / taxa_aproximada
else:  # SAC
    cor_modelo = "#2ca02c"  # verde
    taxa_aproximada = 0.02  # suposição média (2%)
    PV = parcela * prazo_total
    for _ in range(10):
        A = PV / prazo_total
        parcela_inicial = A + PV * taxa_aproximada
        PV = parcela * prazo_total / parcela_inicial * PV
    A = PV / prazo_total
    saldo_devedor = PV - parcelas_pagas * A

# Resultados
st.subheader("📊 Resultado da Simulação")

col1, col2 = st.columns(2)

col1.metric("💸 Quanto ainda falta pagar" if modo_leigo else "💸 Saldo devedor atual", f"R$ {saldo_devedor:,.2f}")
col2.metric("📈 Juros por mês" if modo_leigo else "📈 Taxa de Juros Mensal Estimada", f"{taxa_aproximada * 100:.2f} %")

# Gráfico de saldo restante
meses = np.arange(parcelas_pagas, prazo_total + 1)
saldos = []

if modelo == "PRICE":
    for m in meses:
        sd = PV * (1 + taxa_aproximada) ** m - parcela * ((1 + taxa_aproximada) ** m - 1) / taxa_aproximada
        saldos.append(sd)
else:
    for m in meses:
        saldos.append(PV - m * A)

fig = go.Figure()
fig.add_trace(go.Scatter(x=meses, y=saldos, fill='tozeroy', line_color=cor_modelo,
                         name="Saldo Devedor", mode="lines+markers"))

fig.update_layout(
    title="📉 Evolução do Saldo Devedor",
    xaxis_title="Meses Restantes",
    yaxis_title="R$",
    template="simple_white",
    font=dict(size=14),
    showlegend=False,
    height=400
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("⚙️ Desenvolvido com foco em clareza e experiência — estilo engenheiro por Victor.")
