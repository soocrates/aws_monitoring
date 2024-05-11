import boto3
from datetime import datetime, timedelta, timezone
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

def list_aws_regions():
    ec2 = boto3.client('ec2')
    response = ec2.describe_regions()
    return [region['RegionName'] for region in response['Regions']]

def list_running_instances(region):
    session = boto3.Session(region_name=region)
    ec2 = session.client('ec2')
    response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            volume_ids = [vol['Ebs']['VolumeId'] for vol in instance['BlockDeviceMappings'] if 'Ebs' in vol]
            volumes_info = []
            if volume_ids:
                volumes_response = ec2.describe_volumes(VolumeIds=volume_ids)
                for volume in volumes_response['Volumes']:
                    volume_info = {
                        'VolumeId': volume['VolumeId'],
                        'Type': volume['VolumeType'],
                        'Size': f"{volume['Size']} GB",
                    }
                    volumes_info.append(volume_info)
            instance_info = {
                'Region': region,
                'InstanceId': instance['InstanceId'],
                'InstanceType': instance['InstanceType'],
                'PublicIP': instance.get('PublicIpAddress', None),
                'Volumes': volumes_info
            }
            instances.append(instance_info)
    return instances

def get_cloudwatch_metrics(client, namespace, metric_name, unit, dimensions, start_time, end_time, period=3600):
    response = client.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        StartTime=start_time,
        EndTime=end_time,
        Period=period,
        Statistics=['Minimum', 'Maximum', 'Average'],
        Unit=unit
    )
    datapoints = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])  # Sort to ensure latest datapoint is used
    if datapoints:
        return {
            'Minimum': datapoints[-1]['Minimum'],
            'Maximum': datapoints[-1]['Maximum'],
            'Average': datapoints[-1]['Average']
        }
    else:
        return {'Minimum': '--', 'Maximum': '--', 'Average': '--'}

def fetch_instance_metrics(cloudwatch, instance, start_time, end_time):
    return {
        'InstanceMetrics': {
            metric_name: get_cloudwatch_metrics(
                cloudwatch, 'AWS/EC2', metric_name, unit,
                [{'Name': 'InstanceId', 'Value': instance['InstanceId']}],
                start_time, end_time
            )
            for metric_name, unit in [
                ('CPUUtilization', 'Percent'),
                ('NetworkIn', 'Bytes'),
                ('NetworkOut', 'Bytes'),
                ('NetworkPacketsIn', 'Count'),
                ('NetworkPacketsOut', 'Count'),
                ('DiskReadBytes', 'Bytes'),
                ('DiskReadOps', 'Count'),
                ('DiskWriteBytes', 'Bytes'),
                ('DiskWriteOps', 'Count'),
                ('EBSWriteBytes', 'Bytes'),
                ('EBSReadBytes', 'Bytes'),
                ('EBSWriteOps', 'Count'), 
                ('EBSReadOps', 'Count'),
                ('CPUCreditUsage', 'Count'),
                ('CPUCreditBalance', 'Count')
            ]
        }
    }

def analyze_instance_and_volume_metrics(regions, start_time, end_time):
    all_data = []
    with ThreadPoolExecutor() as executor:
        future_to_region = {executor.submit(list_running_instances, region): region for region in regions}
        for future in as_completed(future_to_region):
            region = future_to_region[future]
            try:
                instances = future.result()
                cloudwatch = boto3.client('cloudwatch', region_name=region)
                futures = []
                for instance in instances:
                    futures.append(executor.submit(fetch_instance_metrics, cloudwatch, instance, start_time, end_time))
                for future in as_completed(futures):
                    instance_metrics = future.result()
                    all_data.append(instance_metrics)
            except Exception as exc:
                print(f'Region {region} generated an exception: {exc}')
    
    with open('ec2_volume_metrics.json', 'w') as file:
        json.dump(all_data, file, indent=2)

# Define time range for metrics
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=7)

regions = list_aws_regions()
analyze_instance_and_volume_metrics(regions, start_time, end_time)
