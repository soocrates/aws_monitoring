import boto3

def list_aws_regions():
    # Initialize the EC2 client with default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()
    
    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions

def list_nacl(region):
  # Create an EC2 client
  ec2 = boto3.client('ec2', region_name=region)

  # Retrieve all network ACLs
  network_acls = ec2.describe_network_acls()

  return network_acls


regions = list_aws_regions()
for region in regions: 
  print(f"___________For Region: {region} ___________")
  network_acls = list_nacl(region)
# Print details about each network ACL
  for acl in network_acls['NetworkAcls']:
      print(f"Network ACL ID: {acl['NetworkAclId']}")
      print(f"VPC ID: {acl['VpcId']}")
      # print(f"Is Default: {'Yes' if acl['IsDefault'] else 'No'}")
      print("Associated Subnets:", ", ".join([assoc['SubnetId'] for assoc in acl['Associations']]))
      print()  # Blank line for better readability
