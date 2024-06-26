import boto3
from datetime import datetime, timedelta, timezone

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
                        'Volume ID': volume['VolumeId'],
                        'Type': volume['VolumeType'],
                        'Size': volume['Size'],
                        'IOPS': volume.get('Iops', 'N/A'),
                        'Throughput': volume.get('Throughput', 'N/A')
                    }
                    volumes_info.append(volume_info)
            instance_info = {
                'Region': region,
                'Instance ID': instance['InstanceId'],
                'Instance Type': instance['InstanceType'],
                'Public IP': instance.get('PublicIpAddress', 'None'),
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
    for region in regions:
        ec2 = boto3.client('ec2', region_name=region)
        cloudwatch = boto3.client('cloudwatch', region_name=region)
        running_instances = list_running_instances(region)
        
        for instance in running_instances:
            print("\n")
            print("| Region  | Instance ID       | Instance Type | Public IP |")
            print("|---------|-------------------|---------------|-----------|")
            print(f"|{region} | {instance['Instance ID']} | {instance['Instance Type']}| {instance['Public IP']}")

            instance_metrics = [
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
            
            print("\n")
            print("\nInstance Metrics:")
            print("| Metric  |        Min       |       Max      |     Avg |")
            print("|---------|------------------|----------------|-----------|")
            for metric, unit in instance_metrics:
                data = get_cloudwatch_metrics(cloudwatch, 'AWS/EC2', metric, unit, [{'Name': 'InstanceId', 'Value': instance['Instance ID']}], start_time, end_time)
                print(f"|{metric}|{data['Minimum']}|{data['Maximum']}| {data['Average']}")

            volume_metrics = [
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

            for volume in instance['Volumes']:
                    print("\n")
                    print("| Volume ID  | Instance ID |        Type       |       Size      |")
                    print("|------------|-------------|-------------------|-----------------|")
                    print(f"| {volume['Volume ID']} | {instance['Instance ID']} | {volume['Type']} |{volume['Size']} GB")
                    print("\n")
                    print("  Volume Metrics:")
                    print("| Metric  |        Min       |       Max      |     Avg |")
                    print("|---------|------------------|----------------|-----------|")
                    for metric, unit in volume_metrics:
                        data = get_cloudwatch_metrics(cloudwatch, 'AWS/EBS', metric, unit, [{'Name': 'VolumeId', 'Value': volume['Volume ID']}], start_time, end_time)
                        print(f"|{metric}|{data['Minimum']}|{data['Maximum']}| {data['Average']}")

# Define time range for metrics
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=7)

regions = list_aws_regions()
analyze_instance_and_volume_metrics(regions, start_time, end_time)