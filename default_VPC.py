import logging
import boto3
import csv
import json
import os
from datetime import datetime, timedelta, timezone
import logging
import argparse
from argparse import ArgumentParser, HelpFormatter
from botocore.exceptions import ClientError, ProfileNotFound
 
 
DEFAULT_REGION="us-east-1"

date_time_now = datetime.now().strftime('%Y/%m/%d  %H:%M:%S')
enilist = igwlist = ec2list = sglist = acllist = rtblist = subnetlist = elblist = ekslist = rdslist = asglist = lambdalist = natlist = subnetlist = vpceplist =   []
 
def parse_commandline_arguments():
    global REGION
    global ACCOUNT_ID
    # ACCOUNT_ID = "820195296780"
    global report_filename
 
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Create a CSV Report for IAM policies affected by Upcoming Elastic Load Balancing API change.')
    parser.add_argument("-id", "--accountID", dest="account_id", type=str,required=True,
                        help="The AWS Account Name for which the RDS info is neeeded")
    parser.add_argument("-r", "--region", dest="region", type=str,
                        default=DEFAULT_REGION, help="Specify the global region to pull the report")
    parser.add_argument("-f", "--report", dest="reportname", type=str,
                        help="Specify the report file Name with path")
    args = parser.parse_args()
 
    ACCOUNT_ID= args.account
    REGION = args.region
    report_filename = args.reportname
 
# logger config
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(message)s')
 
 
def ec2_client(region):
    """
    Connects to EC2, returns a connection object
    """
    import sys
    try:
        conn = boto3.client('ec2', region_name=region)
 
    except Exception as e:
        sys.stderr.write(
            'Could not connect to region: %s. Exception: %s\n' % (region, e))
        conn = None
 
    return conn
     
def rds_client(region):
    """
    Connects to RDS, returns a connection object
    """
    import sys
    try:
        conn = boto3.client('rds', region_name=region)
 
    except Exception as e:
        sys.stderr.write(
            'Could not connect to region: %s. Exception: %s\n' % (region, e))
        conn = None
 
    return conn
     
def elbV2_client(region):
    """
    Connects to ELB, returns a connection object
    """
    import sys
    try:
        conn = boto3.client('elbv2', region_name=region)
 
    except Exception as e:
        sys.stderr.write(
            'Could not connect to region: %s. Exception: %s\n' % (region, e))
        conn = None
 
    return conn
     
 
def elb_client(region):
    """
    Connects to ELB, returns a connection object
    """
    import sys
    try:
        conn = boto3.client('elb', region_name=region)
 
    except Exception as e:
        sys.stderr.write(
            'Could not connect to region: %s. Exception: %s\n' % (region, e))
        conn = None
 
    return conn
     
def lambda_client(region):
    """
    Connects to ELB, returns a connection object
    """
    import sys
    try:
        conn = boto3.client('lambda', region_name=region)
 
    except Exception as e:
        sys.stderr.write(
            'Could not connect to region: %s. Exception: %s\n' % (region, e))
        conn = None
 
    return conn
     
def eks_client(region):
    """
    Connects to EKS, returns a connection object
    """
    import sys
    try:
        conn = boto3.client('eks', region_name=region)
 
    except Exception as e:
        sys.stderr.write(
            'Could not connect to region: %s. Exception: %s\n' % (region, e))
        conn = None
 
    return conn
     
def asg_client(region):
    """
    Connects to EKS, returns a connection object
    """
    import sys
    try:
        conn = boto3.client('autoscaling', region_name=region)
 
    except Exception as e:
        sys.stderr.write(
            'Could not connect to region: %s. Exception: %s\n' % (region, e))
        conn = None
 
    return conn
 
 
def check_vpc_exists(ec2_client):
    global default_vpc_id
    vpc_exists = False
    response = ec2_client.describe_vpcs(
        Filters=[{
            'Name': 'isDefault', 'Values': ['true']
        }]
    )
#print(response)
    vpc_exists = False
    if len(response['Vpcs']) > 0:
        for vpcs in response['Vpcs']:
            default_vpc_id = vpcs['VpcId']
            vpc_exists = True
    return vpc_exists
 
