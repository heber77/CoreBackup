from agent_query import KeywordExtractionAgent
from agent_busca import LegalSearchAgent
import json

def process_legal_text(texto: str) -> None:
    """
    Processa um texto juridico usando os dois agentes em sequencia:
    1. KeywordExtractionAgent: gera a query estruturada
    2. LegalSearchAgent: faz a busca
    """
    print("\n=== Processando texto juridico ===")
    
    # Primeiro agente: extrai a query estruturada do texto
    print("\n1. Gerando query estruturada...")
    extractor = KeywordExtractionAgent()
    query_struct = extractor.extract_keywords(texto)
    
    # Converte a string JSON em dicionario
    try:
        query_dict = json.loads(query_struct)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar a query: {str(e)}")
        return
    
    print("\nQuery estruturada gerada:")
    print(f"Area do Direito: {query_dict['area_direito']}")
    print(f"Conceitos-chave: {', '.join(query_dict['conceitos_chave'])}")
    print(f"Situacao: {query_dict['situacao']}")
    print(f"Query principal: {query_dict['query_text']}")
    
    # Segundo agente: faz a busca com a query gerada
    print("\n2. Realizando busca...")
    search_agent = LegalSearchAgent()
    results = search_agent.search(query_dict['query_text'])
    
    if results:
        print("\nResultados encontrados:")
        # Formata os resultados de maneira mais legivel
        for idx, result in enumerate(results.get('results', []), 1):
            print(f"\nResultado {idx}:")
            print(f"ID: {result.get('id_documento')}")
            print(f"Ministro Relator: {result.get('ministroRelator')}")
            print(f"Ementa: {result.get('ementa')[:200]}...")  # Mostra apenas os primeiros 200 caracteres
    else:
        print("\nNenhum resultado encontrado.")


if __name__ == "__main__":
    # Texto juridico de exemplo
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
    sabe o que e e que nao fora utilizado pelo consumidor.
    """,
    texto_exemplo2 = """
Trata-se de Habeas Corpus impetrado em favor de jornalista 
investigativo que foi condenado por criticas a agentes publicos 
em redes sociais. A defesa argumenta que a decisao de primeira instancia 
desconsiderou a liberdade de expressao, prevista no artigo 5º, inciso IV, 
da Constituicao Federal. Alem disso, sustenta-se que a manifestacao do 
paciente nao configura discurso de odio ou incitacao a violencia, 
tratando-se de mero exercicio do direito de critica. Diante disso, 
analisemos a jurisprudencia do STF sobre os limites da liberdade de 
expressao e a possibilidade de sancoes penais por manifestacoes em ambiente digital.





"""
    texto_exemplo3 = """
O consumidor identificou, em sua conta de energia elétrica, 
a cobrança de valores referentes a "serviços adicionais" que não foram contratados. 
Ao entrar em contato com a concessionária, foi informado de que tais valores estavam 
previstos no contrato, porém sem qualquer especificação clara. Diante da ausência de 
consentimento expresso e da violação ao princípio da transparência, busca-se a 
restituição dos valores pagos indevidamente, bem como a aplicação da penalidade 
prevista no Código de Defesa do Consumidor. Para embasar a argumentação, 
analisemos a jurisprudência acerca da devolução de cobranças indevidas em serviços públicos.


    """
    
    # Processa o texto
    process_legal_text(texto_exemplo) 





