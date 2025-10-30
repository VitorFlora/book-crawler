import pandas as pd
from fastapi import FastAPI, HTTPException
from typing import Optional

# Cria uma instância da aplicação FastAPI
app = FastAPI(
    title="API de Livros",
    description="Uma API para consulta de dados de livros extraídos do site 'books.tscrape.com'",
    version="1.0.0"
)

CSV_FILE_PATH = 'data/books.csv'

try:
    df_books = pd.read_csv(CSV_FILE_PATH)
    df_books['id'] = df_books['id'].astype(int)         # erro de leitura como string
    df_books.set_index('id', inplace=True) 
    
except FileNotFoundError:
    print(f"Erro: O arquivo '{CSV_FILE_PATH}' não foi encontrado. Execute o scraper primeiro.")
    df_books = pd.DataFrame()
except Exception as e:
    print(f"Erro ao carregar e processar o DataFrame: {e}")
    df_books = pd.DataFrame()


# Endpoints
@app.get("/")
def read_root():
    """Endpoint raiz que exibe uma mensagem de boas-vindas."""
    return {"messages": [
        "Bem-vindo à API de Livros! Acesse /docs para ver a documentação interativa (Swagger).",
        "Acesse /api/v1/books para ver a lista de livros.",
        "Acesse /api/v1/categories para ver a lista de categorias.",
        "Use /api/v1/books/search?title=nome&category=categoria para buscar livros por título e/ou categoria."
    ]}

@app.get("/api/v1/health")
def health_check():
    """Verifica o status da API."""
    return {"status": "ok", "message": "API está funcionando normalmente."}

@app.get("/api/v1/books")
def get_all_books():
    """Retorna uma lista de todos os livros disponíveis na base de dados."""
    if df_books.empty:
        return {"message": "Nenhum dado de livro encontrado."}
    
    df_with_id = df_books.reset_index()
    return df_with_id.to_dict('records')

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

    results_with_id = results.reset_index()
    return results_with_id.to_dict('records')

@app.get("/api/v1/books/{book_id}")
def get_book_by_id(book_id: int):
    """Retorna os detalhes de um livro específico pelo seu ID."""
    
    if df_books.empty:
         raise HTTPException(status_code=503, detail="Dados de livros não carregados.")

    try:
        book_series = df_books.loc[book_id]
        book_data = book_series.to_dict()
        book_data['id'] = book_id
        
        return book_data
        
    except KeyError:
        raise HTTPException(status_code=404, detail="Livro com o ID fornecido não encontrado.")