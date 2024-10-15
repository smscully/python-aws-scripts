# Terraform AWS Test Environment: Insecure SSH and NetBIOS Configurations
The [main.tf](./main.tf) Terraform script creates the resources for an AWS test environment with insecure SSH and NetBIOS configurations. The resources created by the script can be used to test the Python scripts in [this repository](..), which facilitate finding, deleting, and updating insecure AWS resources.

The architectural diagram below shows the AWS resources created by the script.

![AWS-Test-Env diagram](./img/aws-test-env.png)

Before launching the script, review the resources that will be created, as the EC2 image may incur charges depending on plan type. Please refer to the [Amazon VPC Pricing](https://aws.amazon.com/vpc/pricing/) page for specific regional pricing.  

## Script Overview
The [main.tf](./main.tf) script creates the AWS resources listed below.

+ Virtual Private Cloud
+ Internet Gateway (IGW)
+ Public Subnet
+ Custom Route Table
+ Network Access Control List (NACL)
+ Security Group
+ EC2 Instance (Ubuntu Server)
+ Key Pair for SSH Access

### NACL Configuration
The NACL is configured with the rules below, which allow SSH (port 22) and NetBIOS (ports 137-139) traffic.

|Type|Rule Number|Protocol|Port Range|Source/Destination|Allow/Deny|
|----|-----------|--------|----------|------------------|----------|
|Inbound|100|TCP|22|0.0.0.0/0|Allow|
|Inbound|110|TCP|137-139|0.0.0.0/0|Allow|
|Outbound|100|TCP|1024-65535|0.0.0.0/0|Allow|
|Outbound|110|TCP|137-139|0.0.0.0/0|Allow|

### Security Group Configuration
The Security Group is configured with the rules below, which allow SSH (port 22) ingress traffic and NetBIOS (ports 137-139) egress traffic.

|Type|Protocol|Port Range|Source/Destination|
|----|--------|----------|------------------|
|Inbound|TCP|22|0.0.0.0/0|
|Outbound|TCP|137-139|0.0.0.0/0|

### Key Pair Configuration
To access the EC2 instance, the public key of an SSH key pair must uploaded to AWS and attached to the instance. Although an existing key pair can be used, the usage instructions below provide the steps to create a new Ed25519 key pair with a name and location that matches the path in the Terraform script.

## Getting Started

### Dependencies

+ Terraform (For installation instructions, [click here](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli).)
+ AWS CLI (For installation instructions, [click here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).)
+ Established connection to an AWS account

### Installation
To install the script, either clone the [python-aws-scripts](..) repo or download the files in the [terraform-aws-test-env](.) folder to the local host. 

## Usage

### Create the SSH Key Pair
On standard Linux distributions with OpenSSH installed, the following command will create an SSH key pair of type Ed25519 (-t ed25519) in the given location (-f ~/.ssh/aws-test-env-ed25519) expected by the Terraform script as currently configured. If a different key type or location are used, the script must be updated accordingly.
```bash
sudo ssh-keygen -f ~/.ssh/aws-test-env-ed25519 -t ed25519
```
> **NOTE:** The command above should also work for Windows and macOS implementations of OpenSSH.

### Run the Terraform Script
To run the script, follow standard Terraform practices by navigating to the directory that holds the `main.tf` script, then running the commands to initialize and apply the script:
```bash
terraform init
terraform plan
terraform apply
```
### Access the EC2 Instance via SSH
To access the EC2 instance, enter the command below in the Bash shell. To the find the IP address of the EC2 instance, check the outputs of the Terraform script, or review the instance details in the AWS console.
```bash
sudo ssh -i ~/.ssh/aws-test-env-ed25519 ubuntu@[instance-ip]
```
## License
Licensed under the [GNU General Public License v3.0](./LICENSE).
