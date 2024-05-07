import boto3

def list_aws_regions():
    # Initialize the EC2 client with default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()
    
    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions

def list_nat(region):
    # Create an EC2 client
    ec2 = boto3.client('ec2', region_name=region)

    # Retrieve all NAT Gateways
    nat_gateways = ec2.describe_nat_gateways()

    return nat_gateways

print("| Region       | NAT Gateway ID      | VPC ID         | State       | Subnet ID      | IP Addresses     |")
print("|--------------|---------------------|----------------|-------------|----------------|------------------|")


regions = list_aws_regions()
for region in regions: 
    nat_gateways = list_nat(region)
    # Print details about each NAT Gateway
    for nat in nat_gateways['NatGateways']:
        # Extracting data
        nat_gateway_id = nat['NatGatewayId']
        vpc_id = nat['VpcId']
        state = nat['State']
        subnet_id = nat['SubnetId']
        ip_addresses = ", ".join([addr['PublicIp'] for addr in nat.get('NatGatewayAddresses', [])])
        
        # Print table row
        print(f"| {region} | {nat_gateway_id} | {vpc_id} | {state} | {subnet_id} | {ip_addresses} |")
