terraform {
  source = "../../../modules//helm"
}

include "root" {
  path = find_in_parent_folders()
}

include "env"{
  path = find_in_parent_folders("env.hcl")
  expose         = true
  merge_strategy = "no_merge"
}

include "account"{
  path = find_in_parent_folders("account.hcl")
  expose         = true
  merge_strategy = "no_merge"
}

dependency "eks" {
  config_path = "../eks"
  mock_outputs = {eks_cluster_name = "eks_cluster_name", eks_cluster_certificate_authority_data = "eks_cluster_certificate_authority_data", eks_cluster_endpoint = "eks_cluster_endpoint" }
}


locals {
  # Given that your terragrunt.hcl is in Repository/Terraform/resources/prod,
  # go 3 levels up to reach the repository root.
  repo_root = abspath("${get_terragrunt_dir()}/../../../../")
}

inputs = {
  repo_root = local.repo_root
  release_name = "obs"
  namespace = "default"

  cluster_name                         = "eks"
  environment  = include.env.locals.environment_name
  project_name = include.env.locals.project_name  

}

