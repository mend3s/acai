import pandas as pd
import streamlit as st
import streamlit-pills as stp
import seaborn as sns
import matplotlib.pyplot as plt
from functions import setup
import sqlite3
import plotly.express as px
import plotly.graph_objects as go


# --- Configuração da Página (DEVE SER A PRIMEIRA CHAMADA DO STREAMLIT) ---
st.set_page_config(
    page_title="Açai Dashboard",
    page_icon="📊",
    layout="wide",
)

#ESTILIZANDO OS CARDS DE DASHBOARD
st.markdown("""
<style>
/* --- ESTILO BASE DO CARD --- */
.kpi-card {
    position: relative; /* Necessário para o tooltip */
    background-color: #FFFFFF;
    padding: 20px;
    border-radius: 10px;
    border-left: 8px solid #000; /* Borda padrão, será sobrescrita pela cor específica */
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5); /* Sombra mais destacada */
    height: 160px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: all 0.3s ease;
    color: #333333; /* Cor do texto padrão escura para contraste com fundo branco */
}
.kpi-card:hover {
    transform: translateY(-5px); /* Efeito de "levantar" ao passar o mouse */
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}
/* Estilo dos textos dentro do card */
.kpi-card h3 { margin: 0; font-size: 1.1em; text-transform: uppercase; font-weight: 600; color: #666666; }
.kpi-card h2 { margin: 5px 0; font-size: 2.1em; font-weight: bolder; color: #2A2A2A; }

/* --- PALETA DE CORES PARA AS BORDAS --- */
/* Cores da primeira fileira (baseadas na cor do texto do seu código) */
.kpi-card.color-1 { border-left-color: #0d47a1; } /* Receita Total */
.kpi-card.color-2 { border-left-color: #1b5e20; } /* Vendas Realizadas */
.kpi-card.color-3 { border-left-color: #e65100; } /* Ticket Médio */
.kpi-card.color-4 { border-left-color: #4a148c; } /* Clientes Ativos */
/* Cores da segunda fileira (baseadas na cor do fundo do seu código) */
.kpi-card.color-5 { border-left-color: #0B5351; } /* Produto Campeão */
.kpi-card.color-6 { border-left-color: #009E73; } /* Pagamento Preferido */
.kpi-card.color-7 { border-left-color: #E69F00; } /* Dia de Pico */
.kpi-card.color-8 { border-left-color: #5F50FA; } /* Horário de Pico */
/* Cores dos cards das paginas (baseadas na cor do fundo do seu código) */          
.kpi-card.color-9 { border-left-color: #F9E7CB; } /* Horário de Pico Interno */
.kpi-card.color-10 { border-left-color: #28FA82; } /* Dia de Pico Interno */
.kpi-card.color-11 { border-left-color: #E1DFFA; } /* Produto Campeão Interno*/
.kpi-card.color-12 { border-left-color: #7AA0FA; } /* Categoria Campeão Interno*/
.kpi-card.color-13 { border-left-color: #1b5e20; } /* Vendas Realizadas */
.kpi-card.color-14 { border-left-color: #e65100; } /* Ticket Médio */
.kpi-card.color-15 { border-left-color: #4a148c; } /* Clientes Ativos */
.kpi-card.color-16 { border-left-color: #0d47a1; } /* Receita Total */            
            


/* --- ESTILO DO TOOLTIP (DICA NO HOVER) --- */
.kpi-card .tooltip-text {
    visibility: hidden;
    width: 220px;
    background-color: #333;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 8px;
    position: absolute;
    z-index: 1;
    bottom: 110%;
    left: 50%;
    margin-left: -110px;
    opacity: 0;
    transition: opacity 0.3s;
}
.kpi-card:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
}
</style>
""", unsafe_allow_html=True)


