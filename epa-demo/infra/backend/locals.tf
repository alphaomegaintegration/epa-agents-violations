data "aws_eks_cluster_auth" "this" {
  name = local.cluster_name
}

data "aws_eks_cluster" "this" {
  name = local.cluster_name
}

locals {
  region                    = "us-east-1"
  cluster_name              = data.terraform_remote_state.base_state.outputs.cluster_name
  cluster_endpoint          = data.aws_eks_cluster.this.endpoint
  cluster_token             = data.terraform_remote_state.tools_state.outputs.jenkins_sa_token
  cluster_ca_certificate    = base64decode(data.aws_eks_cluster.this.certificate_authority[0].data)

  tags = {
    Terraform   = "true"
    Environment = "${var.name}"
  }

  eks_oidc_provider_arn = data.terraform_remote_state.eks_state.outputs.oidc_provider_arn
}