import boto3

def list_aws_regions():
    # Initialize the EC2 client with default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()
    
    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions

def list_running_instances(region):
    # Initialize a session using your credentials
    session = boto3.Session(region_name=region)
    # Initialize the EC2 client
    ec2 = session.client('ec2')
    
    # Fetch all instances that are currently running
    response = ec2.describe_instances()
    
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            # You can add more details as needed
            instance_info = {
                'Region': region,
                'Instance ID': instance['InstanceId'],
                'Instance Type': instance['InstanceType'],
                'Public IP': instance.get('PublicIpAddress')
            }
            instances.append(instance_info)
    
    return instances

# Specify your region (e.g., 'us-east-1')
regions = list_aws_regions()

# Print table head
print("| Region  | Instance ID       | Instance Type | Public IP |")
print("|---------|-------------------|---------------|-----------|")

# Iterate over regions
for region in regions: 
    running_instances = list_running_instances(region)
    if running_instances:
        for instance in running_instances:
            # Print table row
            print(f"| {instance['Region']} | {instance['Instance ID']} | {instance['Instance Type']} | {instance['Public IP']}|")