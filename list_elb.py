import boto3

def list_aws_regions():
    # Initialize the EC2 client with default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()
    
    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions


def list_network_elbs(region):
    # Initialize an ELBv2 client for the specified region
    elbv2 = boto3.client('elbv2', region_name=region)

    # List Network Load Balancers in the region
    response = elbv2.describe_load_balancers(PageSize=100)

    network_elbs = response.get('LoadBalancers', [])
    
    return network_elbs


def list_classic_elbs(region):
    # Initialize an ELB client for the specified region
    elb = boto3.client('elb', region_name=region)

    # List Classic Load Balancers in the region
    response = elb.describe_load_balancers()

    classic_elbs = response.get('LoadBalancerDescriptions', [])
    
    return classic_elbs


def list_albs(region):
    # Initialize an ELBv2 client for the specified region
    elbv2 = boto3.client('elbv2', region_name=region)

    # List all Load Balancers in the region
    response = elbv2.describe_load_balancers()

    # Filter ALBs from the response
    albs = [lb for lb in response['LoadBalancers'] if lb['Type'] == 'application']

    return albs


# Get all AWS regions
regions = list_aws_regions()

# Print table headers
print("| Region | ELB Name | Type | VPC ID | Scheme |")
print("|--------|----------|------|--------|--------|")

# Iterate over each region
for region in regions:
    # List Network Load Balancers
    network_elbs = list_network_elbs(region)
    for elb in network_elbs:
        print(f"| {region} | {elb['LoadBalancerName']} | Network | {elb['VpcId']} | {elb['Scheme']} |")

    # List Classic Load Balancers
    classic_elbs = list_classic_elbs(region)
    for elb in classic_elbs:
        print(f"| {region} | {elb['LoadBalancerName']} | Classic | {elb['VPCId']} | {elb['Scheme']} |")

    # List Application Load Balancers
    albs = list_albs(region)
    for alb in albs:
        print(f"| {region} | {alb['LoadBalancerName']} | Application | {alb['VpcId']} | {alb['Scheme']} |")
