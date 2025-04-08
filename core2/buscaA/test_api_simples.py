import requests
import json

# URL base da API
BASE_URL = "http://127.0.0.1:8000"

def test_processar_texto(texto):
    """Testa o endpoint de processamento de texto jurídico"""
    print(f"\n=== Processando texto jurídico ===")
    print(f"Texto enviado: {texto[:100]}...")  # Mostra apenas o início do texto
    
    # Faz a requisição POST para a API
    response = requests.post(
        f"{BASE_URL}/processar",
        headers={"Content-Type": "application/json"},
        json={"texto": texto}
    )
    
    # Verifica se a requisição foi bem sucedida
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        # Formata e exibe o resultado
        resultado = response.json()
        print("\n=== Query Estruturada ===")
        print(f"Área do Direito: {resultado['query_estruturada']['area_direito']}")
        print(f"Conceitos-chave: {', '.join(resultado['query_estruturada']['conceitos_chave'])}")
        print(f"Situação: {resultado['query_estruturada']['situacao']}")
        print(f"Query principal: {resultado['query_estruturada']['query_text']}")
        
        print("\n=== Resultados da Busca ===")
        if resultado['resultados']:
            for idx, result in enumerate(resultado['resultados'], 1):
                print(f"\nResultado {idx}:")
                print(f"ID: {result.get('id_documento')}")
                print(f"Ministro Relator: {result.get('ministroRelator')}")
                print(f"Ementa: {result.get('ementa')[:200]}...")  # Mostra apenas os primeiros 200 caracteres
        else:
            print("Nenhum resultado encontrado.")
    else:
        print(f"Erro na requisição: {response.text}")

if __name__ == "__main__":
    # Texto para teste
    texto = """Deste modo, nao havendo possibilidade de devolucao em
    dobro do valor correspondente a Tarifa de Cadastro cobrada, que
    seja ao menos devolvido o valor pago em excesso de forma dobrada.
    Vale destacar que, o presente caso esta sendo vedado ao
    consumidor o direito minimo a informacao, sendo esta cobranca
    claramente abusiva, tendo em vista que exige vantagem
    manifestamente excessiva, ja que no contrato a fonte da letra nao
    respeita a previsao legal, tornando mais dificultoso a leitura de
    clausulas e valores, bem como a cobranca por servico que nao se
    sabe o que e e que nao fora utilizado pelo consumidor."""
    
    # Executa o teste
    test_processar_texto(texto) 