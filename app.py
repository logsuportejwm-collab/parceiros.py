import streamlit as st
import pandas as pd
import unicodedata
import mysql.connector
import os

# =========================================================
# CRIANDO TABDELA DE USUÁRIOS 
# =========================================================
CREATE TABLE usuarios_app (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    ativo TINYINT DEFAULT 1
);

INSERT INTO usuarios_app (usuario, senha)
VALUES ('admin', SHA2('123', 256));

# =========================================================
# FUNÇÕES DE LOGIN
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
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    return resultado is not None

# =========================================================
# CONTROLE DE LOGIN
# =========================================================
if "logado" not in st.session_state:
    st.session_state.logado = False

def tela_login():
    st.title("🔐 Login - Parceiros JWM")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if autenticar(usuario, senha):
            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.rerun()
        else:
            st.error("❌ Usuário ou senha inválidos")

if not st.session_state.logado:
    tela_login()
    st.stop()
