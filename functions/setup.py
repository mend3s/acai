import sqlite3
import pandas as pd # Removido se não usado diretamente aqui, mas pode ser útil para formatar saídas
import streamlit as st # Removido se não usado diretamente aqui # Removido se não usado diretamente aqui
from datetime import date # Importe 'date' para usar nos filtros
from functions import setup

# 📦 Conecta (ou cria) o banco de dados SQLite
# Esta conexão e cursor são globais e criados quando o módulo é importado.
conn = sqlite3.connect("acai.db", check_same_thread=False)
cursor = conn.cursor() # Este é o cursor global que suas funções podem usar

# 🏗️ Criação das tabelas (DDL)
cursor.execute('''
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco_unitario REAL NOT NULL,
    categoria_id INTEGER NOT NULL,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    preco_unitario_venda REAL NOT NULL, 
    valor_total_item REAL NOT NULL,   
    data_venda TEXT NOT NULL,         -- Formato 'YYYY-MM-DD HH:MM:SS'
    cliente_id INTEGER NOT NULL,
    formas_pagamento_id INTEGER NOT NULL,
    transacao_id INTEGER, 
    FOREIGN KEY (produto_id) REFERENCES produtos(id),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (formas_pagamento_id) REFERENCES formas_pagamento(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_categoria TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS formas_pagamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT NOT NULL
)
''')

# Aplica as criações de tabelas no banco de dados
conn.commit() # Adicionado para garantir que as tabelas sejam criadas/salvas.

#____________________________________________________________________________________________________________________________________________#

# FUNÇÕES DE CÁLCULO
# Todas as funções abaixo recebem um 'cursor_param' como argumento.
# Elas usarão esse cursor passado, não o global 'cursor' diretamente (a menos que você passe setup.cursor para elas).

def calcular_valor_total_vendas(cursor_param):
    cursor_param.execute("SELECT SUM(valor_total_item) FROM vendas;")
    resultado = cursor_param.fetchone()
    return resultado[0] if resultado and resultado[0] is not None else 0

def calcular_quantidade_vendas(cursor_param):
    cursor_param.execute("SELECT SUM(quantidade) FROM vendas;")
    resultado = cursor_param.fetchone()
    return resultado[0] if resultado and resultado[0] is not None else 0

def calcular_ticket_medio(cursor_param):
    """
    Calcula o ticket médio (valor total de vendas / número de transações distintas).
    Executa uma única query no banco de dados para maior eficiência.
    """
    # Esta query SQL faz todo o trabalho.
    # O banco de dados retornará NULL (None) se não houver transações, evitando erro de divisão por zero.
    query = """
    SELECT 
        SUM(valor_total_item) / COUNT(DISTINCT transacao_id) 
    FROM vendas 
    WHERE transacao_id IS NOT NULL;
    """
    
    cursor_param.execute(query)
    resultado = cursor_param.fetchone()
    
    # Se o 'resultado' existir e o valor dentro dele (resultado[0]) não for nulo, retorne o valor.
    # Caso contrário, retorne 0.
    return resultado[0] if resultado and resultado[0] is not None else 0

def total_clientes(cursor_param):
    cursor_param.execute("SELECT COUNT(*) FROM clientes;")
    resultado = cursor_param.fetchone()
    return resultado[0] if resultado and resultado[0] is not None else 0

def get_top_clientes(conn, limite=10):
    """Busca os clientes que mais gastaram, com um limite opcional."""
    query = """
    SELECT c.nome AS "Cliente", SUM(v.valor_total_item) AS "Total Gasto"
    FROM clientes c JOIN vendas v ON c.id = v.cliente_id
    GROUP BY c.id, c.nome ORDER BY "Total Gasto" DESC LIMIT ?;
    """
    return pd.read_sql_query(query, conn, params=(limite,))

