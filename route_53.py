import boto3

def list_aws_regions():
    # Initialize the EC2 client with default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()
    
    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions


def list_route53_hosted_zones(region):
    # Initialize a Route 53 client for the specified region
    route53 = boto3.client('route53', region_name=region)

    # List hosted zones in Route 53
    response = route53.list_hosted_zones()

    hosted_zones = response.get('HostedZones', [])
    
    return hosted_zones


# Get all AWS regions
regions = list_aws_regions()

# Print table headers
print("| Region | Hosted Zone ID | Name |")
print("|--------|----------------|------|")

# Iterate over each region
for region in regions:
    # List hosted zones in Route 53 for the region
    hosted_zones = list_route53_hosted_zones(region)
    
    # Print hosted zones
    for zone in hosted_zones:
        print(f"| {region} | {zone['Id'].split('/')[-1]} | {zone['Name']} |")