st.title("DASHBOARD")
opcoes_menu = ["Visão Geral", "Análise de Vendas", "Análise de Produtos & Categorias", "Análises de Formas de Pagamento", "Análises de Clientes"]
icones_menu = ["💡", "💰", "🗃️", "📈", "👥"] # Ícones são usados apenas para display nos pills

# Inicializa 'pagina_selecionada' no session_state se ainda não existir
if 'pagina_selecionada' not in st.session_state:
    if opcoes_menu: # Garante que há opções
        st.session_state.pagina_selecionada = opcoes_menu[0]
    else:
        st.session_state.pagina_selecionada = None

# Verifica se a pagina_selecionada atual ainda é válida (caso as opções mudem)
if st.session_state.pagina_selecionada not in opcoes_menu and opcoes_menu:
    st.session_state.pagina_selecionada = opcoes_menu[0]
elif not opcoes_menu:
    st.session_state.pagina_selecionada = None


# Determina o índice padrão para o componente pills
default_index = 0
if st.session_state.pagina_selecionada and opcoes_menu:
    try:
        default_index = opcoes_menu.index(st.session_state.pagina_selecionada)
    except ValueError:
        if opcoes_menu:
            st.session_state.pagina_selecionada = opcoes_menu[0]
            default_index = 0
        else:
            st.session_state.pagina_selecionada = None

# Inicializa pagina_atual para o caso de não haver opcoes_menu
pagina_atual = None

# Renderiza os pills
if opcoes_menu:
    pagina_atual = stp.pills(
        label="Navegue pelo Dashboard:",
        options=opcoes_menu,
        icons=icones_menu,
        index=default_index,
        key="menu_pills_dashboard_acai"
    )
    # Atualiza o session_state com a nova seleção do usuário
    st.session_state.pagina_selecionada = pagina_atual
else:
    st.info("Nenhuma seção disponível para navegação.")
    # Garante que pagina_atual seja o que está em session_state se não houver pills para renderizar
    pagina_atual = st.session_state.get('pagina_selecionada')


