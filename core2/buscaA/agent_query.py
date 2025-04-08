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
            load_dotenv()  # Carrega do arquivo .env padrao
            api_key = os.getenv("OPENAI_API_KEY")

            if api_key is None:
                raise ValueError("API key nao encontrada. Por favor, forneca a chave como parametro ou configure no arquivo .env")

        # Inicializa o LLM do CrewAI
        self.llm = LLM(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=api_key
        )

        # Cria o agente especializado em extracao de palavras-chave
        self.agent = Agent(
            role='Especialista em Analise de Textos Juridicos e Construcao de Queries',
            goal='''Analisar textos juridicos escritos por advogados que descrevem situacoes juridicas, 
                    problemas ou argumentos, e extrair os elementos mais relevantes para construir queries 
                    de busca eficientes''',
            backstory="""Sou um especialista em analise de textos juridicos com profundo conhecimento em:
                     - Identificacao de problemas juridicos centrais em textos
                     - Extracao de termos tecnicos juridicos relevantes
                     - Reconhecimento de direitos em discussao (direito do consumidor, contratos, etc.)
                     - Identificacao de tipos de cobrancas, servicos ou praticas questionadas
                     - Compreensao de fundamentos legais (abuso de direito, onus da prova, etc.)
                     - Construcao de queries estruturadas mantendo linguagem natural e objetiva

                     Minha especialidade e transformar textos juridicos complexos em queries 
                     de busca eficientes, mantendo todos os elementos relevantes de forma organizada.""",
            llm=self.llm,
            verbose=False
        )

    def extract_json_from_text(self, text: str) -> str:
        """
        Extrai um objeto JSON de um texto que pode conter outros elementos.
        
        Args:
            text: Texto que pode conter um objeto JSON
            
        Returns:
            String contendo apenas o objeto JSON
        """
        # Tenta encontrar um objeto JSON no texto usando regex
        json_pattern = r'\{[\s\S]*\}'
        json_match = re.search(json_pattern, text)
        
        if json_match:
            return json_match.group(0)
        return text

    def extract_elements(self, context: str) -> Dict:
        """
        Extrai os elementos basicos de um texto juridico: area do direito, 
        conceitos-chave e situacao especifica.

        Args:
            context: Texto juridico para analise

        Returns:
            Dict com os elementos extraidos
        """
        prompt = f"""
        Analise o seguinte texto juridico e extraia os elementos fundamentais para uma busca jurisprudencial.

        ### **Formato esperado da resposta**
        A resposta deve ser um JSON com a seguinte estrutura:
        {{
            "tribunal": "tribunal mencionado (se houver)",
            "area_direito": "area do direito relacionada",
            "conceitos_chave": ["lista", "de", "conceitos", "juridicos"],
            "situacao": "descricao da situacao especifica"
        }}

        ### **Instrucoes**
        - **Identifique o tribunal** apenas se explicitamente mencionado no texto
        - **Determine a area do direito** principal relacionada ao caso
        - **Liste os conceitos_chave** mais relevantes para a busca (4-6 conceitos)
        - **Descreva a situacao** de forma concisa e especifica
        - **Nao tente adivinhar informacoes ausentes**
        - **IMPORTANTE**: Retorne APENAS o JSON, sem texto adicional antes ou depois

        Agora, extraia os elementos com base no seguinte contexto:

        ---

        **Texto para analise:**
        {context}

        ---

        Retorne **apenas** o JSON estruturado, sem explicacoes adicionais.
        """

        task = Task(
            description=prompt,
            expected_output="Elementos extraidos em formato JSON"
        )

        elements_json = self.agent.execute_task(task)
        
        # Tenta extrair apenas o JSON da resposta
        json_str = self.extract_json_from_text(elements_json.strip())
        
        try:
            elements = json.loads(json_str)
            
            # Verifica se os campos obrigatórios estão presentes
            if "area_direito" not in elements or not elements["area_direito"]:
                elements["area_direito"] = "Direito Geral"
                
            if "conceitos_chave" not in elements or not elements["conceitos_chave"]:
                elements["conceitos_chave"] = ["direito", "jurisprudencia", "processo"]
                
            if "situacao" not in elements or not elements["situacao"]:
                elements["situacao"] = "situacao juridica identificada no texto"
                
            return elements
        except json.JSONDecodeError as e:
            # Fallback genérico para qualquer texto
            return {
                "tribunal": "",
                "area_direito": "Direito Geral",
                "conceitos_chave": ["termo juridico", "jurisprudencia", "legislacao", "processo"],
                "situacao": "situacao juridica descrita no texto"
            }

    def build_query(self, elements: Dict) -> str:
        """
        Constroi uma query de busca baseada nos elementos extraidos.

        Args:
            elements: Dicionario com os elementos extraidos (area do direito, 
                     conceitos-chave, situacao)

        Returns:
            String com a query construida
        """
        prompt = f"""
        Com base nos elementos juridicos extraidos, construa uma query de busca eficiente 
        para encontrar jurisprudencias relevantes.

        ### **Elementos extraidos**
        - **Area do Direito**: {elements['area_direito']}
        - **Conceitos-chave**: {', '.join(elements['conceitos_chave'])}
        - **Situacao**: {elements['situacao']}
        - **Tribunal** (se especificado): {elements.get('tribunal', '')}

        ### **Instrucoes para construcao da query**
        - Formule a query como uma busca que um usuario digitaria em um sistema de pesquisa juridica
        - NÃO use formato de pergunta (não comece com "como", "quais", etc.)
        - Use preposições e conectores entre os termos (de, em, por, sobre, para, etc.)
        - A query deve formar uma expressão coesa e natural, não apenas palavras soltas
        - Priorize os conceitos juridicos mais relevantes
        - Inclua termos tecnicos especificos da area do direito
        - Mantenha a query objetiva e direta
        - Nao use operadores booleanos (AND, OR, NOT)
        - Limite a query a uma unica frase concisa (maximo 15-20 palavras)
        - IMPORTANTE: Retorne APENAS o texto da query, sem aspas ou formatacao adicional

        ### **Exemplos de boas queries**
        - "devolucao em dobro de tarifa bancaria por cobranca abusiva no direito do consumidor"
        - "tarifa de cadastro em contrato bancario com cobranca indevida e devolucao de valores"
        - "direito a informacao do consumidor em contratos com clausulas abusivas"

        ### **Exemplos de queries ruins (apenas palavras soltas)**
        - "devolucao dobro tarifa bancaria cobranca abusiva direito consumidor"
        - "tarifa cadastro cobranca indevida contrato bancario devolucao valores"

        ### **Formato da resposta**
        Retorne apenas o texto da query, sem explicacoes adicionais.
        """

        task = Task(
            description=prompt,
            expected_output="Query de busca em texto simples"
        )

        query_text = self.agent.execute_task(task)
        
        # Remove aspas se presentes
        query_text = query_text.strip().strip('"\'')
        
        return query_text

    def extract_keywords(self, context: str) -> str:
        """
        Extrai palavras-chave de um texto juridico e constroi uma query estruturada.

        Args:
            context: Texto juridico para analise

        Returns:
            String JSON com a query estruturada contendo:
            - query_text: texto principal da query
            - tribunal: tribunal mencionado (se houver)
            - area_direito: area do direito relacionada
            - conceitos_chave: conceitos juridicos relevantes
            - situacao: situacao especifica descrita
        """
        # Primeiro extrai os elementos basicos
        elements = self.extract_elements(context)
        
        # Depois constroi a query com base nos elementos
        query_text = self.build_query(elements)
        
        # Monta o resultado final
        result = {
            "query_text": query_text,
            "tribunal": elements.get("tribunal", ""),
            "area_direito": elements["area_direito"],
            "conceitos_chave": elements["conceitos_chave"],
            "situacao": elements["situacao"]
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)


# Exemplo de uso
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