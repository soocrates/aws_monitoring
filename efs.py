import boto3

def list_aws_regions():
    # Initialize the EC2 client with default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()
    
    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions

def list_efs_file_systems(region):
    # Create an EFS client for the specified region
    efs = boto3.client('efs', region_name=region)

    # Initialize a list to hold all file systems
    file_systems = []

    # Retrieve all EFS file systems
    paginator = efs.get_paginator('describe_file_systems')
    for page in paginator.paginate():
        file_systems.extend(page['FileSystems'])

    return file_systems

# Specify the region you are interested in
regions = list_aws_regions()

# Print details about each file system
for region in regions: 
  print(f"___________For Region: {region} ___________")
  # Get the list of EFS file systems
  efs_file_systems = list_efs_file_systems(region)
  print(efs_file_systems)
  # for fs in efs_file_systems:
  #     print(f"File System ID: {fs['FileSystemId']}")
  #     print(f"Name: {fs.get('Name', 'No name provided')}")
  #     print(f"Creation Time: {fs['CreationTime']}")
  #     print(f"Life Cycle State: {fs['LifeCycleState']}")
  #     print(f"Number of Mount Targets: {len(fs['MountTargets'])}")
  #     print()  # Print a newline for better readability
