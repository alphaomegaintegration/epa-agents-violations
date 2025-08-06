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

  challenge_domain      = data.terraform_remote_state.base_state.outputs.challenge_domain
  environment_certificate_arns = {
    dev  = data.terraform_remote_state.eks_addons.outputs.dev_cert_arn
    stg  = data.terraform_remote_state.eks_addons.outputs.stg_cert_arn
    prod = data.terraform_remote_state.eks_addons.outputs.prod_cert_arn
  }
  certificate_arn = lookup(local.environment_certificate_arns, var.environment)
}