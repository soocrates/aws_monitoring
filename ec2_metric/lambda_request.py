import json
import requests

def send_instance_data(lambda_url, instance_data):
    """Send instance data to the specified Lambda URL via POST request."""
    # Serialize the instance data to a JSON string with no unnecessary spaces
    compact_instance_data = json.dumps(instance_data, separators=(',', ':'))
    headers = {'Content-Type': 'application/json'}  # Ensure the content type is set to application/json
    response = requests.post(lambda_url, data=compact_instance_data, headers=headers)
    return response.status_code, response.text

def main():
    # Path to the JSON file with EC2 volume metrics
    json_file_path = 'ec2_volume_metrics.json'
    
    # URL of the Lambda function to which the data is to be sent
    function_url = "https://jtw73guowlfexo2uglln2hbgeu0ihero.lambda-url.us-east-1.on.aws/"

    # Read the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Iterate through each instance record in the JSON data
    for instance in data:
        # Send each instance as a payload to the Lambda function
        status_code, response = send_instance_data(function_url, instance)
        # Print detailed information after each request
        print(f"Request sent for Instance ID: {instance.get('InstanceId', 'Unknown')}")
        print(f"Response Status Code: {status_code}")
        print(f"Response Body: {response}")
        print("--------------------------------------------------")  # Separator for readability

if __name__ == "__main__":
    main()
