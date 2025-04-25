terraform {
  required_version = ">= 1.0"
 
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.33.0, < 6.0"
    }
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = "1.14.0"
    }
  }
}
