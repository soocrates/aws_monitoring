import boto3

def list_aws_regions():
    # Initialize the EC2 client with default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()
    
    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions

def get_cost_data(session, aws_regions, time_period):
    # Create a Cost Explorer client
    cost_explorer = session.client('ce')

    # Fetch the cost and usage data with monthly granularity
    return cost_explorer.get_cost_and_usage(
        TimePeriod=time_period,
        Granularity='MONTHLY',
        Metrics=["UnblendedCost"],
        GroupBy=[
            {'Type': 'DIMENSION', 'Key': 'SERVICE'},
            {'Type': 'DIMENSION', 'Key': 'REGION'}
        ]
    )

def process_data(results, regions):
    # Initialize data structure with all regions and months
    data = []

    # Organize data by region and month for EC2 only
    for monthly_data in results:
        month = monthly_data['TimePeriod']['Start'][:7]  # Format YYYY-MM
        for item in monthly_data['Groups']:
            region = item['Keys'][1]
            service = item['Keys'][0]
            cost = float(item['Metrics']['UnblendedCost']['Amount'])
            if service == 'Amazon Elastic Compute Cloud - Compute' and region in regions:
                data.append({
                    'Region': region,
                    'Month': month,
                    'Cost': cost
                })

    return data

# Initialize a session using the default profile
session = boto3.Session()

# Fetch the available regions dynamically
aws_regions = list_aws_regions()

# Define the time period for the report
time_period = {
    'Start': '2023-10-01',
    'End': '2024-05-11'
}

# Fetch the data
response = get_cost_data(session, aws_regions, time_period)

# Process the data
processed_data = process_data(response['ResultsByTime'], aws_regions)

# Print the formatted table
print("| Region         | Month       | Cost     |")
print("|----------------|-------------|----------|")
for entry in processed_data:
    print(f"| {entry['Region']:<14} | {entry['Month']:<11} | {entry['Cost']:8.2f} |")
