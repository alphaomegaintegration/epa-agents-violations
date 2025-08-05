data "terraform_remote_state" "eks_state" {
  backend = "s3"
  config = {
    bucket = var.state_bucket
    key    = "${var.region}/2-eks/terraform.tfstate"
    region = var.region
  }
}

data "terraform_remote_state" "tools_state" {
  backend = "s3"
  config = {
    bucket = var.state_bucket
    key    = "${var.region}/4-tools/terraform.tfstate"
    region = var.region
  }
}
