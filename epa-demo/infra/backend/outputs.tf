output "ecr_repository_name" {
  description = "The name of the ECR repository for the backend service"
  value       = aws_ecr_repository.app_repo.name
}

output "ecr_repository_url" {
  description = "The URL of the ECR repository for the backend service"
  value       = aws_ecr_repository.app_repo.repository_url
}

output "ecr_repository_arn" {
  description = "The ARN of the ECR repository for the backend service"
  value       = aws_ecr_repository.app_repo.arn
}

output "argocd_application_name" {
  description = "The name of the ArgoCD application for the backend service"
  value       = "backend-${var.environment}"
}

output "argocd_application_namespace" {
  description = "The namespace in which the ArgoCD application is deployed"
  value       = "argocd"
}