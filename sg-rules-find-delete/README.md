# Find and Delete AWS Security Group Rules
The [sg-rules-find-delete.py](./sg-rules-find-delete.py) script uses the AWS Boto3 Python library to find and delete AWS security group rules that meet user-provided criteria. A typical use case is deleting insecure rules, such as those that allow SSH connections from any IPv4 address.

To run the script against a test AWS environment, please refer to the [Terraform script](../terraform-aws-test-env) in this repository, which creates a VPC with a subnet, an EC2 instance, insecure security group rules, and insecure network ACL rules.

## Description
Upon invocation, the `main` function establishes the run order of the script, as follows:

+ Parse Arguments
+ Check AWS User ID and Arguments
+ Call Core Script Functions

### 1. Parse Arguments
The script first parses the required command line arguments listed below. The argument names are identical to the corresponding parameters used by Boto3 methods.

|Argument|Allowed Values|
|--------|--------------|
|IsEgress|False for inbound rules, True for outbound|
|IpProtocol|tcp or udp|
|FromPort|0-65535|
|ToPort|0-65535|
|CidrIpv4|Valid CIDR IPv4 address|

The Python `argparse` module reads the arguments, performs type validation, and stores the values in a dictionary object. Built-in `argparse` help (-h) is available.

### 2. Check AWS User ID and Arguments
The `main` function then checks the AWS User ID and command line arguments by calling the following functions:

|Function|Description|
|--------|-----------|
|check_aws_user_id|Checks the current AWS User ID.|
|check_ip_protocol|Checks if IpProtocol value is valid.|
|check_port|Checks if port range value is valid.|
|check_cidr_ipv4|Checks if CidrIpv4 value is a valid IPv4 CIDR address.|

The `check_port` function is called twice: once to check the `ToPort` value and a second time to check the `FromPort` value. All functions exit the script on error.

### 3. Call Core Script Functions
Finally, `main` calls the core script functions to find and delete rules that match the criteria provided by the user.

The `find_sg_rules` function uses the Boto3 `describe_security_group_rules` method to search for rules that match the values in the `IsEgress`, `IpProtocol`, `FromPort`, `ToPort`, and `CidrIpv4` command line arguments.

If `find_sg_rules` returns any matches, a conditional statement uses the value of the `IsEgress` argument to call either the `delete_sg_rules_ingress` or `delete_sg_rules_egress` function. Separate functions are required to delete ingress and egress rules because Boto3 uses different methods for each rule type.

### Exit Codes
If the script runs without an error, it returns an exit code of 0. Non-zero exit codes are as follows:

|Exit Code|Description|
|---------|-----------|
|50|AWS User ID required.|
|51|Invalid IP Protocol value.|
|52|Invalid port range value.|
|53|Invalid IPv4 CIDR address.|

## Getting Started

### Dependencies

+ Python: Version 3.8 or higher
+ AWS Boto3 Library: Latest version
+ Established connection to AWS account

For Boto3 installation instructions, visit the AWS Boto3 [Quickstart page](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html). Following best security practices, the script does not create a Boto3 client connection using hard coded credentials. As such, it is expected that the user has established a connection to AWS, and the script will therefore load credential parameters from the local environmental variables, the AWS config file, or the AWS shared credential file. For instructions, review the Boto3 [Credentials page](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html).

### Installation
To install the script, either clone the [python-aws-scripts](..) repo or download the [sg-rules-find-delete.py](./sg-rules-find-delete.py) file to the local host. 

## Usage
To run the script, use the syntax below:

```bash
python3 sg-rules-find-delete.py [IsEgress] [IpProtocol] [FromPort] [ToPort] [CidrIpv4]
```

As an example, the command below searches for and deletes ingress security group rules (IsEgress=False) that support TCP traffic (IpProtocol=tcp), allow traffic ranging from port 22 (FromPort=22) to port 22 (ToPort=22), and accept any IPv4 address (CidrIpv4=0.0.0.0/0).

```bash
python3 sg-rules-find-delete.py False tcp 22 22 0.0.0.0/0
```

## License
Licensed under the [GNU General Public License v3.0](../LICENSE).
