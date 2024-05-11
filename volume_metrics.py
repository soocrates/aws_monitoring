import boto3
from datetime import datetime, timedelta

def fetch_metrics(cloudwatch_client, metric_name, namespace, dimensions, start_time, end_time, period, stat):
    metric_data = cloudwatch_client.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'm1',
                'MetricStat': {
                    'Metric': {
                        'Namespace': namespace,
                        'MetricName': metric_name,
                        'Dimensions': dimensions
                    },
                    'Period': period,
                    'Stat': stat
                },
                'ReturnData': True
            }
        ],
        StartTime=start_time,
        EndTime=end_time
    )
    # Returning the last data point if available
    return metric_data['MetricDataResults'][0]['Values'][-1] if metric_data['MetricDataResults'][0]['Values'] else 'N/A'

def list_aws_regions():
    ec2 = boto3.client('ec2')
    response = ec2.describe_regions()
    return [region['RegionName'] for region in response['Regions']]

print("| Region       | Volume ID          | Type | Size | IOPS | Throughput | Volume state | Attach resources | Read Ops | Write Ops |")
print("|--------------|---------------------|------|------|------|------------|--------------|------------------|----------|-----------|")

regions = list_aws_regions()
for region in regions: 
    ec2 = boto3.client('ec2', region_name=region)
    cloudwatch = boto3.client('cloudwatch', region_name=region)

    # Describe all volumes
    volumes = ec2.describe_volumes()

    for volume in volumes['Volumes']:
        volume_id = volume['VolumeId']
        volume_type = volume['VolumeType']
        size = f"{volume['Size']} GiB"
        iops = volume.get('Iops', 'N/A')
        throughput = f"{volume.get('Throughput', 'N/A')} MB/s"
        volume_state = volume['State']
        attach_resources = ", ".join([attachment['InstanceId'] for attachment in volume['Attachments']]) if volume['Attachments'] else "No attachments"

        # Fetch CloudWatch metrics for volume
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)  # Last 1 hour
        period = 300  # 5 minutes
        
        read_ops = fetch_metrics(cloudwatch, 'VolumeReadOps', 'AWS/EBS', [{'Name': 'VolumeId', 'Value': volume_id}], start_time, end_time, period, 'Sum')
        write_ops = fetch_metrics(cloudwatch, 'VolumeWriteOps', 'AWS/EBS', [{'Name': 'VolumeId', 'Value': volume_id}], start_time, end_time, period, 'Sum')
        
        # Print table row
        print(f"| {region} | {volume_id} | {volume_type} | {size} | {iops} | {throughput} | {volume_state} | {attach_resources} | {read_ops} | {write_ops} |")
