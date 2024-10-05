########################################
# Configure AWS Provider
########################################
provider "aws" {
  region  = "us-east-1"
  profile = "default"
}

########################################
# Retrieve List of AZs
########################################
data "aws_availability_zones" "available" {}

########################################
# Create VPC 
########################################
resource "aws_vpc" "vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "${var.environment_name} VPC"
  }
}

########################################
# Create Internet Gateway
########################################
resource "aws_internet_gateway" "internet_gateway" {
  vpc_id = aws_vpc.vpc.id
  tags = {
    Name = "${var.environment_name} Internet Gateway"
  }
}

########################################
# Create Subnet
########################################
resource "aws_subnet" "subnet" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = "10.0.10.0/24"
  availability_zone       = tolist(data.aws_availability_zones.available.names)["0"]
  map_public_ip_on_launch = true
  tags = {
    Name = "${var.environment_name} Subnet Public"
  }
}

########################################
# Create Route Table
########################################
resource "aws_route_table" "route_table" {
  vpc_id = aws_vpc.vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.internet_gateway.id
  }
  tags = {
    Name = "${var.environment_name} Subnet Public Route Table"
  }
}

########################################
# Create Route Table Association
########################################
resource "aws_route_table_association" "route_table_association" {
  route_table_id = aws_route_table.route_table.id
  subnet_id      = aws_subnet.subnet.id
}

########################################
# Create Security Group
########################################
resource "aws_security_group" "security_group" {
  name        = "Security Group Public"
  description = "Security group for public access servers"
  vpc_id      = aws_vpc.vpc.id
  tags = {
    Name = "${var.environment_name} Security Group Public"
  }
}

########################################
# Create Security Group Rules
########################################
resource "aws_vpc_security_group_ingress_rule" "security_group_ingress_rule" {
  security_group_id = aws_security_group.security_group.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = "22"
  to_port           = "22"
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "security_group_egress_rule" {
  security_group_id = aws_security_group.security_group.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = "137"
  to_port           = "139"
  ip_protocol       = "tcp"
}

########################################
# Create Network ACL
########################################
resource "aws_network_acl" "network_acl" {
  vpc_id     = aws_vpc.vpc.id
  subnet_ids = [aws_subnet.subnet.id]
  tags = {
    Name = "${var.environment_name} NACL Subnet Public"
  }
}

########################################
# Create Network ACL Rule
########################################
resource "aws_network_acl_rule" "network_acl_rule_inbound_100" {
  network_acl_id = aws_network_acl.network_acl.id
  rule_number    = "100"
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 22
  to_port        = 22
}

resource "aws_network_acl_rule" "network_acl_rule_outbound_100" {
  network_acl_id = aws_network_acl.network_acl.id
  rule_number    = "100"
  egress         = true
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 22
  to_port        = 22
}

########################################
# Retrieve Instance Data
########################################
data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

########################################
# Create Instance
########################################
resource "aws_instance" "instance" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"
  # key_name = ""
  vpc_security_group_ids = [aws_security_group.security_group.id]
  subnet_id              = aws_subnet.subnet.id
  tags = {
    Name = "${var.environment_name} SSH Instance"
  }
}
