import boto3

def list_nat(vpc_id,region):
    # Create an EC2 client
    ec2 = boto3.client('ec2', region_name=region)

    # Retrieve all NAT Gateways
    nat_gateways = ec2.describe_nat_gateways(
      Filters=[
          {
              'Name': 'vpc-id',
              'Values': [vpc_id]  # Replace 'vpc-yourvpcid' with your VPC ID
          }
      ]
    )
    print(nat_gateways)
    return nat_gateways

region = "us-west-2"
vpc_id = 'vpc-08b9678dc70652eca'

nat_gateways = list_nat(vpc_id,region)
