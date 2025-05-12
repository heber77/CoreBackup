from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from agent_query import KeywordExtractionAgent
from agent_busca import LegalSearchAgent
import json
import uvicorn

#Modelos de dados para a API
class TextoJuridicoInput(BaseModel):
    texto: str

class QueryResponse(BaseModel):
    query: str
    resultados: List[Dict[str, Any]]

#Inicialização da API
app = FastAPI(
    title="API geração de queries e busca jurídica",
    description="API para extração de keywords e busca jurídica a partir de textos jurídicos",
    version="1.0.0",
    docs_url="/",  # Swagger UI na rota raiz
    redoc_url=None,
    openapi_url="/openapi.json",
)

@app.post("/processar", response_model=QueryResponse)
async def processar_texto_juridico(input_data: TextoJuridicoInput):
    """
    Processa um texto jurídico extraindo a query e realizando busca jurisprudencial
    
    - **texto**: Texto jurídico a ser processado
    
    Retorna:
    - **query**: Query gerada para busca jurisprudencial
    - **resultados**: Lista de documentos jurídicos encontrados
    """
    try:
        # Primeiro agente: extrai a query do texto
        extractor = KeywordExtractionAgent()
        query = extractor.extract_keywords(input_data.texto)
        
        # Segundo agente: faz a busca com a query gerada
        search_agent = LegalSearchAgent()
        results = search_agent.search(query)
        
        if not results:
            # Se não houver resultados, retorna a query com uma lista vazia
            return {
                "query": query,
                "resultados": []
            }
        
        # Prepara a resposta com a query e os resultados da busca
        return {
            "query": query,
            "resultados": results.get('results', [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

#Adiciona uma rota de saúde para verificar se a API está funcionando
@app.get("/health")
async def health_check():
    """
    Verifica se a API está funcionando corretamente
    
    Retorna:
    - **status**: Status da API ('online' se estiver funcionando)
    """
    return {"status": "online"}

#Para execução local
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 