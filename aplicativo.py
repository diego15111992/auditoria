import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import date


# Configuração inicial do Streamlit
st.set_page_config(page_title="Controle de Pallets", layout="wide")
st.title("Gerenciamento de Pallets Mariza Group")

col1,col2,col3,col4 = st.columns(4)

#with col1:
    #st.image("c5.png",width=190)
#with col2:
    #st.image("mariza.png",width=190)
#with col3:
    #st.image("polar.png",width=150)
#with col4:
    #st.image("fruasul.png")    
        
# Configurar o banco de dados SQLite
conn = sqlite3.connect("pallets.db")
c = conn.cursor()

# Criar tabela no banco de dados
c.execute('''CREATE TABLE IF NOT EXISTS pallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nota_fiscal TEXT,
    cliente TEXT,
    data_mov DATE,
    quantidade INTEGER,
    tipo_movimento TEXT,
    filial TEXT,
    status TEXT,
    observacoes TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)''')
conn.commit()

# Funções auxiliares para autenticação
def autenticar_usuario(username, password):
    user = c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
    return user

def criar_usuario(username, password):
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        st.error("Usuário já existe!")

# Funções auxiliares para manipulação de dados
def adicionar_registro(nota_fiscal, cliente, data_mov, quantidade, tipo_movimento, filial, status, observacoes):
    c.execute('''INSERT INTO pallets (nota_fiscal, cliente, data_mov, quantidade, tipo_movimento, filial, status, observacoes)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (nota_fiscal, cliente, data_mov, quantidade, tipo_movimento, filial, status, observacoes))
    conn.commit()

def obter_dados():
    return pd.read_sql_query("SELECT * FROM pallets", conn)

def limpar():
    pass

def editar_registro(id, nota_fiscal, cliente, data_mov, quantidade, tipo_movimento, filial, status, observacoes):
    c.execute('''UPDATE pallets
                 SET nota_fiscal = ?, cliente = ?, data_mov = ?, quantidade = ?, tipo_movimento = ?, filial = ?, status = ?, observacoes = ?
                 WHERE id = ?''',
              (nota_fiscal, cliente, data_mov, quantidade, tipo_movimento, filial, status, observacoes, id))
    conn.commit()

def deletar_registro(id):
    c.execute('DELETE FROM pallets WHERE id = ?', (id,))
    conn.commit()

# Tela de login
def tela_login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Usuário")
    password = st.sidebar.text_input("Senha", type="password")
    if st.sidebar.button("Entrar"):
        if autenticar_usuario(username, password):
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = username
            st.success(f"Bem-vindo, {username}!")
        else:
            st.error("Usuário ou senha inválidos.")

def tela_cadastro():
    st.sidebar.title("Cadastro de Usuário")
    username = st.sidebar.text_input("Novo Usuário")
    password = st.sidebar.text_input("Nova Senha", type="password")
    
    # Botão para criar novo usuário
    if st.sidebar.button("Cadastrar"):
        criar_usuario(username, password)
        st.success("Usuário cadastrado com sucesso!")
    
    # Seção de filtros dinâmicos
    st.subheader("Usuários Cadastrados")
    with st.expander("Filtros Dinâmicos"):
        filtro_id = st.text_input("Filtrar por ID", "")
        filtro_nome = st.text_input("Filtrar por Nome de Usuário", "")
    
    # Aplicar filtros
    query = "SELECT * FROM users WHERE 1=1"  # Base da query (filtro sempre verdadeiro)
    params = []
    
    if filtro_id.strip():
        query += " AND id = ?"
        params.append(filtro_id.strip())
    
    if filtro_nome.strip():
        query += " AND username LIKE ?"
        params.append(f"%{filtro_nome.strip()}%")
    
    df_usuarios = pd.read_sql_query(query, conn, params=params)
    st.dataframe(df_usuarios)

    # Formulário para edição ou deleção de usuários
    with st.form("editar_deletar_usuarios"):
        st.write("**Editar ou Deletar Usuários**")
        user_id = st.number_input("ID do Usuário", min_value=1, step=1)
        novo_username = st.text_input("Novo Nome de Usuário (para editar)")
        nova_senha = st.text_input("Nova Senha (para editar)", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            editar_usuario_btn = st.form_submit_button("Editar")
        with col2:
            deletar_usuario_btn = st.form_submit_button("Deletar")
        
        # Ações dos botões
        if editar_usuario_btn:
            editar_usuario(user_id, novo_username, nova_senha)
            st.success(f"Usuário com ID {user_id} foi editado com sucesso!")
        
        if deletar_usuario_btn:
            deletar_usuario(user_id)
            st.success(f"Usuário com ID {user_id} foi deletado com sucesso!")

# Função para editar usuário
def editar_usuario(user_id, novo_username, nova_senha):
    if novo_username and nova_senha:
        try:
            c.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (novo_username, nova_senha, user_id))
            conn.commit()
        except sqlite3.IntegrityError:
            st.error("O nome de usuário já existe. Escolha outro.")
    else:
        st.error("Por favor, preencha o novo nome de usuário e a nova senha.")

# Função para deletar usuário
def deletar_usuario(user_id):
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()


# Verificar autenticação
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    tela_login()
    st.stop()

# Configuração de abas
aba = st.sidebar.selectbox("Selecione a aba", ["Lançamentos", "Visão Geral","Cadastro de Usuario"])
imagem = st.sidebar.image("pallet_image.png")
if aba == "Lançamentos":
    
    # Obter dados do banco
    df = obter_dados()
    
    # Filtros dinâmicos
    st.sidebar.header("Filtros Dinâmicos")
    
    filtro_nota_fiscal = st.sidebar.text_input("Filtrar por Nota Fiscal", "")
    filtro_cliente = st.sidebar.text_input("Filtrar por Cliente", "")
    filtro_filial = st.sidebar.multiselect(
        "Filtrar por Filial", 
        options=df["filial"].unique(), 
        default=df["filial"].unique()
    )
    filtro_status = st.sidebar.multiselect(
        "Filtrar por Status", 
        options=df["status"].unique(), 
        default=df["status"].unique()
    )
    filtro_data_inicio = st.sidebar.date_input("Data Inicial", value=date.today().replace(day=1))
    filtro_data_final = st.sidebar.date_input("Data Final", value=date.today())

    # Aplicar filtros
    filtros = (df["filial"].isin(filtro_filial)) & \
              (df["status"].isin(filtro_status)) & \
              (df["data_mov"] >= str(filtro_data_inicio)) & \
              (df["data_mov"] <= str(filtro_data_final))

    if filtro_nota_fiscal.strip():
        filtros &= df["nota_fiscal"].str.contains(filtro_nota_fiscal.strip(), case=False, na=False)

    if filtro_cliente.strip():
        filtros &= df["cliente"].str.contains(filtro_cliente.strip(), case=False, na=False)

    df_filtrado = df[filtros]
    
    # Exibir lançamentos filtrados
    st.subheader("Histórico de Lançamentos")
    df_renomeado = df_filtrado.rename(columns={
        "id": "ID", 
        "nota_fiscal": "NOTA FISCAL", 
        "cliente": "CLIENTE", 
        "data_mov": "DATA_MOVI", 
        "quantidade": "QTD", 
        "tipo_movimento": "TIPO_MOVIMENTO", 
        "filial": "FILIAL", 
        "status": "STATUS", 
        "observacoes": "OBSERVAÇÕES"
    })
    st.dataframe(df_renomeado.reset_index(drop=True))
    
    # Formulário de lançamentos
    st.subheader("Novo Lançamento")
    with st.form("lancamentos"):
        nota_fiscal = st.text_input("Nota Fiscal")
        cliente = st.text_input("Cliente")
        data_mov = st.date_input("Data", value=date.today())
        quantidade = st.number_input("Quantidade", min_value=1, step=1)
        tipo_movimento = st.selectbox("Tipo de Movimento", options=["Entrada", "Saída"])
        filial = st.selectbox("Filial", options=["Matriz Castanhal", "C5 São Paulo", "Fruta Sul", "João Pessoa", "Polar"])
        status = st.selectbox("Status", options=["Em Estoque", "Em Trânsito", "Quebrado", "Extraviado"])
        observacoes = st.text_area("Observações")
        submit_lancamento = st.form_submit_button("Lançar")

        if submit_lancamento:
            adicionar_registro(nota_fiscal, cliente, data_mov, quantidade, tipo_movimento, filial, status, observacoes)
            st.success("Lançamento realizado com sucesso!")
    
    # Formulário para editar e deletar registros
    st.subheader("Editar/Deletar Lançamentos")
    with st.form("editar_deletar"):
        id_registro = st.number_input("ID do Registro", min_value=1, step=1)
        nota_fiscal = st.text_input("Nota Fiscal (Editar)")
        cliente = st.text_input("Cliente (Editar)")
        data_mov = st.date_input("Data (Editar)", value=date.today())
        quantidade = st.number_input("Quantidade (Editar)", min_value=1, step=1)
        tipo_movimento = st.selectbox("Tipo de Movimento (Editar)", options=["Entrada", "Saída"])
        filial = st.selectbox("Filial (Editar)", options=["Matriz Castanhal", "C5 São Paulo", "Fruta Sul", "João Pessoa", "Polar"])
        status = st.selectbox("Status (Editar)", options=["Em Estoque", "Em Trânsito", "Quebrado", "Extraviado"])
        observacoes = st.text_area("Observações (Editar)")
        col1, col2 = st.columns(2)
        with col1:
            submit_editar = st.form_submit_button("Editar")
        with col2:
            submit_deletar = st.form_submit_button("Deletar")

        if submit_editar:
            editar_registro(id_registro, nota_fiscal, cliente, data_mov, quantidade, tipo_movimento, filial, status, observacoes)
            st.success("Registro editado com sucesso!")
        if submit_deletar:
            deletar_registro(id_registro)
            st.success("Registro deletado com sucesso!")

elif aba == "Visão Geral":
    # Filtros dinâmicos
    st.sidebar.header("Filtros")
    df = obter_dados()
    filial_filtro = st.sidebar.multiselect("Filtrar por Filial", options=df["filial"].unique(), default=df["filial"].unique())
    status_filtro = st.sidebar.multiselect("Filtrar por Status", options=df["status"].unique(), default=df["status"].unique())
    data_inicio = st.sidebar.date_input("Data Inicial", value=date.today().replace(day=1))
    data_final = st.sidebar.date_input("Data Final", value=date.today())

    # Aplicar filtros
    filtros = (df["filial"].isin(filial_filtro)) & (df["status"].isin(status_filtro)) & (df["data_mov"] >= str(data_inicio)) & (df["data_mov"] <= str(data_final))
    df_filtrado = df[filtros]

    # Exibir métricas
    st.header("Resumo Geral")
    estoque_total = df_filtrado[df_filtrado["status"] == "Em Estoque"]["quantidade"].sum()
    transito_total = df_filtrado[df_filtrado["status"] == "Em Trânsito"]["quantidade"].sum()
    quebrados_total = df_filtrado[df_filtrado["status"] == "Quebrado"]["quantidade"].sum()
    extraviado_total = df_filtrado[df_filtrado["status"] == "Extraviado"]["quantidade"].sum()

    col1, col2, col3,col4 = st.columns(4)
    col1.metric("Em Estoque", estoque_total)
    col2.metric("Em Trânsito", transito_total)
    col3.metric("Quebrado",quebrados_total)
    col4.metric("Extraviado", extraviado_total)

   
    # Gráfico de barras
    st.subheader("Análise por Filial")
    grafico_barras = px.bar(
    df_filtrado.groupby(["filial", "status"]).sum().reset_index(),
    x="filial",
    y="quantidade",
    color="status",
    barmode="group",
    title="",
    labels={"filial": "", "quantidade": "", "status": ""}
)
    st.plotly_chart(grafico_barras, use_container_width=True)


    # Gráfico de pizza por status
    st.subheader("Análise por Status")
    grafico_pizza = px.pie(
    df_filtrado,
    names="status",
    values="quantidade",
    title="",
    hole=0.4,
    labels={"status": "", "quantidade": ""},
)
    st.plotly_chart(grafico_pizza, use_container_width=True)

    # Tabela dos dados filtrados
    st.subheader("Tabela de Dados Filtrados")
    st.dataframe(df_filtrado.reset_index(drop=True))

    # Botão para exportar relatório
    st.subheader("Exportar Relatório")
    exportar_csv = st.button("Exportar para CSV")
    if exportar_csv:
        csv = df_filtrado.to_csv(index=False)
        st.download_button(
            label="Baixar CSV",
            data=csv,
            file_name="relatorio_pallets.csv",
            mime="text/csv",
        )
elif aba == "Cadastro de Usuario":
    tela_cadastro()
    