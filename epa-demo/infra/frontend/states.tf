data "terraform_remote_state" "base_state" {
  backend = "s3"
  config = {
    bucket = var.state_bucket
    key    = "us-east-1/1-core/terraform.tfstate"
    region = "us-east-1"
  }
}

data "terraform_remote_state" "eks_addons" {
  backend = "s3"
  config = {
    bucket = var.state_bucket
    key    = "us-east-1/3-eks-addons/terraform.tfstate"
    region = "us-east-1"
  }
}

data "terraform_remote_state" "tools_state" {
  backend = "s3"
  config = {
    bucket = var.state_bucket
    key    = "us-east-1/4-tools/terraform.tfstate"
    region = "us-east-1"
  }
}
