import boto3
from datetime import datetime, timedelta, timezone
import json

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
                'InstanceId': instance['InstanceId'],
                'Region': region,
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

def analyze_instance_and_volume_metrics(regions, start_time, end_time):
    all_data = []
    for region in regions:
        ec2 = boto3.client('ec2', region_name=region)
        cloudwatch = boto3.client('cloudwatch', region_name=region)
        running_instances = list_running_instances(region)

        for instance in running_instances:
            instance_metrics_names = [
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
            instance_metrics = {}
            for metric, unit in instance_metrics_names:
                data = get_cloudwatch_metrics(cloudwatch, 'AWS/EC2', metric, unit, [{'Name': 'InstanceId', 'Value': instance['InstanceId']}], start_time, end_time)
                instance_metrics[metric] = data

            for volume in instance['Volumes']:
                volume_metrics_names = [
                    ('VolumeReadBytes','Bytes'),
                    ('VolumeWriteBytes', 'Bytes'),
                    ('VolumeReadOps','Count'),
                    ('VolumeWriteOps','Count'),
                    ('VolumeTotalReadTime','Seconds'),
                    ('VolumeTotalWriteTime','Seconds'),
                    ('VolumeIdleTime', 'Seconds'),
                    ('VolumeQueueLength','Count'),
                    ('VolumeConsumedReadWriteOps','Count'),
                    ('BurstBalance', 'Percent')
                ]
                volume_metrics = {}
                for metric, unit in volume_metrics_names:
                    data = get_cloudwatch_metrics(cloudwatch, 'AWS/EBS', metric, unit, [{'Name': 'VolumeId', 'Value': volume['VolumeId']}], start_time, end_time)
                    volume_metrics[metric] = data
                volume['VolumeMetrics'] = volume_metrics
            
            instance['InstanceMetrics'] = instance_metrics
            all_data.append(instance)

    print(json.dumps(all_data, indent=2))
    return all_data

# Define time range for metrics
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=7)

regions = list_aws_regions()
data = analyze_instance_and_volume_metrics(regions, start_time, end_time)
