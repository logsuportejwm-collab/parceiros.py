import streamlit as st
import pandas as pd
import unicodedata
import mysql.connector
import io

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
    if x is None:
        return ""
    return unicodedata.normalize("NFKD", str(x).strip()) \
        .encode("ascii", "ignore") \
        .decode() \
@@ -78,22 +80,22 @@
filtros = [
    ("PLACA", "Placa"),
    ("INDICACAO", "Indicação"),
    ("RASTREADOR","Rastreador"),
    ("ESTADO","Estado"),
    ("CIDADE","Cidade"),
    ("TIPO DE VEICULO","Tipo Veículo"),
    ("ANO","Ano"),
    ("MOTORISTA","Motorista"),
    ("TAGS","Tags"),
    ("USUARIO","Usuário")
    ("RASTREADOR", "Rastreador"),
    ("ESTADO", "Estado"),
    ("CIDADE", "Cidade"),
    ("TIPO DE VEICULO", "Tipo Veículo"),
    ("ANO", "Ano"),
    ("MOTORISTA", "Motorista"),
    ("TAGS", "Tags"),
    ("USUARIO", "Usuário")
]

for col,_ in filtros:
for col, _ in filtros:
    st.session_state.setdefault(f"f_{col}", [])

def filtrar(df):
    temp = df.copy()
    for col,_ in filtros:
    for col, _ in filtros:
        if st.session_state[f"f_{col}"]:
            temp = temp[temp[col].isin(st.session_state[f"f_{col}"])]
    return temp
@@ -111,27 +113,32 @@

with st.sidebar:
    st.title("Filtros")

    for col, label in filtros:
        ops = sorted([v for v in df_base[col].unique() if v])
        st.multiselect(label, ops, key=f"f_{col}")

    st.markdown("---")

    # -----------------------------------------------------
    # DOWNLOAD MODELO DE IMPORTAÇÃO
    # DOWNLOAD MODELO DE IMPORTAÇÃO (XLSX)
    # -----------------------------------------------------
    st.markdown("### ⬇️ Modelo de Importação")

    modelo = pd.DataFrame(columns=[
        "PLACA","MARCA","MODELO","ANO","TIPO DE VEICULO","MOTORISTA",
        "TELEFONE","CIDADE","ESTADO","RASTREADOR","CURSO MOP",
        "DATA DO CADASTRO","INDICACAO","TAGS","USUARIO"
    ])

    buffer = io.BytesIO()
    modelo.to_excel(buffer, index=False)
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        modelo.to_excel(writer, index=False, sheet_name="MODELO")

    buffer.seek(0)

    st.download_button(
        "⬇️ Baixar modelo de importação",
        "📥 Baixar modelo (.xlsx)",
        buffer,
        file_name="modelo_importacao_parceiros.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
@@ -140,8 +147,12 @@
    # -----------------------------------------------------
    # IMPORTAÇÃO DE PLANILHA
    # -----------------------------------------------------
    st.markdown("### 📥 Importar Planilha")
    arquivo = st.file_uploader("Selecione o arquivo (.xls ou .xlsx)", type=["xls","xlsx"])
    st.markdown("### 📤 Importar Planilha")

    arquivo = st.file_uploader(
        "Selecione o arquivo (.xls ou .xlsx)",
        type=["xls", "xlsx"]
    )

    if arquivo:
        try:
@@ -161,21 +172,21 @@

            for _, row in df_import.iterrows():
                cursor.execute(sql, (
                    norm(row["PLACA"]),
                    norm(row["MARCA"]),
                    norm(row["MODELO"]),
                    norm(row["ANO"]),
                    norm(row["TIPO DE VEICULO"]),
                    norm(row["MOTORISTA"]),
                    norm(row["TELEFONE"]),
                    norm(row["CIDADE"]),
                    norm(row["ESTADO"]),
                    norm(row["RASTREADOR"]),
                    norm(row["CURSO MOP"]),
                    norm(row["DATA DO CADASTRO"]),
                    norm(row["INDICACAO"]),
                    norm(row["TAGS"]),
                    norm(row["USUARIO"]),
                    norm(row.get("PLACA")),
                    norm(row.get("MARCA")),
                    norm(row.get("MODELO")),
                    norm(row.get("ANO")),
                    norm(row.get("TIPO DE VEICULO")),
                    norm(row.get("MOTORISTA")),
                    norm(row.get("TELEFONE")),
                    norm(row.get("CIDADE")),
                    norm(row.get("ESTADO")),
                    norm(row.get("RASTREADOR")),
                    norm(row.get("CURSO MOP")),
                    norm(row.get("DATA DO CADASTRO")),
                    norm(row.get("INDICACAO")),
                    norm(row.get("TAGS")),
                    norm(row.get("USUARIO")),
                ))

            conn.commit()
@@ -196,9 +207,10 @@
st.dataframe(filtrar(df_base), use_container_width=True)

# ---------------------------------------------------------
# FORMULÁRIO
# FORMULÁRIO MANUAL
# ---------------------------------------------------------
st.markdown("## 📝 Cadastro Manual")

with st.form("cadastro"):
    col1, col2, col3, col4 = st.columns(4)

@@ -211,18 +223,18 @@
    with col2:
        ano = st.text_input("Ano")
        motorista = st.text_input("Motorista")
        curso = st.selectbox("Curso MOP", ["SIM","NAO"])
        indicacao = st.selectbox("Indicação", ["SIM","NAO"])
        curso = st.selectbox("Curso MOP", ["SIM", "NAO"])
        indicacao = st.selectbox("Indicação", ["SIM", "NAO"])

    with col3:
        telefone = st.text_input("Telefone")
        cidade = st.text_input("Cidade")
        estado = st.text_input("Estado")
        rastreador = st.selectbox("Rastreador", ["SIM","NAO"])
        rastreador = st.selectbox("Rastreador", ["SIM", "NAO"])

    with col4:
        data = st.text_input("Data do cadastro")
        tags = st.selectbox("Tags", ["CONECT CAR","SEM PARAR","VELOE","MOVE MAIS"])
        tags = st.selectbox("Tags", ["CONECT CAR", "SEM PARAR", "VELOE", "MOVE MAIS"])
        usuario = st.text_input("Usuário")

    send = st.form_submit_button("💾 SALVAR")
