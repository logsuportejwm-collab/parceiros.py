import streamlit as st
import pandas as pd
import unicodedata
import os

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
# ARQUIVOS
# -------------------------------------------- 
PASTA_BASE = r"J:/SETOR LOGÍSTICA/SETOR AVIAÇÃO/SETOR TCL/COLABORADORES/DAVI NUNES/8 - PARCEIROS_JWM/"
arquivo = os.path.join(PASTA_BASE, "PARCEIROS JWM.xlsx")
imagem_instrucoes = os.path.join(PASTA_BASE, "instrucoes.png")
ABA = "PLANILHA COMPLETA "

# --------------------------------------------
# NORMALIZADOR
# --------------------------------------------
def norm(x):
    return unicodedata.normalize("NFKD", str(x).strip()).encode("ascii", "ignore").decode().upper()

# --------------------------------------------
# GARANTIR EXCEL
# --------------------------------------------
def garantir_excel(path):
    if not os.path.exists(path):
        df_vazio = pd.DataFrame(columns=[
            "PLACA","MARCA","MODELO","ANO","TIPO DE VEICULO","MOTORISTA","TELEFONE",
            "CIDADE","ESTADO","RASTREADOR","CURSO MOP","DATA DO CADASTRO","INDICACAO",
            "TAGS", "USUÁRIO"
        ])
        df_vazio.to_excel(path, sheet_name=ABA, index=False)

garantir_excel(arquivo)

# -------------------------------------------- 
# CARREGAR PLANILHA
# -------------------------------------------- 
@st.cache_data(show_spinner=False)
def carregar_df():
    try:
        df = pd.read_excel(arquivo, sheet_name=ABA, dtype=str).fillna("")
    except Exception:
        st.error("❌ Erro ao carregar planilha. Verifique se ela está aberta!")
        return pd.DataFrame()
    df.columns = [norm(c) for c in df.columns]
    return df

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
    ("DATA DO CADASTRO", "Data do cadastro"),
    ("TAGS", "Tags"),
    ("USUARIO", "Usuário")
]

# --------------------------------------------
# Session state (FILTROS)
# --------------------------------------------

for col,_ in filtros:
    st.session_state.setdefault(f"f_{col}", [])

def clear_filter(col):
    st.session_state[f"f_{col}"] = []

def clear_all_filters():
    for col,_ in filtros:
        st.session_state[f"f_{col}"] = []

# --------------------------------------------
# FUNÇÃO DE FILTRAGEM FINAL
# --------------------------------------------
def filtrar(df):
    temp = df.copy()
    for col,_ in filtros:
        vals = st.session_state.get(f"f_{col}", [])
        if vals:  # há seleção para a coluna
            temp = temp[temp[col].isin(vals)]
    return temp

# --------------------------------------------
# *** CORREÇÃO DO CLEAR DO FORMULÁRIO ***
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
    "data": "",
    "tags": "",
    "usuario": ""
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
    st.image(os.path.join(PASTA_BASE, "topo_JWMNovo.jpg"), use_container_width=True)
    st.title("Gestão de Parceiros 🚛💼🌎")
    st.write("Motoristas Terceiros")
with colB:
    st.image(os.path.join(PASTA_BASE, "mapinha.png"), use_container_width=True)

# --------------------------------------------
# SIDEBAR (FILTROS INTELIGENTES AJUSTADOS)
# --------------------------------------------
df_base = carregar_df()