def get_top_produtos(conn, limite=None): # O padrão agora é None
    """
    Busca os produtos mais vendidos (em valor).
    Se um limite for fornecido, aplica o LIMIT. Senão, busca todos.
    """
    query = """
    SELECT p.nome AS "Produto", SUM(v.valor_total_item) AS "Total Vendido"
    FROM produtos p JOIN vendas v ON p.id = v.produto_id
    GROUP BY p.nome ORDER BY "Total Vendido" DESC
    """
    params = []
    
    # Adiciona o LIMIT apenas se um valor for passado
    if limite is not None:
        query += " LIMIT ?;"
        params.append(limite)
    
    return pd.read_sql_query(query, conn, params=params)


def get_top_categorias(conn, limite=None): # O padrão agora é None
    """
    Busca as categorias mais vendidas (em valor).
    Se um limite for fornecido, aplica o LIMIT. Senão, busca todas.
    """
    query = """
    SELECT c.nome_categoria AS "Categoria", SUM(v.valor_total_item) AS "Total Vendido"
    FROM vendas v JOIN produtos p ON v.produto_id = p.id JOIN categorias c ON p.categoria_id = c.id
    GROUP BY c.nome_categoria ORDER BY "Total Vendido" DESC
    """
    params = []
    
    if limite is not None:
        query += " LIMIT ?;"
        params.append(limite)

    return pd.read_sql_query(query, conn, params=params)

def get_delta_style(cursor_param):
    if cursor > 0:
        # Aumento (bom) -> Verde
        return "color: #28a745;", "▲" # Cor verde e seta para cima
    elif cursor < 0:
        # Queda (ruim) -> Vermelho
        return "color: #dc3545;", "▼" # Cor vermelha e seta para baixo
    else:
        # Sem mudança
        return "color: #808080;", "" # Cor cinza e sem seta

def get_evolucao_vendas_diaria(conn):
    """Busca o total de vendas POR DIA."""
    query = """
    SELECT DATE(data_venda) AS "Dia", SUM(valor_total_item) AS "Total Vendido"
    FROM vendas GROUP BY "Dia" ORDER BY "Dia" ASC;
    """
    return pd.read_sql_query(query, conn)

def obter_dados_vendas(conn):
    """
    Busca o total de vendas AGRUPADO POR DIA.
    Esta é a forma correta para criar um gráfico de evolução limpo.
    """
    # A query foi corrigida para usar os nomes de coluna corretos:
    # 'data_venda' e 'valor_total_item'.
    # E já agrupa os dados por dia para o gráfico.
    query = """
    SELECT
        DATE(data_venda) AS "Dia",
        SUM(valor_total_item) AS "Total Vendido"
    FROM
        vendas
    GROUP BY
        "Dia"
    ORDER BY
        "Dia" ASC;
    """
    try:
        # Usa o pandas para ler o resultado da query diretamente para um DataFrame
        df = pd.read_sql_query(query, conn)
        # Converte a coluna 'Dia' para o tipo datetime, essencial para gráficos
        df['Dia'] = pd.to_datetime(df['Dia'])
        return df
    except Exception as e:
        print(f"Erro em obter_dados_vendas: {e}")
        return pd.DataFrame(columns=["Dia", "Total Vendido"])
    
def get_vendas_por_hora_do_dia(conn):
    """
    Busca o total de vendas consolidado para cada hora do dia (0-23h).
    Retorna um DataFrame pronto para um gráfico de barras.
    """
    # A função strftime('%H', data_venda) extrai apenas a hora (ex: '14', '15')
    # de cada registro de venda.
    query = """
    SELECT
        strftime('%H', data_venda) || 'h' AS "Hora", -- Adiciona um 'h' para ficar mais legível
        SUM(valor_total_item) AS "Total Vendido"
    FROM
        vendas
    GROUP BY
        "Hora"
    ORDER BY
        "Hora" ASC; -- Ordena das 0h às 23h
    """
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Erro em get_vendas_por_hora_do_dia: {e}")
        return pd.DataFrame(columns=["Hora", "Total Vendido"])
    
