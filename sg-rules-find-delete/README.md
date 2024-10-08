# Find and Delete AWS Security Group Rules
The [sg-rules-find-delete.py](./sg-rules-find-delete.py) script uses the AWS Boto3 Python library to find and delete AWS security group rules that meet user-provided criteria. A typical use includes deleting insecure rules, such as those that allow SSH connections from all IPv4 addresses.

To run the script against a test AWS environment, please refer to the [Terraform script](../terraform-aws-test-env) in this repository, which creates a VPC with a subnet, an EC2 instance, insecure security group rules, and insecure Network ACL rules.

## Description
Upon invocation, the `main` function establishes the run order of the script, as follows:

+ Parse Arguments
+ Check AWS User ID and Arguments
+ Call Core Script Functions

### 1. Parse Arguments
The script first parses the following required command line arguments:

|Argument|Description|
|--------|-----------
|is_egress|False for inbound rules, True for outbound|
|ip_protocol|IP protocol|
|from_port|Lower number of port range|
|to_port|Upper number of port range|
|cidr_ipv4|Valid CIDR IPv4 address|

The Python `argparse` module reads the arguments, performs type validation, and stores the values in a dictionary object. Built-in `argparse` help (-h) is also provided.

### 2. Check AWS User ID and Arguments
The `main` function then checks the AWS User ID and command line arguments by calling the following functions:

|Function|Description|
|--------|-----------|
|check_aws_user_id|Checks the current AWS User ID.|
|check_ip_protocol|Checks if ip_protocol value is tcp or udp.|
|check_port|Checks if port range value is valid.|
|check_cidr_ipv4|Checks if cidr_ipv4 value is a valid IPv4 CIDR address.|

The `check_port` function is called twice: once to check the `to_port` value and a second time to check the `from_port` value. All functions exit the script on error.

### 3. Call Core Script Functions
Finally, `main` calls the core script functions to find and delete rules that match the criteria provided by user.

The `find_sg_rules` function uses the Boto3 `describe_security_group_rules` method to search for rules that match the values in the `is_egress`, `ip_protocol`, `from_port`, `to_port`, and `cidr_ipv4` command line arguments.

If any matches are found, a conditional statement uses the value of `is_egress` argument to call either the `delete_sg_rules_ingress` or `delete_sg_rules_egress` function. Separate functions are required to delete ingress and egress rules because Boto3 uses different methods to delete each rule type.

### Exit Codes
If the script runs without an error, it returns an exit code of 0. Non-zero exit codes are as follows:

|Exit Code|Description|
|---------|-----------|
|50|AWS User ID required|
|51|Invalid IP Protocol value|
|52|Invalid port range value|
|53|Invalid IPv4 CIDR address|

## Getting Started

### Dependencies

+ Python: Version 3.8 or higher
+ AWS Boto3 Library: Latest version
+ Established connection to AWS account

For Boto3 installation instructions, visit the AWS [Quickstart page](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html). Following best security practices, this script does not create a Boto3 client connection using hard coded credentials. As such, it is expected that the user has established a connection to AWS, and the script will therefore load credential parameters from the local environmental variables, the AWS config file, or the AWS shared credential file. For instructions, review the Boto3 [Credentials page](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html).

### Installation
To install the script, either clone the [python-aws-scripts](..) repo or download the [sg-rules-find-delete.py](./sg-rules-find-delete.py) file to the local host. 

## Usage
To run the script, use the syntax below:

```bash
python3 sg-rules-find-delete.py [is_egress] [ip_protocol] [from_port] [to_port] [cidr_ipv4]
```

The following example searches for and deletes any security group rules that are 1) ingress rules (False), 2) support TCP traffic (tcp), allow traffic ranging 3) from port 22 (22) and 4) to port 22 (22), and 5) allow all IPv4 addresses (0.0.0.0/0).

```bash
python3 sg-rules-find-delete.py False tcp 22 22 0.0.0.0/0
```

## License
Licensed under the [GNU General Public License v3.0](../LICENSE).
