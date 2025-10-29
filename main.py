import pandas as pd
from fastapi import FastAPI
from typing import Optional
from fastapi.exceptions import HTTPException

app = FastAPI(
    title="API de Livros",
    description="API para consulta de dados de livros",
    version="1.0.0"
)

#Carregamento dos dados do CSV
CSV_FILE_PATH = 'data/books.csv'

try:
    df_books = pd.read_csv(CSV_FILE_PATH).reset_index().rename(columns={'index': 'id'})
except FileNotFoundError:
    print(f"Erro: O arquivo '{CSV_FILE_PATH}' não foi encontrado. Execute o scraper primeiro.")
    df_books = pd.DataFrame()

# Endpoints

@app.get("/")
def read_root():
    """Endpoint raiz que exibe uma mensagem de boas-vindas."""
    return {"message": "Bem-vindo à API de Livros! Acesse /docs para ver a documentação interativa."}


@app.get("/api/v1/health")
def health_check():
    """Verifica o status da API."""
    return {"status": "ok", "message": "API está funcionando normalmente."}

@app.get("/api/v1/books")
def get_all_books():
    """Retorna uma lista de todos os livros disponíveis na base de dados."""
    if df_books.empty:
        return {"message": "Nenhum dado de livro encontrado."}
    return df_books.to_dict('records')

@app.get("/api/v1/categories")
def get_categories():
    """Retorna a lista de todas as categorias de livros únicas."""
    if df_books.empty:
        return {"message": "Nenhum dado de livro encontrado."}
    
    categories = df_books['category'].unique().tolist()
    return {"categories": categories}

@app.get("/api/v1/books/search")
def search_books(title: Optional[str] = None, category: Optional[str] = None):
    """
    Busca livros por título e/ou categoria.
    Ambos os parâmetros são opcionais.
    """
    results = df_books.copy()

    if not title and not category:
        raise HTTPException(status_code=400, detail="Forneça pelo menos um critério de busca: 'title' ou 'category'.")

    if title:
        results = results[results['title'].str.contains(title, case=False, na=False)]
    
    if category:
        results = results[results['category'].str.lower() == category.lower()]

    if results.empty:
        return {"message": "Nenhum livro encontrado com os critérios fornecidos."}

    return results.to_dict('records')

@app.get("/api/v1/books/{book_id}")
def get_book_by_id(book_id: int):
    """Retorna os detalhes de um livro específico pelo seu ID."""
    if book_id not in df_books['id'].values:
        raise HTTPException(status_code=404, detail="Livro com o ID fornecido não encontrado.")
    
    book = df_books[df_books['id'] == book_id].to_dict('records')
    return book[0]