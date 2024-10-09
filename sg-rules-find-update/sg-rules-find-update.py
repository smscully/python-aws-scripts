#!/usr/bin/python3

"""Uses the AWS Boto3 Python library to find and update security group rules based on user-provided criteria. This program is licensed under the terms of the GNU General Public License v3.0.
"""

import argparse
import boto3
import ipaddress
import json
import os
import sys

def check_aws_user_id() -> str:
    """Checks the current AWS User ID; exits on failure."""
    try:
        return boto3.client("sts").get_caller_identity().get("UserId")
    except:
        print("AWS User ID is required.")
        raise SystemExit(50)


def check_is_egress(IsEgress: str):
    """Checks if IsEgress value is true or false; exits on failure."""
    egress = ["True", "False"]
    if IsEgress not in egress:
        print("Invalid IsEgress value for this script. Please enter True or False.")
        raise SystemExit(51)


def check_ip_protocol(IpProtocol: str):
    """Checks if IpProtocol value is tcp or udp; exits on failure."""
    protocols  = ["tcp", "udp"]
    if IpProtocol not in protocols:
        print("Invalid IpProtocol value for this script. Please enter tcp or udp.")
        raise SystemExit(52)


def check_port(port: int):
    """Checks if port range value is valid; exits on failure."""
    if port not in range(65536):
        print("Invalid port range value. Please enter a number in the range of 0-65535.")
        raise SystemExit(53)


def check_cidr_ipv4(CidrIpv4: str):
    """Checks if CidrIpv4 value is a valid IPv4 CIDR address; exits on failure."""
    try:
        ip = ipaddress.ip_network(CidrIpv4)
    except ValueError:
        print("Invalid CidrIpv4 value. Please enter a valid IPv4 CIDR address.")
        raise SystemExit(54)


def check_params_file(params_file: str):
    """Checks if find or update params file exists; exits on failure."""
    if not os.path.isfile(params_file):
        print(f"The params file {params_file} does not exist. Please provide a valid path to the file.")
        raise SystemExit(55)


def find_sg_rules(find_params_file: str) -> str:
    """Searches for rules based on criteria in params file; returns JSON string"""
    # Open find params file to read criteria
    find_params_file_src = open(f'{find_params_file}')
    find_params_file_json = json.load(find_params_file_src)

    # Check that find params file criteria are valid
    check_is_egress(find_params_file_json['IsEgress'])
    check_ip_protocol(find_params_file_json['IpProtocol'])
    check_port(find_params_file_json['FromPort'])
    check_port(find_params_file_json['ToPort'])
    check_cidr_ipv4(find_params_file_json['CidrIpv4'])

    # Declare list and dictionary to store rules that meet find criteria
    sg_rules_list: list[dict] = [] 
    sg_rule_dict: dict[str, str] = {}

    # Get dictionary of existing rules
    client = boto3.client("ec2")
    sg_rules_existing = client.describe_security_group_rules().get("SecurityGroupRules")

    # Search for exising rules that meet find params file criteria and append to list
    for rule in sg_rules_existing:
        if (
            rule.get("IsEgress") == eval(find_params_file_json['IsEgress']) and
            rule.get("IpProtocol") == find_params_file_json['IpProtocol'] and
            rule.get("FromPort") == find_params_file_json['FromPort'] and
            rule.get("ToPort") == find_params_file_json['ToPort'] and
            rule.get("CidrIpv4") == find_params_file_json['CidrIpv4']
        ):
            sg_rule_dict = {
                "GroupId":rule.get("GroupId"),
                "SecurityGroupRuleId":rule.get("SecurityGroupRuleId"),
            }
            sg_rules_list.append(sg_rule_dict)

    # Convert list of rules that meet criteria to JSON string and return
    sg_rules_json = json.dumps(sg_rules_list, indent=2)
    return sg_rules_json


def update_sg_rules(update_params_file: str, sg_rules_json: str):
    """Udates list of rules that met find criteria with values in update params file."""
    # Open update params file to read new params for rules
    update_params_file_src = open(f'{update_params_file}')
    update_params_file_json = json.load(update_params_file_src)

    # Check that update params file values are valid
    check_ip_protocol(update_params_file_json['IpProtocol'])
    check_port(update_params_file_json['FromPort'])
    check_port(update_params_file_json['ToPort'])
    check_cidr_ipv4(update_params_file_json['CidrIpv4'])

    # Parse JSON string and convert into dictionary
    sg_rules_json_dict = json.loads(sg_rules_json)

    # Update rules that met find criteria with new params
    client_ec2 = boto3.client("ec2")
    for rule in sg_rules_json_dict:
        response = client_ec2.modify_security_group_rules(
            GroupId='{}'.format(rule['GroupId']),
            SecurityGroupRules=[
                {
                    'SecurityGroupRuleId': '{}'.format(rule['SecurityGroupRuleId']),
                    'SecurityGroupRule': {
                        'IpProtocol': '{}'.format(update_params_file_json['IpProtocol']),
                        'FromPort': update_params_file_json['FromPort'],
                        'ToPort': update_params_file_json['ToPort'],
                        'CidrIpv4': '{}'.format(update_params_file_json['CidrIpv4'])
                    }
                },
            ],
        )
        if response['Return'] == True:
            print("SUCCESS - The following rule was updated:", rule['SecurityGroupRuleId'])
        else:
            print("ERROR - The following rule was NOT updated:", rule['SecurityGroupRuleId'])         


def main(arguments):
    # Parse arguments
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('find_params_file', help='Path to file with find params')
    parser.add_argument('update_params_file', help='Path to file with update params')
    args = parser.parse_args(arguments)

    # Check AWS User ID and that params files exist
    check_aws_user_id
    check_params_file(args.find_params_file)
    check_params_file(args.update_params_file)

    # Find rules that meet criteria in find params file and send to update function 
    sg_rules_json = find_sg_rules(args.find_params_file)
    if len(json.loads(sg_rules_json)) == 0:
        print("No rules found meeting the provided criteria.")
    else:
        update_sg_rules(args.update_params_file, sg_rules_json)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
