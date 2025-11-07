##
# Dockerfile para o serviço LLM Assistant
#
# Utiliza a imagem oficial do Python slim para minimizar o tamanho.  As
# dependências são instaladas em uma camada separada para aproveitar o
# cache.  A aplicação é executada via Uvicorn e exposta na porta 8000.

FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copia apenas requirements para instalar dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

EXPOSE 8000

# Comando padrão para executar o serviço
CMD ["uvicorn", "services.llm_assistant.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Healthcheck simples que verifica se o endpoint /assist responde
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD curl -f http://localhost:8000/assist -X POST -H 'Content-Type: application/json' -d '{"prompt":"ping"}' || exit 1