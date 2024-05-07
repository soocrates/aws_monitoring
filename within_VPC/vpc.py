import boto3

region = "us-west-2"
vpc_id = 'vpc-08b9678dc70652eca'

def list_subnet(vpc_id, region):
    ec2_client = boto3.client('ec2', region_name=region)
  
    try:
        response = ec2_client.describe_subnets(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc_id]},
            ],
        )
        subnets = response['Subnets']
        if not subnets:
            print(f"No subnets found for VPC ID {vpc_id}")
        return subnets
    except Exception as e:
        print(f"Error retrieving subnets for VPC ID {vpc_id}: {str(e)}")
        return []

def list_route_table(vpc_id, region):
  ec2_client = boto3.client('ec2', region_name=region)

  # Describe route tables in a specific VPC
  response = ec2_client.describe_route_tables(
      Filters=[
          {
              'Name': 'vpc-id',
              'Values': [vpc_id]  # Replace 'vpc-yourvpcid' with your VPC ID
          }
      ]
  )
  return response

def list_nat(vpc_id, region):
    # Create an EC2 client
    ec2 = boto3.client('ec2', region_name=region)

    # Retrieve all NAT Gateways
    response = ec2.describe_nat_gateways(
        Filters=[
            {
                'Name': 'vpc-id',
                'Values': [vpc_id]  # Replace 'vpc-yourvpcid' with your VPC ID
            }
        ]
    )
    return response['NatGateways']
def list_igw(vpc_id, region):
    # Create an EC2 client
    ec2 = boto3.client('ec2', region_name=region)

    # Retrieve all internet gateways
    response = ec2.describe_internet_gateways()
    igws = []

    # Filter IGWs by checking if they are attached to the specified VPC ID
    for igw in response['InternetGateways']:
        for attachment in igw['Attachments']:
            if attachment['VpcId'] == vpc_id:
                igws.append(igw)

    return igws


print("_______________________________________________________")
print(f"_________VPC ID: {vpc_id}__________")
print("_______________________________________________________")
subnets = list_subnet(vpc_id, region)
if subnets:
    for subnet in subnets:
        print(f"Subnet ID: {subnet['SubnetId']} - CIDR: {subnet['CidrBlock']} - AZ: CIDR: {subnet['AvailabilityZone']} ")
else:
    print(f"No subnets found for VPC ID {vpc_id}")
route_tables = list_route_table(vpc_id, region)
print("_______________________________________________________")
for route_table in route_tables['RouteTables']:
  print(f"Route Table ID: {route_table['RouteTableId']}")  
    
print("_______________________________________________________")
print("_______________________________________________________")
nat_gateways = list_nat(vpc_id, region)
for nat in nat_gateways:
    print(nat['NatGatewayId'])
print("_______________________________________________________")
igw_gateways = list_igw(vpc_id, region)
for igw in igw_gateways:
    print(igw['InternetGatewayId'])