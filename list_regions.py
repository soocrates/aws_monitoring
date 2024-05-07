import boto3
import logging
from botocore.exceptions import ClientError

def list_aws_regions():
    # Initialize the EC2 client with default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()
    
    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions
  
# logging.basicConfig(level=logging.DEBUG)

try:
    regions = list_aws_regions()
    print(regions)
except ClientError as e:
    logging.error(e)