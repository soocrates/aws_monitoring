import boto3

def list_aws_regions():
    # Initialize the EC2 client with the default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()

    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions

def check_lambda_existence(region):
    try:
        # Initialize a Lambda client for the specified region
        lambda_client = boto3.client('lambda', region_name=region)

        # List Lambda functions in the region
        lambda_functions = lambda_client.list_functions()

        # Extract Lambda function details
        functions_details = []
        for function in lambda_functions['Functions']:
            function_arn = function['FunctionArn']
            runtime = function['Runtime']
            code_size = function['CodeSize']
            memory_size = function['MemorySize']
            timeout = function['Timeout']
            functions_details.append((function_arn, runtime, code_size, memory_size, timeout))

        return functions_details
    except Exception as e:
        return f"Error retrieving Lambda functions in {region}: {e}"

# Print table head
print("| Region       | Lambda Function ARN                          | Runtime | CodeSize | MemorySize | Timeout |")
print("|--------------|---------------------------------------------|---------|----------|------------|---------|")

# Call the function to check Lambda existence in each AWS region
regions = list_aws_regions()
for region in regions:
    lambda_functions = check_lambda_existence(region)
    if lambda_functions:
        for function_details in lambda_functions:
            # Print table row
            print(f"| {region} | {' | '.join(map(str, function_details))} |")
