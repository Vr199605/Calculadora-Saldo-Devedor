import streamlit as st
import math

# Configuração da página
st.set_page_config(
    page_title="Calculadora Consignado - Price",
    page_icon="📊",
    layout="centered"
)

# Estilo CSS
st.markdown("""
    <style>
    .main {
        max-width: 800px;
        padding: 2rem;
    }
    .stNumberInput>div>div>input {
        border-radius: 8px;
        padding: 10px;
    }
    .result-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .highlight {
        color: #2e7d32;
        font-weight: bold;
    }
    .error {
        color: #d32f2f;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Título
st.title("📉 Calculadora Consignado - Sistema Price")
st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <p>Descubra o saldo devedor atual e a taxa implícita do seu empréstimo</p>
    </div>
""", unsafe_allow_html=True)

# Funções de cálculo
def calcular_taxa(parcela, valor_emprestimo, prazo, iteracoes=100, precisao=1e-6):
    """Calcula a taxa de juros mensal usando o método de Newton-Raphson"""
    taxa = 0.01  # Estimativa inicial de 1% ao mês
    
    for _ in range(iteracoes):
        if taxa == 0:
            vp = parcela * prazo
        else:
            vp = parcela * (1 - (1 + taxa)**(-prazo)) / taxa
        
        # Derivada corrigida e simplificada
        if taxa == 0:
            derivada = -parcela * prazo * (prazo + 1) / 2
        else:
            termo = (1 + taxa)**(-prazo - 1)
            derivada = (parcela * (termo * (prazo * taxa + prazo + 1) - 1)) / (taxa**2)
        
        nova_taxa = taxa - (vp - valor_emprestimo) / derivada
        
        if abs(nova_taxa - taxa) < precisao:
            break
            
        taxa = nova_taxa
    
    return taxa

def calcular_saldo_devedor(parcela, taxa, prazo_restante):
    """Calcula o saldo devedor atual pelo sistema Price"""
    if taxa == 0:
        return parcela * prazo_restante
    return parcela * (1 - (1 + taxa)**(-prazo_restante)) / taxa

# Entrada de dados
with st.form("dados_emprestimo"):
    col1, col2 = st.columns(2)
    
    with col1:
        valor_parcela = st.number_input(
            "Valor da Parcela (R$)",
            min_value=0.01,
            value=500.0,
            step=50.0,
            key='parcela'
        )
    
    with col2:
        prazo_total = st.number_input(
            "Prazo Total (meses)",
            min_value=1,
            value=24,
            step=1,
            key='prazo_total'
        )
    
    prazo_restante = st.number_input(
        "Prazo Restante (meses)",
        min_value=1,
        max_value=prazo_total,
        value=prazo_total//2,
        step=1,
        key='prazo_restante'
    )
    
    calcular = st.form_submit_button("Calcular Saldo Devedor e Taxa")

# Cálculos e resultados
if calcular:
    try:
        # Estimar o valor inicial do empréstimo (VP)
        # Usando uma taxa média de consignado (1.5% a.m.) para estimativa inicial
        taxa_estimada = 0.015
        valor_emprestimo = calcular_saldo_devedor(valor_parcela, taxa_estimada, prazo_total)
        
        # Calcular taxa de juros implícita
        taxa_mensal = calcular_taxa(valor_parcela, valor_emprestimo, prazo_total)
        taxa_anual = ((1 + taxa_mensal)**12 - 1) * 100
        
        # Calcular saldo devedor atual
        saldo_atual = calcular_saldo_devedor(valor_parcela, taxa_mensal, prazo_restante)
        
        # Calcular valor para quitação
        valor_quitacao = saldo_atual
        
        # Exibir resultados
        st.markdown("---")
        st.markdown(f"""
            <div class="result-card">
                <h3>Resultados</h3>
                <p>Valor estimado do empréstimo: <span class="highlight">R$ {valor_emprestimo:,.2f}</span></p>
                <p>Taxa de juros mensal: <span class="highlight">{taxa_mensal*100:.2f}%</span></p>
                <p>Taxa de juros anual: <span class="highlight">{taxa_anual:.2f}%</span></p>
                <p>Saldo devedor atual: <span class="highlight">R$ {saldo_atual:,.2f}</span></p>
                <p>Valor para quitação: <span class="highlight">R$ {valor_quitacao:,.2f}</span></p>
            </div>
        """, unsafe_allow_html=True)
        
        # Detalhes do cálculo
        with st.expander("🔍 Como funciona o cálculo?"):
            st.markdown("""
                **Fórmulas utilizadas:**
                
                1. **Valor do empréstimo (estimado)**:
                ```
                VP = Parcela × [1 - (1 + i)^-n] / i
                Onde i = 1.5% a.m. (taxa média para consignado)
                ```
                
                2. **Taxa de juros implícita**:
                ```
                Encontramos a taxa (i) que satisfaz:
                VP = Parcela × [1 - (1 + i)^-n] / i
                ```
                
                3. **Saldo devedor atual**:
                ```
                Saldo = Parcela × [1 - (1 + i)^-k] / i
                Onde k = prazo restante
                ```
                
                4. **Taxa anual equivalente**:
                ```
                Taxa Anual = [(1 + Taxa Mensal)^12 - 1] × 100
                ```
            """)
    
    except Exception as e:
        st.markdown(f"""
            <div class="error">
                Não foi possível calcular a taxa com os valores informados. Verifique:
                - Valor da parcela deve ser positivo
                - Prazo restante deve ser menor ou igual ao prazo total
                - Valores devem ser consistentes
            </div>
        """, unsafe_allow_html=True)

# Rodapé
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; font-size: 14px;">
        <p>Calculadora baseada no sistema Price (parcelas iguais)</p>
        <p>Para empréstimos consignados - Valores estimados</p>
    </div>
""", unsafe_allow_html=True)