
provider "aws" {
region  = "ap-south-1"
#profile = "730335384723_Devops_POC"
assume_role {
    session_name = "terraform"
    role_arn = "arn:aws:iam::730335384723:role/admin-role"
  }
}
