resource "aws_ecr_repository" "app_repo" {
  name                 = "${var.name}-${var.environment}-backend"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags         = local.tags
  force_delete = true
}





module "backend_irsa" {
  source   = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"

  role_name = "${var.name}-backend-irsa-${var.environment}"

  role_policy_arns = {}

  oidc_providers = {
    main = {
      provider_arn               = local.eks_oidc_provider_arn
      namespace_service_accounts = ["${var.environment}:epa-backend"]
    }
  }
}

resource "kubectl_manifest" "app-backend" {
  yaml_body =<<YAML
  apiVersion: argoproj.io/v1alpha1
  kind: Application
  metadata:
    name: "epa-backend-${var.environment}"
    namespace: argocd
    labels:
      name: "epa-backend-${var.environment}"
    annotations:
      argocd-image-updater.argoproj.io/image-list: ecr-backend=${var.aws_account_id}.dkr.ecr.us-east-1.amazonaws.com/${var.name}-${var.environment}-backend:latest
      argocd-image-updater.argoproj.io/ecr-backend.update-strategy: digest
  spec:
    project: default
    # Source of the application manifests
    source:
      repoURL: ${var.git_url_project}
      targetRevision: ${var.environment == "prod" ? "main" : var.environment}
      path: epa-demo/infra/backend/chart
      helm:
        values: |
          replicaCount: 2
          aws_iam_role_arn: ${module.backend_irsa.iam_role_arn}
          image:
            repository: ${var.aws_account_id}.dkr.ecr.${var.region}.amazonaws.com/${var.name}-${var.environment}-backend
            tag: latest
            pullPolicy: Always
          service:
            type: ClusterIP
            port: 8000
          secrets:
            anthropicApiKey: "${var.anthropic_api_key}"
            serpApiKey: "${var.serp_api_key}"
          env:
            LOG_LEVEL: "INFO"
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
        # Release name override (defaults to application name)
        releaseName: epa-backend
    # Destination cluster and namespace to deploy the application
    destination:
      server: https://kubernetes.default.svc
      namespace: ${var.environment}

    # Sync policy
    syncPolicy:
      automated:
        prune: true
        selfHeal: true
        allowEmpty: false
      syncOptions:
      - Validate=false
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
      retry:
        limit: 5
        backoff:
          duration: 5s
          factor: 2
          maxDuration: 3m
    revisionHistoryLimit: 5
  YAML
}