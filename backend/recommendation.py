import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

class CollaborativeFilteringRecommender:
    """
    Sistema de Recomendação com Filtragem Colaborativa baseada em usuário.
    Utiliza a similaridade de cosseno para encontrar usuários com gostos parecidos
    e gerar recomendações.
    """
    def __init__(self, ratings_path: str, movies_path: str):
        """
        Inicializa o recomendador carregando e pré-processando os dados.
        """
        self.ratings = pd.read_csv(ratings_path)
        self.movies = pd.read_csv(movies_path)
        self.user_item_matrix = None
        self.user_similarity = None
        self._preprocess_data()

    def _preprocess_data(self):
        """
        Cria a matriz de usuário-item, essencial para a filtragem colaborativa.
        Valores ausentes (NaN) indicam que o usuário não avaliou o item.
        """
        self.user_item_matrix = self.ratings.pivot(
            index='userId',
            columns='movieId',
            values='rating'
        ).fillna(0)

        # Para o cálculo da similaridade, usamos uma matriz esparsa para eficiência
        user_item_sparse = csr_matrix(self.user_item_matrix.values)
        
        # Calcula a similaridade de cosseno entre todos os usuários
        self.user_similarity = pd.DataFrame(
            cosine_similarity(user_item_sparse),
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.index
        )

    def get_recommendations(self, user_id: int, n_recommendations: int = 5) -> list:
        """
        Gera uma lista de filmes recomendados para um determinado usuário.
        """
        if user_id not in self.user_item_matrix.index:
            return []

        # 1. Encontra os usuários mais similares (excluindo o próprio usuário)
        similar_users = self.user_similarity[user_id].sort_values(ascending=False).iloc[1:]

        if similar_users.empty:
            return []

        # 2. Obtém os filmes que o usuário-alvo já avaliou
        rated_movies_by_target_user = self.user_item_matrix.loc[user_id]
        rated_movies_by_target_user = rated_movies_by_target_user[rated_movies_by_target_user > 0].index

        # 3. Itera sobre os usuários similares para encontrar novos filmes
        recommendations = {}
        for other_user_id, similarity_score in similar_users.items():
            if similarity_score <= 0:  # Ignora usuários não similares
                continue

            # Obtém os filmes avaliados pelo usuário similar
            rated_movies_by_similar_user = self.user_item_matrix.loc[other_user_id]
            rated_movies_by_similar_user = rated_movies_by_similar_user[rated_movies_by_similar_user > 0]
            
            for movie_id, rating in rated_movies_by_similar_user.items():
                # Se o filme não foi visto pelo usuário-alvo, considera para recomendação
                if movie_id not in rated_movies_by_target_user:
                    if movie_id not in recommendations:
                        recommendations[movie_id] = {'total_score': 0, 'similarity_sum': 0}
                    
                    # Calcula o score ponderado pela similaridade
                    recommendations[movie_id]['total_score'] += rating * similarity_score
                    recommendations[movie_id]['similarity_sum'] += similarity_score
        
        if not recommendations:
            return []

        # 4. Calcula a nota prevista para cada filme
        predicted_ratings = {
            movie_id: data['total_score'] / data['similarity_sum']
            for movie_id, data in recommendations.items() if data['similarity_sum'] > 0
        }
        
        # 5. Ordena as recomendações pela nota prevista
        sorted_recommendations = sorted(predicted_ratings.items(), key=lambda item: item[1], reverse=True)
        
        # 6. Formata o resultado final com o nome do filme
        recommended_movie_ids = [movie_id for movie_id, score in sorted_recommendations[:n_recommendations]]
        
        recommended_movies = self.movies[self.movies['movieId'].isin(recommended_movie_ids)][['movieId', 'title']]
        
        # Garante a ordem correta
        result_df = pd.DataFrame({'movieId': recommended_movie_ids}).merge(recommended_movies, on='movieId', how='left')
        
        return result_df.to_dict('records')

# Instancia o recomendador para ser usado na API
recommender_engine = CollaborativeFilteringRecommender('ratings.csv', 'movies.csv')