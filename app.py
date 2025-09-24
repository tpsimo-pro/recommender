# app.py
import streamlit as st
import requests
import pandas as pd

# URL da nossa API FastAPI
FASTAPI_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Painel de Dados", layout="wide")

st.title("Painel de Dados com Streamlit e FastAPI")

st.write("Este é um exemplo de frontend em Streamlit que consome dados de um backend FastAPI.")

# --- Interação com o Backend ---

# Busca a mensagem de boas-vindas da API
try:
    response_root = requests.get(f"{FASTAPI_URL}/")
    if response_root.status_code == 200:
        st.success(f"Conexão com a API bem-sucedida: **{response_root.json()['message']}**")
    else:
        st.error(f"Não foi possível conectar à API. Status: {response_root.status_code}")
except requests.exceptions.ConnectionError:
    st.error("Erro de conexão. Verifique se o servidor FastAPI está rodando.")


# Botão para buscar e exibir os dados
st.header("Buscar Dados da API")
if st.button("Buscar Dados Aleatórios"):
    try:
        response_data = requests.get(f"{FASTAPI_URL}/data")
        if response_data.status_code == 200:
            data = response_data.json()
            
            st.subheader("Dados Recebidos")
            st.write(data)
            
            st.subheader("Dados em formato de Tabela (Pandas DataFrame)")
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            st.subheader("Gráfico Simples")
            st.bar_chart(df.set_index('name')['value'])
            
        else:
            st.error(f"Erro ao buscar dados. Status: {response_data.status_code}")
            
    except requests.exceptions.ConnectionError:
        st.error("Erro de conexão. Verifique se o servidor FastAPI está rodando.")

# Para rodar a aplicação Streamlit:
# streamlit run app.py