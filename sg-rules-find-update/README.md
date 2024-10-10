# Find and Update AWS Security Group Rules
The [sg-rules-find-update.py](./sg-rules-find-update.py) script uses the AWS Boto3 Python library to find and update AWS security group rules based on user-provided criteria.

A typical use case is finding insecure rules, such as those that allow SSH connections from any IPv4 address. In such a case, the update could limit the IPv4 range to one specific address and assign the SSH traffic to a non-standard port, since standard port 22 can be easily found using basic recon scans.

To run the script against a test AWS environment, please refer to the [Terraform script](../terraform-aws-test-env) in this repository, which creates a VPC with a subnet, an EC2 instance, insecure security group rules, and insecure network ACL rules.

## Description
Upon invocation, the `main` function establishes the run order of the script, as follows:

+ Parse Arguments
+ Check AWS User ID and That Params Files Exist
+ Call Core Script Functions

### 1. Parse Arguments
The script first parses the required command line arguments listed below. 

|Argument|Allowed Values|
|--------|--------------|
|find_params_file|Path to the JSON file with find params|
|update_params_file|Path to the JSON file with update params|

The Python `argparse` module reads the arguments and stores the values in a dictionary object. Built-in `argparse` help (-h) is available.

### 2. Check AWS User ID and That Params Files Exist
The `main` function then checks the AWS User ID and confirms the params files exist by calling the following functions:

|Function|Description|
|--------|-----------|
|check_aws_user_id|Checks the current AWS User ID.|
|check_params_file|Checks if the params file exists.|

The `check_params_file function is called twice: once to check the `find_params_file` path and a second time to check the `update_params_file` path. Both functions exit the script on error.

### 3. Call Core Script Functions
Finally, `main` calls the core script functions to find rules that match the criteria provided by the user, then update the rules.

??Revise this to two sentences??
The `find_sg_rules` function uses the Boto3 `describe_security_group_rules` method to search for rules that match the values for the `IsEgress`, `IpProtocol`, `FromPort`, `ToPort`, and `CidrIpv4` field names in the JSON file identified by the `find_params_file` argument.

The results returned by the `find_sg_rules` function are converted to a JSON string, and if any matches were found, the `print_find_results` and `write_find_results` functions are called. The `print_find_results` function simply prints the JSON string of rules to stdout, while `write_find_results` uses the Boto3 S3 client `put_object` method to write the JSON string to the S3 bucket.
???
For the AWS Security Group rule IP Protocol value, valid values are the range of IANA protocol numbers and certain string values. (See [here]( https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_SecurityGroupRule.html).) This script, however, limits the IP Protocols to TCP and UDP, primarily because the error checking required to avoid Boto3 exceptions to the ` modify_security_group_rules` function is beyond the scope of this script. As an example, modifying a rule to accept all protocols would then required that the from_port and to_port values be null, while modifying a rule to accept the ICMPv6 protocol would require the port range to be either not be specified or specified as from=-1 and to=-1. These and other particular cases ???
NOTE: The `find.json` and `update.json` files differ in that there is no is_egress parameter in the `fix.json` file. The reason for this is that the egress state of a security group rule cannot be modified using Boto3. The Boto3 `describe_security_group_rules` function(?) supports searching for rules based on the egress state, but the corresponding Boto3 `modify_security_group_rules` does no provide the option to change the egress state.

For demonstration purposes, the `update.json` file included in the repository updates the insecure IPv4 CIDR address to a private IP address. 

### Exit Codes
If the script runs without an error, it returns an exit code of 0. Non-zero exit codes are as follows:

|Exit Code|Description|
|---------|-----------|
|50|AWS User ID required.|
|51|Invalid IP Protocol value.|
|52|Invalid port range value.|
|53|Invalid IPv4 CIDR address.|
|54|S3 Bucket error.|
|55|S3 object exists.|
|56|Error writing to S3.|

## Getting Started

### Dependencies

+ Python: Version 3.8 or higher
+ AWS Boto3 Library: Latest version
+ Established connection to an AWS account

For Boto3 installation instructions, visit the AWS Boto3 [Quickstart page](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html). Following best security practices, the script does not create a Boto3 client connection using hard coded credentials. As such, it is expected that the user has established a connection to AWS, and the script will therefore load credential parameters from the local environmental variables, the AWS config file, or the AWS shared credential file. For instructions, review the Boto3 [Credentials page](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html).

### Installation
To install the script, either clone the [python-aws-scripts](..) repo or download the [sg-rules-find.py](./sg-rules-find.py) file to the local host. 

## Usage
To run the script, use the syntax below:

```bash
python3 sg-rules-find.py [IsEgress] [IpProtocol] [FromPort] [ToPort] [CidrIpv4] [bucket] [key]
```

```json
{
  "IsEgress": "False",
  "IpProtocol": "tcp",
  "FromPort": 22,
  "ToPort": 22,
  "CidrIpv4": "0.0.0.0/0"
}
```

```json
{
  "IpProtocol": "tcp",
  "FromPort": 63456,
  "ToPort": 63456,
  "CidrIpv4": "192.168.100.100/32"
}
```
As an example, the command below searches for ingress security group rules (IsEgress=False) that support TCP traffic (IpProtocol=tcp), allow traffic ranging from port 22 (FromPort=22) to port 22 (ToPort=22), and accept any IPv4 address (CidrIpv4=0.0.0.0/0).

If any rules are found, they are printed to stdout and exported to the S3 bucket called "test-bucket-001" (bucket=test-bucket-001) with an object key of "results.json" (key=results.json).

```bash
python3 sg-rules-find.py False tcp 22 22 0.0.0.0/0 test-bucket-001 results.json 
```

## License
Licensed under the [GNU General Public License v3.0](../LICENSE).