def get_asgs(asg_client,ec2client,vpc_id):
    global asglist
    asglist = []
    logger.info("ASGs in VPC {}:".format(vpc_id))
    asgs = asg_client.describe_auto_scaling_groups()['AutoScalingGroups']
    for asg in asgs:
        asg_name = asg['AutoScalingGroupName']
        if asg_in_vpc(asg,ec2client,vpc_id):
            logger.info(asg_name)
            asglist.append(asg_name)
    logger.info("--------------------------------------------")
    return
 
 
def asg_in_vpc(asg,vpc_client,vpc_id):
    subnets_list = asg['VPCZoneIdentifier'].split(',')
    for subnet in subnets_list:
        try:
            sub_description = vpc_client.describe_subnets(SubnetIds=[subnet])['Subnets']
            if sub_description[0]['VpcId'] == vpc_id:
                logger.info("{} resides in {}".format(asg['AutoScalingGroupName'], vpc_id))
                return True
        except ClientError:
            pass
 
    return False
 
 
def get_ekss(eks_client,vpc_id):
    global ekslist
    ekslist = []
    ekss = eks_client.list_clusters()['clusters']
 
    logger.info("EKSs in VPC {}:".format(vpc_id))
    for eks in ekss:
        eks_desc = eks_client.describe_cluster(name=eks)['cluster']
        if eks_desc['resourcesVpcConfig']['vpcId'] == vpc_id:
            logger.info(eks_desc['name'])
            ekslist.append(eks_desc['name'])
    logger.info("--------------------------------------------")
    return
 
 
def get_ec2s(vpc_client,vpc_id):
    global ec2list
    ec2list = []
    waiter = vpc_client.get_waiter('instance_terminated')
    reservations = vpc_client.describe_instances(Filters=[{"Name": "vpc-id",
                                                           "Values": [vpc_id]}])['Reservations']
 
    # Get a list of ec2s
    ec2s = [ec2['InstanceId'] for reservation in reservations for ec2 in reservation['Instances']]
 
    logger.info("EC2s in VPC {}:".format(vpc_id))
    for ec2 in ec2s:
        logger.info(ec2)
        ec2list.append(ec2)
    logger.info("--------------------------------------------")
    return
 
 
def get_lambdas(lambda_client,vpc_id):
    global lambdalist
    lambdalist = []
    lmbds = lambda_client.list_functions()['Functions']
 
    lambdas_list = [lmbd['FunctionName'] for lmbd in lmbds
                    if 'VpcConfig' in lmbd and lmbd['VpcConfig']['VpcId'] == vpc_id]
 
    logger.info("Lambdas in VPC {}:".format(vpc_id))
    for lmbda in lambdas_list:
        logger.info(lmbda)
        lambdalist.append(lmbda)
    logger.info("--------------------------------------------")
    return
 
 
def get_rdss(rds_client,vpc_id):
    global rdslist
    rdslist = []
    rdss = rds_client.describe_db_instances()['DBInstances']
 
    rdsss_list = [rds['DBInstanceIdentifier'] for rds in rdss if rds['DBSubnetGroup']['VpcId'] == vpc_id]
 
    logger.info("RDSs in VPC {}:".format(vpc_id))
    for rds in rdsss_list:
        logger.info(rds)
        rdslist.append(rds)
    logger.info("--------------------------------------------")
    return
 
 
def get_elbs(elb_client,vpc_id):
    global elblist
    elblist = []
    elbs = elb_client.describe_load_balancers()['LoadBalancerDescriptions']
 
    elbs = [elb['LoadBalancerName'] for elb in elbs if elb['VPCId'] == vpc_id]
 
    logger.info("Classic ELBs in VPC {}:".format(vpc_id))
    for elb in elbs:
        logger.info(elb)
        elblist.append(elb)
    logger.info("--------------------------------------------")
    return
 
 
def get_elbsV2(elbV2_client,vpc_id):
    elbs = elbV2_client.describe_load_balancers()['LoadBalancers']
 
    elbs_list = [elb['LoadBalancerArn'] for elb in elbs if elb['VpcId'] == vpc_id]
 
    logger.info("ELBs V2 in VPC {}:".format(vpc_id))
    for elb in elbs_list:
        logger.info(elb)
 
    logger.info("--------------------------------------------")
    return
 
 
