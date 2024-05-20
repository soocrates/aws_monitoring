import boto3
from datetime import datetime, timedelta, timezone

# Initialize the CloudWatch client
cloudwatch = boto3.client('cloudwatch')
# Initialize the EC2 client
ec2 = boto3.client('ec2')

# Specify the instance ID
instance_id = 'i-0687fdc27af20f058'

def get_compute_resource_usage(instance_id, metric_name, unit, start_time, end_time, period=10800):
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
        if not response['Datapoints']:
            print(f"No data points found for {metric_name}")
        return response['Datapoints']
    
    except Exception as e:
        print(f"An error occurred fetching {metric_name}: {e}")
        return []

def analyze_usage_trends(datapoints):
    if not datapoints:
        return {'Average': 0, 'Sum': 0, 'Minimum': 0, 'Maximum': 0}  # Return zero values if no data points
    average = sum(dp['Average'] for dp in datapoints if 'Average' in dp) / len(datapoints)
    sum_values = sum(dp['Sum'] for dp in datapoints if 'Sum' in dp)
    minimum = min(dp['Minimum'] for dp in datapoints if 'Minimum' in dp)
    maximum = max(dp['Maximum'] for dp in datapoints if 'Maximum' in dp)
    return {'Average': average, 'Sum': sum_values, 'Minimum': minimum, 'Maximum': maximum}

# Specify the time range for the analysis (e.g., last 7 days)
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=7)

# Metrics to retrieve
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
    ('CPUCreditUsage', 'Count'),
    ('CPUCreditBalance', 'Count'),
    ('EBSWriteBytes', 'Bytes'),
    ('EBSReadBytes', 'Bytes'),
    ('EBSWriteOps', 'Count'), 
    ('EBSReadOps', 'Count')
]

# Retrieve and analyze data for each metric
for metric_name, unit in metrics_info:
    datapoints = get_compute_resource_usage(instance_id, metric_name, unit, start_time, end_time)
    analysis = analyze_usage_trends(datapoints)
    print(f"{metric_name}: {analysis}")
