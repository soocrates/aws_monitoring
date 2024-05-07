import boto3

# Initialize the EC2 client
ec2_client = boto3.client('ec2')

# Describe Internet Gateways
response = ec2_client.describe_internet_gateways()

# Extract Internet Gateway IDs
internet_gateway_ids = [igw['InternetGatewayId'] for igw in response['InternetGateways']]

# Print the Internet Gateway IDs
print("Internet Gateway IDs:")
for igw_id in internet_gateway_ids:
    print(igw_id)
