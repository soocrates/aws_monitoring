import boto3

# Initialize the EC2 client
ec2_client = boto3.client('ec2')

# Describe subnets in the specified VPC
response = ec2_client.describe_subnets(
    Filters=[
        {
            'Name': 'vpc-id',
            'Values': ['vpc-05b90d9cdeb8787b4'],
        },
    ],
)

# Print the response
print(response)
