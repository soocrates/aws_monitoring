import boto3

# Create an Auto Scaling client
autoscaling = boto3.client('autoscaling', region_name='us-west-2')

# Retrieve all Auto Scaling groups
response = autoscaling.describe_auto_scaling_groups()

# Print details about each Auto Scaling group
for asg in response['AutoScalingGroups']:
    print(f"Auto Scaling Group Name: {asg['AutoScalingGroupName']}")
    print(f"Launch Configuration: {asg.get('LaunchConfigurationName', 'N/A')}")
    print(f"Desired Capacity: {asg['DesiredCapacity']}")
    print(f"Minimum Size: {asg['MinSize']}")
    print(f"Maximum Size: {asg['MaxSize']}")
    print("Instance IDs:", ", ".join([instance['InstanceId'] for instance in asg['Instances']]))
    print()  # Blank line for better readability
