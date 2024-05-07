import boto3

def list_aws_regions():
    # Initialize the EC2 client with default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()
    
    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions

def list_eks_cluster(region):
    # Create an EKS client for the specific region
    eks = boto3.client('eks', region_name=region)

    # List all EKS clusters (returns a list of cluster names)
    eks_clusters = eks.list_clusters()
    
    # Retrieve details about each cluster
    clusters_info = []
    if eks_clusters['clusters']:
        for cluster_name in eks_clusters['clusters']:
            cluster_info = eks.describe_cluster(name=cluster_name)
            cluster = cluster_info['cluster']
            clusters_info.append({
                'name': cluster['name'],
                'arn': cluster['arn'],
                'status': cluster['status'],
                'created_at': cluster['createdAt'],
                'endpoint': cluster['endpoint'],
                'version': cluster['version'],
                'role_arn': cluster['roleArn'],
                'vpc_config': cluster['resourcesVpcConfig']
            })
    return clusters_info

regions = list_aws_regions()
for region in regions: 
    print(f"___________For Region: {region} ___________")
    eks_clusters_info = list_eks_cluster(region)
    if eks_clusters_info:
        for cluster in eks_clusters_info:
            print(f"Cluster Name: {cluster['name']}")
            print(f"Cluster ARN: {cluster['arn']}")
            print(f"Status: {cluster['status']}")
            print(f"Created At: {cluster['created_at']}")
            print(f"Endpoint: {cluster['endpoint']}")
            print(f"Kubernetes Version: {cluster['version']}")
            print(f"Role ARN: {cluster['role_arn']}")
            print(f"VPC Configuration: {cluster['vpc_config']}")
            print()  # Blank line for better readability
    else:
        print("No EKS clusters found.")
