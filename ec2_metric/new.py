import asyncio
import aiobotocore.session
from datetime import datetime, timedelta, timezone
import json

async def list_aws_regions(client):
    response = await client.describe_regions()
    return [region['RegionName'] for region in response['Regions']]

async def list_running_instances(client, region):
    async with client.create_client('ec2', region_name=region) as ec2:
        response = await ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                volume_ids = [vol['Ebs']['VolumeId'] for vol in instance['BlockDeviceMappings'] if 'Ebs' in vol]
                volumes_info = []
                if volume_ids:
                    volumes_response = await ec2.describe_volumes(VolumeIds=volume_ids)
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

async def get_cloudwatch_metrics(client, namespace, metric_name, unit, dimensions, start_time, end_time, period=3600):
    response = await client.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        StartTime=start_time,
        EndTime=end_time,
        Period=period,
        Statistics=['Minimum', 'Maximum', 'Average'],
        Unit=unit
    )
    datapoints = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
    if datapoints:
        return {
            'Minimum': round(datapoints[-1]['Minimum'], 3),
            'Maximum': round(datapoints[-1]['Maximum'], 3),
            'Average': round(datapoints[-1]['Average'], 3)
        }
    else:
        return None

async def analyze_instance_and_volume_metrics(client, regions, start_time, end_time):
    all_data = []
    tasks = [list_running_instances(client, region) for region in regions]
    instances_per_region = await asyncio.gather(*tasks)

    for instances, region in zip(instances_per_region, regions):
        for instance in instances:
            # Prepare tasks for fetching metrics for both instances and volumes
            metric_tasks = [
                get_cloudwatch_metrics(client, 'AWS/EC2', metric_name, unit, [{'Name': 'InstanceId', 'Value': instance['InstanceId']}], start_time, end_time)
                for metric_name, unit in [
                    ('CPUUtilization', 'Percent'),
                    ('NetworkIn', 'Bytes'),
                    ('NetworkOut', 'Bytes'),
                    ('DiskReadBytes', 'Bytes'),
                    ('DiskWriteBytes', 'Bytes'),
                    ('DiskReadOps', 'Count'),
                    ('DiskWriteOps', 'Count')
                ]
            ]
            results = await asyncio.gather(*metric_tasks)
            metrics_names = [
                'CPUUtilization', 'NetworkIn', 'NetworkOut', 'DiskReadBytes', 'DiskWriteBytes', 'DiskReadOps', 'DiskWriteOps'
            ]
            instance['InstanceMetrics'] = {name: metric for name, metric in zip(metrics_names, results) if metric}
            all_data.append(instance)
    
    with open('ec2_volume_metrics_async.json', 'w') as file:
        json.dump(all_data, file, indent=2)

async def main():
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=7)
    session = aiobotocore.session.get_session()
    async with session.create_client('ec2') as client:
        regions = await list_aws_regions(client)
        await analyze_instance_and_volume_metrics(client, regions, start_time, end_time)

if __name__ == "__main__":
    asyncio.run(main())
