aws_region  = "us-east-1"
project     = "portfolio-secnet"
environment = "dev"

# Choose 2 AZs available in your region
azs = ["us-east-1a", "us-east-1b"]

cidrs = {
  dev     = "10.10.0.0/20"
  prod    = "10.20.0.0/20"
  shared  = "10.30.0.0/20"
  inspect = "10.40.0.0/20"
}

tags = {
  Owner   = "Jamie-Christian-II"
  Purpose = "AWS-Security-Networking-Portfolio"
}