def get_evolucao_receita_mensal(cursor):
    """
    Calcula a receita do mês atual e anterior para o delta do card.
    Retorna o valor atual e a variação percentual.
    """
    query = """
    SELECT
        SUM(CASE WHEN strftime('%Y-%m', data_venda) = strftime('%Y-%m', 'now', 'localtime') THEN valor_total_item ELSE 0 END),
        SUM(CASE WHEN strftime('%Y-%m', data_venda) = strftime('%Y-%m', 'now', '-1 month', 'localtime') THEN valor_total_item ELSE 0 END)
    FROM vendas
    WHERE strftime('%Y-%m', data_venda) IN (strftime('%Y-%m', 'now', 'localtime'), strftime('%Y-%m', 'now', '-1 month', 'localtime'));
    """
    cursor.execute(query)
    receita_atual, receita_anterior = cursor.fetchone()
    receita_atual = receita_atual or 0
    receita_anterior = receita_anterior or 0
    
    variacao_perc = ((receita_atual - receita_anterior) / receita_anterior) * 100 if receita_anterior > 0 else float('inf')
    return receita_atual, variacao_perc
 
def get_vendas_por_dia_da_semana(conn):
    """
    Busca o total de vendas consolidado para cada dia da semana (Domingo, Segunda, etc.).
    Retorna um DataFrame ordenado de Domingo (0) a Sábado (6).
    """
    # A mágica acontece aqui no SQL:
    # 1. strftime('%w', data_venda) extrai o dia da semana como um número (0=Domingo, 1=Segunda, etc.)
    # 2. A declaração CASE...WHEN...END traduz esses números para os nomes dos dias em português.
    # 3. Agrupamos e ordenamos pelo NÚMERO do dia da semana para manter a ordem cronológica.
    query = """
    SELECT
        CASE strftime('%w', data_venda)
            WHEN '0' THEN 'Domingo'
            WHEN '1' THEN 'Segunda-feira'
            WHEN '2' THEN 'Terça-feira'
            WHEN '3' THEN 'Quarta-feira'
            WHEN '4' THEN 'Quinta-feira'
            WHEN '5' THEN 'Sexta-feira'
            WHEN '6' THEN 'Sábado'
        END AS "Dia da Semana",
        SUM(valor_total_item) AS "Total Vendido"
    FROM
        vendas
    GROUP BY
        strftime('%w', data_venda) -- Agrupa pelo número do dia
    ORDER BY
        strftime('%w', data_venda) ASC; -- Ordena pelo número do dia
    """
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Erro em get_vendas_por_dia_da_semana: {e}")
        return pd.DataFrame(columns=["Dia da Semana", "Total Vendido"])
    

def get_vendas_por_produto(conn):
    """Busca o valor total de vendas para cada produto."""
    query = """
    SELECT p.nome AS "Produto", SUM(v.valor_total_item) AS "Total Vendido"
    FROM produtos p JOIN vendas v ON p.id = v.produto_id
    GROUP BY p.nome ORDER BY "Total Vendido" DESC;
    """
    return pd.read_sql_query(query, conn)

def get_vendas_por_forma_pagamento(conn):
    """Busca o valor total de vendas para cada forma de pagamento."""
    query = """
    SELECT fp.descricao AS "Forma de Pagamento", SUM(v.valor_total_item) AS "Total Vendido"
    FROM formas_pagamento fp JOIN vendas v ON fp.id = v.formas_pagamento_id
    GROUP BY fp.descricao ORDER BY "Total Vendido" DESC;
    """
    return pd.read_sql_query(query, conn)


#funções de hanking

