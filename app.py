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
# ESTILOS CSS PERSONALIZADOS - MAIS LIMPO
# ==========================================
st.markdown("""
<style>
    /* Cabeçalho principal */
    .main-header {
        background: linear-gradient(135deg, #1a3a5c 0%, #2a6b9e 100%);
        padding: 2rem 2rem 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.85;
        font-size: 1.1rem;
        font-weight: 300;
    }
    
    /* Cards de métricas */
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #2a6b9e;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
        margin: 0.25rem 0;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a3a5c;
        margin: 0.3rem 0 0.2rem 0;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #6b7280;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #9ca3af;
        margin-top: 0.2rem;
    }
    
    /* Caixas de informação */
    .info-box {
        background: #f0f7ff;
        padding: 1.25rem;
        border-radius: 10px;
        border: 1px solid #dbeafe;
        border-left: 4px solid #2a6b9e;
    }
    
    /* Botões */
    .stButton > button {
        background: #2a6b9e;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        border: none;
        transition: all 0.25s;
        letter-spacing: 0.3px;
    }
    .stButton > button:hover {
        background: #1a4f7a;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(42, 107, 158, 0.3);
    }
    
    /* Divisor */
    .divider {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #e5e7eb;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: #f8fafc;
    }
    
    /* Títulos das seções */
    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #1a3a5c;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DADOS PADRÃO
# ==========================================
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
    consumo_total_l = df_inventario["Consumo_Anual_Geral_L"].sum()
    reserva_tecnica_l = consumo_total_l * 0.10
    volume_total_recomendado = consumo_total_l + reserva_tecnica_l
    
    custo_consumo = consumo_total_l * preco_litro
    custo_reserva = reserva_tecnica_l * preco_litro
    custo_total_estimado = volume_total_recomendado * preco_litro
    
    dados_financeiros = {
        "Rubrica": ["Consumo Operacional", "Reserva Técnica (10%)", "TOTAL PREVISTO"],
        "Volume (L)": [consumo_total_l, reserva_tecnica_l, volume_total_recomendado],
        "Preço Unit. (R$)": [preco_litro, preco_litro, "-"],
        "Custo Total (R$)": [custo_consumo, custo_reserva, custo_total_estimado]
    }
    
    return pd.DataFrame(dados_financeiros)

def criar_graficos(df_inventario, df_financeiro, preco_unitario):
    # Gráfico 1: Consumo por Equipamento - Visual mais limpo
    fig_consumo = px.bar(
        df_inventario,
        x="Equipamento",
        y="Consumo_Anual_Geral_L",
        text="Consumo_Anual_Geral_L",
        color="Equipamento",
        color_discrete_sequence=px.colors.qualitative.Set2,
        title="Consumo Anual de Lubrificante por Equipamento"
    )
    fig_consumo.update_traces(
        textposition="outside",
        texttemplate="%{text:.1f} L",
        hovertemplate="<b>%{x}</b><br>Consumo: %{y:.1f} L/ano<extra></extra>"
    )
    fig_consumo.update_layout(
        showlegend=False,
        height=400,
        plot_bgcolor="white",
        yaxis=dict(
            title="Consumo (Litros/ano)",
            gridcolor="#f0f0f0",
            gridwidth=1
        ),
        xaxis=dict(
            title="",
            tickangle=0
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        font=dict(size=12)
    )
    
    # Gráfico 2: Distribuição de Custos - Mais clean
    df_pie = df_financeiro[df_financeiro["Rubrica"] != "TOTAL PREVISTO"].copy()
    fig_custos = px.pie(
        df_pie,
        values="Custo Total (R$)",
        names="Rubrica",
        title="Distribuição dos Custos",
        color_discrete_sequence=["#2a6b9e", "#f59e0b"],
        hole=0.35
    )
    fig_custos.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percent}<extra></extra>"
    )
    fig_custos.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=12),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1)
    )
    
    # Gráfico 3: Comparativo Volume vs Custo - Eixo duplo mais claro
    df_volume_custo = df_inventario.copy()
    df_volume_custo["Custo_Total"] = df_volume_custo["Consumo_Anual_Geral_L"] * preco_unitario
    
    fig_comparativo = go.Figure()
    fig_comparativo.add_trace(go.Bar(
        name="Volume",
        x=df_volume_custo["Equipamento"],
        y=df_volume_custo["Consumo_Anual_Geral_L"],
        marker_color="#2a6b9e",
        text=df_volume_custo["Consumo_Anual_Geral_L"].apply(lambda x: f"{x:.1f} L"),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Volume: %{y:.1f} L<extra></extra>"
    ))
    fig_comparativo.add_trace(go.Scatter(
        name="Custo",
        x=df_volume_custo["Equipamento"],
        y=df_volume_custo["Custo_Total"],
        mode="lines+markers",
        line=dict(color="#dc2626", width=3),
        marker=dict(size=10, color="#dc2626"),
        yaxis="y2",
        text=df_volume_custo["Custo_Total"].apply(lambda x: f"R$ {x:,.0f}"),
        textposition="top center",
        hovertemplate="<b>%{x}</b><br>Custo: R$ %{y:,.2f}<extra></extra>"
    ))
    fig_comparativo.update_layout(
        title="Comparativo: Volume vs Custo por Equipamento",
        height=400,
        plot_bgcolor="white",
        yaxis=dict(
            title="Volume (L)",
            gridcolor="#f0f0f0",
            gridwidth=1,
            side="left"
        ),
        yaxis2=dict(
            title="Custo (R$)",
            overlaying="y",
            side="right",
            gridcolor="#f0f0f0",
            gridwidth=0,
            showgrid=False
        ),
        xaxis=dict(title=""),
        margin=dict(l=40, r=60, t=40, b=40),
        font=dict(size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig_consumo, fig_custos, fig_comparativo

# ==========================================
# 3. INTERFACE PRINCIPAL
# ==========================================
st.markdown("""
<div class="main-header">
    <h1>⚙️ Gestão de Lubrificação</h1>
    <p>Planejamento e controle estratégico de lubrificantes</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    
    st.markdown("---")
    
    preco_unitario = st.number_input(
        "💰 Preço do Lubrificante",
        min_value=0.01,
        value=28.00,
        step=0.50,
        format="%.2f",
        help="Valor atual por litro do óleo lubrificante"
    )
    
    st.markdown("---")
    
    st.markdown("### 📝 Editar Inventário")
    st.caption("Modifique os dados para simular cenários")
    
    equipamentos = st.text_area(
        "Equipamentos",
        value="Torno Mecânico, Centro de Usinagem CNC, Fresadora Universal",
        help="Lista separada por vírgula",
        height=68
    )
    
    col1, col2 = st.columns(2)
    with col1:
        quantidades = st.text_input(
            "Quantidade Ativa",
            value="2,1,1",
            help="Quantidade de cada equipamento"
        )
        volumes = st.text_input(
            "Volume Individual (L)",
            value="10,60,15",
            help="Volume de óleo por equipamento"
        )
    with col2:
        consumos = st.text_input(
            "Consumo Anual (L)",
            value="40,180,30",
            help="Consumo total anual por equipamento"
        )
    
    st.markdown("---")
    
    if st.button("🔄 Atualizar Dashboard", use_container_width=True):
        st.rerun()

# Processar dados
try:
    lista_equipamentos = [e.strip() for e in equipamentos.split(",")]
    lista_quantidades = [int(q.strip()) for q in quantidades.split(",")]
    lista_volumes = [float(v.strip()) for v in volumes.split(",")]
    lista_consumos = [float(c.strip()) for c in consumos.split(",")]
    
    if len(lista_equipamentos) == len(lista_quantidades) == len(lista_volumes) == len(lista_consumos):
        data_inventario = {
            "Equipamento": lista_equipamentos,
            "Quantidade_Ativos": lista_quantidades,
            "Volume_Individual_L": lista_volumes,
            "Consumo_Anual_Geral_L": lista_consumos
        }
        df_inventario = pd.DataFrame(data_inventario)
    else:
        st.warning("⚠️ Todos os campos devem ter o mesmo número de itens. Usando dados padrão.")
        df_inventario = pd.DataFrame(DEFAULT_INVENTARIO)
        preco_unitario = 28.00
except Exception as e:
    st.warning(f"⚠️ Erro no processamento. Usando dados padrão.")
    df_inventario = pd.DataFrame(DEFAULT_INVENTARIO)
    preco_unitario = 28.00

# Calcular dados
df_financeiro = calcular_custos(df_inventario, preco_unitario)

# ==========================================
# 4. MÉTRICAS PRINCIPAIS
# ==========================================
st.markdown('<p class="section-title">📊 Indicadores Gerais</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    consumo_operacional = df_financeiro[df_financeiro["Rubrica"] == "Consumo Operacional"]["Volume (L)"].values[0]
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Consumo Total Anual</div>
        <div class="metric-value">{consumo_operacional:.1f} L</div>
        <div class="metric-sub">Volume operacional líquido</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    reserva = df_financeiro[df_financeiro["Rubrica"] == "Reserva Técnica (10%)"]["Volume (L)"].values[0]
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Reserva Técnica</div>
        <div class="metric-value">{reserva:.1f} L</div>
        <div class="metric-sub">10% do consumo anual</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    custo_total = df_financeiro[df_financeiro["Rubrica"] == "TOTAL PREVISTO"]["Custo Total (R$)"].values[0]
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Custo Total Previsto</div>
        <div class="metric-value">R$ {custo_total:,.2f}</div>
        <div class="metric-sub">Consumo + reserva técnica</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Preço Unitário</div>
        <div class="metric-value">R$ {preco_unitario:.2f}</div>
        <div class="metric-sub">Por litro de lubrificante</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ==========================================
# 5. GRÁFICOS
# ==========================================
fig_consumo, fig_custos, fig_comparativo = criar_graficos(df_inventario, df_financeiro, preco_unitario)

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.plotly_chart(fig_consumo, use_container_width=True)

with col2:
    st.plotly_chart(fig_custos, use_container_width=True)

st.plotly_chart(fig_comparativo, use_container_width=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ==========================================
# 6. TABELAS DE DADOS
# ==========================================
tab1, tab2 = st.tabs(["📋 Inventário Detalhado", "💰 Resumo Financeiro"])

with tab1:
    st.markdown("### Inventário e Consumo por Equipamento")
    
    df_display = df_inventario.copy()
    df_display["Custo Anual Estimado"] = df_display["Consumo_Anual_Geral_L"] * preco_unitario
    df_display["Custo Anual Estimado"] = df_display["Custo Anual Estimado"].apply(lambda x: f"R$ {x:,.2f}")
    df_display["Volume Individual"] = df_display["Volume_Individual_L"].apply(lambda x: f"{x:.1f} L")
    df_display["Consumo Anual"] = df_display["Consumo_Anual_Geral_L"].apply(lambda x: f"{x:.1f} L")
    
    st.dataframe(
        df_display[["Equipamento", "Quantidade_Ativos", "Volume Individual", "Consumo Anual", "Custo Anual Estimado"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Equipamento": st.column_config.TextColumn("Equipamento", width="medium"),
            "Quantidade_Ativos": st.column_config.NumberColumn("Unidades", width="small"),
            "Volume Individual": st.column_config.TextColumn("Volume/Unidade", width="small"),
            "Consumo Anual": st.column_config.TextColumn("Consumo Total", width="small"),
            "Custo Anual Estimado": st.column_config.TextColumn("Custo Estimado", width="small")
        }
    )

with tab2:
    st.markdown("### Resumo Financeiro e Orçamento")
    
    df_financeiro_display = df_financeiro.copy()
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
            "Rubrica": st.column_config.TextColumn("Rubrica", width="medium"),
            "Volume (L)": st.column_config.TextColumn("Volume", width="small"),
            "Preço Unit. (R$)": st.column_config.TextColumn("Preço Unitário", width="small"),
            "Custo Total (R$)": st.column_config.TextColumn("Custo Total", width="small")
        }
    )
    
    custo_total_valor = df_financeiro[df_financeiro['Rubrica'] == 'TOTAL PREVISTO']['Custo Total (R$)'].values[0]
    st.info(f"💡 **Orçamento Total Previsto para o Período:** R$ {custo_total_valor:,.2f}")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ==========================================
# 7. DOWNLOAD
# ==========================================
st.markdown('<p class="section-title">📥 Exportar Relatórios</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    csv_inventario = df_inventario.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📊 Inventário (CSV)",
        data=csv_inventario,
        file_name="inventario_lubrificacao.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    csv_financeiro = df_financeiro.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💰 Financeiro (CSV)",
        data=csv_financeiro,
        file_name="resumo_financeiro.csv",
        mime="text/csv",
        use_container_width=True
    )

with col3:
    # Combinar dados em um único arquivo
    df_completo = df_inventario.copy()
    df_completo["Custo_Anual_Estimado"] = df_completo["Consumo_Anual_Geral_L"] * preco_unitario
    csv_completo = df_completo.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📋 Dados Completos (CSV)",
        data=csv_completo,
        file_name="dados_completos_lubrificacao.csv",
        mime="text/csv",
        use_container_width=True
    )

# ==========================================
# 8. RODAPÉ
# ==========================================
st.markdown("""
<div style="text-align: center; padding: 1.5rem; background: #f8fafc; border-radius: 10px; margin-top: 2rem;">
    <p style="color: #4b5563; margin: 0; font-size: 0.95rem;">
        ⚙️ <strong>Sistema de Gestão de Lubrificação</strong>
    </p>
    <p style="color: #9ca3af; margin: 0.25rem 0 0 0; font-size: 0.85rem;">
        Dashboard interativo para planejamento estratégico • Dados atualizados em tempo real
    </p>
    <p style="color: #d1d5db; margin: 0.5rem 0 0 0; font-size: 0.75rem;">
        Valores monetários em Reais (R$)
    </p>
</div>
""", unsafe_allow_html=True)