# --- Conteúdo das Páginas ---
if pagina_atual == "Visão Geral":
    st.header(f"Visão Geral do Negócio 💡")
    st.caption("Passe o mouse sobre os cards para ver mais detalhes.")
    st.markdown("---")
    
    # --- BUSCA DE TODOS OS DADOS NECESSÁRIOS ---
    cursor = setup.cursor
    conn = setup.conn
    
    # Dados para os cards
    total_vendas_valor = setup.calcular_valor_total_vendas(cursor)
    qtd_vendas = setup.calcular_quantidade_vendas(cursor)
    ticket_medio = setup.calcular_ticket_medio(cursor)
    num_clientes = setup.total_clientes(cursor)

    df_produtos = setup.get_vendas_por_produto(conn)
    df_pagamentos = setup.get_vendas_por_forma_pagamento(conn)
    df_dias = setup.get_vendas_por_dia_da_semana(conn)
    df_horas = setup.get_vendas_por_hora_do_dia(conn)
    df_categorias = setup.get_top_categorias(setup.conn)

    # 2. Pegue o NOME da primeira da lista (a mais vendida)

    # Encontra os valores de destaque
    produto_top = df_produtos.iloc[0]["Produto"] if not df_produtos.empty else "N/D"
    pagamento_top = df_pagamentos.iloc[0]["Forma de Pagamento"] if not df_pagamentos.empty else "N/D"
    dia_pico = df_dias.sort_values(by="Total Vendido", ascending=False).iloc[0]["Dia da Semana"] if not df_dias.empty else "N/D"
    hora_pico = df_horas.sort_values(by="Total Vendido", ascending=False).iloc[0]["Hora"] if not df_horas.empty else "N/D"
    categoria_top = df_categorias.iloc[0]["Categoria"] if not df_categorias.empty else "N/D"


    # --- FILEIRA 1: CARDS NUMÉRICOS ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card color-1">
            <h3>Receita Total</h3>
            <h2>R$ {total_vendas_valor:,.2f}</h2>
            <span class="tooltip-text">Faturamento total desde o início das operações.</span>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card color-2">
            <h3>Vendas Realizadas</h3>
            <h2>{qtd_vendas}</h2>
            <span class="tooltip-text">Número total de itens vendidos em todas as transações.</span>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card color-3">
            <h3>Ticket Médio</h3>
            <h2>R$ {ticket_medio:,.2f}</h2>
            <span class="tooltip-text">Valor médio gasto por cada transação ou compra.</span>
        </div>""", unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card color-4">
            <h3>Clientes Ativos</h3>
            <h2>{num_clientes}</h2>
            <span class="tooltip-text">Número de clientes únicos que já realizaram compras.</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- FILEIRA 2: CARDS DE DESTAQUE ---
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.markdown(f"""
        <div class="kpi-card color-5">
            <h3>Produto Campeão</h3>
            <h2>{produto_top}</h2>
            <span class="tooltip-text">O produto que mais gerou receita para o negócio.</span>
        </div>""", unsafe_allow_html=True)
        
    with col6:
        st.markdown(f"""
        <div class="kpi-card color-6">
            <h3>Pagamento Preferido</h3>
            <h2>{pagamento_top}</h2>
            <span class="tooltip-text">A forma de pagamento que acumulou o maior valor em vendas.</span>
        </div>""", unsafe_allow_html=True)

    with col7:
        st.markdown(f"""
        <div class="kpi-card color-7">
            <h3>Dia de Pico</h3>
            <h2>{dia_pico}</h2>
            <span class="tooltip-text">O dia da semana que, historicamente, possui o maior volume de vendas.</span>
        </div>""", unsafe_allow_html=True)

    with col8:
        st.markdown(f"""
        <div class="kpi-card color-8">
            <h3>Horário de Pico</h3>
            <h2>{hora_pico}</h2>
            <span class="tooltip-text">A hora do dia que, em média, concentra o maior faturamento.</span>
        </div>""", unsafe_allow_html=True)

elif pagina_atual == "Análise de Vendas": # <--- CORRIGIDO
    st.header(f"Análise de Vendas {icones_menu[opcoes_menu.index(pagina_atual)]}")
    st.write("Desempenho das vendas e sua peridiocidade")
    cursor = setup.cursor
    conn = setup.conn

    df_dias = setup.get_vendas_por_dia_da_semana(conn)
    df_horas = setup.get_vendas_por_hora_do_dia(conn)
    df_pico_horarios = setup.get_vendas_por_hora_do_dia(setup.conn)
    total_vendas_valor = setup.calcular_valor_total_vendas(cursor)
    qtd_vendas = setup.calcular_quantidade_vendas(cursor)
    ticket_medio = setup.calcular_ticket_medio(cursor)
    dia_pico = df_dias.sort_values(by="Total Vendido", ascending=False).iloc[0]["Dia da Semana"] if not df_dias.empty else "N/D"
    hora_pico = df_horas.sort_values(by="Total Vendido", ascending=False).iloc[0]["Hora"] if not df_horas.empty else "N/D"
    
    col1, col2, col3, col4, col5= st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="kpi-card color-10">
            <h3>Maior dia de Pico</h3>
            <h2>{dia_pico}</h2>
            <span class="tooltip-text">O dia da semana que, historicamente, possui o maior volume de vendas.</span>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card color-9">
            <h3>Horário de Pico</h3>
            <h2>{hora_pico}</h2>
            <span class="tooltip-text">A hora do dia que, em média, concentra o maior faturamento.</span>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card color-13">
            <h3>Vendas Realizadas</h3>
            <h2>{qtd_vendas}</h2>
            <span class="tooltip-text">Número total de itens vendidos em todas as transações.</span>
        </div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card color-14">
            <h3>Ticket Médio</h3>
            <h2>R$ {ticket_medio:,.2f}</h2>
            <span class="tooltip-text">Valor médio gasto por cada transação ou compra.</span>
        </div>""", unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="kpi-card color-16">
            <h3>Ticket Médio</h3>
            <h2>R$ {total_vendas_valor:,.2f}</h2>
            <span class="tooltip-text">Faturamento total desde o início das operações.</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    # Cria duas colunas para organizar os gráficos
    col3, col4 = st.columns(2)

    # --- GRÁFICO 1: DIAS DA SEMANA (na primeira coluna) ---
    with col3:
        st.subheader("Vendas por Dia da Semana")
        df_dia_semana = setup.get_vendas_por_dia_da_semana(setup.conn)
                # Plota o gráfico de barras
        st.bar_chart(df_dia_semana.set_index("Dia da Semana"))

        with st.expander("Ver dados detalhados"):
            st.dataframe(df_dia_semana, hide_index=True, use_container_width=True)
        

    # --- GRÁFICO 2: HORÁRIOS DE PICO (na segunda coluna) ---
    with col4:
        st.subheader("Vendas por Hora do Dia")
    
        st.bar_chart(df_pico_horarios.set_index("Hora"))

        with st.expander("Ver dados detalhados"):
            st.dataframe(df_pico_horarios, hide_index=True, use_container_width=True)

    st.markdown("---")


    st.subheader("Evolução Histórica das Vendas 📈")
    st.caption("Use o scroll do mouse para dar zoom e navegar pela linha do tempo.")
    df_evolucao = setup.obter_dados_vendas(setup.conn)

    # Criar gráfico de evolução de vendas)
    st.line_chart(df_evolucao.set_index("Dia"))

