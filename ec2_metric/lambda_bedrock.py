import boto3
import os

def lambda_handler(event, context):
    # Extract the bucket name and key from the event that triggered the Lambda
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Create an S3 client
    s3_client = boto3.client('s3')

    try:
        # Fetch the object based on the key provided in the event
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        
        # Read the content of the file
        content = response['Body'].read().decode('utf-8')
        print(content)  # This prints the content to the Lambda log

        return {
            'statusCode': 200,
            'body': content
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': str(e)
        }
