FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY ./services/llm_router/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./services/llm_router/app/ /app/app/

EXPOSE 8002

ENV APP_VERSION=0.1.0-k8s

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]