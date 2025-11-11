FROM python:3.11-slim

WORKDIR /app

# Evitar stdout truncado
ENV PYTHONUNBUFFERED=1

# Instalar dependências de sistema (ex: build-essential para psycopg2)
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY ./services/recommender_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia apenas o código-fonte do microsserviço
COPY ./services/recommender_service/app/ /app/app/

# Porta padrão do Uvicorn
EXPOSE 8000

# Variáveis de ambiente serão injetadas pelo ConfigMap do Kubernetes
# ENV APP_VERSION=0.1.0-k8s
# ENV MLFLOW_TRACKING_URI=...
# ENV MLFLOW_MODEL_URI=...
# ENV CACHE_ENABLED=True

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]