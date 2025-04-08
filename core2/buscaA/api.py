from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from agent_query import KeywordExtractionAgent
from agent_busca import LegalSearchAgent
import json
import uvicorn

# Modelos de dados para a API
class TextoJuridicoInput(BaseModel):
    texto: str

class ConceitosChave(BaseModel):
    query_text: str
    tribunal: Optional[str] = ""
    area_direito: str
    conceitos_chave: List[str]
    situacao: str

class ResultadoBusca(BaseModel):
    id_documento: str
    ministroRelator: str
    ementa: str
    url: Optional[str] = None
    url_download: Optional[str] = None

class ProcessamentoResponse(BaseModel):
    query_estruturada: ConceitosChave
    resultados: List[Dict[str, Any]]

# Inicialização da API
app = FastAPI(
    title="API de Processamento Jurídico",
    description="API para extração de keywords e busca jurídica a partir de textos jurídicos",
    version="1.0.0"
)

@app.post("/processar", response_model=ProcessamentoResponse)
async def processar_texto_juridico(input_data: TextoJuridicoInput):
    """
    Processa um texto jurídico extraindo palavras-chave e realizando busca
    
    - **texto**: Texto jurídico a ser processado
    
    Retorna:
    - **query_estruturada**: Query estruturada extraída do texto
    - **resultados**: Lista de documentos jurídicos encontrados
    """
    try:
        # Primeiro agente: extrai a query estruturada do texto
        extractor = KeywordExtractionAgent()
        query_struct = extractor.extract_keywords(input_data.texto)
        
        # Converte a string JSON em dicionário
        try:
            query_dict = json.loads(query_struct)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Erro ao decodificar a query: {str(e)}")
        
        # Segundo agente: faz a busca com a query gerada
        search_agent = LegalSearchAgent()
        results = search_agent.search(query_dict['query_text'])
        
        if not results:
            # Se não houver resultados, retorna a query estruturada com uma lista vazia
            return {
                "query_estruturada": query_dict,
                "resultados": []
            }
        
        # Prepara a resposta com a query estruturada e os resultados da busca
        return {
            "query_estruturada": query_dict,
            "resultados": results.get('results', [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

# Adiciona uma rota de saúde para verificar se a API está funcionando
@app.get("/health")
async def health_check():
    return {"status": "online"}

# Para execução local
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 