#!/usr/bin/python3

"""Uses the AWS Boto3 Python library to find and delete security group rules that meet user-provided criteria. This program is licensed under the terms of the GNU General Public License v3.0.
"""

import argparse
import boto3
import ipaddress
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
                "security_group_rule_id":rule.get("SecurityGroupRuleId")
            }
            sg_rules_list.append(sg_rule_dict)

    return sg_rules_list


def delete_sg_rules_ingress(sg_rules_list: list):
    """Deletes existing ingress rules that met find criteria."""
    client = boto3.client("ec2")
    for rule in sg_rules_list:
        response = client.revoke_security_group_ingress(
            GroupId='{}'.format(rule['security_group_id']),
            SecurityGroupRuleIds=['{}'.format(rule['security_group_rule_id'])]
        )
        if response['Return'] == True:
            print("SUCCESS - The following rule was deleted:", rule['security_group_rule_id'])
        else:
            print("ERROR - The following rule was NOT deleted:", rule['security_group_rule_id'])         


def delete_sg_rules_egress(sg_rules_list: list):
    """Deletes existing rules that met find criteria."""
    client = boto3.client("ec2")
    for rule in sg_rules_list:
        response = client.revoke_security_group_egress(
            GroupId='{}'.format(rule['security_group_id']),
            SecurityGroupRuleIds=['{}'.format(rule['security_group_rule_id'])]
        )
        if response['Return'] == True:
            print("SUCCESS - The following rule was deleted:", rule['security_group_rule_id'])
        else:
            print("ERROR - The following rule was NOT deleted:", rule['security_group_rule_id'])         


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
    args = parser.parse_args(arguments)

    # Check arguments
    check_ip_protocol(args.ip_protocol)
    check_port(args.from_port)
    check_port(args.to_port)
    check_cidr_ipv4(args.cidr_ipv4)

    # Find rules that meet find criteria and send to appropriate delete function 
    sg_rules_list = find_sg_rules(args)
    if len(sg_rules_list) == 0:
        print("No rules found meeting the provided criteria.")
    else:
        if eval(args.is_egress) == True:
            delete_sg_rules_egress(sg_rules_list)
        elif eval(args.is_egress) == False:
            delete_sg_rules_ingress(sg_rules_list)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
