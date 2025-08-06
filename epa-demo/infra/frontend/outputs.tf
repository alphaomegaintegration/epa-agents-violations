output "ecr_repository_name" {
  description = "The name of the ECR repository for the frontend service"
  value       = aws_ecr_repository.app_repos.name
}

output "ecr_repository_url" {
  description = "The URL of the ECR repository for the frontend service"
  value       = aws_ecr_repository.app_repos.repository_url
}

output "ecr_repository_arn" {
  description = "The ARN of the ECR repository for the frontend service"
  value       = aws_ecr_repository.app_repos.arn
}

output "argocd_application_name" {
  description = "The name of the ArgoCD application for the frontend"
  value       = "epa-frontend-${var.environment}"
}

output "ingress_host" {
  description = "The hostname for the ingress of the frontend application"
  value       = "epa.${var.environment}.${local.challenge_domain}"
}
