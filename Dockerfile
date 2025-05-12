# Use a imagem base Python oficial
FROM python:3.12-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala as dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copia o requirements.txt para o container
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia os arquivos da aplicação para o container
COPY buscaAutomatica/ .

# Expõe a porta em que a API vai rodar
EXPOSE 8000

# Defina uma variável de ambiente para a chave da API OpenAI
# (esta deve ser sobrescrita durante a execução do container)
ENV OPENAI_API_KEY="sua_chave_aqui"

# Comando para iniciar a aplicação
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"] 