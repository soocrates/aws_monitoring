import boto3

def list_aws_regions():
    # Initialize the EC2 client with the default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()

    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions

def list_ecs_clusters(region):
    try:
        # Initialize an ECS client for the specified region
        ecs = boto3.client('ecs', region_name=region)

        # List all ECS clusters (returns a list of cluster ARNs)
        ecs_clusters = ecs.list_clusters()
        return ecs_clusters['clusterArns']
    except Exception as e:
        return None

# Print table head
print("| Region       | ECS Cluster ARN                             |")
print("|--------------|---------------------------------------------|")

# Call the function to list ECS clusters in each AWS region
regions = list_aws_regions()
for region in regions:
    ecs_clusters = list_ecs_clusters(region)
    if ecs_clusters:
        for cluster_arn in ecs_clusters:
            # Print table row
            print(f"| {region} | {cluster_arn} |")