# Em functions/setup.py
def get_analise_formas_pagamento(conn):
    """
    Calcula o Valor Total, a Quantidade de Transações e o Ticket Médio 
    para cada forma de pagamento. Retorna UM DataFrame completo.
    """
    query = """
    SELECT
        fp.descricao AS "Forma de Pagamento",
        SUM(v.valor_total_item) AS "Valor Total",
        COUNT(DISTINCT v.transacao_id) AS "Qtd. Transações",
        CASE
            WHEN COUNT(DISTINCT v.transacao_id) > 0
            THEN SUM(v.valor_total_item) / COUNT(DISTINCT v.transacao_id)
            ELSE 0
        END AS "Ticket Médio"
    FROM formas_pagamento fp JOIN vendas v ON fp.id = v.formas_pagamento_id
    WHERE v.transacao_id IS NOT NULL
    GROUP BY fp.descricao ORDER BY "Valor Total" DESC;
    """
    return pd.read_sql_query(query, conn)
    """
    Calcula o Valor Total, a Quantidade de Transações e o Ticket Médio para cada forma de pagamento.
    Retorna um DataFrame completo para análise.
    """
    # Esta query junta as tabelas e usa funções de agregação para calcular tudo de uma vez.
    query = """
    SELECT
        fp.descricao AS "Forma de Pagamento",
        SUM(v.valor_total_item) AS "Valor Total",
        COUNT(DISTINCT v.transacao_id) AS "Qtd. Transações",
        -- Usamos CASE para evitar divisão por zero se não houver transações
        CASE
            WHEN COUNT(DISTINCT v.transacao_id) > 0
            THEN SUM(v.valor_total_item) / COUNT(DISTINCT v.transacao_id)
            ELSE 0
        END AS "Ticket Médio"
    FROM
        formas_pagamento fp
    JOIN
        vendas v ON fp.id = v.formas_pagamento_id
    WHERE
        v.transacao_id IS NOT NULL
    GROUP BY
        fp.descricao
    ORDER BY
        "Valor Total" DESC;
    """
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Erro em get_analise_formas_pagamento: {e}")
        return pd.DataFrame()
    
def get_frequencia_forma_pagamento(conn):
    """
    Busca a QUANTIDADE DE TRANSAÇÕES para cada forma de pagamento, ordenado da mais frequente para a menos.
    """
    query = """
    SELECT fp.descricao AS "Forma de Pagamento", COUNT(DISTINCT v.transacao_id) AS "Qtd. Transações"
    FROM formas_pagamento fp JOIN vendas v ON fp.id = v.formas_pagamento_id
    WHERE v.transacao_id IS NOT NULL
    GROUP BY fp.descricao ORDER BY "Qtd. Transações" DESC;
    """
    return pd.read_sql_query(query, conn)
    


def get_novos_clientes_por_mes(conn):
    """Retorna um DataFrame com a contagem de novos clientes para cada mês."""
    query = """
    WITH PrimeiraCompra AS (
        SELECT cliente_id, MIN(DATE(data_venda)) as data_primeira_compra
        FROM vendas GROUP BY cliente_id
    )
    SELECT strftime('%Y-%m', data_primeira_compra) || '-01' AS "Mês", COUNT(cliente_id) AS "Novos Clientes"
    FROM PrimeiraCompra GROUP BY "Mês" ORDER BY "Mês" ASC;
    """
    df = pd.read_sql_query(query, conn)
    df['Mês'] = pd.to_datetime(df['Mês'])
    return df

def get_distribuicao_frequencia(conn):
    """Retorna um DataFrame com a contagem de clientes por número de compras."""
    query = """
    WITH FrequenciaPorCliente AS (
        SELECT cliente_id, COUNT(DISTINCT transacao_id) AS num_compras
        FROM vendas WHERE transacao_id IS NOT NULL GROUP BY cliente_id
    )
    SELECT 
        CASE 
            WHEN num_compras = 1 THEN '1 Compra'
            WHEN num_compras = 2 THEN '2 Compras'
            WHEN num_compras BETWEEN 3 AND 5 THEN '3-5 Compras'
            ELSE '6+ Compras'
        END AS "Grupo de Frequência",
        COUNT(cliente_id) AS "Número de Clientes"
    FROM FrequenciaPorCliente GROUP BY "Grupo de Frequência";
    """
    return pd.read_sql_query(query, conn)

def calcular_receita_media_por_cliente(cursor):
    """Calcula o valor médio que cada cliente gastou no total."""
    query = "SELECT SUM(valor_total_item) / COUNT(DISTINCT cliente_id) FROM vendas WHERE cliente_id IS NOT NULL;"
    try:
        cursor.execute(query)
        resultado = cursor.fetchone()
        return resultado[0] if resultado and resultado[0] is not None else 0
    except Exception as e:
        print(f"Erro em calcular_receita_media_por_cliente: {e}")
        return 0