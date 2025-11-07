# -------------------------
# Infraestrutura AWS para o Helius Sim Lab
#
# Este arquivo define os recursos essenciais para a operação da simulação
# em um ambiente de produção ou de testes na AWS.  Inclui a criação
# de uma VPC, cluster EKS, registros de container (ECR), buckets S3,
# banco de dados RDS, papéis IAM e integração básica com CloudWatch.
#
# Para simplificar, utilizamos módulos comunitários do Terraform
# (terraform-aws-modules) para VPC e EKS.  Outros recursos são
# declarados diretamente.

# ------------------------------------------------------------------
# Criação da VPC e sub-redes
# Utiliza módulo oficial terraform-aws-modules/vpc/aws.
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-vpc"
  cidr = var.vpc_cidr

  azs             = slice(data.aws_availability_zones.available.names, 0, length(var.public_subnets))
  public_subnets  = var.public_subnets
  private_subnets = var.private_subnets

  enable_nat_gateway = true
  single_nat_gateway = true

  tags = var.tags
}

# Data source para listar zonas de disponibilidade
data "aws_availability_zones" "available" {
  state = "available"
}

# ------------------------------------------------------------------
# Cluster EKS
#
# Provisiona o control-plane do Kubernetes e grupos de nós gerenciados.
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version
  subnet_ids      = concat(module.vpc.public_subnets, module.vpc.private_subnets)
  vpc_id          = module.vpc.vpc_id

  # Logging do cluster para CloudWatch
  enable_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  # Grupos de nós padrão
  eks_managed_node_groups = {
    default = {
      instance_types = [var.node_instance_type]
      min_size       = var.node_min_size
      desired_size   = var.node_desired_size
      max_size       = var.node_max_size
      subnets        = module.vpc.private_subnets
      labels = {
        role = "core"
      }
    }
    edge = {
      instance_types = ["t3.small"]
      min_size       = 1
      desired_size   = 1
      max_size       = 2
      subnets        = module.vpc.public_subnets
      labels = {
        role = "edge"
      }
    }
    # Grupo opcional de GPU
    gpu = var.enable_gpu_nodes ? {
      instance_types = ["g5.xlarge"]
      min_size       = 0
      desired_size   = 0
      max_size       = 1
      subnets        = module.vpc.private_subnets
      labels = {
        role = "gpu"
      }
      taints = [
        {
          key    = "gpu"
          value  = "true"
          effect = "NoSchedule"
        }
      ]
    } : null
  }

  tags = var.tags
}

# ------------------------------------------------------------------
# Repositório de Containers (ECR)
resource "aws_ecr_repository" "services" {
  name                 = "${var.project_name}-services"
  image_tag_mutability = "MUTABLE"
  tags                 = var.tags
}

# ------------------------------------------------------------------
# Buckets S3
#
# Três buckets: dados brutos, dados processados e artefatos do MLflow.
resource "aws_s3_bucket" "raw_data" {
  bucket = var.s3_raw_bucket_name
  acl    = "private"
  force_destroy = true
  tags  = var.tags
}

resource "aws_s3_bucket" "processed_data" {
  bucket = var.s3_processed_bucket_name
  acl    = "private"
  force_destroy = true
  tags  = var.tags
}

resource "aws_s3_bucket" "mlflow_artifacts" {
  bucket = var.s3_mlflow_bucket_name
  acl    = "private"
  force_destroy = true
  tags  = merge(var.tags, { Purpose = "mlflow" })
}

# Ativa versionamento nos buckets para rastrear mudanças
resource "aws_s3_bucket_versioning" "versioning" {
  for_each = {
    raw       = aws_s3_bucket.raw_data.id
    processed = aws_s3_bucket.processed_data.id
    mlflow    = aws_s3_bucket.mlflow_artifacts.id
  }
  bucket = each.value
  versioning_configuration {
    status = "Enabled"
  }
}

# ------------------------------------------------------------------
# Banco de dados RDS Postgres
#
# Um banco simples para armazenar metadados e servir como backend do MLflow.
resource "aws_db_subnet_group" "rds" {
  name       = "${var.project_name}-rds-subnet-group"
  subnet_ids = module.vpc.private_subnets
  tags       = var.tags
}

resource "aws_db_instance" "postgres" {
  identifier              = "${var.project_name}-rds"
  engine                  = "postgres"
  engine_version          = "15.2"
  instance_class          = var.rds_instance_class
  db_name                 = var.rds_db_name
  username                = var.rds_username
  password                = var.rds_password
  allocated_storage       = 20
  max_allocated_storage   = 100
  storage_encrypted       = true
  kms_key_id              = aws_kms_key.rds_key.id
  publicly_accessible     = false
  vpc_security_group_ids  = [aws_security_group.rds.id]
  db_subnet_group_name    = aws_db_subnet_group.rds.name
  skip_final_snapshot     = true
  deletion_protection     = false
  tags                    = var.tags
}

# ------------------------------------------------------------------
# Segurança e IAM
#
# Cria papéis utilizados pelo EKS e permissões básicas para o RDS.
module "iam_roles" {
  source  = "terraform-aws-modules/iam/aws"
  version = "~> 5.0"
  roles   = {
    eks = {
      name = "${var.project_name}-eks-role"
      assume_role_policy = data.aws_iam_policy_document.eks_assume_role.json
      managed_policy_arns = [
        "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy",
        "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
        "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
      ]
    }
  }
}

data "aws_iam_policy_document" "eks_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["eks.amazonaws.com"]
    }
  }
}

# Grupo de segurança para RDS
resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Permite acesso ao banco de dados apenas do cluster EKS"
  vpc_id      = module.vpc.vpc_id
  ingress {
    description = "Postgres"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    security_groups = [module.eks.cluster_security_group_id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = var.tags
}

# ------------------------------------------------------------------
# KMS para criptografia de dados
resource "aws_kms_key" "rds_key" {
  description             = "Chave KMS para encriptar instâncias RDS"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  tags                    = var.tags
}

# ------------------------------------------------------------------
# Variável outputs
output "eks_cluster_endpoint" {
  description = "URL do endpoint do cluster Kubernetes"
  value       = module.eks.cluster_endpoint
}

output "eks_cluster_name" {
  description = "Nome do cluster Kubernetes"
  value       = module.eks.cluster_name
}

output "ecr_repository_url" {
  description = "URL do repositório ECR para imagens de serviços"
  value       = aws_ecr_repository.services.repository_url
}

output "s3_buckets" {
  description = "Nomes dos buckets S3 criados"
  value = {
    raw_data       = aws_s3_bucket.raw_data.id
    processed_data = aws_s3_bucket.processed_data.id
    mlflow         = aws_s3_bucket.mlflow_artifacts.id
  }
}

output "rds_endpoint" {
  description = "Endpoint do RDS Postgres"
  value       = aws_db_instance.postgres.endpoint
}

output "iam_role_arn" {
  description = "ARN do papel IAM criado para o cluster EKS"
  value       = module.iam_roles.roles["eks"].arn
}