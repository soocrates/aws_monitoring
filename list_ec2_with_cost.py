import boto3
from datetime import datetime

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
    response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            # Extract launch time and format it
            launch_time = instance['LaunchTime']
            formatted_launch_time = launch_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Instance information including launch time
            instance_info = {
                'Region': region,
                'Instance ID': instance['InstanceId'],
                'Instance Type': instance['InstanceType'],
                'Public IP': instance.get('PublicIpAddress'),
                'Launch Time': formatted_launch_time
            }
            instances.append(instance_info)
    
    return instances

# List all regions
regions = list_aws_regions()

# Print table head
print("| Region  | Instance ID       | Instance Type | Public IP | Launch Time         |")
print("|---------|-------------------|---------------|-----------|---------------------|")

# Iterate over regions
for region in regions: 
    running_instances = list_running_instances(region)
    for instance in running_instances:
        # Print table row
        print(f"| {instance['Region']} | {instance['Instance ID']} | {instance['Instance Type']} | {instance['Public IP'] or 'None'} | {instance['Launch Time']} |")
