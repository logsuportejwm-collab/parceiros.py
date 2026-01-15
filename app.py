import streamlit as st
import pandas as pd
import unicodedata
import os
from db import get_connection

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

# --------------------------------------------
# NORMALIZADOR
# --------------------------------------------
def norm(x):
    return unicodedata.normalize("NFKD", str(x).strip()) \
        .encode("ascii", "ignore") \
        .decode() \
        .upper()

# --------------------------------------------
# CARREGAR DADOS DO BANCO
# --------------------------------------------
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
        st.error(f"❌ Erro ao carregar dados do banco: {e}")
        return pd.DataFrame()

# --------------------------------------------
# LISTA DE FILTROS
# --------------------------------------------
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

# --------------------------------------------
# SESSION STATE (FILTROS)
# --------------------------------------------
for col,_ in filtros:
    st.session_state.setdefault(f"f_{col}", [])

def clear_filter(col):
    st.session_state[f"f_{col}"] = []

def clear_all_filters():
    for col,_ in filtros:
        st.session_state[f"f_{col}"] = []

# --------------------------------------------
# FUNÇÃO DE FILTRAGEM
# --------------------------------------------
def filtrar(df):
    temp = df.copy()
    for col,_ in filtros:
        vals = st.session_state.get(f"f_{col}", [])
        if vals:
            temp = temp[temp[col].isin(vals)]
    return temp

# --------------------------------------------
# CONTROLE DE LIMPEZA DO FORMULÁRIO
# --------------------------------------------
inputs = {
    "placa": "",
    "marca": "",
    "modelo": "",
    "tipo": "",
    "ano": "",
    "motorista": "",
    "curso": "SIM",
    "indicacao": "SIM",
    "telefone": "",
    "cidade": "",
    "estado": "",
    "rastreador": "SIM",
    "data": ""
}

st.session_state.setdefault("do_clear", False)

if st.session_state["do_clear"]:
    for k, v in inputs.items():
        st.session_state[f"w_{k}"] = v
    st.session_state["do_clear"] = False

for k, v in inputs.items():
    st.session_state.setdefault(f"w_{k}", v)

# --------------------------------------------
# CABEÇALHO
# --------------------------------------------
colA, colB = st.columns([2, 1])
with colA:
    st.title("Gestão de Parceiros 🚛💼🌎")
    st.write("Motoristas Terceiros")
with colB:
    pass

# --------------------------------------------
# SIDEBAR
# --------------------------------------------
df_base = carregar_df()

with st.sidebar:
    st.title("Filtros")
    with st.expander("🎛️ Filtros Inteligentes"):
        for i in range(0, len(filtros), 2):
            colA, colB = st.columns(2)

            fcol1, flabel1 = filtros[i]
            with colA:
                df_temp = df_base.copy()
                for col_other,_ in filtros:
                    if col_other != fcol1 and st.session_state[f"f_{col_other}"]:
                        df_temp = df_temp[df_temp[col_other].isin(st.session_state[f"f_{col_other}"])]
                ops = sorted([v for v in df_temp[fcol1].unique() if v])
                st.multiselect(
                    flabel1,
                    ops,
                    default=st.session_state[f"f_{fcol1}"],
                    key=f"f_{fcol1}"
                )
                st.button("❌ Limpar", on_click=clear_filter, args=(fcol1,), key=f"c_{fcol1}")

            if i + 1 < len(filtros):
                fcol2, flabel2 = filtros[i+1]
                with colB:
                    df_temp = df_base.copy()
                    for col_other,_ in filtros:
                        if col_other != fcol2 and st.session_state[f"f_{col_other}"]:
                            df_temp = df_temp[df_temp[col_other].isin(st.session_state[f"f_{col_other}"])]
                    ops2 = sorted([v for v in df_temp[fcol2].unique() if v])
                    st.multiselect(
                        flabel2,
                        ops2,
                        default=st.session_state[f"f_{fcol2}"],
                        key=f"f_{fcol2}"
                    )
                    st.button("❌ Limpar", on_click=clear_filter, args=(fcol2,), key=f"c_{fcol2}")

    st.button("🧹 LIMPAR TODOS OS FILTROS", on_click=clear_all_filters)

# --------------------------------------------
# TABELA
# --------------------------------------------
df_filtrado = filtrar(df_base).drop(columns=["INDICACAO"], errors="ignore")
st.subheader("📋 Dados filtrados")
st.dataframe(df_filtrado, use_container_width=True)

# --------------------------------------------
# FORMULÁRIO
# --------------------------------------------
st.markdown("## 📝 Cadastro de Parceiro / Motorista")
with st.form("cadastro", clear_on_submit=False):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.text_input("Placa", key="w_placa")
        st.text_input("Marca", key="w_marca")
        st.text_input("Modelo", key="w_modelo")
        st.text_input("Tipo de Veículo / Carroceria", key="w_tipo")

    with col2:
        st.text_input("Ano", key="w_ano")
        st.text_input("Motorista", key="w_motorista")
        st.selectbox("Curso", ["SIM","NAO"], key="w_curso")
        st.selectbox("Indicação", ["SIM","NAO"], key="w_indicacao")

    with col3:
        st.text_input("Telefone", key="w_telefone")
        st.text_input("Cidade", key="w_cidade")
        st.text_input("Estado", key="w_estado")
        st.selectbox("Rastreador", ["SIM","NAO"], key="w_rastreador")

    with col4:
        st.text_input("Data do cadastro", key="w_data")

    colSave, colClear = st.columns(2)
    send = colSave.form_submit_button("💾 SALVAR")
    clear = colClear.form_submit_button("🧹 LIMPAR CAMPOS")

# --------------------------------------------
# LIMPAR FORM
# --------------------------------------------
if clear:
    st.session_state["do_clear"] = True
    st.rerun()

# --------------------------------------------
# SALVAR NO BANCO
# --------------------------------------------
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
            norm(st.session_state["w_placa"]),
            norm(st.session_state["w_marca"]),
            norm(st.session_state["w_modelo"]),
            norm(st.session_state["w_ano"]),
            norm(st.session_state["w_tipo"]),
            norm(st.session_state["w_motorista"]),
            norm(st.session_state["w_telefone"]),
            norm(st.session_state["w_cidade"]),
            norm(st.session_state["w_estado"]),
            norm(st.session_state["w_rastreador"]),
            norm(st.session_state["w_curso"]),
            norm(st.session_state["w_data"]),
            norm(st.session_state["w_indicacao"]),
        )

        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()

        st.success("✔ Registro salvo no banco com sucesso!")
        st.cache_data.clear()
        st.rerun()

    except Exception as e:
        st.error(f"❌ Erro ao salvar no banco: {e}")
