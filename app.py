import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Gestão de Lubrificação",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# ESTILOS CSS PERSONALIZADOS
# ==========================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1F4E78 0%, #2E7DB5 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1F4E78;
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1F4E78;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        font-weight: 500;
    }
    .info-box {
        background-color: #e8f0fe;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c5d8f0;
    }
    .stButton > button {
        background-color: #1F4E78;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        border: none;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #2E7DB5;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(31, 78, 120, 0.3);
    }
    .divider {
        margin: 2rem 0;
        border-top: 2px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DADOS PADRÃO E ENTRADA DO USUÁRIO
# ==========================================

# Dados padrão do inventário
DEFAULT_INVENTARIO = {
    "Equipamento": ["Torno Mecânico", "Centro de Usinagem CNC", "Fresadora Universal"],
    "Quantidade_Ativos": [2, 1, 1],
    "Volume_Individual_L": [10, 60, 15],
    "Consumo_Anual_Geral_L": [40, 180, 30]
}

# ==========================================
# 2. FUNÇÕES DE CÁLCULO
# ==========================================

def calcular_custos(df_inventario, preco_litro):
    """Calcula os totais de volume e custos financeiros."""
    
    consumo_total_l = df_inventario["Consumo_Anual_Geral_L"].sum()
    reserva_tecnica_l = consumo_total_l * 0.10
    volume_total_recomendado = consumo_total_l + reserva_tecnica_l
    
    custo_consumo = consumo_total_l * preco_litro
    custo_reserva = reserva_tecnica_l * preco_litro
    custo_total_estimado = volume_total_recomendado * preco_litro
    
    dados_financeiros = {
        "Rubrica": ["Consumo Operacional Líquido", "Reserva Técnica Estratégica (10%)", "TOTAL PREVISTO"],
        "Volume (L)": [consumo_total_l, reserva_tecnica_l, volume_total_recomendado],
        "Preço Unit. (R$)": [preco_litro, preco_litro, "-"],
        "Custo Total (R$)": [custo_consumo, custo_reserva, custo_total_estimado]
    }
    
    return pd.DataFrame(dados_financeiros)

def criar_graficos(df_inventario, df_financeiro):
    """Cria visualizações interativas."""
    
    # Gráfico 1: Consumo por Equipamento
    fig_consumo = px.bar(
        df_inventario,
        x="Equipamento",
        y="Consumo_Anual_Geral_L",
        text="Consumo_Anual_Geral_L",
        color="Equipamento",
        color_discrete_sequence=px.colors.qualitative.Set2,
        title="Consumo Anual de Óleo por Equipamento",
        labels={"Consumo_Anual_Geral_L": "Consumo (Litros/ano)"}
    )
    fig_consumo.update_traces(textposition="outside")
    fig_consumo.update_layout(
        showlegend=False,
        height=400,
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis_gridcolor="#e0e0e0"
    )
    
    # Gráfico 2: Distribuição de Custos
    fig_custos = px.pie(
        df_financeiro[df_financeiro["Rubrica"] != "TOTAL PREVISTO"],
        values="Custo Total (R$)",
        names="Rubrica",
        title="Distribuição dos Custos",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4
    )
    fig_custos.update_layout(height=400)
    fig_custos.update_traces(textposition="inside", textinfo="percent+label")
    
    # Gráfico 3: Comparativo Volume vs Custo
    df_volume_custo = df_inventario.copy()
    df_volume_custo["Custo_Total"] = df_volume_custo["Consumo_Anual_Geral_L"] * PRECO_UNITARIO_LITRO
    
    fig_comparativo = go.Figure()
    fig_comparativo.add_trace(go.Bar(
        name="Volume (L)",
        x=df_volume_custo["Equipamento"],
        y=df_volume_custo["Consumo_Anual_Geral_L"],
        marker_color="#1F4E78",
        text=df_volume_custo["Consumo_Anual_Geral_L"],
        textposition="outside"
    ))
    fig_comparativo.add_trace(go.Scatter(
        name="Custo (R$)",
        x=df_volume_custo["Equipamento"],
        y=df_volume_custo["Custo_Total"],
        mode="lines+markers",
        line=dict(color="#FF6B6B", width=3),
        marker=dict(size=12),
        yaxis="y2",
        text=df_volume_custo["Custo_Total"].apply(lambda x: f"R$ {x:,.2f}"),
        textposition="top center"
    ))
    fig_comparativo.update_layout(
        title="Volume vs Custo por Equipamento",
        height=400,
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="Volume (L)", gridcolor="#e0e0e0"),
        yaxis2=dict(title="Custo (R$)", overlaying="y", side="right", gridcolor="#e0e0e0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig_consumo, fig_custos, fig_comparativo

# ==========================================
# 3. INTERFACE PRINCIPAL
# ==========================================

st.markdown('<div class="main-header"><h1 style="margin:0;">⚙️ Gestão de Lubrificação - Dashboard</h1><p style="margin:0;opacity:0.9;">Sistema de planejamento e controle de lubrificantes</p></div>', unsafe_allow_html=True)

# Sidebar - Configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    
    st.subheader("Preço do Óleo")
    PRECO_UNITARIO_LITRO = st.number_input(
        "Preço por litro (R$)",
        min_value=0.01,
        value=28.00,
        step=0.50,
        format="%.2f",
        help="Valor atual do litro do óleo lubrificante no mercado"
    )
    
    st.divider()
    
    st.subheader("Editar Inventário")
    st.info("Modifique os valores abaixo para simular diferentes cenários")
    
    # Editor do inventário
    equipamentos = st.text_area(
        "Equipamentos (separados por vírgula)",
        value="Torno Mecânico, Centro de Usinagem CNC, Fresadora Universal",
        help="Liste os equipamentos separados por vírgula"
    )
    
    quantidades = st.text_input(
        "Quantidades Ativas (separadas por vírgula)",
        value="2,1,1",
        help="Quantidade de cada equipamento"
    )
    
    volumes = st.text_input(
        "Volume Individual (L) - separados por vírgula",
        value="10,60,15",
        help="Volume de óleo por equipamento"
    )
    
    consumos = st.text_input(
        "Consumo Anual Total (L) - separados por vírgula",
        value="40,180,30",
        help="Consumo total anual por equipamento"
    )
    
    st.divider()
    
    if st.button("🔄 Atualizar Dashboard", use_container_width=True):
        st.rerun()

# Processamento dos dados
try:
    lista_equipamentos = [e.strip() for e in equipamentos.split(",")]
    lista_quantidades = [int(q.strip()) for q in quantidades.split(",")]
    lista_volumes = [float(v.strip()) for v in volumes.split(",")]
    lista_consumos = [float(c.strip()) for c in consumos.split(",")]
    
    # Criar DataFrame com os dados personalizados
    data_inventario = {
        "Equipamento": lista_equipamentos,
        "Quantidade_Ativos": lista_quantidades,
        "Volume_Individual_L": lista_volumes,
        "Consumo_Anual_Geral_L": lista_consumos
    }
    df_inventario = pd.DataFrame(data_inventario)
    
except Exception as e:
    st.error(f"❌ Erro ao processar os dados: {e}")
    st.info("Utilizando dados padrão do sistema")
    df_inventario = pd.DataFrame(DEFAULT_INVENTARIO)
    PRECO_UNITARIO_LITRO = 28.00

# Calcular dados financeiros
df_financeiro = calcular_custos(df_inventario, PRECO_UNITARIO_LITRO)

# ==========================================
# 4. MÉTRICAS PRINCIPAIS
# ==========================================

st.subheader("📊 Indicadores Gerais")

col1, col2, col3, col4 = st.columns(4)

with col1:
    consumo_operacional = df_financeiro[df_financeiro["Rubrica"] == "Consumo Operacional Líquido"]["Volume (L)"].values[0]
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Consumo Total Anual</div>
        <div class="metric-value">{consumo_operacional:.1f} L</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    reserva = df_financeiro[df_financeiro["Rubrica"] == "Reserva Técnica Estratégica (10%)"]["Volume (L)"].values[0]
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Reserva Técnica</div>
        <div class="metric-value">{reserva:.1f} L</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    custo_total = df_financeiro[df_financeiro["Rubrica"] == "TOTAL PREVISTO"]["Custo Total (R$)"].values[0]
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Custo Total Anual</div>
        <div class="metric-value">R$ {custo_total:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Preço Unitário</div>
        <div class="metric-value">R$ {PRECO_UNITARIO_LITRO:.2f}/L</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==========================================
# 5. GRÁFICOS INTERATIVOS
# ==========================================

fig_consumo, fig_custos, fig_comparativo = criar_graficos(df_inventario, df_financeiro)

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_consumo, use_container_width=True)

with col2:
    st.plotly_chart(fig_custos, use_container_width=True)

st.plotly_chart(fig_comparativo, use_container_width=True)

st.divider()

# ==========================================
# 6. TABELAS DE DADOS
# ==========================================

tab1, tab2 = st.tabs(["📋 Inventário Detalhado", "💰 Resumo Financeiro"])

with tab1:
    st.subheader("Inventário e Consumo por Equipamento")
    
    # Adicionar colunas calculadas
    df_inventario_display = df_inventario.copy()
    df_inventario_display["Custo_Anual_Estimado"] = df_inventario_display["Consumo_Anual_Geral_L"] * PRECO_UNITARIO_LITRO
    df_inventario_display["Custo_Anual_Estimado"] = df_inventario_display["Custo_Anual_Estimado"].apply(lambda x: f"R$ {x:,.2f}")
    
    st.dataframe(
        df_inventario_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Equipamento": st.column_config.TextColumn("Equipamento"),
            "Quantidade_Ativos": st.column_config.NumberColumn("Quantidade Ativa"),
            "Volume_Individual_L": st.column_config.NumberColumn("Volume Individual (L)", format="%.1f L"),
            "Consumo_Anual_Geral_L": st.column_config.NumberColumn("Consumo Anual (L)", format="%.1f L"),
            "Custo_Anual_Estimado": st.column_config.TextColumn("Custo Anual Estimado")
        }
    )

with tab2:
    st.subheader("Resumo Financeiro e Orçamento")
    
    # Criar uma cópia para exibição formatada
    df_financeiro_display = df_financeiro.copy()
    
    # Formatar as colunas separadamente
    df_financeiro_display["Volume (L)"] = df_financeiro_display["Volume (L)"].apply(
        lambda x: f"{x:.1f} L" if isinstance(x, (int, float)) else x
    )
    
    df_financeiro_display["Preço Unit. (R$)"] = df_financeiro_display["Preço Unit. (R$)"].apply(
        lambda x: f"R$ {x:.2f}" if isinstance(x, (int, float)) else x
    )
    
    df_financeiro_display["Custo Total (R$)"] = df_financeiro_display["Custo Total (R$)"].apply(
        lambda x: f"R$ {x:,.2f}" if isinstance(x, (int, float)) else x
    )
    
    st.dataframe(
        df_financeiro_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rubrica": st.column_config.TextColumn("Rubrica"),
            "Volume (L)": st.column_config.TextColumn("Volume"),
            "Preço Unit. (R$)": st.column_config.TextColumn("Preço Unitário"),
            "Custo Total (R$)": st.column_config.TextColumn("Custo Total")
        }
    )
    
    # Destaque para o total
    custo_total_valor = df_financeiro[df_financeiro['Rubrica'] == 'TOTAL PREVISTO']['Custo Total (R$)'].values[0]
    st.info(f"💡 **Orçamento Total Previsto:** R$ {custo_total_valor:,.2f}")

st.divider()

# ==========================================
# 7. DOWNLOAD DE RELATÓRIO
# ==========================================

st.subheader("📥 Exportar Dados")

col1, col2 = st.columns(2)

with col1:
    # Botão para baixar CSV do inventário
    csv_inventario = df_inventario.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📊 Baixar Inventário (CSV)",
        data=csv_inventario,
        file_name="inventario_lubrificacao.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    # Botão para baixar CSV do financeiro
    csv_financeiro = df_financeiro.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💰 Baixar Resumo Financeiro (CSV)",
        data=csv_financeiro,
        file_name="resumo_financeiro_lubrificacao.csv",
        mime="text/csv",
        use_container_width=True
    )

# ==========================================
# 8. RODAPÉ
# ==========================================

st.markdown("""
<div style="text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 8px; margin-top: 2rem;">
    <p style="color: #666; margin: 0; font-size: 0.9rem;">
        ⚙️ Sistema de Gestão de Lubrificação - Dashboard Interativo
    </p>
    <p style="color: #999; margin: 0.25rem 0 0 0; font-size: 0.8rem;">
        Dados atualizados em tempo real • Valores em Reais (R$)
    </p>
</div>
""", unsafe_allow_html=True)