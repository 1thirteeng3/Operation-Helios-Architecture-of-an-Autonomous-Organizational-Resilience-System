# Runbook de Responders

Este runbook define os papéis e responsabilidades de cada membro durante um incidente. O objetivo é garantir clareza de funções, comunicação eficiente e resolução ágil.

## SRE (Site Reliability Engineer)

- **Monitoramento e detecção:** Configurar e manter sistemas de observabilidade; confirmar alertas e determinar severidade.
- **Infraestrutura:** Diagnosticar e corrigir problemas de redes, clusters Kubernetes, instâncias de cloud e pipelines CI/CD.
- **Escalonamento:** Coordenar com DevOps ou engenharia de plataforma para prover recursos adicionais e ajustar autoscaling.

## Engenheiro(a) de ML

- **Modelos e dados:** Verificar integridade de datasets, pipelines de feature engineering e inferência; identificar drift ou corrupção de modelos.
- **Treinamento e rollback:** Acionar re‑treinamento rápido ou realizar rollback para versão estável via MLflow.
- **Performance:** Ajustar hiperparâmetros ou arquitetura de modelos em resposta a incidentes de latência ou qualidade.

## Segurança (Security Engineer)

- **Detecção de ameaças:** Identificar inputs maliciosos (prompt injection, poisoning) e coordenar com times de resposta a incidentes.
- **Resposta a vulnerabilidades:** Avaliar e remediar pacotes com CVEs, hardening de contêineres, IAM e segredos.
- **Auditoria:** Garantir que logs e trilhas de auditoria estejam disponíveis para investigação forense.

## Product Owner / Gestor(a)

- **Prioridades de negócios:** Avaliar impacto do incidente nas metas de negócio e definir se é necessário acionar planos de contingência.
- **Comunicação interna:** Manter stakeholders informados sobre progresso, riscos e decisões; alinhar expectativas de clientes e parceiros.
- **Aprovação de mudanças:** Tomar decisões sobre rollout de correções e feature flags em produção.

## Comunicação / Relações Públicas

- **Mensagem externa:** Elaborar e divulgar comunicados para clientes e imprensa quando relevante; manter transparência e consistência.
- **Coordenação interna:** Trabalhar com SRE e Product Owner para entender o impacto técnico e traduzi-lo para linguagem não técnica.
- **Gestão de reputação:** Monitorar reações externas e ajustar mensagens conforme necessário.