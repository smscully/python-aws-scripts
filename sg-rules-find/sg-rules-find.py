#!/usr/bin/python3

"""Uses the AWS Boto3 Python library to find security group rules that meet user-provided criteria, then exports the list of rules to S3. This program is licensed under the terms of the GNU General Public License v3.0.
"""

import argparse
import boto3
import botocore
import ipaddress
import json
import sys

def check_aws_user_id() -> str:
    """Checks the current AWS User ID; exits on failure."""
    try:
        return boto3.client("sts").get_caller_identity().get("UserId")
    except:
        print("AWS User ID is required.")
        raise SystemExit(50)


def check_ip_protocol(ip_protocol: str):
    """Checks if ip_protocol value is tcp or udp; exits on failure."""
    protocols  = ["tcp", "udp"]
    if ip_protocol not in protocols:
        print("Invalid ip_protocol value for this script. Please enter tcp or udp.")
        raise SystemExit(51)


def check_port(port: int):
    """Checks if port range value is valid; exits on failure."""
    if port not in range(65536):
        print("Invalid port range value. Please enter a number in the range of 0-65535.")
        raise SystemExit(52)


def check_cidr_ipv4(cidr_ipv4: str):
    """Checks if cidr_ipv4 value is a valid IPv4 CIDR address; exits on failure."""
    try:
        ip = ipaddress.ip_network(cidr_ipv4)
    except ValueError:
        print("Invalid cidr_ipv4 value. Please enter a valid IPv4 CIDR address.")
        raise SystemExit(53)


def check_bucket(bucket: str):
    """Checks to confirm S3 bucket exists; exits on failure."""
    client = boto3.client("s3")
    try:
        response = client.head_bucket(Bucket=f'{bucket}')
    except botocore.exceptions.ClientError as err:
    # Note: botocore used because expected NoSuchBucket exception is not thrown
    # See: https://github.com/boto/boto3/issues/2499
        print("S3 Bucket Error: ", err.response['Error']['Message'])
        raise SystemExit(54)


def check_key(bucket: str, key: str) -> bool:
    """Checks for S3 key; exits if exists."""
    client = boto3.client("s3")
    try:
        client.get_object(Bucket=f'{bucket}', Key=f'{key}')
        print("The S3 object already exists. Please enter a different key value.")
        raise SystemExit(55)
    except client.exceptions.NoSuchKey:
        pass


def find_sg_rules(args: list) -> list:
    """Searches for rules based on find criteria."""
    # Declare list and dictionary to store rules that meet find criteria
    sg_rules_list: list[dict] = [] 
    sg_rule_dict: dict[str, str] = {}

    # Get dictionary of existing rules
    client = boto3.client("ec2")
    sg_rules_existing = client.describe_security_group_rules().get("SecurityGroupRules")

    # Search for exising rules that meet find criteria and append to list
    for rule in sg_rules_existing:
        if (
            rule.get("IsEgress") == eval(args.is_egress) and
            rule.get("IpProtocol") == args.ip_protocol and
            rule.get("FromPort") == args.from_port and
            rule.get("ToPort") == args.to_port and
            rule.get("CidrIpv4") == args.cidr_ipv4
        ):
            sg_rule_dict = {
                "security_group_id":rule.get("GroupId"),
                "security_group_rule_id":rule.get("SecurityGroupRuleId"),
                "is_egress":rule.get("IsEgress"),
                "ip_protocol":rule.get("IpProtocol"),
                "from_port":rule.get("FromPort"),
                "to_port":rule.get("ToPort"),
                "cidr_ipv4":rule.get("CidrIpv4")
            }
            sg_rules_list.append(sg_rule_dict)

    return sg_rules_list


def print_find_results(sg_rules_json: str):
    """Prints find results to stdout."""
    print("The following rules were found that met the find criteria:")
    print(sg_rules_json)


def write_find_results(sg_rules_json: str, bucket: str, key: str):
    """Creates S3 object with JSON list of rules that met the find criteria."""
    client = boto3.client("s3")
    try:
        response = client.put_object(
            Body=f'{sg_rules_json}',
            Bucket=f'{bucket}',
            Key=f'{key}',
            ServerSideEncryption='AES256'
        )
        print("The list of rules that met the find criteria is located here:")
        print("Bucket:", bucket)
        print("Key:", key)
    except:
        print("There was an error writing the list of rules to S3.")
        raise SystemExit(56)


def main(arguments):
    # Parse arguments
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('is_egress', help='False for inbound rules, True for outbound',
        type=str, choices=['False', 'True'])
    parser.add_argument('ip_protocol', help='IP protocol')
    parser.add_argument('from_port', help='Lower number of port range', type=int)
    parser.add_argument('to_port', help='Upper number of port range', type=int)
    parser.add_argument('cidr_ipv4', help='Valid CIDR IPv4 address')
    parser.add_argument('bucket', help='Name of existing S3 bucket')
    parser.add_argument('key', help='Unique key of rules file object')
    args = parser.parse_args(arguments)

    # Check arguments
    check_ip_protocol(args.ip_protocol)
    check_port(args.from_port)
    check_port(args.to_port)
    check_cidr_ipv4(args.cidr_ipv4)
    check_bucket(args.bucket)
    check_key(args.bucket, args.key)

    # Find rules that meet find criteria 
    sg_rules_list = find_sg_rules(args)
    # Convert list of rules that met find criteria to JSON string
    sg_rules_json = json.dumps(sg_rules_list, indent=2)
    # Print find results to stdout and write to S3 bucket
    if len(json.loads(sg_rules_json)) != 0:
        print_find_results(sg_rules_json)
        write_find_results(sg_rules_json, args.bucket, args.key)
    else:
        print("No rules found meeting the provided criteria.")


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