with st.sidebar:
    st.title("Filtros")
    with st.expander("🎛️ Filtros Inteligentes"):
        for i in range(0, len(filtros), 2):
            colA, colB = st.columns(2)

            # --------- FILTRO A ---------
            fcol1, flabel1 = filtros[i]
            with colA:
                df_temp = df_base.copy()
                # aplica todos os filtros exceto o atual
                for col_other,_ in filtros:
                    if col_other == fcol1:
                        continue
                    val_list = st.session_state[f"f_{col_other}"]
                    if val_list:
                        df_temp = df_temp[df_temp[col_other].isin(val_list)]
                ops = sorted([v for v in df_temp[fcol1].unique() if v])
                st.multiselect(
                    flabel1,
                    ops,
                    default=st.session_state.get(f"f_{fcol1}", []),
                    key=f"f_{fcol1}",
                    placeholder="(TODOS)"
                )
                st.button("❌ Limpar", on_click=clear_filter, args=(fcol1,), key=f"clear_{fcol1}")

            # --------- FILTRO B ---------
            if i + 1 < len(filtros):
                fcol2, flabel2 = filtros[i+1]
                with colB:
                    df_temp = df_base.copy()
                    for col_other,_ in filtros:
                        if col_other == fcol2:
                            continue
                        val_list = st.session_state[f"f_{col_other}"]
                        if val_list:
                            df_temp = df_temp[df_temp[col_other].isin(val_list)]
                    ops2 = sorted([v for v in df_temp[fcol2].unique() if v])
                    st.multiselect(
                        flabel2,
                        ops2,
                        default=st.session_state.get(f"f_{fcol2}", []),
                        key=f"f_{fcol2}",
                        placeholder="(TODOS)"
                    )
                    st.button("❌ Limpar", on_click=clear_filter, args=(fcol2,), key=f"clear_{fcol2}")

    # instrção
    with st.expander("📘 IST(Instrução de Trabalho)"):
        if os.path.exists("QR Code.png"):
            st.image("QR Code.png", width=90)

        else:
            st.error("❌ Arquivo 'Manual.png' não encontrado!")
    st.button("🧹 LIMPAR TODOS OS FILTROS", on_click=clear_all_filters)
    st.markdown("### 🔗 Links importantes")
    st.markdown("""
        - 🌐 **Site JWM** → [Acessar](https://jwmlogistica.com.br)
        - 🗺️ **Google Maps** → [Abrir](https://www.google.com/maps)
        - 📊 **Power BI** → [Dashboard](https://app.powerbi.com/links/MSe9_-szX0?ctid=c8335dcc-510d-4853-a36f-b12b7f4be009&pbi_source=linkShare)
        - 📦🚚 **Dimensionamento Veículo** → [App](https://dimensionamento-de-ve-culos---jwm-dvxn4ufxfmnmyanmv3ohte.streamlit.app/)
    """)

# --------------------------------------------
# TABELA
# --------------------------------------------
df_filtrado = filtrar(df_base)
df_filtrado = df_filtrado.drop(columns=["INDICACAO"], errors="ignore")
st.subheader("📋 Dados filtrados")
st.dataframe(df_filtrado, use_container_width=True)

# --------------------------------------------
# FORMULÁRIO
# --------------------------------------------
st.markdown("## 📝 Cadastro de Parceiro / Motorista")
with st.form("cadastro", clear_on_submit=False):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        placa = st.text_input("Placa", key="w_placa")
        marca = st.text_input("Marca", key="w_marca")
        modelo = st.text_input("Modelo", key="w_modelo")
        tipo = st.text_input("Tipo de Veículo / Carroceria", key="w_tipo")
    with col2:
        ano = st.text_input("Ano", key="w_ano")
        motorista = st.text_input("Motorista", key="w_motorista")
        curso = st.selectbox("Curso", ["SIM","NAO"], key="w_curso")
        indicacao = st.selectbox("Indicação", ["SIM","NAO"], key="w_indicacao")
    with col3:
        telefone = st.text_input("Telefone", key="w_telefone")
        cidade = st.text_input("Cidade", key="w_cidade")
        estado = st.text_input("Estado", key="w_estado")
        rastreador = st.selectbox("Rastreador", ["SIM","NAO"], key="w_rastreador")
    with col4:
        data = st.text_input("Data do cadastro", key="w_data")
        usuario = st.text_input("Usuário", key="w_usuario")
        tags = st.selectbox("Tags",["CONECT CAR", "SEM PARAR", "VELOE", "MOVE MAIS"], key="w_tags")

    colSave, colClear = st.columns(2)
    send = colSave.form_submit_button("💾 SALVAR")
    clear = colClear.form_submit_button("🧹 LIMPAR CAMPO")


if clear:
    st.session_state["do_clear"] = True
    st.rerun()  

# salvar
if send:
    try:
        nova_linha = pd.DataFrame([{
            "PLACA": norm(st.session_state["w_placa"]),
            "MARCA": norm(st.session_state["w_marca"]),
            "MODELO": norm(st.session_state["w_modelo"]),
            "ANO": norm(st.session_state["w_ano"]),
            "TIPO DE VEICULO": norm(st.session_state["w_tipo"]),
            "MOTORISTA": norm(st.session_state["w_motorista"]),
            "TELEFONE": norm(st.session_state["w_telefone"]),
            "CIDADE": norm(st.session_state["w_cidade"]),
            "ESTADO": norm(st.session_state["w_estado"]),
            "RASTREADOR": norm(st.session_state["w_rastreador"]),
            "CURSO MOP": norm(st.session_state["w_curso"]),
            "DATA DO CADASTRO": norm(st.session_state["w_data"]),
            "INDICACAO": norm(st.session_state["w_indicacao"]),
            "TAGS": norm(st.session_state["w_tags"]),
            "USUÁRIO": norm(st.session_state["w_usuario"])
        }])
        df_atual = carregar_df()
        df_novo = pd.concat([df_atual, nova_linha], ignore_index=True)
        df_novo.to_excel(arquivo, sheet_name=ABA, index=False)
        st.success("✔ Registro salvo com sucesso!")
        st.cache_data.clear()
        st.rerun() 
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
