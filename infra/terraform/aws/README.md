# Infraestrutura AWS com Terraform

Este diretório contém definições do Terraform para provisionar a
infraestrutura necessária à simulação da Helius na AWS.  A abordagem
adota módulos comunitários (``terraform-aws-modules``) para criar de forma
rápida uma VPC e um cluster EKS, além de recursos adicionais como
repositórios ECR, buckets S3, banco de dados RDS Postgres, chaves KMS
e papéis IAM.  Os arquivos principais são:

- **versions.tf** – define a versão mínima do Terraform e as versões
  necessárias dos providers ``aws`` e ``kubernetes``.
- **variables.tf** – lista as variáveis de entrada que controlam nomes,
  tamanhos, regiões e outros parâmetros da infraestrutura.
- **main.tf** – descreve a criação da VPC, cluster EKS, grupos de nós
  (incluindo grupos ``edge`` e opcionais ``gpu``), repositório ECR,
  buckets S3 para dados e artefatos, RDS/Postgres, KMS e IAM.
- **outputs.tf** – exporta valores úteis (endpoint do cluster, URLs de
  repositórios, nomes de buckets, etc.) após o ``terraform apply``.

## Pré‑requisitos

1. **Terraform 1.0+** instalado em sua máquina local ou pipeline.
2. **AWS CLI** configurado com credenciais que possuam permissões para
   criar VPCs, EKS, IAM, RDS e S3. Utilize ``aws configure`` ou
   variáveis de ambiente.
3. Um **backend remoto** opcional (por exemplo, S3 + DynamoDB) para
   armazenar o estado do Terraform. Por padrão, o estado é salvo localmente.

## Uso

Execute os comandos a seguir na pasta ``infra/terraform/aws``:

```bash
terraform init        # baixa os providers e módulos necessários
terraform plan        # mostra a lista de recursos que serão criados
terraform apply       # aplica as mudanças (responder 'yes' quando solicitado)
```

Você pode ajustar variáveis passando ``-var key=value`` ou criando um
arquivo ``terraform.tfvars``.  Por exemplo, para definir uma senha do
RDS e habilitar nós GPU:

```bash
cat > terraform.tfvars <<EOF
rds_password = "S3nh4Seguro!"
enable_gpu_nodes = true
EOF
terraform apply
```

Após a aplicação, os outputs exibem o endpoint do cluster EKS, os nomes
dos buckets S3 e o endpoint do banco de dados.  Esses valores podem
ser utilizados na configuração de pipelines (CI/CD), scripts de
deploy e nos serviços do laboratório.

## Próximos passos

- Criar **pipelines de CI/CD** (GitHub Actions) que executem ``terraform
  plan`` e ``terraform apply`` em ambientes controlados.
- Configurar **perfis de IAM** e políticas mais granularizadas para
  serviços específicos (por exemplo, pods do Kubernetes usando IAM
  Roles for Service Accounts – IRSA).
- Implementar **segredos** via AWS Secrets Manager ou HashiCorp Vault
  para armazenar senhas e chaves de API sem hard‑coding.
- Integrar **CloudWatch Logs** e **CloudWatch Alarms** para monitorar o
  estado do cluster e instâncias.