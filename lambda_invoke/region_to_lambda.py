import boto3
import requests
from botocore.exceptions import ClientError

def list_aws_regions():
    # Initialize the EC2 client with default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()
    
    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions

def send_data_to_lambda_function(data, function_url):
    try:
        response = requests.post(function_url, json=data)
        if response.status_code == 200:
            print("Data sent to Lambda function successfully")
        else:
            print("Failed to send data to Lambda function. Status code:", response.status_code)
    except Exception as e:
        print("Error sending data to Lambda function:", e)

# Get the list of AWS regions
regions = list_aws_regions()

# Send the regions data to Lambda function
function_url = "https://jtw73guowlfexo2uglln2hbgeu0ihero.lambda-url.us-east-1.on.aws/"
response_text = send_data_to_lambda_function(regions, function_url)
print("Response from Lambda function:", response_text)