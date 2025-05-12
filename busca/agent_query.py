from crewai import Agent, Task, LLM
from typing import Dict, List
import os
from dotenv import load_dotenv
import json
import re


class KeywordExtractionAgent:
    def __init__(self, api_key: str = None):
        # Carrega a chave da API
        if api_key is None:
            load_dotenv()  #Carrega do arquivo .env padrao
            api_key = os.getenv("OPENAI_API_KEY")

            if api_key is None:
                raise ValueError("API key não encontrada. Por favor, forneça a chave como parâmetro ou configure no arquivo .env")

        #Inicializa o LLM do CrewAI
        self.llm = LLM(
            model="gpt-4o-mini",
            temperature=0.2,  # Redução da temperatura para respostas mais diretas e rápidas
            api_key=api_key
        )

        #Cria o agente que faz a extração de palavras-chave
        self.agent = Agent(
            role='Especialista jurídico',
            goal='''Gerar queries de busca jurisprudencial eficientes a partir de textos jurídicos''',
            backstory="""Especialista em análise de textos jurídicos e formulação de queries 
                      com foco em termos técnicos e linguagem jurídica adequada.""",
            llm=self.llm,
            verbose=False
        )

    def extract_json_from_text(self, text: str) -> str:
        """
        Extrai um objeto JSON de um texto. Versão super otimizada.
        
        Args:
            text: Texto que pode conter um objeto JSON
            
        Returns:
            String contendo apenas o objeto JSON
        """
        text = text.strip()
        
        # Se já começa e termina com chaves, assume que é JSON
        if text.startswith('{') and text.endswith('}'):
            return text
            
        # Caso contrário, usa regex simples para extrair
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        return json_match.group(0) if json_match else '{}'

    def _analyze_text_for_query_elements(self, context: str) -> Dict:
        """
        Analisa o texto para extrair elementos que ajudarão a construir uma query melhor.
        Este método é apenas para uso interno.

        Args:
            context: Texto jurídico para análise

        Returns:
            Dict com elementos para ajudar a construir a query final
        """
        prompt = f"""
        Texto: {context}

        Analise o texto acima e extraia elementos para construir uma busca jurisprudencial eficiente.

        Formato: {{
            "area_direito": "área específica do direito identificada",
            "conceitos_chave": ["conceito1", "conceito2", "conceito3", "conceito4", "conceito5"],
            "situacao": "descrição concisa da situação jurídica"
        }}

        Instruções:
        - Identifique a área do direito específica (ex: "direito do consumidor", "direito penal", etc.)
        - Extraia 3 a 5 conceitos-chave relevantes para a busca jurisprudencial
        - Descreva a situação jurídica em uma frase curta
        - Use termos técnicos jurídicos apropriados

        Responda APENAS com o JSON.
        """

        task = Task(
            description=prompt,
            expected_output="JSON com elementos para query"
        )

        result_json = self.agent.execute_task(task)
        
        # Extrai apenas o JSON da resposta
        json_str = self.extract_json_from_text(result_json.strip())
        
        try:
            elements = json.loads(json_str)
            return elements
        except (json.JSONDecodeError, AttributeError):
            # Fallback mínimo
            return {
                "area_direito": "Direito Geral",
                "conceitos_chave": ["jurisprudência"],
                "situacao": "análise jurídica"
            }

    def _build_query_from_elements(self, elements: Dict) -> str:
        """
        Constrói uma query otimizada a partir dos elementos extraídos.
        
        Args:
            elements: Dicionário com área do direito, conceitos-chave e situação
            
        Returns:
            String com a query otimizada
        """
        prompt = f"""
        Elementos jurídicos:
        - Área do direito: {elements.get('area_direito', 'Direito Geral')}
        - Conceitos-chave: {', '.join(elements.get('conceitos_chave', ['jurisprudência']))}
        - Situação: {elements.get('situacao', 'análise jurídica')}

        Construa uma query de busca jurisprudencial otimizada usando os elementos acima.
        
        Instruções:
        - Use termos jurídicos relevantes (15-20 palavras)
        - Use linguagem natural com conectores
        - Evite operadores booleanos
        - Inclua termos técnicos da área do direito identificada
        - Use os conceitos-chave mais relevantes
        - Contextualize com base na situação jurídica

        Exemplos de queries:
        - "devolucao em dobro de tarifa bancaria por cobranca abusiva no direito do consumidor"
        - "indenizacao por danos morais em cobranca indevida de servicos bancarios"
        - "revisao contratual por clausulas abusivas e onerosidade excessiva"

        Responda APENAS com a query em texto simples, sem formatação ou explicações.
        """

        task = Task(
            description=prompt,
            expected_output="Query textual"
        )

        result = self.agent.execute_task(task)
        
        # Limpa a resposta
        query = result.strip().strip('"\'')
        
        return query

    def extract_keywords(self, context: str) -> str:
        """
        Gera uma query de busca a partir de um texto jurídico.
        Usa análise interna de área do direito, conceitos-chave e situação
        para construir uma query mais eficiente.

        Args:
            context: Texto jurídico para análise

        Returns:
            String contendo a query para busca
        """
        # Primeiro analisa o texto para extrair elementos úteis (apenas para uso interno)
        elements = self._analyze_text_for_query_elements(context)
        
        # Depois constrói a query baseada nesses elementos
        query = self._build_query_from_elements(elements)
        
        # Retorna apenas a query final como string
        return query


# Exemplo de uso
'''
if __name__ == "__main__":
    try:
        # Inicializa o agente
        agent = KeywordExtractionAgent()

        # Exemplo de texto juridico
        texto_exemplo = """
                Deste modo, nao havendo possibilidade de devolucao em
        dobro do valor correspondente a Tarifa de Cadastro cobrada, que
        seja ao menos devolvido o valor pago em excesso de forma dobrada.
        Vale destacar que, o presente caso esta sendo vedado ao
        consumidor o direito minimo a informacao, sendo esta cobranca
        claramente abusiva, tendo em vista que exige vantagem
        manifestamente excessiva, ja que no contrato a fonte da letra nao
        respeita a previsao legal, tornando mais dificultoso a leitura de
        clausulas e valores, bem como a cobranca por servico que nao se
        sabe o que e e que nao fora utilizado pelo consumidor. Desta
        forma, vejamos posicionamento jurisprudencial sobre o tema:
        """

        # Extrai palavras-chave e constroi a query
        query = agent.extract_keywords(texto_exemplo)
        print("\nQuery construida:")
        print(query)

    except Exception as e:
        print(f"Erro ao inicializar o agente: {str(e)}") 
'''