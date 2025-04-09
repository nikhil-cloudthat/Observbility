output "eks_cluster_name" {
  description = "name of the created EKS cluster"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "The endpoint of the created EKS Cluster"
  value       = module.eks.cluster_endpoint
}

output "eks_oidc_id" {
  description = "oidc provider id"
  value       = regex("oidc\\.eks\\..*\\/id/(.*)", module.eks.oidc_provider_arn)[0]
}

output "oidc_provider_arn" {
  description = "oidc provider arn"
  value       = module.eks.oidc_provider_arn
}

# output "eks_cluster_certificate_authority_data"{
#   description = "certificate_authority_data"
#   value = module.eks.cluster_certificate_authority_data
# }

# output "eks_cluster_certificate_authority_data" { value = module.eks.certificate_authority.data }