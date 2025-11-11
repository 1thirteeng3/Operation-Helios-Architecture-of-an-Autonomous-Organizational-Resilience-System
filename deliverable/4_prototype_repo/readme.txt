Helius Systems: Protótipo de Arquitetura Resiliente (FASE 4)Este repositório contém o protótipo funcional da Arquitetura Ciber-Resiliente da Helius, conforme definido no Blueprint (Fase 1, 2 e 3) e validado na simulação (Fase 3).O objetivo deste protótipo é demonstrar a implementação prática dos seguintes princípios de resiliência:Isolamento de Falha (Fase 1): Os serviços de controle (MLflow, Grafana) não são mais SPOFs. Eles rodam em modo HA (replicas: 3) com armazenamento persistente (RDS/S3) e podAntiAffinity para resiliência de AZ.Degradação Controlada (Fase 2): O recommender-service implementa um padrão de Cache/Fallback, garantindo que ele sempre inicie (/health OK) e sirva predições, mesmo que o MLflow (dependência) esteja offline.Controle Cibernético (Fase 3): A observabilidade é ativa. O Prometheus usa Service Discovery e monitora métricas de degradação (ex: reco_engine_in_fallback_mode), que podem ser usadas pelo Control Plane para acionar a autocontenção.1. Estrutura do Repositório/
├── services/
│   └── recommender_service/  # Serviço FastAPI com lógica de fallback (Fase 2)
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py         # (com métricas Prometheus)
│       │   ├── model.py        # (lógica de fallback)
│       │   ├── mlflow_utils.py
│       │   └── schemas.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── k8s/  (Manifestos Kubernetes Resilientes)
│   ├── 00-namespace.yaml
│   ├── 01-mlflow-ha.yaml     # (Fase 1: replicas: 3, RDS/S3, AntiAffinity)
│   ├── 02-grafana-ha.yaml    # (Fase 1: replicas: 3, AntiAffinity)
│   └── 03-recommender-ha.yaml # (Fase 2: com fallback, Fase 3: replicas: 3)
│
├── monitoring/
│   ├── prometheus.yml        # (Fase 3: Configurado para K8s Service Discovery)
│   └── alerts-resilient.yml  # (Fase 3: Alertas para Backlog e Modo Fallback)
│
└── .github/workflows/
    └── ci.yml                # (Testa build e health checks)
2. Deploy da Arquitetura ResilientePré-requisitos:Um cluster Kubernetes (EKS, GKE, etc.).kubectl configurado para o cluster.Um backend RDS (PostgreSQL) e um bucket S3 (para o MLflow HA).Instruções de Deploy:Criar o Namespace:kubectl apply -f k8s/00-namespace.yaml
Configurar Segredos (MLflow):Crie um segredo do Kubernetes no namespace helius com as credenciais do RDS:kubectl create secret generic mlflow-db-creds -n helius \
  --from-literal=DB_USER=helius_admin \
  --from-literal=DB_PASS=YOUR_RDS_PASSWORD
Aplicar os Manifestos HA:Implante o control plane (MLflow, Grafana) e o serviço de recomendação resiliente.# (Opcional) Construa e envie suas imagens para seu registry (ex: ECR)
# docker build -t your-registry/helius-reco-service:latest ./services/recommender_service/
# docker push your-registry/helius-reco-service:latest
# (Atualize a imagem em k8s/03-recommender-ha.yaml)

kubectl apply -f k8s/
3. Teste e Observabilidade (Fase 3)Verificar o Deploy:kubectl get pods -n helius -w

# Você deve ver 3 réplicas de cada pod (mlflow, grafana, reco-service)
# NAME                                 READY   STATUS    RESTARTS   AGE
# grafana-core-deployment-7d...        1/1     Running   0          2m
# grafana-core-deployment-7d...        1/1     Running   0          2m
# grafana-core-deployment-7d...        1/1     Running   0          2m
# mlflow-tracker-deployment-5c...      1/1     Running   0          2m
# mlflow-tracker-deployment-5c...      1/1     Running   0          2m
# mlflow-tracker-deployment-5c...      1/1     Running   0          2m
# helius-reco-deployment-6f...         1/1     Running   0          2m
# helius-reco-deployment-6f...         1/1     Running   0          2m
# helius-reco-deployment-6f...         1/1     Running   0          2m
Testar o Endpoint (via Port-Forward):kubectl port-forward svc/helius-reco-service -n helius 8080:80
Em outro terminal, acesse o health check (que agora reporta o modo do modelo):curl http://localhost:8080/health

# Resposta (Saudável, MLflow conectado):
# {"status":"ok", "service":"helius-reco-service", "version":"0.1.0-k8s", "mlflow_connected":true, "model_version":"mlflow-model-v1"}
Observar Métricas (Prometheus/Grafana):Exponha seu Grafana (que agora é HA) e acesse o dashboard. Você poderá consultar as novas métricas de resiliência:reco_engine_requests_total: Contagem de predições.reco_engine_requests_latency_seconds: Latência das predições.reco_engine_in_fallback_mode: (Gauge) 1 se o serviço estiver em modo degradado (Fase 2), 0 se estiver saudável.