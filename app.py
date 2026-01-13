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
@@ -46,57 +45,45 @@
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
                indicacao AS INDICACAO,
                tags AS TAGS,
                usuario AS USUARIO
            FROM parceiros_jwm
        """
        df = pd.read_sql(query, conn)
        conn.close()
        df.columns = [norm(c) for c in df.columns]
        return df.fillna("")
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()
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

# ---------------------------------------------------------
# FILTROS
# ---------------------------------------------------------
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
    ("PLACA","Placa"),("INDICACAO","Indicação"),("RASTREADOR","Rastreador"),
    ("ESTADO","Estado"),("CIDADE","Cidade"),("TIPO DE VEICULO","Tipo Veículo"),
    ("ANO","Ano"),("MOTORISTA","Motorista"),("TAGS","Tags"),("USUARIO","Usuário")
]

for col, _ in filtros:
for col,_ in filtros:
    st.session_state.setdefault(f"f_{col}", [])

def filtrar(df):
    temp = df.copy()
    for col, _ in filtros:
    for col,_ in filtros:
        if st.session_state[f"f_{col}"]:
            temp = temp[temp[col].isin(st.session_state[f"f_{col}"])]
    return temp
@@ -114,90 +101,96 @@

with st.sidebar:
    st.title("Filtros")

    for col, label in filtros:
    for col,label in filtros:
        ops = sorted([v for v in df_base[col].unique() if v])
        st.multiselect(label, ops, key=f"f_{col}")

    st.markdown("---")

    # -----------------------------------------------------
    # DOWNLOAD MODELO DE IMPORTAÇÃO (XLSX)
    # -----------------------------------------------------
    # -----------------------------------------
    # MODELO DE IMPORTAÇÃO
    # -----------------------------------------
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
        "📥 Baixar modelo (.xlsx)",
        buffer,
        file_name="modelo_importacao_parceiros.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # -----------------------------------------------------
    # IMPORTAÇÃO DE PLANILHA
    # -----------------------------------------------------
    st.markdown("---")

    # -----------------------------------------
    # IMPORTAÇÃO COM CONFIRMAÇÃO
    # -----------------------------------------
    st.markdown("### 📤 Importar Planilha")

    arquivo = st.file_uploader(
    uploaded = st.file_uploader(
        "Selecione o arquivo (.xls ou .xlsx)",
        type=["xls", "xlsx"]
        type=["xls","xlsx"]
    )

    if arquivo:
        try:
            df_import = pd.read_excel(arquivo).fillna("")
            df_import.columns = [norm(c) for c in df_import.columns]

            conn = get_connection()
            cursor = conn.cursor()

            sql = """
                INSERT INTO parceiros_jwm
                (placa, marca, modelo, ano, tipo_veiculo, motorista,
                 telefone, cidade, estado, rastreador,
                 curso_mop, data_cadastro, indicacao, tags, usuario)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            for _, row in df_import.iterrows():
                cursor.execute(sql, (
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
            cursor.close()
            conn.close()

            st.success("✔ Importação realizada com sucesso!")
            st.cache_data.clear()
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erro na importação: {e}")
    if uploaded:
        df_import = pd.read_excel(uploaded).fillna("")
        df_import.columns = [norm(c) for c in df_import.columns]

        st.session_state["df_import"] = df_import

        st.info(f"📄 {len(df_import)} registros carregados. Confirme para importar.")
        st.dataframe(df_import, use_container_width=True)

        if st.button("✅ CONFIRMAR IMPORTAÇÃO"):
            try:
                conn = get_connection()
                cursor = conn.cursor()

                sql = """
                    INSERT INTO parceiros_jwm
                    (placa, marca, modelo, ano, tipo_veiculo, motorista,
                     telefone, cidade, estado, rastreador,
                     curso_mop, data_cadastro, indicacao, tags, usuario)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """

                for _, row in df_import.iterrows():
                    cursor.execute(sql, (
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
                cursor.close()
                conn.close()

                st.success("✔ Importação concluída com sucesso!")
                st.session_state.pop("df_import", None)
                st.cache_data.clear()
                st.rerun()

            except Exception as e:
                st.error(f"❌ Erro na importação: {e}")

# ---------------------------------------------------------
# TABELA
@@ -209,9 +202,8 @@
# FORMULÁRIO MANUAL
# ---------------------------------------------------------
st.markdown("## 📝 Cadastro Manual")

with st.form("cadastro"):
    col1, col2, col3, col4 = st.columns(4)
    col1,col2,col3,col4 = st.columns(4)

    with col1:
        placa = st.text_input("Placa")
@@ -222,30 +214,26 @@
    with col2:
        ano = st.text_input("Ano")
        motorista = st.text_input("Motorista")
        curso = st.selectbox("Curso MOP", ["SIM", "NAO"])
        indicacao = st.selectbox("Indicação", ["SIM", "NAO"])
        curso = st.selectbox("Curso MOP", ["SIM","NAO"])
        indicacao = st.selectbox("Indicação", ["SIM","NAO"])

    with col3:
        telefone = st.text_input("Telefone")
        cidade = st.text_input("Cidade")
        estado = st.text_input("Estado")
        rastreador = st.selectbox("Rastreador", ["SIM", "NAO"])
        rastreador = st.selectbox("Rastreador", ["SIM","NAO"])

    with col4:
        data = st.text_input("Data do cadastro")
        tags = st.selectbox("Tags", ["CONECT CAR", "SEM PARAR", "VELOE", "MOVE MAIS"])
        tags = st.selectbox("Tags", ["CONECT CAR","SEM PARAR","VELOE","MOVE MAIS"])
        usuario = st.text_input("Usuário")

    send = st.form_submit_button("💾 SALVAR")

# ---------------------------------------------------------
# SALVAR MANUAL
# ---------------------------------------------------------
if send:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO parceiros_jwm
            (placa, marca, modelo, ano, tipo_veiculo, motorista,
@@ -259,14 +247,11 @@
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
