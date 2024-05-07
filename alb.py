import boto3

def list_albs(region):
    # Initialize an ELBv2 client for the specified region
    elbv2 = boto3.client('elbv2', region_name=region)

    # List all Load Balancers in the region
    response = elbv2.describe_load_balancers()

    # Filter ALBs from the response
    albs = [lb for lb in response['LoadBalancers'] if lb['Type'] == 'application']

    return albs

# Call the function to list ALBs in a specific AWS region
region = 'us-west-2'  # Change to your desired region
albs = list_albs(region)

print("Application Load Balancers:")
for alb in albs:
    print(f"Name: {alb['LoadBalancerName']}")
    print(f"DNS Name: {alb['DNSName']}")
    print(f"VPC ID: {alb['VpcId']}")
    print(f"Availability Zones: {', '.join(alb['AvailabilityZones'])}")
    print(f"Type: {alb['Type']}")
    print(f"Date created: {alb['CreatedTime']}")
    print()
