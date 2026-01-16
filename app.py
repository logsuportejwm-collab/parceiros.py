import streamlit as st
import pandas as pd
import unicodedata
import mysql.connector
import os

# =========================================================
# CONFIGURAÇÃO BASE
# =========================================================
PASTA_BASE = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="Parceiros JWM",
    layout="wide"
)

# =========================================================
# CONEXÃO MYSQL
# =========================================================
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        port=st.secrets["mysql"]["port"]
    )

# =========================================================
# AUTENTICAÇÃO
# =========================================================
def autenticar(usuario, senha):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT usuario
        FROM usuarios_app
        WHERE usuario = %s
          AND senha = SHA2(%s, 256)
          AND ativo = 1
    """, (usuario, senha))
    ok = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return ok

# =========================================================
# CONTROLE LOGIN
# =========================================================
if "logado" not in st.session_state:
    st.session_state.logado = False

# =========================================================
# TELA LOGIN (FORÇADA À ESQUERDA)
# =========================================================


def tela_login():
    # CSS do login (compacto e alinhado à esquerda)
    st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(65% 120% at 0% 50%, #0e1624 0%, #0b1220 40%, #0a1120 100%);
    }
    .login-container {
        position: fixed;
        top: 50%;
        left: 8vw;                 /* ajusta a posição mais à esquerda */
        transform: translateY(-50%);
        width: 320px;              /* caixa menor */
        z-index: 10;
    }
    .login-box {
        background: rgba(14, 22, 36, 0.92);
        padding: 22px;             /* padding menor */
        border-radius: 14px;
        box-shadow: 0 10px 28px rgba(0,0,0,0.35);
        border: 1px solid rgba(255,255,255,0.06);
    }
    .login-title {
        font-size: 22px;
        color: #e9edf5;
        font-weight: 600;
        margin: 0 0 12px 0;
        letter-spacing: 0.2px;
    }
    label, .stTextInput label, .stPassword label {
        font-size: 12px !important;
        color: #cbd6e2 !important;
        margin-bottom: 4px !important;
    }
    div[data-testid="stTextInput"] input {
        background-color: #0b1320 !important;
        height: 34px !important;
        font-size: 13px !important;
        color: #e5eefc !important;
        border: 1.5px solid #263448 !important;
        border-radius: 10px !important;
        padding: 6px 10px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #2f89ff !important;
        box-shadow: 0 0 0 2px rgba(47,137,255,0.15) !important;
    }
    .login-box .block-container > div,
    .login-box div[data-testid="stTextInput"] {
        margin-bottom: 10px;
    }
    .stButton button {
        width: 120px;              /* botão menor */
        height: 34px;
        font-size: 13px;
        font-weight: 600;
        color: #ffffff;
        background: linear-gradient(90deg, #0a84ff, #35b8ff);
        border: none;
        border-radius: 10px;
        transition: transform .15s ease, filter .15s ease;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        filter: brightness(1.05);
    }
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}

    /* Responsivo: em telas estreitas, centraliza */
    @media (max-width: 768px) {
        .login-container {
            left: 50%;
            transform: translate(-50%, -50%);
            width: 92vw;
            max-width: 360px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-container"><div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔐 Login - Parceiros JWM</div>', unsafe_allow_html=True)

    with st.form("form_login", clear_on_submit=False):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        col_btn, _ = st.columns([1, 3])
        entrar = col_btn.form_submit_button("Entrar")

    if entrar:
        if autenticar(usuario, senha):
            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.rerun()
        else:
            st.error("❌ Usuário ou senha inválidos")

    st.markdown('</div></div>', unsafe_allow_html=True)


# =========================================================
# BLOQUEIA APP SEM LOGIN
# =========================================================
if not st.session_state.logado:
    tela_login()
    st.stop()

# =========================================================
# FUNDO DO APP 
# =========================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right,#000000, #09203f, #517fa4);
    background-attachment: fixed;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# CABEÇALHO
# =========================================================
colA, colB = st.columns([2, 1])

with colA:
    if os.path.exists(os.path.join(PASTA_BASE, "topo_JWMNovo.jpg")):
        st.image(os.path.join(PASTA_BASE, "topo_JWMNovo.jpg"), use_container_width=True)
    st.title("Gestão de Parceiros 🚛💼🌎")
    st.write("Motoristas Terceiros")

with colB:
    if os.path.exists(os.path.join(PASTA_BASE, "mapinha.png")):
        st.image(os.path.join(PASTA_BASE, "mapinha.png"), use_container_width=True)

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
        if os.path.exists(os.path.join(PASTA_BASE, "QR Code.png")):
            st.image(os.path.join(PASTA_BASE, "QR Code.png"), width=120)
        else:
            st.info("QR Code não encontrado")

    st.markdown("### 🔗 Links importantes")
    st.markdown("""
    - 🌐 **Site JWM** → [Acessar](https://jwmlogistica.com.br)
    - 🗺️ **Google Maps** → [Abrir](https://www.google.com/maps)
    - 📊 **Power BI** → [Dashboard](https://app.powerbi.com/links/MSe9_-szX0?ctid=c8335dcc-510d-4853-a36f-b12b7f4be009&pbi_source=linkShare)
    - 📦🚚 **Dimensionamento Veículo** → [App](https://dimensionamento-de-ve-culos---jwm-dvxn4ufxfmnmyanmv3ohte.streamlit.app/)
    """)

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
