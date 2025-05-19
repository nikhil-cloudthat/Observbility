locals {
  environment_name = "Dev"
  region = "ap-south-1"
  vpc_id = "vpc-06a75748eff1098c6"
  vpc_cidr = "10.0.0.0/16"

  karpenter_tag_key = "karpenter.sh/discovery"


  
  eks_controlplane_subnet_az1 = "subnet-0b09c1c0d536b65ec"
  eks_controlplane_subnet_az2 = "subnet-0ac235439140055cc"

  project_name = "OCO"
  }
