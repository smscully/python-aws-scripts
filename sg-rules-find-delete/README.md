# Find and Delete AWS Security Group Rules
The [sg-rules-find-delete.py](./sg-rules-find-delete.py) script uses the AWS Boto3 Python library to find and delete AWS security group rules that meet user-provided criteria. 

## Description
To support modularization and improve readability, the script is comprised of three general function classifications: 

+ Utility Functions
+ Core Script Function: `backup`
+ Exit and Cleanup Functions

These functions are called in logical fashion by the `main` function, which establishes the run order upon script invocation.

### 1. Error Checking Functions
The `main` function first calls the following utility functions:

|Function|Description|
|--------|-----------|
|check_aws_user_id|Checks the current AWS User ID; exits on failure.|
|check_ip_protocol|Checks if ip_protocol value is tcp or udp; exits on failure.|
|check_port|Checks if port range value is valid; exits on failure.|
|check_cidr_ipv4|Checks if cidr_ipv4 value is a valid IPv4 CIDR address; exits on failure.|

### 2. Core Script Function: `backup`
To find security group rules, [aws-find-sg-rules.py](./aws-find-sg-rules.py) uses search criteria provided by the user, specifically CidrIpv4, FromPort, and ToPort values, and then saves a list of the discovered rules as an S3 object. One of the primary uses for the script is to find insecure security group rules. For example, AWS Best Practices recommend that SSH access to bastion hosts be limited to specific IPv4 addresses. As such, any security group rule that has port 22 open to all IP addresses (0.0.0.0/0) would be considered insecure and could be found using the script.

Finding insecure rules, of course, is only half the battle, so the complimentary script [aws-fix-sg-rules.py](./aws-fix-sg-rules.py) reads the list of insecure rules and updates them according to new rules provided by the user. In the case of the open SSH port described above, this could be changed to limit the IPv4 range to a specific address, as well as assign the SSH traffic to a non-standard ports, since port 22 will be easily found using basic recon scans.

To test [aws-find-sg-rules.py](./aws-find-sg-rules.py) and [aws-fix-sg-rules.py](./aws-fix-sg-rules.py), this repository includes the Terraform script [terraform-aws-test-env](../terraform-aws-test-env), which creates a basic VPC with a security group, Network ACLs, and an EC2 instance.

### 3. Exit and Cleanup Functions

|Exit Code|Description|
|---------|-----------|
|50|AWS User ID required|
|51|Invalid egress value|
|52|Invalid IP address|
|53|Invalid port number|
|54|S3 Bucket error|
|55|S3 Key error|
|56|S3 error writing list of rules|


For the AWS Security Group rule IP Protocol value, valid values are the range of IANA protocol numbers and certain string values. (See [here]( https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_SecurityGroupRule.html).) This script, however, limits the IP Protocols to TCP and UDP, primarily because the error checking required to avoid Boto3 exceptions to the ` modify_security_group_rules` function is beyond the scope of this script. As an example, modifying a rule to accept all protocols would then required that the from_port and to_port values be null, while modifying a rule to accept the ICMPv6 protocol would require the port range to be either not be specified or specified as from=-1 and to=-1. These and other particular cases ???

NOTE: The `finds.json` and `fix.json` files differ in that there is no is_egress parameter in the `fix.json` file. The reason for this is that the egress state of a security group rule cannot be modified using Boto3. The Boto3 `describe_security_group_rules` function(?) supports searching for rules based on the egress state, but the corresponding Boto3 `modify_security_group_rules` does no provide the option to change the egress state.

find_sg_rules
Searches for rules based on find criteria.

The `delete_sg_rules_ingress` and `delete_sg_rules_egress` functions, respectively, delete existing ingress and egress rules that met the find criteria.

## Getting Started

### Dependencies

+ Python: Version 3.8 or higher
+ AWS Boto3 Library: Latest version
+ Established connection to AWS account

For Boto3 installation instructions, visit the AWS [Quickstart page](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html). Following best security practices, this script does not create a Boto3 client connection using hard coded credentials. As such, it is expected that the user has established a connection to AWS, and the script will therefore load credential parameters from the local environmental variables, the AWS config file, or the AWS shared credential file. For instructions, review the Boto3 [Credentials page](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html).

### Installation
To install the script, either clone the [python-aws-scripts](..) repo or download the [sg-rules-find-delete.py](./sg-rules-find-delete.py) file to the local host. 

## Usage
The script requires the following arguments:

|Argument|Description|
|--------|-----------
|is_egress|False for inbound rules, True for outbound|
|ip_protocol|IP protocol|
|from_port|Lower number of port range|
|to_port|Upper number of port range|
|cidr_ipv4|Valid CIDR IPv4 address|

The following example searches for and deletes any security group rules that are 1) ingress rules (False), 2) support TCP traffic (tcp), allow traffic ranging 3) from port 22 (22) and 4) to port 22 (22), and 5) allow all IPv4 addresses (0.0.0.0/0).

```bash
python3 sg-rules-find-delete.py False tcp 22 22 0.0.0.0/0
```

Standard Python Argparse help (-h) is also available.

## License
Licensed under the [GNU General Public License v3.0](../LICENSE).
