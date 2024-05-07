import boto3

def list_s3_buckets():
    try:
        # Initialize the S3 client
        s3 = boto3.client('s3')

        # Retrieve list of S3 buckets
        response = s3.list_buckets()
        # Iterate through each bucket
        for bucket in response['Buckets']:
            bucket_name = bucket['Name']
            creation_date = bucket['CreationDate']

            # Print simple details for each bucket
            print(f"Bucket Name: {bucket_name}______Created at: {creation_date}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Call the function to list S3 buckets with simple details
list_s3_buckets()
