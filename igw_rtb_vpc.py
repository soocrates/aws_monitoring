import boto3

def find_internet_gateways_by_vpc(ec2_client, vpc_id):
    """
    Find internet gateways attached to a specific VPC.
    """
    response = ec2_client.describe_internet_gateways(
        Filters=[
            {'Name': 'attachment.vpc-id', 'Values': [vpc_id]}
        ]
    )
    return response

# Initialize the EC2 client
ec2_client = boto3.client('ec2', region_name='us-west-2')

# Specify the VPC ID
vpc_id = 'vpc-08b9678dc70652eca'  # Replace 'vpc-yourvpcid' with your VPC ID

# Step 1: Find internet gateways by VPC
internet_gateways = find_internet_gateways_by_vpc(ec2_client, vpc_id)
print(internet_gateways)

