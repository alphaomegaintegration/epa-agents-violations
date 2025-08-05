variable "aws_account_id" {
  type = string 
}

variable "region" {
  type = string
  default = "us-east-1"
}

variable "state_bucket" {
  description = "S3 Bucket Name for TF State"
  type        = string
}

variable "cluster_issuer_name" {
  description = "cluster issuer name"
  type        = string
}

variable "environment" {
  description = "Environment"
  type        = string
}

variable "name" {
  description = "Name"
  default     = "mock"
  type        = string
}

variable "git_url_project" {
  description = "Git URL project"
  type        = string
}