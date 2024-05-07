import boto3

def list_aws_regions():
    # Initialize the EC2 client with default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()
    
    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions
  
def list_rds_instances(region):
      # Initialize a session using your credentials
      session = boto3.Session(region_name=region)
      # Initialize the RDS client
      rds = session.client('rds')

      # Call the RDS describe_db_instances method
      response = rds.describe_db_instances()

      # Extract and return instance details
      instances = response['DBInstances']
      return instances

# Call the function to list RDS instances in us-east-1 region
regions = list_aws_regions()
for region in regions: 
  print(f"___________For Region: {region} ___________")
  rds_instances = list_rds_instances(region)
  print(rds_instances)