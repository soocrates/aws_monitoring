import boto3

def list_aws_regions():
    # Initialize the EC2 client with default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()
    
    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions

def describe_dynamodb_table(region, table_name):
    # Initialize a session using your credentials
    session = boto3.Session(region_name=region)
    # Initialize the DynamoDB client
    dynamodb = session.client('dynamodb')
    
    # Describe the DynamoDB table
    response = dynamodb.describe_table(TableName=table_name)
    
    return response['Table']

def list_dynamodb_tables(region):
    # Initialize a session using your credentials
    session = boto3.Session(region_name=region)
    # Initialize the DynamoDB client
    dynamodb = session.client('dynamodb')
    
    # Initialize an empty list to store table details
    tables_info = []
    
    # Call the DynamoDB list_tables method
    response = dynamodb.list_tables()
    
    # Add table details to the list
    if 'TableNames' in response:
        for table_name in response['TableNames']:
            table_info = describe_dynamodb_table(region, table_name)
            tables_info.append(table_info)
    
    # Check for more tables if the response is paginated
    while 'LastEvaluatedTableName' in response:
        response = dynamodb.list_tables(
            ExclusiveStartTableName=response['LastEvaluatedTableName']
        )
        for table_name in response['TableNames']:
            table_info = describe_dynamodb_table(region, table_name)
            tables_info.append(table_info)
    
    return tables_info

# Specify your region (e.g., 'us-east-1')
regions = list_aws_regions()

# Print table head
print("| Region  | Table Name       | Status | Item Count | Size (Bytes) |")
print("|---------|------------------|--------|------------|--------------|")

# Iterate over regions
for region in regions: 
    dynamodb_tables = list_dynamodb_tables(region)
    if dynamodb_tables:
        for table in dynamodb_tables:
            # Extract table information
            table_name = table['TableName']
            status = table['TableStatus']
            item_count = table['ItemCount']
            size_bytes = table['TableSizeBytes']
            # Print table row
            print(f"| {region} | {table_name} | {status} | {item_count} | {size_bytes} |")
