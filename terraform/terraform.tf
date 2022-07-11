terraform {
  backend "s3" {
    bucket = "yawna-terraform-state"
    key    = "flagrantBackend/terraform.tfstate"
    region = "us-east-2"
  }
}
