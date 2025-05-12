# Busca Automática de Jurisprudência

Este projeto implementa uma API para processamento automático de textos jurídicos, extração de palavras-chave e busca em bases de jurisprudência. O sistema utiliza modelos de linguagem através do CrewAI para construir consultas jurídicas otimizadas.

## Visão geral

A aplicação consiste em um sistema que recebe textos jurídicos, analisa seu conteúdo, constrói uma query otimizada e realiza buscas em bases de jurisprudência. A arquitetura é composta por três componentes principais:

1. **agent_query.py**: Responsável por analisar textos jurídicos e extrair elementos (área do direito, conceitos-chave, situação) para construir uma query otimizada.

2. **agent_busca.py**: Recebe a query gerada e realiza buscas em bases de jurisprudência via API externa.

3. **api.py**: Integra os agentes de query e busca, expondo endpoints para processamento de textos.

## Requisitos

- Chave de API da OpenAI (necessária para o CrewAI)
- Acesso à API de jurisprudência (por padrão, usa https://jurisprudencias.corejur.com.br)

## Configuração

1. **Clone o repositório:**
   ```bash
   git clone <repositório>
   cd buscaAutomatica
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
   
   As principais dependências incluem:
   - fastapi
   - uvicorn
   - pydantic
   - crewai
   - requests
   - python-dotenv

3. **Configure a API key da OpenAI:**
   
   É **obrigatório** criar um arquivo `.env` na raiz do projeto com:
   ```
   OPENAI_API_KEY=sua_chave_aqui
   ```
   
   Sem esta configuração, o agente de extração de keywords não funcionará.

## Execução com Docker

Este projeto inclui arquivos para execução em containers Docker, o que facilita a implantação e evita problemas de dependências.

### Requisitos para Docker

- Docker instalado no sistema
- Docker Compose (incluído no Docker Desktop para Windows/Mac)

### Construção e execução com Docker Compose

1. **Configure a variável de ambiente para a API key da OpenAI:**
   
   Crie um arquivo `.env` na raiz do projeto com:
   ```
   OPENAI_API_KEY=sua_chave_aqui
   ```

2. **Execute com Docker Compose:**
   ```bash
   docker-compose up -d
   ```
   
   Isso irá:
   - Construir a imagem Docker da aplicação
   - Iniciar um container na porta 8000
   - Configurar a API key da OpenAI a partir do seu arquivo .env local
   - Configurar reinício automático em caso de falhas

3. **Verificar o status:**
   ```bash
   docker-compose ps
   ```

4. **Ver logs:**
   ```bash
   docker-compose logs -f
   ```

5. **Parar a aplicação:**
   ```bash
   docker-compose down
   ```

### Construção manual da imagem Docker

Se preferir construir e executar manualmente:

```bash
# Construir a imagem
docker build -t busca-juridica .

# Executar o container
docker run -p 8000:8000 -e OPENAI_API_KEY="sua_chave_aqui" busca-juridica
```

## Execução Local (sem Docker)

Para iniciar o servidor API localmente:

```bash
python api.py
```

Por padrão, a API estará disponível em http://0.0.0.0:8000 e você pode acessar a documentação Swagger UI diretamente na rota raiz.

## Testando a API

Você pode testar a API usando o Swagger UI integrado ou fazendo suas próprias requisições:

### Usando o Postman:

Configure uma requisição POST:
- URL: `http://localhost:8000/processar`
- Headers: `Content-Type: application/json`
- Body (raw, JSON):
  ```json
  {
      "texto": "Deste modo, nao havendo possibilidade de devolucao em dobro do valor correspondente a Tarifa de Cadastro cobrada, que seja ao menos devolvido o valor pago em excesso de forma dobrada. Vale destacar que, o presente caso esta sendo vedado ao consumidor o direito minimo a informacao, sendo esta cobranca claramente abusiva."
  }
  ```

### Usando Python:

```python
import requests

url = "http://localhost:8000/processar"
texto = """Deste modo, nao havendo possibilidade de devolucao em dobro do valor 
correspondente a Tarifa de Cadastro cobrada, que seja ao menos devolvido o 
valor pago em excesso de forma dobrada."""

response = requests.post(
    url,
    headers={"Content-Type": "application/json"},
    json={"texto": texto}
)

print(response.json())
```

## API Endpoints

### POST /processar

Processa um texto jurídico, gera uma query otimizada e realiza busca jurisprudencial.

**Request Body:**
```json
{
    "texto": "seu texto jurídico aqui"
}
```

**Response:**
```json
{
    "query": "texto da query otimizada para busca",
    "resultados": [
        {
            "id_documento": "id do documento",
            "ministroRelator": "nome do ministro relator",
            "ementa": "texto da ementa",
            "url": "url do documento (STJ)",
            "url_download": "url para download (STF)"
        }
    ]
}
```

### GET /health

Verifica o status da API.

**Response:**
```json
{
    "status": "online"
}
```

## Como o Sistema Funciona

### 1. Processamento do Texto (agent_query.py)

O `KeywordExtractionAgent` executa duas etapas principais:

- **Análise do texto (método `_analyze_text_for_query_elements`):**
  - Identifica a área do direito específica
  - Extrai 3-5 conceitos-chave relevantes
  - Descreve a situação jurídica de forma concisa
  
- **Construção da query (método `_build_query_from_elements`):**
  - Usa os elementos extraídos para construir uma query otimizada
  - Aplica técnicas de linguagem natural para criar uma busca eficiente
  - Retorna apenas a string final da query

Este processo interno de análise e construção permite gerar consultas mais precisas sem expor a complexidade para o usuário final.

### 2. Busca de Jurisprudência (agent_busca.py)

O `LegalSearchAgent` realiza as seguintes operações:

- Identifica o tribunal apropriado com base na query (STF por padrão, ou STJ se mencionado)
- Adapta os campos (features) a serem retornados conforme o tribunal
- Estrutura a requisição para a API externa
- Realiza a busca e retorna os resultados formatados

### 3. Integração (api.py)

A API FastAPI orquestra o processo:

- Recebe o texto do usuário via endpoint `/processar`
- Chama o `KeywordExtractionAgent` para gerar a query
- Envia a query para o `LegalSearchAgent` para realizar a busca
- Retorna ao usuário um JSON com a query e os resultados

## Arquitetura do Sistema

```
┌───────────────┐     ┌────────────────────┐     ┌───────────────────┐
│  Texto        │     │  KeywordExtraction │     │  LegalSearch      │
│  Jurídico     │────▶│  Agent             │────▶│  Agent            │
│  (Input)      │     │  - Análise interna │     │  - Identifica     │
└───────────────┘     │  - Gera query      │     │    tribunal       │
                      └────────────────────┘     │  - Realiza busca  │
                                                 └───────────────────┘
                                                           │
                                                           ▼
                                                 ┌───────────────────┐
                                                 │  Resposta API     │
                                                 │  - Query          │
                                                 │  - Resultados     │
                                                 └───────────────────┘
```

## Soluções para Problemas Comuns

1. **Erro "API key não encontrada"**:
   - Verifique se o arquivo `.env` existe na raiz do projeto
   - Confirme que contém a linha `OPENAI_API_KEY=sua_chave_aqui`
   - A chave deve ser válida e ter acesso ao modelo gpt-4o-mini

2. **Erro de conexão com a API externa**:
   - Verifique se a API de jurisprudência está acessível (padrão: https://jurisprudencias.corejur.com.br)
   - O endereço pode ser alterado em `agent_busca.py` no parâmetro `base_url` do método `search`

3. **Resultados não relevantes**:
   - Tente fornecer textos jurídicos mais detalhados e específicos
   - O sistema funciona melhor com descrições claras de situações jurídicas

## Configurações Avançadas

### Alterando o Modelo de Linguagem

O sistema utiliza o modelo `gpt-4o-mini` por padrão. Para alterar:

```python
# Em agent_query.py
self.llm = LLM(
    model="gpt-4o",  # Altere para outro modelo compatível
    temperature=0.2,
    api_key=api_key
)
```

### Ajustando os Parâmetros de Busca

Os parâmetros de busca podem ser ajustados em `agent_busca.py`:

```python
data = {
    "query_text": query,
    "query_type": "bm25",  # Tipo de busca
    "target_vector": "inteiro_teor",  # Campo alvo
    "limit": 5,  # Número de resultados
    "features": features,
    "filters": []  # Filtros adicionais
}
```




