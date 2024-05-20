import boto3
from datetime import datetime, timedelta, timezone

def list_aws_regions():
    # Initialize the EC2 client with default region
    ec2 = boto3.client('ec2')

    # Retrieve all regions that work with EC2
    response = ec2.describe_regions()
    
    # Extract region names from the response
    regions = [region['RegionName'] for region in response['Regions']]
    return regions

def list_running_instances(region):
    # Initialize a session using your credentials
    session = boto3.Session(region_name=region)
    # Initialize the EC2 client
    ec2 = session.client('ec2')
    
    # Fetch all instances that are currently running
    response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            # Gather all volume IDs
            volume_ids = [vol['Ebs']['VolumeId'] for vol in instance['BlockDeviceMappings'] if 'Ebs' in vol]
            # Fetch volume details for each volume ID
            volumes_info = []
            if volume_ids:
                volumes_response = ec2.describe_volumes(VolumeIds=volume_ids)
                for volume in volumes_response['Volumes']:
                    volume_info = {
                        'Volume ID': volume['VolumeId'],
                        'Type': volume['VolumeType'],
                        'Size': volume['Size'],
                        'IOPS': volume.get('Iops', 'N/A'),  # Not all volume types will have IOPS
                        'Throughput': volume.get('Throughput', 'N/A')  # Throughput info might not be available for all types
                    }
                    volumes_info.append(volume_info)
            # Collect instance details
            instance_info = {
                'Region': region,
                'Instance ID': instance['InstanceId'],
                'Instance Type': instance['InstanceType'],
                'Volumes': volumes_info
            }
            instances.append(instance_info)
    
    return instances
def get_compute_resource_usage(instance_id,metric_name, unit, start_time, end_time, region, period=10800):


    cloudwatch = boto3.client('cloudwatch', region_name=region)
    try:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName=metric_name,
            Dimensions=[
                {'Name': 'InstanceId', 'Value': instance_id},
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Average', 'Sum', 'Minimum', 'Maximum'],
            Unit=unit
        )
        return response['Datapoints']
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def analyze_usage_trends(datapoints):
    if not datapoints:
        return {'Average': 0, 'Sum': 0, 'Minimum': 0, 'Maximum': 0}  # Return zero values if no data points
    average = sum(dp['Average'] for dp in datapoints) / len(datapoints)
    sum_values = sum(dp['Sum'] for dp in datapoints)
    minimum = min(dp['Minimum'] for dp in datapoints)
    maximum = max(dp['Maximum'] for dp in datapoints)
    return {'Average': average, 'Sum': sum_values, 'Minimum': minimum, 'Maximum': maximum}
  

# Specify your region (e.g., 'us-east-1')
regions = list_aws_regions()
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=7)

metrics_info = [
    ('CPUUtilization', 'Percent'),
    ('NetworkIn', 'Bytes'),
    ('NetworkOut', 'Bytes'),
    ('NetworkPacketsIn', 'Count'),
    ('NetworkPacketsOut', 'Count'),
    ('DiskReadBytes', 'Bytes'),
    ('DiskReadOps', 'Count'),
    ('DiskWriteBytes', 'Bytes'),
    ('DiskWriteOps', 'Count'),
    ('CPUCreditBalance', 'Count'),
    ('EBSWriteBytes', 'Bytes'),
    ('EBSReadBytes', 'Bytes'),
    ('EBSWriteOps', 'Count'), 
    ('EBSReadOps', 'Count'),
    ('CPUCreditUsage', 'Count'),
    ('CPUCreditBalance', 'Count')
]

# Iterate over regions
for region in regions: 
    running_instances = list_running_instances(region)
    if running_instances:
        for instance in running_instances:
            # Print table head
            instance_id = instance['Instance ID']
            region = instance['Region']
            print("| Region  | Instance ID       | Instance Type | Volume Info                                    |")
            print("|---------|-------------------|---------------|------------------------------------------------|")

            volume_info_str = ' | '.join([f"{vol['Volume ID']} Type: {vol['Type']}, Size: {vol['Size']} GB, IOPS: {vol['IOPS']}, Throughput: {vol['Throughput']} Mbps" for vol in instance['Volumes']])
            # Print table row
            print(f"| {instance['Region']} | {instance['Instance ID']} | {instance['Instance Type']} | {volume_info_str} |")
            
            print()
            
            for metric_name, unit in metrics_info:
              datapoints = get_compute_resource_usage(instance_id, metric_name, unit, start_time, end_time, region)
              analysis = analyze_usage_trends(datapoints)
              print(f"{metric_name}: {analysis}")
            print()