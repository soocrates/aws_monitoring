import boto3

def get_ec2_client(region):
    return boto3.client('ec2', region_name=region)

def find_route_table_for_subnet(ec2_client, subnet_id):
    # Fetch all route tables and filter by associations to find the relevant route table for a given subnet
    route_tables = ec2_client.describe_route_tables().get('RouteTables', [])
    for rt in route_tables:
        for assoc in rt.get('Associations', []):
            if assoc.get('SubnetId') == subnet_id:
                return rt['RouteTableId']
    return None

def find_gateway_for_route_table(ec2_client, route_table_id):
    # Check routes in the specified route table for any references to IGWs or NAT Gateways
    route_tables = ec2_client.describe_route_tables(RouteTableIds=[route_table_id]).get('RouteTables', [])
    if route_tables:
        routes = route_tables[0].get('Routes', [])
        for route in routes:
            if 'GatewayId' in route and route['GatewayId'].startswith('igw-'):
                return route['GatewayId'], 'Internet Gateway'
            elif 'NatGatewayId' in route:
                return route['NatGatewayId'], 'NAT Gateway'
    return None, None

region = 'us-west-2'
ec2_client = get_ec2_client(region)
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

# Example subnet ID
subnet_ids = list_subnet(vpc_id, region)  # Replace 'subnet-xxxxxxxx' with actual subnet ID

# Find route table associated with a subnet
for subnet in subnet_ids:
  route_table_id = find_route_table_for_subnet(ec2_client, subnet['SubnetId'])
  if route_table_id:
      print(f"Subnet ID {subnet['SubnetId']} is associated with Route Table ID {route_table_id}")

      # Find gateway associated with the route table
      gateway_id, gateway_type = find_gateway_for_route_table(ec2_client, route_table_id)
      if gateway_id:
          print(f"Route Table ID {route_table_id} is connected to {gateway_type} {gateway_id}")
      else:
          print(f"No Internet or NAT Gateway is associated with Route Table ID {route_table_id}")
  else:
      print(f"No route table found for Subnet ID {subnet['SubnetId']}")
