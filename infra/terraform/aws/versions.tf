terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

# Provedor AWS principal.  O perfil e região podem ser configurados via
# variáveis ou arquivo de credenciais (~/.aws/credentials).
provider "aws" {
  region = var.region
}

########################################
# Observação
#
# Este módulo assume que você possui credenciais AWS configuradas no
# ambiente em que o Terraform é executado.  Utilize o comando
# `aws configure` ou defina variáveis de ambiente (AWS_ACCESS_KEY_ID,
# AWS_SECRET_ACCESS_KEY) antes de executar `terraform init` e
# `terraform apply`.
########################################