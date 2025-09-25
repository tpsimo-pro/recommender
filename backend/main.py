from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# A importação deve ser local, pois os arquivos estão na mesma pasta
from recommendation import recommender_engine

app = FastAPI(
    title="API de Sistema de Recomendação",
    description="Uma API para gerar recomendações de filmes com base na filtragem colaborativa.",
    version="1.0.0",
)

# Configuração do CORS para permitir que o frontend se comunique com a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restrinja para o domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelos Pydantic para validação de dados
class RecommendationRequest(BaseModel):
    user_id: int
    n_recommendations: int = 5


class Movie(BaseModel):
    movieId: int
    title: str


@app.post("/recomendar", response_model=List[Movie])
def get_recommendations_endpoint(request: RecommendationRequest):
    """
    Endpoint que recebe um ID de usuário e retorna uma lista de filmes recomendados.
    """
    try:
        recommendations = recommender_engine.get_recommendations(
            user_id=request.user_id, n_recommendations=request.n_recommendations
        )
        if not recommendations:
            raise HTTPException(
                status_code=404,
                detail=f"Não foi possível gerar recomendações para o usuário com ID {request.user_id}. "
                "O usuário pode não existir ou não ter avaliações suficientes.",
            )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def read_root():
    return {"status": "API do sistema de recomendação está funcionando."}