elif pagina_atual == "Análise de Produtos & Categorias":
    st.header(f"Análise de Produtos & Categorias 🗃️")
    st.markdown("---")

    df_produtos = setup.get_vendas_por_produto(setup.conn)
    # Encontra os valores de destaque
    produto_top = df_produtos.iloc[0]["Produto"] if not df_produtos.empty else "N/D"
    df_categorias = setup.get_top_categorias(setup.conn)

    # 2. Pegue o NOME da primeira da lista (a mais vendida)
    categoria_top = df_categorias.iloc[0]["Categoria"] if not df_categorias.empty else "N/D"

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="kpi-card color-11">
            <h3>Produto Campeão</h3>
            <h2>{produto_top}</h2>
            <span class="tooltip-text">O produto que mais gerou receita para o negócio.</span>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card color-12" title="A categoria de produtos que mais gerou receita.">
            <h3>Categoria Destaque</h3>
            <h2>{categoria_top}</h2>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("🏆 Produtos Mais Rentáveis")
        try:
            # 1. Busca a LISTA COMPLETA de todos os produtos
            df_todos_produtos = setup.get_top_produtos(setup.conn, limite=None)

            if not df_todos_produtos.empty:
                # 2. Cria uma "fatia" menor, apenas com o Top 3, para o GRÁFICO
                df_grafico = df_todos_produtos.head(3)
                
                # 3. Usa a fatia menor (Top 3) no gráfico
                st.bar_chart(df_grafico.set_index("Produto"))

                # 4. Usa a lista COMPLETA na tabela dentro do expander
                with st.expander("Ver lista completa de produtos"):
                    st.dataframe(
                        df_todos_produtos, 
                        hide_index=True, 
                        use_container_width=True
                    )
            else:
                st.warning("Não há dados de produtos para exibir.")
        except Exception as e:
            st.error(f"Erro ao buscar dados de produtos: {e}")

    with col4:
        st.subheader("🏆 Categorias Mais Rentáveis")
        
            # Lógica idêntica para as categorias
        df_todas_categorias = setup.get_top_categorias(setup.conn, limite=None)

            
        df_grafico_cat = df_todas_categorias.head(3)
                
        st.bar_chart(df_grafico_cat.set_index("Categoria"))

        with st.expander("Ver lista completa de categorias"):
                    st.dataframe(
                        df_todas_categorias, 
                        hide_index=True, 
                        use_container_width=True
                    )
        
