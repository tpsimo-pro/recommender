import streamlit as st
import requests
import pandas as pd

# --- Configuração da Página ---
st.set_page_config(
    page_title="Sistema de Recomendação de Filmes", page_icon="🎬", layout="centered"
)

# --- Título e Descrição ---
st.title("🎬 Sistema de Recomendação de Filmes")
st.markdown("""
Bem-vindo ao nosso sistema de recomendação! Este projeto utiliza **filtragem colaborativa** para sugerir filmes com base nas avaliações de usuários com gostos similares.
""")

# --- URL do Backend ---
# Certifique-se de que o backend FastAPI está rodando.
BACKEND_URL = "http://127.0.0.1:8000/recomendar"

# --- Interface do Usuário ---

st.header("✨ Obtenha suas Recomendações")

# Carregando os IDs de usuário disponíveis do mesmo arquivo CSV que o backend usa
try:
    # O ideal é que o frontend seja independente, mas para este exemplo,
    # vamos ler os IDs de usuário do CSV para popular o seletor.
    # Em um cenário real, poderia haver um endpoint no backend para buscar usuários.
    df_ratings = pd.read_csv("../backend/ratings.csv")
    available_users = sorted(df_ratings["userId"].unique())
except FileNotFoundError:
    st.error(
        "Arquivo 'ratings.csv' não encontrado. Certifique-se de que a estrutura de pastas está correta."
    )
    available_users = [1, 2, 3, 4, 5]  # Fallback

# Entrada de dados simulados (seleção de usuário) [cite: 32]
selected_user_id = st.selectbox(
    "Selecione o seu ID de Usuário:", options=available_users
)

# Entrada para o número de recomendações
num_recommendations = st.slider(
    "Quantos filmes você gostaria de receber como recomendação?",
    min_value=3,
    max_value=10,
    value=5,
)

# Botão para gerar as recomendações [cite: 33]
if st.button("Gerar Recomendações", type="primary"):
    if selected_user_id:
        with st.spinner("Buscando recomendações para você... Por favor, aguarde."):
            try:
                # Monta o corpo da requisição
                payload = {
                    "user_id": int(
                        selected_user_id
                    ),  # Adicionamos a conversão int() aqui
                    "n_recommendations": num_recommendations,
                }

                # Faz a requisição POST para a API do backend
                response = requests.post(BACKEND_URL, json=payload)

                # Verifica se a requisição foi bem-sucedida
                if response.status_code == 200:
                    recommendations = response.json()

                    st.success(
                        f"Aqui estão {len(recommendations)} filmes recomendados para você!"
                    )

                    # Exibição clara dos itens recomendados [cite: 34]
                    for movie in recommendations:
                        st.markdown(f"- **{movie['title']}** (ID: {movie['movieId']})")

                elif response.status_code == 404:
                    st.warning(
                        f"Não foi possível gerar recomendações. O usuário {selected_user_id} pode não ter dados suficientes ou não existe."
                    )
                else:
                    st.error(
                        f"Ocorreu um erro no servidor: {response.status_code} - {response.text}"
                    )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Não foi possível conectar ao backend. Verifique se o servidor FastAPI está em execução no endereço correto (http://127.0.0.1:8000)."
                )
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado: {e}")

# --- Rodapé ---
st.markdown("---")
st.write("Desenvolvido como parte do projeto de Sistema de Recomendação.")
