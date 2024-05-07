import boto3

# Initialize a session using the default profile
session = boto3.Session()

# Create a Cost Explorer client
cost_explorer = session.client('ce')

# Define the time period for the report
time_period = {
    'Start': '2024-04-06',
    'End': '2024-05-01'
}

# Fetch the cost and usage data
response = cost_explorer.get_cost_and_usage(
    TimePeriod=time_period,
    Granularity='MONTHLY',
    Metrics=["UnblendedCost", "UsageQuantity"],
    GroupBy=[
        {'Type': 'DIMENSION', 'Key': 'SERVICE'},
        {'Type': 'DIMENSION', 'Key': 'REGION'}
    ]
)

def process_data(groups):
    region_data = {}
    # Organize data by region, filtering out zero costs
    for item in groups:
        region = item['Keys'][1]
        service = item['Keys'][0]
        cost = float(item['Metrics']['UnblendedCost']['Amount'])
        if cost > 0:  # Only consider non-zero costs
            if region not in region_data:
                region_data[region] = []
            region_data[region].append({
                'Service': service,
                'Cost': cost
            })

    # Filter out regions with no costs
    filtered_region_data = {region: services for region, services in region_data.items() if any(service['Cost'] > 0 for service in services)}
    return filtered_region_data

# Process the data
groups = response['ResultsByTime'][0]['Groups']
processed_data = process_data(groups)

# Print the header
header = ['Region', 'Service', 'Cost']
print(f"| {header[0]:<15} | {header[1]:<50} | {header[2]:>10} |")
print(f"|{'-'*16}|{'-'*51}|{'-'*11}|")

# Iterate through the regions and services
for region, services in processed_data.items():
    for service in services:
        service_name = service['Service']
        cost = service['Cost']
        print(f"| {region:<15} | {service_name:<50} | {cost:>10.2f} |")
