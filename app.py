import streamlit as st
import pandas as pd
import unicodedata
import mysql.connector
import os

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Parceiros JWM",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right,#000000, #09203f, #517fa4);
    background-attachment: fixed;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.image(
    "https://jwmlogistica.com.br/wp-content/uploads/2022/06/cropped-logo-jwm.png",
    width=420
)
st.markdown("## **Gestão de Parceiros 🚛💼🌎**")
st.write("**Motoristas Terceiros**")
st.markdown("---")

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================
def norm(x):
    if x is None:
        return ""
    return unicodedata.normalize(
        "NFKD", str(x).strip()
    ).encode("ascii", "ignore").decode().upper()

def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        port=st.secrets["mysql"]["port"]
    )

# =========================================================
# CARREGAR DADOS
# =========================================================
@st.cache_data(show_spinner=False)
def carregar_df():
    conn = get_connection()
    df = pd.read_sql("""
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
            indicacao AS INDICACAO,
            tags AS TAGS,
            usuario AS USUARIO
        FROM parceiros_jwm
    """, conn)
    conn.close()
    df.columns = [norm(c) for c in df.columns]
    return df.fillna("")

df_base = carregar_df()

# =========================================================
# FILTROS
# =========================================================
filtros = [
    ("PLACA", "Placa"),
    ("INDICACAO", "Indicação"),
    ("RASTREADOR", "Rastreador"),
    ("ESTADO", "Estado"),
    ("CIDADE", "Cidade"),
    ("TIPO DE VEICULO", "Tipo Veículo"),
    ("ANO", "Ano"),
    ("MOTORISTA", "Motorista"),
    ("TAGS", "Tags"),
    ("USUARIO", "Usuário")
]

for col, _ in filtros:
    st.session_state.setdefault(f"f_{col}", [])

def clear_all_filters():
    for col, _ in filtros:
        st.session_state[f"f_{col}"] = []

def filtrar(df):
    temp = df.copy()
    for col, _ in filtros:
        valores = st.session_state.get(f"f_{col}")
        if valores:
            temp = temp[temp[col].isin(valores)]
    return temp

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.title("🎛️ Filtros")
    colA, colB = st.columns(2)

    for i, (col, label) in enumerate(filtros):
        opcoes = sorted([v for v in df_base[col].unique() if v])
        with (colA if i % 2 == 0 else colB):
            st.multiselect(label, opcoes, key=f"f_{col}")

    st.markdown("---")
    st.button("🧹 LIMPAR TODOS OS FILTROS", on_click=clear_all_filters)

    with st.expander("📘 IST (Instrução de Trabalho)"):
        if os.path.exists("QR Code.png"):
            st.image("QR Code.png", width=120)
        else:
            st.info("QR Code não encontrado")

    st.markdown("### 🔗 Links Importantes")
    st.markdown("""
    - 🗺️ [Google Maps](https://www.google.com/maps)
    - 🌐 [Site JWM](https://jwmlogistica.com.br)
    - 📊 [Power BI](https://app.powerbi.com)
    - 📦🚚 [Dimensionamento Veículo](https://dimensionamento-de-ve-culos---jwm-dvxn4ufxfmnmyanmv3ohte.streamlit.app/)
    """)

# =========================================================
# IMPORTAÇÃO
# =========================================================
st.markdown("## 📤 Importar Planilha")
uploaded = st.file_uploader(
    "Selecione o arquivo (.xls ou .xlsx)",
    type=["xls", "xlsx"]
)

if uploaded:
    df_import = pd.read_excel(uploaded).fillna("")
    df_import.columns = [norm(c) for c in df_import.columns]

    st.info(f"📄 {len(df_import)} registros prontos para importação")
    st.dataframe(df_import, use_container_width=True)

    if st.button("✅ CONFIRMAR IMPORTAÇÃO"):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            for _, row in df_import.iterrows():
                cursor.execute("""
                    INSERT INTO parceiros_jwm
                    (placa, marca, modelo, ano, tipo_veiculo, motorista,
                     telefone, cidade, estado, rastreador,
                     curso_mop, data_cadastro, indicacao, tags, usuario)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, tuple(norm(row.get(c)) for c in df_import.columns))

            conn.commit()
            cursor.close()
            conn.close()

            st.success("✔ Importação realizada com sucesso!")
            st.cache_data.clear()
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erro na importação: {e}")

st.markdown("---")

# =========================================================
# TABELA
# =========================================================
st.subheader("📋 Dados Filtrados")
st.dataframe(filtrar(df_base), use_container_width=True)

# =========================================================
# FUNÇÃO LIMPAR FORMULÁRIO
# =========================================================
def limpar_formulario():
    for k in [
        "placa","marca","modelo","tipo","ano","motorista",
        "telefone","cidade","estado","data","usuario"
    ]:
        st.session_state[k] = ""

    st.session_state.update({
        "curso": "SIM",
        "indicacao": "SIM",
        "rastreador": "SIM",
        "tags": "CONECT CAR"
    })

# =========================================================
# CADASTRO MANUAL
# =========================================================
st.markdown("## 📝 Cadastro Manual")

with st.form("cadastro"):
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        placa = st.text_input("Placa", key="placa")
        marca = st.text_input("Marca", key="marca")
        modelo = st.text_input("Modelo", key="modelo")
        tipo = st.text_input("Tipo de Veículo", key="tipo")

    with c2:
        ano = st.text_input("Ano", key="ano")
        motorista = st.text_input("Motorista", key="motorista")
        curso = st.selectbox("Curso MOP", ["SIM","NAO"], key="curso")
        indicacao = st.selectbox("Indicação", ["SIM","NAO"], key="indicacao")

    with c3:
        telefone = st.text_input("Telefone", key="telefone")
        cidade = st.text_input("Cidade", key="cidade")
        estado = st.text_input("Estado", key="estado")
        rastreador = st.selectbox("Rastreador", ["SIM","NAO"], key="rastreador")

    with c4:
        data = st.text_input("Data do cadastro", key="data")
        tags = st.selectbox(
            "Tags",
            ["CONECT CAR","SEM PARAR","VELOE","MOVE MAIS"],
            key="tags"
        )
        usuario = st.text_input("Usuário", key="usuario")

    col1, col2 = st.columns(2)
    salvar = col1.form_submit_button("💾 SALVAR")
    limpar = col2.form_submit_button("🧹 LIMPAR CAMPOS")

if limpar:
    limpar_formulario()
    st.rerun()

if salvar:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO parceiros_jwm
            (placa, marca, modelo, ano, tipo_veiculo, motorista,
             telefone, cidade, estado, rastreador,
             curso_mop, data_cadastro, indicacao, tags, usuario)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            norm(placa), norm(marca), norm(modelo), norm(ano),
            norm(tipo), norm(motorista), norm(telefone),
            norm(cidade), norm(estado), norm(rastreador),
            norm(curso), norm(data), norm(indicacao),
            norm(tags), norm(usuario)
        ))

        conn.commit()
        cursor.close()
        conn.close()

        st.success("✔ Registro salvo com sucesso!")
        st.cache_data.clear()
        st.rerun()

    except Exception as e:
        st.error(f"❌ Erro ao salvar: {e}")
