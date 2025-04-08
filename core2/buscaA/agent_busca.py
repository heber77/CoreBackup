from typing import Dict
import os
from dotenv import load_dotenv
import requests


class LegalSearchAgent:
    def __init__(self):
        # Mapeamento de tribunais
        self.tribunal_mapping = {
            'stf': 'STFCustomVector_e5large',
            'stj': 'STJCustomVector_e5large'
        }

        # Mapeamento de features por tribunal
        self.feature_mapping = {
            'STFCustomVector_e5large': ["id_documento", "ministroRelator", "ementa", "url_download"],
            'STJCustomVector_e5large': ["id_documento", "ministroRelator", "ementa", "url"]
        }

    def _get_tribunal_from_query(self, query: str) -> str:
        """Identifica o tribunal com base na query"""
        query_lower = query.lower()
        if 'stf' in query_lower:
            return self.tribunal_mapping['stf']
        elif 'stj' in query_lower:
            return self.tribunal_mapping['stj']
        return 'STFCustomVector_e5large'  # tribunal padrão

    def search(self, query: str, base_url: str = 'http://127.0.0.1:8001') -> Dict:
        """
        Executa a busca na API usando a query fornecida

        Args:
            query: Query em linguagem natural (já processada pelo KeywordExtractionAgent)
            base_url: URL base da API (default: http://127.0.0.1:8001)

        Returns:
            Dict com os resultados da busca
        """
        # Identifica o tribunal
        tribunal = self._get_tribunal_from_query(query)
        
        # Seleciona as features corretas com base no tribunal
        features = self.feature_mapping.get(tribunal, ["id_documento", "ministroRelator", "ementa"])

        # Estrutura da query para a API
        data = {
            "query_text": query,
            "query_type": "bm25",
            "target_vector": "inteiro_teor",
            "limit": 5,
            "features": features,
            "filters": []
        }

        try:
            # Faz a chamada à API
            response = requests.post(
                url=f'{base_url}/query',
                params={'tribunal': tribunal},
                json=data
            )

            # Verifica se a chamada foi bem sucedida
            response.raise_for_status()

            # Retorna os resultados
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"\nErro ao fazer a chamada à API: {str(e)}")
            return None


# Exemplo de uso
if __name__ == "__main__":
    # A query já deve vir processada do KeywordExtractionAgent
    # Para testar, você pode rodar primeiro o extrair.py e copiar a query gerada
    query = "decisões sobre cobrança abusiva de tarifas bancárias e direito à informação do consumidor"
    
    # Inicializa o agente de busca
    search_agent = LegalSearchAgent()
    
    # Executa a busca
    results = search_agent.search(query)
    
    if results:
        print("\nResultados da busca:")
        print(results) 