locals {
  environment_name = "Dev"
  region = "ap-south-1"
  vpc_id = "vpc-05a2ee1bd60533eed"
  vpc_cidr = "182.0.0.0/16"

  karpenter_tag_key = "karpenter.sh/discovery"


  
  eks_controlplane_subnet_az1 = "subnet-0e85a3ca66897090c"
  eks_controlplane_subnet_az2 = "subnet-04de36b3c9d931aaf"

  project_name = "Obs"

  }
