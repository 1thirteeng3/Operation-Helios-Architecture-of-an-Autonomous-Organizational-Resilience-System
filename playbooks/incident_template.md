# Template de Incidente

Use este template para documentar detalhes de um incidente durante ou após sua ocorrência. Complete cada seção com informações específicas do evento.

## Descrição

Uma breve descrição do incidente. Inclua o contexto, os sistemas afetados e o momento de início detectado.

## Linha do tempo

| Horário | Evento |
|--------|--------|
| `HH:MM` | Detecção inicial / alerta acionado |
| `HH:MM` | Primeiras ações de investigação |
| `HH:MM` | Passos de mitigação executados |
| `HH:MM` | Recuperação concluída |

## Impacto

- **Serviços impactados:** (por exemplo, `recommendation`, `ingestion`)
- **Clientes/usuários afetados:** (número ou porcentagem)
- **SLA/latência:** (descrição de violações de SLA ou degradação)
- **Reputação e custo:** (quaisquer danos reputacionais ou custos estimados)

## Causa raiz

Descreva a causa técnica primária que levou ao incidente. Inclua fatores contribuintes como falhas em procedimentos, lacunas de monitoramento ou eventos externos.

## Passos de remediação

1. **Mitigação imediata:** Ações emergenciais para restaurar o serviço (rollback, reiniciar serviços, redirecionar tráfego).
2. **Correção permanente:** Ajustes no código, infraestrutura ou processos para eliminar a vulnerabilidade.
3. **Validação:** Testes para garantir que a correção funciona e não introduz novos problemas.
4. **Monitoramento:** Atualização de alertas e dashboards para detectar recorrência.