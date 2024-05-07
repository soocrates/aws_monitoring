import boto3

def list_aws_regions():
    # Initialize the EC2 client with the default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()

    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions

def list_rds_instances(region):
    try:
        # Initialize an RDS client for the specified region
        rds = boto3.client('rds', region_name=region)

        # List RDS instances in the region
        rds_instances = rds.describe_db_instances()

        # Extract RDS instance details
        instances_details = []
        for instance in rds_instances['DBInstances']:
            instance_identifier = instance['DBInstanceIdentifier']
            engine = instance['Engine']
            engine_version = instance['EngineVersion']
            instance_class = instance['DBInstanceClass']
            status = instance['DBInstanceStatus']
            allocated_storage = instance['AllocatedStorage']
            storage_type = instance['StorageType']
            iops = instance.get('Iops', 'N/A')  # Some instances may not have IOPS
            instances_details.append((instance_identifier, engine, engine_version, instance_class, status, allocated_storage, storage_type, iops))

        return instances_details
    except Exception as e:
        return f"Error retrieving RDS instances in {region}: {e}"

# Print table head
print("| Region       | Instance Identifier | Engine | Engine Version | Instance Class | Status | Allocated Storage (GB) | Storage Type | IOPS |")
print("|--------------|----------------------|--------|----------------|----------------|--------|-------------------------|--------------|------|")

# Call the function to list RDS instances in each AWS region
regions = list_aws_regions()
for region in regions:
    rds_instances = list_rds_instances(region)
    if rds_instances:
        for instance_details in rds_instances:
            # Print table row
            print(f"| {region} | {' | '.join(map(str, instance_details))} |")
