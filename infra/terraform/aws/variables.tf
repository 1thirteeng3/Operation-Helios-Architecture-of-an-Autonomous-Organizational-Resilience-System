# Variáveis de configuração para a infraestrutura AWS

variable "project_name" {
  description = "Nome do projeto ou prefixo para recursos"
  type        = string
  default     = "helius-sim"
}

variable "region" {
  description = "Região AWS em que os recursos serão criados"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR do VPC principal"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  description = "Lista de blocos CIDR para sub-redes públicas"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "private_subnets" {
  description = "Lista de blocos CIDR para sub-redes privadas"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "cluster_name" {
  description = "Nome do cluster Kubernetes (EKS)"
  type        = string
  default     = "helius-cluster"
}

variable "cluster_version" {
  description = "Versão do Kubernetes a ser usada no EKS"
  type        = string
  default     = "1.27"
}

variable "node_instance_type" {
  description = "Tipo de instância EC2 para os nós padrão"
  type        = string
  default     = "t3.medium"
}

variable "node_min_size" {
  description = "Número mínimo de nós no grupo de auto-scaling do EKS"
  type        = number
  default     = 2
}

variable "node_desired_size" {
  description = "Número desejado de nós no grupo de auto-scaling do EKS"
  type        = number
  default     = 3
}

variable "node_max_size" {
  description = "Número máximo de nós no grupo de auto-scaling do EKS"
  type        = number
  default     = 4
}

variable "s3_raw_bucket_name" {
  description = "Nome do bucket S3 para dados brutos"
  type        = string
  default     = "helius-raw-data"
}

variable "s3_processed_bucket_name" {
  description = "Nome do bucket S3 para dados processados"
  type        = string
  default     = "helius-processed-data"
}

variable "s3_mlflow_bucket_name" {
  description = "Nome do bucket S3 para armazenamento de artefatos do MLflow"
  type        = string
  default     = "helius-mlflow-artifacts"
}

variable "rds_db_name" {
  description = "Nome da base de dados para o RDS/Postgres"
  type        = string
  default     = "helius"
}

variable "rds_username" {
  description = "Usuário admin para o RDS/Postgres"
  type        = string
  default     = "helius_admin"
}

variable "rds_password" {
  description = "Senha para o usuário do RDS/Postgres"
  type        = string
  sensitive   = true
}

variable "rds_instance_class" {
  description = "Classe da instância RDS"
  type        = string
  default     = "db.t3.micro"
}

variable "enable_gpu_nodes" {
  description = "Define se grupos de nós GPU serão provisionados"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Mapa de tags para adicionar a todos os recursos"
  type        = map(string)
  default     = {
    Environment = "dev"
    Project     = "helius-sim"
  }
}