def get_nats(vpc_client,vpc_id):
    global natlist
    natlist = []
    nats = vpc_client.describe_nat_gateways(Filters=[{"Name": "vpc-id",
                                                      "Values": [vpc_id]}])['NatGateways']
 
    nats = [nat['NatGatewayId'] for nat in nats]
    logger.info("NAT GWs in VPC {}:".format(vpc_id))
    for nat in nats:
        logger.info(nat)
        #print(nat)
        natlist.append(nat)
 
    logger.info("--------------------------------------------")
    return
 
 
def get_enis(vpc_client,vpc_id):
    global enilist
    enilist = []
    enis = vpc_client.describe_network_interfaces(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])['NetworkInterfaces']
 
    # Get a list of enis
    enis = [eni['NetworkInterfaceId'] for eni in enis]
 
    logger.info("ENIs in VPC {}:".format(vpc_id))
    for eni in enis:
        logger.info(eni)
        #print(eni)
        enilist.append(eni)
 
    logger.info("--------------------------------------------")
    return
 
 
def get_igws(vpc_client,vpc_id):
    global igwlist
    igwlist = []
    igws = vpc_client.describe_internet_gateways(
        Filters=[{"Name": "attachment.vpc-id",
                  "Values": [vpc_id]}])['InternetGateways']
 
    igws = [igw['InternetGatewayId'] for igw in igws]
 
    logger.info("IGWs in VPC {}:".format(vpc_id))
    for igw in igws:
        logger.info(igw)
        igwlist.append(igw)
        #print(igw)
    logger.info("--------------------------------------------")
    return
 
 
def get_vpgws(vpc_client,vpc_id):
    """
  Describe the virtual private gateway
  """
 
    # Get list of dicts
    vpgws = vpc_client.describe_vpn_gateways(
        Filters=[{"Name": "attachment.vpc-id",
                  "Values": [vpc_id]}])['VpnGateways']
 
    vpgws = [vpgw['VpnGatewayId'] for vpgw in vpgws]
 
    logger.info("VPGWs in VPC {}:".format(vpc_id))
    for vpgw in vpgws:
        logger.info(vpgw)
 
    logger.info("--------------------------------------------")
    return
 
 
def get_subnets(vpc_client,vpc_id):
    global subnetlist
    subnetlist = []
    # Get list of dicts of metadata
    subnets = vpc_client.describe_subnets(Filters=[{"Name": "vpc-id",
                                                    "Values": [vpc_id]}])['Subnets']
 
    # Get a list of subnets
    subnets = [subnet['SubnetId'] for subnet in subnets]
 
    logger.info("Subnets in VPC {}:".format(vpc_id))
    for subnet in subnets:
        logger.info(subnet)
        subnetlist.append(subnet)
    logger.info("--------------------------------------------")
    return
 
 
def get_acls(vpc_client,vpc_id):
    global acllist
    acllist = []
    acls = vpc_client.describe_network_acls(Filters=[{"Name": "vpc-id",
                                                      "Values": [vpc_id]}])['NetworkAcls']
 
    # Get a list of subnets
    acls = [acl['NetworkAclId'] for acl in acls]
    logger.info("ACLs in VPC {}:".format(vpc_id))
    for acl in acls:
        logger.info(acl)
        acllist.append(acl)
    logger.info("--------------------------------------------")
    return
 
 
def get_sgs(vpc_client,vpc_id):
    global sglist
    sglist = []
    sgs = vpc_client.describe_security_groups(Filters=[{"Name": "vpc-id",
                                                        "Values": [vpc_id]}])['SecurityGroups']
 
    # Get a list of subnets
    # sgs = [sg['GroupId'] for sg in sgs]
    logger.info("Security Groups in VPC {}:".format(vpc_id))
 
    for sg in sgs:
        logger.info(sg['GroupId'])
        sglist.append(sg['GroupId'])
 
    logger.info("--------------------------------------------")
    return
 
 