# Em dashboard.py
elif pagina_atual == "Análises de Formas de Pagamento":
    st.header(f"Análises de Formas de Pagamento 📈")
    st.markdown("---")
    
    df_analise_pag = setup.get_analise_formas_pagamento(setup.conn)
    # --- Carrega os dados uma única vez ---
    df_pagamentos = setup.get_vendas_por_forma_pagamento(setup.conn)
    # 1. Busca os dados ordenados por frequência
    df_frequente = setup.get_frequencia_forma_pagamento(setup.conn)

    df_pag_qtd = setup.get_frequencia_forma_pagamento(setup.conn)
    # 2. Pega o nome do primeiro da lista
    pagamento_frequente = df_frequente.iloc[0]["Forma de Pagamento"] if not df_frequente.empty else "N/D"
    # 1. Busca os dados ordenados por valor
    df_rentavel = setup.get_vendas_por_forma_pagamento(setup.conn)
    # 2. Pega o nome do primeiro da lista
    pagamento_rentavel = df_rentavel.iloc[0]["Forma de Pagamento"] if not df_rentavel.empty else "N/D"

    # --- Layout em duas colunas para os gráficos principais ---
    col1, col2 = st.columns(2)

    with col1:

        # 3. Exibe o card
        st.markdown(f"""
        <div class="kpi-card color-6" title="A forma de pagamento utilizada no maior número de transações.">
            <h3>Pagamento Mais Frequente</h3>
            <h2>{pagamento_frequente}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # 3. Exibe o card
        st.markdown(f"""
        <div class="kpi-card color-2" title="A forma de pagamento que acumulou o maior valor em R$.">
            <h3>Pagamento Mais Rentável</h3>
            <h2>{pagamento_rentavel}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

    col3, col4, col5 = st.columns(3)
    
    with col3:
                st.subheader("Receita por Forma de Pagamento")
                # --- Gráfico 1: Popularidade por Valor (Donut Chart) ---
                fig = px.bar(
                df_pagamentos,
                x="Total Vendido",    # Valores numéricos vão no eixo X
                y="Forma de Pagamento",        # Nomes/Categorias vão no eixo Y
                orientation='h',    # 'h' para deixar as barras na horizontal
                title="",#titulo do card de grafico 
                text="Total Vendido"  # Adiciona o valor como texto em cada barra
            )

            # 2. Personaliza a aparência do gráfico
                fig.update_traces(
                            marker_color="#295F7F",     # Define uma cor azul bonita para as barras
                            texttemplate='R$ %{text:,.2f}', # Formata o texto para aparecer como moeda
                            textposition='auto',      # Posição do texto (fora da barra)
                            textfont_color='white',
                            textfont_size=16,
                            
                        )

                        # 3. Ordena as barras e ajusta o layout
                fig.update_layout(
                            xaxis_title="Total Vendido (R$)",
                            yaxis_title="Descrição",
                            title="", # Centraliza o título
                            # A linha abaixo é a mais importante: ordena as barras da maior para a menor!
                            yaxis={'categoryorder':'total ascending'}
                        )
                # Exibe o gráfico no Streamlit
                st.plotly_chart(fig, use_container_width=True)      

    with col4:
                # --- Gráfico 2: Comparativo de Ticket Médio (Bar Chart) ---
                st.subheader("Ticket Médio por Pagamento")
                df_ticket = setup.get_analise_formas_pagamento(setup.conn)

       
                fig_ticket = px.bar(
                df_ticket,
                x="Ticket Médio",    # Valores numéricos vão no eixo X
                y="Forma de Pagamento",        # Nomes/Categorias vão no eixo Y
                orientation='h',    # 'h' para deixar as barras na horizontal
                title="",#titulo do card de grafico 
                text="Ticket Médio"  # Adiciona o valor como texto em cada barra
            )

            # 2. Personaliza a aparência do gráfico
                fig_ticket.update_traces(
                            marker_color="#295F7F",     # Define uma cor azul bonita para as barras
                            texttemplate='%{text:,.2f}', # Formata o texto para aparecer como moeda
                            textposition='auto',      # Posição do texto (fora da barra)
                            textfont_color='white',
                            textfont_size=16,
                        )

                        # 3. Ordena as barras e ajusta o layout
                fig_ticket.update_layout(
                            xaxis_title="Total Ticket",
                            yaxis_title="Forma de Pagamento",
                            title="", # Centraliza o título
                            # A linha abaixo é a mais importante: ordena as barras da maior para a menor!
                            yaxis={'categoryorder':'total ascending'}
                        )
                # Exibe o gráfico no Streamlit
                st.plotly_chart(fig_ticket, use_container_width=True)
    with col5:
                st.subheader("Frequência de Uso")
                fig_qtd = px.pie(
                    df_pag_qtd,
                    names="Forma de Pagamento",
                    values="Qtd. Transações", # AQUI ESTÁ A MUDANÇA
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig_qtd.update_traces(textinfo='value+label', textfont_size=16, textfont_color='white')
                fig_qtd.update_layout(showlegend=False, title_text=' ', margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_qtd, use_container_width=True)
                
    st.markdown("---")   

            # --- Tabela com todos os detalhes ---
    with st.expander("Dados Detalhados"):
        total_faturado = df_analise_pag['Valor Total'].sum()
        df_analise_pag['Participação (%)'] = (df_analise_pag['Valor Total'] / total_faturado) * 100
        
        st.dataframe(
            df_analise_pag,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Valor Total": st.column_config.NumberColumn(format="R$ %.2f"),
                "Ticket Médio": st.column_config.NumberColumn(format="R$ %.2f"),
                "Participação (%)": st.column_config.ProgressColumn(
                    label="Participação na Receita",
                    format="%.2f%%",
                    min_value=0,
                    max_value=100,
                ),
            }
        )
elif pagina_atual == "Análises de Clientes":
    st.header(f"Análises de Clientes 👥")
    st.markdown("---")

    # --- CARDS DE KPI PARA CLIENTES ---
    # Busca os dados usando as funções que existem no seu setup.py
    total_de_clientes = setup.total_clientes(setup.cursor)
    
    # AQUI ESTÁ A CORREÇÃO: Chamando a nova função pelo nome correto
    receita_media_cliente = setup.calcular_receita_media_por_cliente(setup.cursor)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="kpi-card color-4"><h3>Total de Clientes</h3><h2>{total_de_clientes}</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card color-8"><h3>Receita Média / Cliente</h3><h2>R$ {receita_media_cliente:,.2f}</h2></div>', unsafe_allow_html=True)
        
    st.markdown("---")

    # --- GRÁFICO DE TOP CLIENTES ---
    st.subheader("Top 5 Clientes por Valor Gasto")
    
    # A função get_top_clientes já existe e está correta
    df_clientes = setup.get_top_clientes(setup.conn, limite=5)
    
    if not df_clientes.empty:
        fig_clientes = px.bar(
            df_clientes,
            x="Total Gasto",
            y="Cliente",
            orientation='h',
            text="Total Gasto"
        )
        fig_clientes.update_traces(
            marker_color='#0072B2',
            texttemplate='R$ %{text:,.2f}',
            textposition='auto'
        )
        fig_clientes.update_layout(
            yaxis={'categoryorder':'total ascending'},
            title_text=''
        )
        st.plotly_chart(fig_clientes, use_container_width=True)
    else:
        st.warning("Não há dados de clientes para exibir.")

else:
    if opcoes_menu:
        st.warning("Página não encontrada. Por favor, selecione uma opção válida no menu.")
