import asyncio
import aiobotocore
from datetime import datetime, timedelta, timezone
import json

async def list_aws_regions(session):
    ec2 = session.create_client('ec2')
    response = await ec2.describe_regions()
    await ec2.close()
    return [region['RegionName'] for region in response['Regions']]

async def list_running_instances(session, region):
    ec2 = session.create_client('ec2', region_name=region)
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
    await ec2.close()
    return instances

async def get_cloudwatch_metrics(session, region, namespace, metric_name, unit, dimensions, start_time, end_time, period=3600):
    cloudwatch = session.create_client('cloudwatch', region_name=region)
    response = await cloudwatch.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        StartTime=start_time,
        EndTime=end_time,
        Period=period,
        Statistics=['Minimum', 'Maximum', 'Average'],
        Unit=unit
    )
    await cloudwatch.close()
    datapoints = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
    if datapoints:
        return {
            'Minimum': datapoints[-1]['Minimum'],
            'Maximum': datapoints[-1]['Maximum'],
            'Average': datapoints[-1]['Average']
        }
    else:
        return {'Minimum': '--', 'Maximum': '--', 'Average': '--'}

async def analyze_instance_and_volume_metrics(session, regions, start_time, end_time):
    tasks = [list_running_instances(session, region) for region in regions]
    all_instances = await asyncio.gather(*tasks)
    all_data = []
    for instances in all_instances:
        for instance in instances:
            metrics_tasks = []
            for metric, unit in [
                ('CPUUtilization', 'Percent'),
                # Add other metrics as needed
            ]:
                metrics_tasks.append(
                    get_cloudwatch_metrics(
                        session,
                        instance['Region'],
                        'AWS/EC2',
                        metric,
                        unit,
                        [{'Name': 'InstanceId', 'Value': instance['InstanceId']}],
                        start_time,
                        end_time
                    )
                )
            metrics_results = await asyncio.gather(*metrics_tasks)
            # Process metrics results as needed

            # Similar for volumes...
            all_data.append(instance)  # Add processed data

    print(json.dumps(all_data, indent=2))
    return all_data

async def main():
    session = aiobotocore.get_session()
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=7)
    regions = await list_aws_regions(session)
    data = await analyze_instance_and_volume_metrics(session, regions, start_time, end_time)

asyncio.run(main())
