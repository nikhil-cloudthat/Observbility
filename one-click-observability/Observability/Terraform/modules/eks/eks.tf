#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

locals {
  cluster_name    = "${var.project_name}-${local.region}-${var.environment}-${var.cluster_name}"
  cluster_version = var.cluster_version
  region          = data.aws_region.current.name
  environment     = var.environment
  azs             = slice(data.aws_availability_zones.available.names, 0, 2)

  tags = {
    service_name = var.service_name
    team_name    = var.team_name
    environment  = var.environment
    launched_by  = var.launched_by
    project_name = var.project_name
  }
}

data "aws_region" "current" {}
data "aws_availability_zones" "available" {}



data "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_name
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  token                  = data.aws_eks_cluster_auth.cluster.token

}

provider "kubectl" {
  apply_retry_count      = 5
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  load_config_file       = false
  token                  = data.aws_eks_cluster_auth.cluster.token

}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    token                  = data.aws_eks_cluster_auth.cluster.token

  }
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws" 
  version = "~> 20.0"

  cluster_name                    = local.cluster_name
  cluster_version                 = local.cluster_version
  cluster_endpoint_private_access = true

  authentication_mode = "API_AND_CONFIG_MAP"

  cluster_enabled_log_types = [ "audit", "api", "authenticator" , "scheduler", "controllerManager"]

  cluster_addons = {
    coredns                = {
      most_recent = true
    }
    kube-proxy             = {
      most_recent = true
    }
    vpc-cni                = {
      most_recent = true
    }
    aws-ebs-csi-driver     = {
      most_recent = true
    }
  }

  enable_cluster_creator_admin_permissions = true

  cluster_security_group_additional_rules = {
    egress_nodes_ephemeral_ports_tcp = {
      description = "ingress from shared services" 
      protocol    = "-1"
      from_port   = 0
      to_port     = 0
      type        = "ingress"
      cidr_blocks = ["182.0.0.0/16"]      
    }
  }

  node_security_group_tags = merge(local.tags, {
    "karpenter.sh/discovery" = local.cluster_name
  })


  vpc_id = var.vpc_id

  subnet_ids               = var.subnet_ids
  control_plane_subnet_ids = var.control_plane_subnet_ids
  eks_managed_node_groups  = var.eks_managed_node_groups

  tags = local.tags
}

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#locals {
  # Given that your terragrunt.hcl is in Repository/Terraform/resources/prod,
  # go 3 levels up to reach the repository root.
#  repo_root = abspath("${get_terragrunt_dir()}/../../..")
#}

#inputs = {
#  repo_root = local.repo_root
#}



#resource "helm_release" "obs" {
#  name      = var.release_name
#  chart     = "${var.repo_root}/helm-chart"
#  namespace = var.namespace

  # Replicate the -f flags from your helm command. Use the repo_root variable.
#  values = [
#    file("${var.repo_root}/helm-chart/prometheus.yaml"),
#    file("${var.repo_root}/helm-chart/alertmanager_values.yaml"),
#    file("${var.repo_root}/helm-chart/alloy_values.yaml"),
#    file("${var.repo_root}/helm-chart/fluentbit_values.yaml"),
#    file("${var.repo_root}/helm-chart/grafana_values.yaml"),
#    file("${var.repo_root}/helm-chart/kubescape_values.yaml"),
#    file("${var.repo_root}/helm-chart/loki-distributed.yaml"),
#    file("${var.repo_root}/helm-chart/tempo_values.yaml"),
#    file("${var.repo_root}/helm-chart/promethus-msteams_values.yaml")
#  ]

#  dependency_update = true
#}



#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#resource "null_resource" "helmfile_apply" {
#  provisioner "local-exec" {
#    command = <<EOT
#      helmfile init
#      helmfile apply -f ${path.module}/../../../helmfile/helmfile.yaml sync
#    EOT
#  }

#  depends_on = [module.eks]  # Ensure the EKS cluster is ready
#}
