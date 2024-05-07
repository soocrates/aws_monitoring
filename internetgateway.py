import boto3

# Initialize the EC2 client
ec2_client = boto3.client('ec2')

response = ec2_client.describe_internet_gateways(
    Filters=[
        {
            'Name': 'attachment.vpc-id',
            'Values': [
                'vpc-08b9678dc70652eca',
            ],
        },
    ],
)

print(response)