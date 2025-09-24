# main.py
from fastapi import FastAPI
from pydantic import BaseModel
import random

# Cria uma instância da aplicação FastAPI
app = FastAPI(
    title="API de Exemplo",
    description="Uma API simples para ser consumida pelo Streamlit.",
    version="1.0.0"
)

# Modelo de dados para os itens (usando Pydantic)
class Item(BaseModel):
    id: int
    name: str
    value: float

# Rota principal (endpoint "/")
@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do nosso projeto!"}

# Rota para obter dados de exemplo
@app.get("/data", response_model=list[Item])
def get_data():
    """Retorna uma lista de itens com dados gerados aleatoriamente."""
    items = [
        Item(id=i, name=f"Item {i}", value=random.uniform(10, 100))
        for i in range(5)
    ]
    return items

# Para rodar o servidor localmente:
# uvicorn main:app --reload