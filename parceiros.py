import streamlit as st
import pandas as pd
import unicodedata
import mysql.connector

# ---------------------------------------------------------
# CONFIGURAÇÃO
# ---------------------------------------------------------
st.set_page_config(page_title="Parceiros JWM", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right,#000000, #09203f, #517fa4);
    background-attachment: fixed;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# NORMALIZADOR
# ---------------------------------------------------------
def norm(x):
    return unicodedata.normalize("NFKD", str(x).strip()) \
        .encode("ascii", "ignore") \
        .decode() \
        .upper()

# ---------------------------------------------------------
# CONEXÃO MYSQL (STREAMLIT)
# ---------------------------------------------------------
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        port=st.secrets["mysql"]["port"]
    )

# ---------------------------------------------------------
# CARREGAR DADOS
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def carregar_df():
    try:
        conn = get_connection()
        query = """
            SELECT
                placa AS PLACA,
                marca AS MARCA,
                modelo AS MODELO,
                ano AS ANO,
                tipo_veiculo AS `TIPO DE VEICULO`,
                motorista AS MOTORISTA,
                telefone AS TELEFONE,
                cidade AS CIDADE,
                estado AS ESTADO,
                rastreador AS RASTREADOR,
                curso_mop AS `CURSO MOP`,
                data_cadastro AS `DATA DO CADASTRO`,
                indicacao AS INDICACAO
            FROM parceiros_jwm
        """
        df = pd.read_sql(query, conn)
        conn.close()
        df.columns = [norm(c) for c in df.columns]
        return df.fillna("")
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()

# ---------------------------------------------------------
# FILTROS
# ---------------------------------------------------------
filtros = [
    ("PLACA", "Placa"),
    ("INDICACAO", "Indicação"),
    ("RASTREADOR","Rastreador"),
    ("ESTADO","Estado"),
    ("CIDADE","Cidade"),
    ("TIPO DE VEICULO","Tipo Veículo"),
    ("ANO","Ano"),
    ("MOTORISTA","Motorista"),
    ("TELEFONE","Telefone"),
    ("CURSO MOP","Curso MOP"),
    ("DATA DO CADASTRO", "Data do cadastro")
]

for col,_ in filtros:
    st.session_state.setdefault(f"f_{col}", [])

def clear_filter(col):
    st.session_state[f"f_{col}"] = []

def clear_all_filters():
    for col,_ in filtros:
        st.session_state[f"f_{col}"] = []

def filtrar(df):
    temp = df.copy()
    for col,_ in filtros:
        vals = st.session_state[f"f_{col}"]
        if vals:
            temp = temp[temp[col].isin(vals)]
    return temp

# ---------------------------------------------------------
# CABEÇALHO
# ---------------------------------------------------------
st.title("Gestão de Parceiros 🚛💼🌎")
st.write("Motoristas Terceiros")

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
df_base = carregar_df()

with st.sidebar:
    st.title("Filtros")
    with st.expander("🎛️ Filtros Inteligentes"):
        for i in range(0, len(filtros), 2):
            colA, colB = st.columns(2)

            fcol1, flabel1 = filtros[i]
            with colA:
                ops = sorted([v for v in df_base[fcol1].unique() if v])
                st.multiselect(flabel1, ops, key=f"f_{fcol1}")
                st.button("❌", on_click=clear_filter, args=(fcol1,), key=f"c_{fcol1}")

            if i + 1 < len(filtros):
                fcol2, flabel2 = filtros[i+1]
                with colB:
                    ops2 = sorted([v for v in df_base[fcol2].unique() if v])
                    st.multiselect(flabel2, ops2, key=f"f_{fcol2}")
                    st.button("❌", on_click=clear_filter, args=(fcol2,), key=f"c_{fcol2}")

    st.button("🧹 LIMPAR TODOS", on_click=clear_all_filters)

# ---------------------------------------------------------
# TABELA
# ---------------------------------------------------------
df_filtrado = filtrar(df_base).drop(columns=["INDICACAO"], errors="ignore")
st.subheader("📋 Dados filtrados")
st.dataframe(df_filtrado, use_container_width=True)

# ---------------------------------------------------------
# FORMULÁRIO
# ---------------------------------------------------------
st.markdown("## 📝 Cadastro de Parceiro / Motorista")

with st.form("cadastro"):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        placa = st.text_input("Placa")
        marca = st.text_input("Marca")
        modelo = st.text_input("Modelo")
        tipo = st.text_input("Tipo de Veículo")

    with col2:
        ano = st.text_input("Ano")
        motorista = st.text_input("Motorista")
        curso = st.selectbox("Curso MOP", ["SIM","NAO"])
        indicacao = st.selectbox("Indicação", ["SIM","NAO"])

    with col3:
        telefone = st.text_input("Telefone")
        cidade = st.text_input("Cidade")
        estado = st.text_input("Estado")
        rastreador = st.selectbox("Rastreador", ["SIM","NAO"])

    with col4:
        data = st.text_input("Data do cadastro")

    send = st.form_submit_button("💾 SALVAR")

# ---------------------------------------------------------
# SALVAR NO MYSQL
# ---------------------------------------------------------
if send:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO parceiros_jwm
            (placa, marca, modelo, ano, tipo_veiculo, motorista,
             telefone, cidade, estado, rastreador,
             curso_mop, data_cadastro, indicacao)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            norm(placa), norm(marca), norm(modelo), norm(ano),
            norm(tipo), norm(motorista), norm(telefone),
            norm(cidade), norm(estado), norm(rastreador),
            norm(curso), norm(data), norm(indicacao)
        )

        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()

        st.success("✔ Registro salvo com sucesso!")
        st.cache_data.clear()
        st.rerun()

    except Exception as e:
        st.error(f"❌ Erro ao salvar: {e}")
