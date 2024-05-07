import boto3

def list_aws_regions():
    # Initialize the EC2 client with default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()
    
    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions
print("| Region       | Volume ID          | Type | Size | IOPS | Throughput | Volume state | Attach resources |")
print("|--------------|---------------------|------|------|------|------------|--------------|------------------|")

regions = list_aws_regions()
for region in regions: 
    # Create an EC2 client
    ec2 = boto3.client('ec2', region_name=region)  # Modify the region as necessary

    # Describe all volumes
    volumes = ec2.describe_volumes()
    print(volumes)

    # Print table head

    # # Print details for each volume
    # for volume in volumes['Volumes']:
    #     # Extracting data
    #     volume_id = volume['VolumeId']
    #     volume_type = volume['VolumeType']
    #     size = f"{volume['Size']} GiB"
    #     iops = volume.get('Iops', 'N/A')
    #     throughput = f"{volume.get('Throughput', 'N/A')} MB/s"
    #     volume_state = volume['State']
    #     attach_resources = "No attachments" if not volume['Attachments'] else ", ".join([attachment['InstanceId'] for attachment in volume['Attachments']])
        
    #     # Print table row
    #     print(f"| {region} | {volume_id} | {volume_type} | {size} | {iops} | {throughput} | {volume_state} | {attach_resources} |")
