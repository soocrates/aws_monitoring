import boto3

def list_aws_regions():
    # Initialize the EC2 client with default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()
    
    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions

def list_eip(region):
    # Create an EC2 client
    ec2 = boto3.client('ec2', region_name=region)

    # Call describe_addresses to retrieve all Elastic IPs
    addresses = ec2.describe_addresses()
    return addresses


print("| Region       | Elastic IP      | Allocation ID              | Associated instance ID |")
print("|--------------|-----------------|----------------------------|------------------------|")

regions = list_aws_regions()
for region in regions:
    addresses = list_eip(region)

    # Print table head

    # Print out the Elastic IPs
    for address in addresses['Addresses']:
        # Extracting data
        elastic_ip = address['PublicIp']
        allocation_id = address['AllocationId']
        instance_id = address.get('InstanceId', 'N/A')
        
        # Print table row
        print(f"| {region} | {elastic_ip} | {allocation_id} | {instance_id} |")
