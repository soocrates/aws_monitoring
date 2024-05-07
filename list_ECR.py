import boto3

def list_aws_regions():
    """List all available AWS regions for ECR."""
    ec2 = boto3.client('ec2')
    response = ec2.describe_regions()
    # Include only regions where ECR is available
    return [region['RegionName'] for region in response['Regions']]

def list_ecr_repositories(region):
    """List all ECR repositories for a given AWS region."""
    ecr = boto3.client('ecr', region_name=region)
    paginator = ecr.get_paginator('describe_repositories')
    repositories = []
    for page in paginator.paginate():
        repositories.extend(page['repositories'])
    return repositories

def main():
    regions = list_aws_regions()
    print("| Region | Repository Name |")
    print("|--------|-----------------|")
    for region in regions:
        repositories = list_ecr_repositories(region)
        for repo in repositories:
            print(f"{region} | {repo['repositoryName']} |")

if __name__ == '__main__':
    main()