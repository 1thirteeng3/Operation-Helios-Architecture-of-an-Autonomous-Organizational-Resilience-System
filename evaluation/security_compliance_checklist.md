# Checklist de Segurança, Conformidade e Governança

Este checklist fornece uma visão geral das práticas recomendadas que devem ser implementadas no laboratório para garantir segurança, conformidade normativa e governança de modelos. Ele serve como guia de verificação para revisões periódicas.

## 1. Controle de Acesso (RBAC e IAM)

- [ ] **RBAC no Kubernetes:** Definir `Roles` e `RoleBindings` específicos para cada serviço, limitando permissões a namespaces e operações necessárias. Evitar conceder permissões cluster‑admin a serviços ou usuários não essenciais.
- [ ] **Grupos de Segurança e Network Policies:** Configurar `NetworkPolicy` para restringir o tráfego entre pods apenas ao necessário; aplicar regras de segurança no VPC (Security Groups) e sub‑redes.
- [ ] **Least privilege IAM:** Criar políticas AWS IAM granulares para serviços (EKS, S3, RDS), garantindo que cada componente possua somente as ações mínimas requeridas; associar roles com anotação `eks.amazonaws.com/role-arn` em pods.
- [ ] **Revisão de acesso:** Agendar auditorias regulares das permissões de usuários e serviços, removendo credenciais ou tokens não utilizados.

## 2. Gestão e Rotação de Segredos

- [ ] **Secrets Manager/Vault:** Armazenar senhas, chaves e tokens em um serviço de cofre (AWS Secrets Manager ou HashiCorp Vault) em vez de arquivos ou variáveis simples. Referenciar segredos no Kubernetes via `ExternalSecrets` ou `sealed-secrets`.
- [ ] **Rotação periódica:** Implementar política de rotação automática de chaves (por exemplo, a cada 90 dias) para bancos de dados, tokens de API e credenciais de acesso.
- [ ] **Auditoria de segredos:** Monitorar acessos a segredos e configurar alertas para acessos não autorizados ou anômalos.

## 3. Criptografia

- [ ] **Em repouso:** Habilitar criptografia de buckets S3 (SSE‑KMS) e encriptar volumes EBS e snapshots; configurar o RDS/Postgres com criptografia de dados em repouso utilizando KMS.
- [ ] **Em trânsito:** Utilizar TLS nas conexões entre serviços (ingress controller com certificados válidos), no acesso a APIs, na comunicação com RDS e na interface web do MLflow. Gerenciar certificados via ACM ou Cert-Manager.
- [ ] **Chaves de criptografia:** Definir políticas de gerenciamento de chaves (KMS) com rotação e controle de acesso apropriado.

## 4. Logs e Auditoria

- [ ] **Retenção de logs:** Estabelecer período de retenção para logs de aplicação e infraestrutura (p. ex., 90 dias), alinhado a requisitos legais. Configurar armazenamento em S3 ou serviços de log (Loki, CloudWatch) com ciclo de vida definido.
- [ ] **Audit Trails:** Habilitar logs de auditoria do Kubernetes (audit logging) e do AWS CloudTrail. Garantir que alterações em recursos sensíveis (IAM, redes, dados) sejam rastreadas.
- [ ] **Monitoramento de integridade:** Utilizar ferramentas que detectem alterações não autorizadas em configurações, imagens ou dependências (por exemplo, Falco, Trivy).

## 5. Privacidade de Dados

- [ ] **Dados sintéticos:** Utilizar dados sintéticos e anonimização para PII nos conjuntos de treinamento e testes. Evitar armazenar dados sensíveis não mascarados em ambientes de desenvolvimento ou demos.
- [ ] **Conformidade LGPD/GDPR:** Assegurar que dados de usuários sejam tratados de acordo com regulamentos de privacidade (consentimento, finalidade, minimização). Incluir termos de uso na política de dados para LLMs.
- [ ] **Política de exclusão:** Definir processos para remoção ou anonimização de dados mediante solicitação de usuários ou fim de uso.

## 6. Governança de Modelos

- [ ] **Registro de modelos (MLflow):** Todos os modelos devem ser registrados no MLflow com metadados (versão do dataset, seed, métricas, data). Utilizar ambientes de *staging* e *production* com aprovação humana para promover modelos.
- [ ] **Gates de aprovação:** Implementar etapas de revisão que verifiquem viés, robustness e conformidade com políticas antes de promover um modelo para produção. Esses gates podem incluir testes de fairness e de desempenho em dados adversariais.
- [ ] **CI/CD de modelos:** Configurar pipelines de CI para treinar modelos automaticamente, executar testes unitários (verificar forma da saída e distribuição de classes) e análises de segurança. Somente após a aprovação é realizado o deploy.
- [ ] **Monitoramento em produção:** Medir drift de dados, qualidade de previsões e performance dos modelos. Definir alertas para limiares de degradação e políticas de rollback.

## 7. Avaliações Periódicas

- [ ] **Revisões de conformidade:** Realizar auditorias internas trimestrais para avaliar aderência às políticas de segurança e governança. Atualizar checklist conforme surgem novas ameaças ou requisitos.
- [ ] **Treinamento de equipe:** Promover sessões regulares de capacitação em segurança, privacidade e respostas a incidentes para todas as equipes envolvidas (SRE, ML, segurança, produto, comunicação).

Esta checklist deve ser adaptada ao contexto específico da organização e usada em conjunto com os playbooks de incidentes para fortalecer a postura de segurança e governança do laboratório.