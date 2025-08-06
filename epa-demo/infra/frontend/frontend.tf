resource "aws_ecr_repository" "app_repos" {
  name                 = "${var.name}-${var.environment}-frontend"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags         = local.tags
  force_delete = true
}

resource "kubectl_manifest" "frontend" {
  yaml_body =<<YAML
  apiVersion: argoproj.io/v1alpha1
  kind: Application
  metadata:
    name: "epa-frontend-${var.environment}"
    namespace: argocd
    labels:
      name: "epa-frontend-${var.environment}"
    annotations:
      argocd-image-updater.argoproj.io/image-list: ecr-frontend=${var.aws_account_id}.dkr.ecr.us-east-1.amazonaws.com/${var.name}-${var.environment}-frontend:latest
      argocd-image-updater.argoproj.io/ecr-frontend.update-strategy: digest
  spec:
    project: default
    # Source of the application manifests
    source:
      repoURL: ${var.git_url_project}
      targetRevision: ${var.environment == "prod" ? "main" : var.environment}
      path: epa-demo/infra/frontend/chart
      helm:
        values: |
          replicaCount: 2
          image:
            repository: ${var.aws_account_id}.dkr.ecr.us-east-1.amazonaws.com/${var.name}-${var.environment}-frontend
            tag: latest
            pullPolicy: Always
          service:
            type: ClusterIP
            port: 80
          env:
            REACT_APP_API_BASE: "https://epa-api.${var.environment}.${local.challenge_domain}"
            REACT_APP_WS_URL: "wss://epa-api.${var.environment}.${local.challenge_domain}/ws"
          ingress:
            enabled: true
            className: alb
            annotations:
              alb.ingress.kubernetes.io/backend-protocol: HTTP
              alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}]'
              alb.ingress.kubernetes.io/scheme: internet-facing
              alb.ingress.kubernetes.io/target-type: ip
              alb.ingress.kubernetes.io/group.name: ${var.environment}
              kubernetes.io/ingress.class: alb
              alb.ingress.kubernetes.io/certificate-arn: ${local.certificate_arn}
              cert-manager.io/cluster-issuer: ${var.cluster_issuer_name}
            hosts:
              - host: "epa.${var.environment}.${local.challenge_domain}"
                paths:
                  - path: /
                    pathType: Prefix
            tls:
              - hosts:
                  - "epa.${var.environment}.${local.challenge_domain}"
                secretName: "epa-tls-secret"
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "200m"
        # Release name override (defaults to application name)
        releaseName: epa-frontend

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