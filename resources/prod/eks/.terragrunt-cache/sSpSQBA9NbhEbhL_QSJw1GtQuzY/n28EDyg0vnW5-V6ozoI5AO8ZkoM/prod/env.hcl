locals {
  environment_name = "Dev"
  region = "ap-south-1"
  vpc_id = "vpc-05ffdb18891be1e06"
  vpc_cidr = "172.16.0.0/20"

  karpenter_tag_key = "karpenter.sh/discovery"


  
  eks_controlplane_subnet_az1 = "subnet-0461fd3764a4a82ed"
  eks_controlplane_subnet_az2 = "subnet-0e6f2adc0065af763"

  project_name = "Observability"

  }