def get_rtbs(vpc_client,vpc_id):
    global rtblist
    rtblist = []
    rtbs = vpc_client.describe_route_tables(Filters=[{"Name": "vpc-id",
                                                      "Values": [vpc_id]}])['RouteTables']
    # Get a list of Routing tables
    rtbs = [rtb['RouteTableId'] for rtb in rtbs]
    logger.info("Routing tables in VPC {}:".format(vpc_id))
    for rtb in rtbs:
        logger.info(rtb)
        rtblist.append(rtb)
    logger.info("--------------------------------------------")
    return
 
 
def get_vpc_epts(vpc_client,vpc_id):
    global vpceplist
    vpceplist = []
    epts = vpc_client.describe_vpc_endpoints(Filters=[{"Name": "vpc-id",
                                                       "Values": [vpc_id]}])['VpcEndpoints']
 
    # Get a list of Routing tables
    epts = [ept['VpcEndpointId'] for ept in epts]
    logger.info("VPC EndPoints in VPC {}:".format(vpc_id))
    for ept in epts:
        logger.info(ept)
        vpceplist.append(ept)
 
    logger.info("--------------------------------------------")
    return
 
 
if __name__ == '__main__':
    try:
        parse_commandline_arguments()
        ec2client = ec2_client(REGION)
        rdsclient = rds_client(REGION)
        elbV2client = elbV2_client(REGION)
        elbclient = elb_client(REGION)
        lambdaclient = lambda_client(REGION)
        eksclient = eks_client(REGION)
        asgclient = asg_client(REGION)
        if not os.path.isfile(report_filename):
            file = open(report_filename, 'w+')
            # Header for the CSV file
            print_string_hdr = "AccountID,Region,Lambdas,Subnets,RouteTables,RDS,NatGW,IGW,EC2List,ENIList,ASGList,EKSList, VPCEndPoints,SecGroups,Reporting_Date_Time\n"
            file.write(print_string_hdr)
        else:
            file = open(report_filename, 'a')        
        if check_vpc_exists(ec2client):
            get_ekss(eksclient,default_vpc_id)
            get_asgs(asgclient,ec2client,default_vpc_id)
            get_rdss(rdsclient,default_vpc_id)
            get_ec2s(ec2client,default_vpc_id)
            get_lambdas(lambdaclient,default_vpc_id)
            get_elbs(elbclient,default_vpc_id)
            get_elbsV2(elbV2client,default_vpc_id)
            get_nats(ec2client,default_vpc_id)
            get_vpc_epts(ec2client,default_vpc_id)
            get_igws(ec2client,default_vpc_id)
            get_vpgws(ec2client,default_vpc_id)
            get_enis(ec2client,default_vpc_id)
            get_sgs(ec2client,default_vpc_id)
            get_rtbs(ec2client,default_vpc_id)
            get_acls(ec2client,default_vpc_id)
            get_subnets(ec2client,default_vpc_id)
            #Convert list to Strings for the CSV file
            listOfenis = ','.join(map(str,enilist))
            listOfigw = ','.join(map(str,igwlist))
            listOfec2 = ','.join(map(str,ec2list))
            listOfsg = ','.join(map(str,sglist))
            listOfacl = ','.join(map(str,acllist))
            listOfrtb = ','.join(map(str,rtblist))
            listOfsubnet = ','.join(map(str,subnetlist))
            listOfelb = ','.join(map(str,elblist))
            listOfeks = ','.join(map(str,ekslist))
            listOfrds = ','.join(map(str,rdslist))
            listOfasg = ','.join(map(str,asglist))
            listOflambda = ','.join(map(str,lambdalist))
            listOfnat = ','.join(map(str,natlist))
            listOfvpcep = ','.join(map(str,vpceplist))
            print_string = ACCOUNT_ID + "," + REGION + "," + listOflambda + "," + listOfsubnet + "," + listOfrtb + "," + listOfrds + "," + listOfnat + "," + listOfigw + "," + listOfec2 + "," + listOfenis + "," + listOfasg + "," + listOfeks + "," + listOfvpcep + "," + listOfsg + "," + date_time_now
            file.write(print_string + "\n")
        else:
            logger.info("The given VPC was not found in {}".format(REGION))
    except Exception as error:
        print(str(error))