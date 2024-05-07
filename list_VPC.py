import boto3

def list_aws_regions():
    # Initialize the EC2 client with default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()
    
    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions

def list_vpcs(region):
    try:
        # Initialize the EC2 client
        ec2 = boto3.client('ec2', region_name=region)

        # Retrieve list of VPCs
        response = ec2.describe_vpcs()

        # Extract VPC details
        vpcs = response['Vpcs']

        vpc_details = []

        # Collect details for each VPC
        for vpc in vpcs:
            vpc_id = vpc['VpcId']
            cidr_block = vpc['CidrBlock']
            state = vpc['State']
            default = vpc['IsDefault']

            # Append details to the list
            vpc_details.append([region, vpc_id, cidr_block, state, default])

        return vpc_details

    except Exception as e:
        print(f"An error occurred: {e}")

# Call the function to list VPCs

regions = list_aws_regions()

# Print table head
print("| Region | VPC ID         | CIDR           | State    | Default |")
print("|--------|----------------|----------------|----------|---------|")

# Iterate over regions
for region in regions: 
    vpc_details = list_vpcs(region)
    if vpc_details:
        for details in vpc_details:
            # Print table row
            print(f"| {details[0]} | {details[1]} | {details[2]} | {details[3]} | {details[4]} |")
    else:
        print("No VPCs found in this region.")
