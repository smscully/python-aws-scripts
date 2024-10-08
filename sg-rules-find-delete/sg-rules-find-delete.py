#!/usr/bin/python3

"""Uses the AWS Boto3 Python library to find and delete AWS security group rules that meet user-provided criteria. This program is licensed under the terms of the GNU General Public License v3.0.
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


def check_ip_protocol(IpProtocol: str):
    """Checks if IpProtocol value is tcp or udp; exits on failure."""
    protocols  = ["tcp", "udp"]
    if IpProtocol not in protocols:
        print("Invalid IpProtocol value for this script. Please enter tcp or udp.")
        raise SystemExit(51)


def check_port(port: int):
    """Checks if port range value is valid; exits on failure."""
    if port not in range(65536):
        print("Invalid port range value. Please enter a number in the range of 0-65535.")
        raise SystemExit(52)


def check_cidr_ipv4(CidrIpv4: str):
    """Checks if CidrIpv4 value is a valid IPv4 CIDR address; exits on failure."""
    try:
        ip = ipaddress.ip_network(CidrIpv4)
    except ValueError:
        print("Invalid CidrIpv4 value. Please enter a valid IPv4 CIDR address.")
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
            rule.get("IsEgress") == eval(args.IsEgress) and
            rule.get("IpProtocol") == args.IpProtocol and
            rule.get("FromPort") == args.FromPort and
            rule.get("ToPort") == args.ToPort and
            rule.get("CidrIpv4") == args.CidrIpv4
        ):
            sg_rule_dict = {
                "GroupId":rule.get("GroupId"),
                "SecurityGroupRuleId":rule.get("SecurityGroupRuleId")
            }
            sg_rules_list.append(sg_rule_dict)

    return sg_rules_list


def delete_sg_rules_ingress(sg_rules_list: list):
    """Deletes existing ingress rules that met find criteria."""
    client = boto3.client("ec2")
    for rule in sg_rules_list:
        response = client.revoke_security_group_ingress(
            GroupId='{}'.format(rule['GroupId']),
            SecurityGroupRuleIds=['{}'.format(rule['SecurityGroupRuleId'])]
        )
        if response['Return'] == True:
            print("SUCCESS - The following rule was deleted:", rule['SecurityGroupRuleId'])
        else:
            print("ERROR - The following rule was NOT deleted:", rule['SecurityGroupRuleId'])         


def delete_sg_rules_egress(sg_rules_list: list):
    """Deletes existing egress rules that met find criteria."""
    client = boto3.client("ec2")
    for rule in sg_rules_list:
        response = client.revoke_security_group_egress(
            GroupId='{}'.format(rule['GroupId']),
            SecurityGroupRuleIds=['{}'.format(rule['SecurityGroupRuleId'])]
        )
        if response['Return'] == True:
            print("SUCCESS - The following rule was deleted:", rule['SecurityGroupRuleId'])
        else:
            print("ERROR - The following rule was NOT deleted:", rule['SecurityGroupRuleId'])         


def main(arguments):
    # Parse arguments
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('IsEgress', help='False for inbound rules, True for outbound',
        type=str, choices=['False', 'True'])
    parser.add_argument('IpProtocol', help='IP protocol')
    parser.add_argument('FromPort', help='Lower number of port range', type=int)
    parser.add_argument('ToPort', help='Upper number of port range', type=int)
    parser.add_argument('CidrIpv4', help='Valid CIDR IPv4 address')
    args = parser.parse_args(arguments)

    # Check arguments
    check_aws_user_id
    check_ip_protocol(args.IpProtocol)
    check_port(args.FromPort)
    check_port(args.ToPort)
    check_cidr_ipv4(args.CidrIpv4)

    # Find rules that meet find criteria and send to appropriate delete function 
    sg_rules_list = find_sg_rules(args)
    if len(sg_rules_list) == 0:
        print("No rules found meeting the provided criteria.")
    else:
        if eval(args.IsEgress) == True:
            delete_sg_rules_egress(sg_rules_list)
        elif eval(args.IsEgress) == False:
            delete_sg_rules_ingress(sg_rules_list)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
