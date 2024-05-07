import boto3

# Initialize the EC2 client
ec2_client = boto3.client('ec2')

# Describe VPCs with a specific VPC ID
response = ec2_client.describe_vpcs(
    Filters=[
        {
            'Name': 'vpc-id',
            'Values': ['vpc-08b9678dc70652eca'],
        },
    ],
)

# Print the response
print(response)
