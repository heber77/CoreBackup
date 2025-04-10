# Consulta de Jurisprudência API

Esta documentação descreve como utilizar a API de Consulta de Jurisprudência, que permite acessar informações sobre tribunais, metadados e realizar consultas detalhadas em coleções jurídicas.

---

## 📚 Endpoints Disponíveis

### 1. **Listar Tribunais Disponíveis**

Retorna a lista de tribunais que podem ser consultados.

**URL:**

```
GET /tribunais
```

**Exemplo de Requisição:**

```python
import requests
response = requests.get(url='http://127.0.0.1:8080/tribunais')
print(response.text)
```

**Exemplo de Resposta:**

```json
{
    "results": ["stf", "stj"]
}
```

---

### 2. **Obter Metadados Disponíveis**

Retorna os metadados que um tribunal possui em sua coleção.

**URL:**

```
GET /properties
```

**Parâmetros:**

| Nome     | Tipo   | Descrição                    |
| -------- | ------ | ---------------------------- |
| tribunal | string | Nome do tribunal (ex: "stf") |

**Exemplo de Requisição:**

```python
response = requests.get(url='http://127.0.0.1:8080/properties', params={'tribunal':'stf'})
print(response.text)
```

**Exemplo de Resposta:**

```json
{
    "results": [
        {
            "name": "partes_lista_texto",
            "description": "This property was generated by Weaviate's auto-schema feature on Tue Jan 14 12:57:37 2025",
            "data_type": "text",
            "index_filterable": true,
            "index_range_filters": false,
            "index_searchable": true,
            "nested_properties": null,
            "tokenization": "word",
            "vectorizer_config": null,
            "vectorizer": "none"
        },
        {
            "name": "ministroRelator",
            "description": "This property was generated by Weaviate's auto-schema feature on Tue Jan 14 12:57:37 2025",
            "data_type": "text",
            "index_filterable": true,
            "index_range_filters": false,
            "index_searchable": true,
            "nested_properties": null,
            "tokenization": "word",
            "vectorizer_config": null,
            "vectorizer": "none"
        },
        {
            "name": "jurisprudenciaCitada",
            "description": "This property was generated by Weaviate's auto-schema feature on Tue Jan 14 12:57:37 2025",
            "data_type": "text",
            "index_filterable": true,
            "index_range_filters": false,
            "index_searchable": true,
            "nested_properties": null,
            "tokenization": "word",
            "vectorizer_config": null,
            "vectorizer": "none"
        },
        {
            "name": "titulo",
            "description": "This property was generated by Weaviate's auto-schema feature on Tue Jan 14 12:57:37 2025",
            "data_type": "text",
            "index_filterable": true,
            "index_range_filters": false,
            "index_searchable": true,
            "nested_properties": null,
            "tokenization": "word",
            "vectorizer_config": null,
            "vectorizer": "none"
        }
    ]
}
```

---

### 3. **Consulta Principal de Jurisprudência**

Realiza uma busca por texto no inteiro teor dos documentos e retorna os metadados especificados.

**URL:**

```
POST /query
```

**Parâmetros de Query:**

| Nome     | Tipo   | Descrição                    |
| -------- | ------ | ---------------------------- |
| tribunal | string | Nome do tribunal (ex: "stf") |

**Operadores de Filtros:**

Os seguintes operadores podem ser utilizados nos filtros da consulta principal:

| Operador         | Descrição                                  |
| ---------------- | ------------------------------------------ |
| Equal            | Igualdade                                  |
| NotEqual         | Diferença                                  |
| LessThan         | Menor que                                  |
| LessThanEqual    | Menor ou igual                             |
| GreaterThan      | Maior que                                  |
| GreaterThanEqual | Maior ou igual                             |
| Like             | Busca por correspondência parcial          |
| IsNull           | Verifica se o campo é nulo                 |
| ContainsAny      | Contém qualquer valor da lista fornecida   |
| ContainsAll      | Contém todos os valores da lista fornecida |

**Exemplo de Body:**

```python
# Exemplo completo de body para consulta principal
{
    "query_text": "Texto de busca no inteiro teor",
    "query_type": "bm25",  # Tipo de algoritmo de busca (ex: bm25, tf-idf)
    "limit": 5,  # Limite de documentos retornados
    "features": ["id_documento", "ministroRelator", "dataPublicacao"],  # Metadados desejados
    "filters": [
        {
            "content": "2024-05-30",  # Valor a ser filtrado
            "query_type": "LessThanEqual",  # Operador de filtro
            "collection_field": "dataPublicacao"  # Campo de metadado a ser filtrado
        },
        {
            "content": "2023-01-01",
            "query_type": "GreaterThanEqual",
            "collection_field": "dataPublicacao"
        },
        {
            "content": "GILMAR",
            "query_type": "Like",
            "collection_field": "ministroRelator"
        }
    ]
}
```

**Exemplo de Requisição em Python:**

```python
data = {
    "query_text": "Quais são os parâmetros estabelecidos pelo STF para a proteção da liberdade de expressão versus o direito à privacidade nas redes sociais?",
    "query_type": "bm25",
    "limit": 5,
    "features": ["id_documento", "ministroRelator", "dataPublicacao"],
    "filters": [
        {
            "content": "2024-05-30",
            "query_type": "LessThanEqual",
            "collection_field": "dataPublicacao"
        },
        {
            "content": "2023-01-01",
            "query_type": "GreaterThanEqual",
            "collection_field": "dataPublicacao"
        },
        {
            "content": "GILMAR",
            "query_type": "Like",
            "collection_field": "ministroRelator"
        }
    ]
}
response = requests.post(url='http://127.0.0.1:8080/query', params={'tribunal':'stf'}, json=data)
print(response.text)
```

**Exemplo de Resposta:**

```json
{
    "results": [
        {
            "id_documento": "sjur482122",
            "ministroRelator": "GILMAR MENDES",
            "dataPublicacao": "2023-06-19T00:00:00-03:00"
        },
        {
            "id_documento": "sjur478159",
            "ministroRelator": "GILMAR MENDES",
            "dataPublicacao": "2023-04-28T00:00:00-03:00"
        },
        {
            "id_documento": "sjur478158",
            "ministroRelator": "GILMAR MENDES",
            "dataPublicacao": "2023-04-28T00:00:00-03:00"
        },
        {
            "id_documento": "sjur478149",
            "ministroRelator": "GILMAR MENDES",
            "dataPublicacao": "2023-04-28T00:00:00-03:00"
        },
        {
            "id_documento": "sjur476959",
            "ministroRelator": "GILMAR MENDES",
            "dataPublicacao": "2023-04-10T00:00:00-03:00"
        }
    ]
}
```

---

### 4. **Consultar Jurisprudencias por Números Processo**

Retorna informações completas sobre processos utilizando os seus números. Feita para receber o metadado de jurisprudencia\_citada obtido na requisição anterior.

**URL:**

```
GET /jurisprudencia
```

**Parâmetros:**

| Nome              | Tipo   | Descrição                     |
| ----------------- | ------ | ----------------------------- |
| tribunal          | string | Nome do tribunal (ex: "stj")  |
| numeros\_processo | list   | Lista de números de processos |

**Exemplo de Requisição:**

```python
response = requests.get(url='http://127.0.0.1:8080/jurisprudencia', params={'tribunal':'stj', 'numeros_processo': ['1763942', '890147']})
print(response.text)
```

**Exemplo de Resposta:**

```json
{
    "1763942": [
        {"dados do processo"},
        {"se tiver mais de um resultado, estarão todos aqui"}
    ],
    "890147": [
        {"dados outro processo citado"}
    ]
}
```
