# import boto3

# # Initialize the EC2 client
# ec2_client = boto3.client('ec2', region_name='us-east-1')

# # Describe route tables in a specific VPC
# response = ec2_client.describe_route_tables(
#     Filters=[
#         {
#             'Name': 'vpc-id',
#             'Values': ['vpc-d0b48baa']  # Replace 'vpc-yourvpcid' with your VPC ID
#         }
#     ]
# )

# # Loop through the route tables to find associated subnets and routes
# for route_table in response['RouteTables']:
#     print(f"Route Table ID: {route_table['RouteTableId']}")    
#     # Checking routes for gateway IDs
#     if 'Routes' in route_table:
#         for route in route_table['Routes']:
#             if 'GatewayId' in route and route['GatewayId'] != 'local':
#                 print(f"Internet Gateway ID: {route['GatewayId']}")
#     else:
#         print("No routes found.")


import boto3

def find_route_table_by_subnet(ec2_client, subnet_id):
    """
    Find the route table associated with a given subnet.
    """
    # Describe route tables that are associated with the specified subnet
    response = ec2_client.describe_route_tables(
        Filters=[
            {
                'Name': 'association.subnet-id',
                'Values': [subnet_id]
            }
        ]
    )

    route_tables = response.get('RouteTables', [])
    if not route_tables:
        print(f"No route table found for subnet ID {subnet_id}")
        return None

    # Assuming a subnet is typically associated with only one route table
    route_table_id = route_tables[0]['RouteTableId']
    print(f"Route Table ID associated with subnet {subnet_id}: {route_table_id}")
    return route_table_id

# Initialize the EC2 client
ec2_client = boto3.client('ec2', region_name='us-east-1')

# Specify the Subnet ID
subnet_id = 'subnet-0d9ca2075b537d7f2'  # Replace 'subnet-yoursubnetid' with your Subnet ID

# Find the route table by subnet ID
route_table_id = find_route_table_by_subnet(ec2_client, subnet_id)


