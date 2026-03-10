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
        port=st.secrets["mysql"]["port"],

        connection_timeout=5, 
        autocommit=True
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
# TELA LOGIN
# =========================================================

def tela_login():
    IMAGEM_LADO = os.path.join(PASTA_BASE, "Group 22.png")

    st.markdown("""
    <style>
    /* Mantém layout no topo sem quebrar */
    .block-container {
        padding-top: 1rem;
    }

    /* Wrapper do login */
    .login-left {
        padding-top: 24px;
        padding-left: 20px;
        padding-right: 20px;
    }

    /* Ajuste fino do título para não cortar emoji */
    .login-left h1 {
        line-height: 1.3;
        margin-top: 0;
        padding-top: 0;
    }

    /* Inputs */
    div[data-baseweb="input"] {
        max-width: 420px;
    }

    input {
        height: 46px !important;
        font-size: 15px !important;
        background: #1f242d !important;
        border-radius: 10px !important;
    }

    /* Botão azul */
    button[kind="primary"] {
        background: #1f6feb !important;
        width: 100% !important;
        max-width: 420px !important;
        height: 46px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }

    /* Coluna direita - imagem compacta e alinhada */
    .img-right {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
    }

    .img-right img {
        max-height: 70vh;
        width: 100%;
        object-fit: contain;
        border-radius: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([45, 55])

    # ===== COLUNA ESQUERDA =====
    with col_left:
        st.markdown('<div class="login-left">', unsafe_allow_html=True)

        st.title("🔐 Login")
        st.caption("Acesse com seu usuário e senha")

        usuario = st.text_input("👤 Usuário")
        senha = st.text_input("🔑 Senha", type="password")

        if st.button("🚪 Entrar", type="primary"):
            if autenticar(usuario, senha):
                st.session_state.logado = True
                st.session_state.usuario = usuario
                st.rerun()
            else:
                st.error("❌ Usuário ou senha inválidos")

        st.markdown('</div>', unsafe_allow_html=True)

    # ===== COLUNA DIREITA =====
    with col_right:
        if os.path.exists(IMAGEM_LADO):
            st.markdown('<div class="img-right">', unsafe_allow_html=True)
            st.image(IMAGEM_LADO, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# BLOQUEIO SEM LOGIN
# =========================================================
if not st.session_state.logado:
    tela_login()
    st.stop()

# =========================================================
# FUNDO PÓS LOGIN
# =========================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right,#000000, #000000, #051121, #0E2646, #2E5173, #9AB6D1);
    background-attachment: fixed;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# CABEÇALHO
# =========================================================
if os.path.exists(os.path.join(PASTA_BASE, "topo_JWMNovo.png")):
    st.image(
        os.path.join(PASTA_BASE, "topo_JWMNovo.png"),
        use_container_width=True
    )

st.title("Gestão de Parceiros 🚛💼🌎")
st.write("Motoristas Terceiros / Agregado")

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
# FILTROS (INTERDEPENDENTES)
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

# Inicializa estado dos filtros
for col, _ in filtros:
    st.session_state.setdefault(f"f_{col}", [])

def clear_all_filters():
    for col, _ in filtros:
        st.session_state[f"f_{col}"] = []

def aplicar_filtros_progressivos(df):
    temp = df.copy()
    for col, _ in filtros:
        valores = st.session_state.get(f"f_{col}")
        if valores:
            temp = temp[temp[col].isin(valores)]
    return temp

# =========================================================
# SIDEBAR – FILTROS TOTALMENTE INTERDEPENDENTES
# =========================================================
with st.sidebar:
    st.title("🎛️ Filtros")

    colA, colB = st.columns(2)

    for i, (col, label) in enumerate(filtros):

        # 🔹 Aplica todos os outros filtros, MENOS o atual
        df_temp = df_base.copy()
        for other_col, _ in filtros:
            if other_col == col:
                continue
            valores = st.session_state.get(f"f_{other_col}")
            if valores:
                df_temp = df_temp[df_temp[other_col].isin(valores)]

        # 🔹 Opções já filtradas corretamente
        opcoes = sorted([v for v in df_temp[col].unique() if v])

        with (colA if i % 2 == 0 else colB):
            st.multiselect(
                label,
                opcoes,
                key=f"f_{col}"
            )

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
# TABELA (USANDO FILTROS EM CASCATA)
# =========================================================
st.subheader("📋 Dados Filtrados")

df_resultado = aplicar_filtros_progressivos(df_base)

st.dataframe(df_resultado, use_container_width=True)

# =========================================================
# FUNÇÃO LIMPAR FORMULÁRIO
# =========================================================
def limpar_formulario():
    chaves_texto = [
        "placa", "marca", "modelo", "tipo", "ano", "motorista",
        "telefone", "cidade", "estado", "data", "usuario"
    ]

    for k in chaves_texto:
        if k in st.session_state:
            st.session_state[k] = ""

    # Selectbox / valores padrão
    if "curso" in st.session_state:
        st.session_state["curso"] = "SIM"
    if "indicacao" in st.session_state:
        st.session_state["indicacao"] = "SIM"
    if "rastreador" in st.session_state:
        st.session_state["rastreador"] = "SIM"
    if "tags" in st.session_state:
        st.session_state["tags"] = "CONECT CAR"

# =========================================================
# CADASTRO MANUAL
# =========================================================
st.markdown("## 📝 Painel de Cadastro")
st.write("Cadastre sem Pontuações e com letra Maiúscula")

with st.form("cadastro"):
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.text_input("Placa", key="placa")
        st.text_input("Marca", key="marca")
        st.text_input("Modelo", key="modelo")
        st.selectbox("Tipo de Veículo", ["Fiorino", "Van Utilitário", "HR Baú", "HR Aberto", "Veículo 3/4 Aberto", "Veículo 3/4 Baú", "Toco Aberto", "Toco Baú", "VUC Baú", "Truck Aberto", "Truck Baú", "Bi-Truck Aberto", "Bi-Truck Baú", "Carreta Sider", "Carreta Wanderleia", "Carreta Wanderleia Aberta", "Carreta Wanderleia Sider", "Carreta Rodo Trem", "Bitruck Sider", "Carreta Grade Baixa", "Wanderleia Carga Seca", ], key="tipo")

    with c2:
        st.text_input("Ano", key="ano")
        st.text_input("Motorista", key="motorista")
        st.selectbox("Curso MOP", ["SIM","NAO"], key="curso")
        st.selectbox("Indicação", ["SIM","NAO"], key="indicacao")

    with c3:
        st.text_input("Telefone", key="telefone")
        st.text_input("Cidade", key="cidade")
        st.text_input("Estado", key="estado")
        st.selectbox("Rastreador", ["SIM","NAO"], key="rastreador")

    with c4:
        st.text_input("Data do cadastro", key="data")
        st.selectbox(
            "Tags",
            ["CONECT CAR","SEM PARAR","VELOE","MOVE MAIS"],
            key="tags"
        )
        st.text_input("Usuário", key="usuario")

    col1, col2 = st.columns(2)

    salvar = col1.form_submit_button("💾 SALVAR")

    col2.form_submit_button(
        "🧹 LIMPAR CAMPOS",
        on_click=limpar_formulario
    )

if salvar:
    try:
        placa = norm(st.session_state.get("placa"))

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO parceiros_jwm
            (placa, marca, modelo, ano, tipo_veiculo, motorista,
             telefone, cidade, estado, rastreador,
             curso_mop, data_cadastro, indicacao, tags, usuario)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            placa,
            norm(st.session_state.get("marca")),
            norm(st.session_state.get("modelo")),
            norm(st.session_state.get("ano")),
            norm(st.session_state.get("tipo")),
            norm(st.session_state.get("motorista")),
            norm(st.session_state.get("telefone")),
            norm(st.session_state.get("cidade")),
            norm(st.session_state.get("estado")),
            norm(st.session_state.get("rastreador")),
            norm(st.session_state.get("curso")),
            norm(st.session_state.get("data")),
            norm(st.session_state.get("indicacao")),
            norm(st.session_state.get("tags")),
            norm(st.session_state.get("usuario"))
        ))

        conn.commit()
        cursor.close()
        conn.close()

        st.success("✔ Motorista cadastrado com sucesso!")
        st.cache_data.clear()
        st.rerun()

    except mysql.connector.errors.IntegrityError:
        st.error("❌ ESTA PLACA JÁ ESTÁ CADASTRADA!")

    except Exception as e:
        st.error(f"❌ Erro ao salvar: {e}")
