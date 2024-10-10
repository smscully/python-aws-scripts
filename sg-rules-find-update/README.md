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

The `check_params_file` function is called twice: once to check the `find_params_file` path and a second time to check the `update_params_file` path. Both functions exit the script on error.

### 3. Call Core Script Functions
Finally, `main` calls the core script functions to find rules that match the criteria provided by the user, then update the rules.

The `find_sg_rules` function uses the Boto3 `describe_security_group_rules` method to search for rules that match the key-value pairs in the JSON file identified by the `find_params_file` argument. The example file in the repository is called find.json, and while the file name is flexible, it must be JSON formated and contain the keys shown in the example below:

```json
{
  "IsEgress": "False",
  "IpProtocol": "tcp",
  "FromPort": 22,
  "ToPort": 22,
  "CidrIpv4": "0.0.0.0/0"
}
```

The results returned by the `find_sg_rules` function are a JSON string, and if any matches were found, the `update_sg_rules` is called. This function updates the rules returned by `find_sg_rules` with the values listed in the JSON file identified by the `update_params_file` argument. The example file in the repository is called update.json, and while the file name is flexible, it must be JSON formated and contain the keys shown in the example below:

```json
{
  "IpProtocol": "tcp",
  "FromPort": 63456,
  "ToPort": 63456,
  "CidrIpv4": "192.168.100.100/32"
}
```

For each rule, a success or failure message will be printed to stdout.

### Difference Between Find and Update Params Files 
The `find.json` and `update.json` files differ in that there is no IsEgress parameter in the `update.json` file. The reason for this is that the egress state of a security group rule cannot be modified using Boto3. The Boto3 `describe_security_group_rules` method supports searching for rules based on the egress state, but the corresponding Boto3 `modify_security_group_rules` does no provide the option to change the egress state.

### Limitations on IP Protocol Values
For the AWS Security Group rule IP Protocol parameter, valid values are the range of IANA protocol numbers and certain string values. (See [here]( https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_SecurityGroupRule.html).) This script, however, limits the IpProtocol key to the values tcp and udp. The reason for this is that the error checking required to avoid Boto3 exceptions to the ` modify_security_group_rules` function is beyond the scope of this script. As an example, modifying a rule to accept all protocols would then required that the FromPort and ToPort values be null, while modifying a rule to accept the ICMPv6 protocol would require the port range to be either not be specified or specified as FromPort=-1 and ToPort=-1.

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
python3 sg-rules-find.py [find_params_file] [update_params_file]
```

For demonstration purposes, the `update.json` file included in the repository updates the insecure IPv4 CIDR address to a private IP address.

```bash
python3 sg-rules-find.py find.json update.json
```

## License
Licensed under the [GNU General Public License v3.0](../LICENSE).
