
provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

provider "helm" {
  kubernetes {
    host                   = data.aws_eks_cluster.cluster.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
    token                  = data.aws_eks_cluster_auth.cluster.token
  }
}

data "aws_region" "current" {}

locals{
  cluster_name    = "${var.project_name}-${local.region}-${var.environment}-${var.cluster_name}"
  region          = data.aws_region.current.name
  environment     = var.environment
  project_name = var.project_name
}

data "aws_eks_cluster" "cluster" {
  name = local.cluster_name
}

data "aws_eks_cluster_auth" "cluster" {
  name = local.cluster_name
}

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

resource "null_resource" "deploy_demo" {
  provisioner "local-exec" {
    command = "kubectl apply -f ${var.repo_root}/Demo/newapp.yaml"
  }

  # Ensures the deployment only runs after your EKS cluster is ready.
  #depends_on = [module.eks]
}

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


resource "helm_release" "obs" {
  name      = var.release_name
  chart     = "${var.repo_root}/helm-chart"
  namespace = var.namespace

  # Replicate the -f flags from your helm command. Use the repo_root variable.
  values = [
    file("${var.repo_root}/helm-chart/prometheus.yaml"),
    file("${var.repo_root}/helm-chart/alertmanager_values.yaml"),
    file("${var.repo_root}/helm-chart/alloy_values.yaml"),
    file("${var.repo_root}/helm-chart/fluentbit_values.yaml"),
    file("${var.repo_root}/helm-chart/grafana_values.yaml"),
    file("${var.repo_root}/helm-chart/kubescape_values.yaml"),
    file("${var.repo_root}/helm-chart/loki-distributed.yaml"),
    file("${var.repo_root}/helm-chart/tempo_values.yaml"),
    file("${var.repo_root}/helm-chart/promethus-msteams_values.yaml")
  ]

  dependency_update = true
}

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#resource "null_resource" "helmfile_apply" {
#  provisioner "local-exec" {
#    command = <<EOT
#      helmfile init
#      helmfile apply -f ${var.repo_root}/helmfile/helmfile.yaml sync
#    EOT
#  }

#  depends_on = [module.eks]  # Ensure the EKS cluster is ready
#}

