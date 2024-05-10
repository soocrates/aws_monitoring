import json

# Load JSON data from file
with open('ec2_volume_metrics.json', 'r') as file:
    data = json.load(file)

# Function to print metrics table
def print_metrics_table(region, instance_id, instance_type, public_ip, instance_metrics, volumes):
    # Replace None values with empty strings
    region = region if region is not None else ""
    instance_id = instance_id if instance_id is not None else ""
    instance_type = instance_type if instance_type is not None else ""
    public_ip = public_ip if public_ip is not None else ""

    # Print table headers for instance
    print("| Region  | Instance ID       | Instance Type | Public IP |")
    print("|---------|-------------------|---------------|-----------|")
    # Print table data for instance
    print("| {:<7} | {:<17} | {:<13} | {:<9} |".format(region, instance_id, instance_type, public_ip))

    # Print instance metrics
    print("\nInstance Metrics:")
    print("| Metric          | Min           | Max           | Avg           |")
    print("|-----------------|---------------|---------------|---------------|")
    for metric, values in instance_metrics.items():
        print("| {:<15} | {:<13} | {:<13} | {:<13} |".format(metric, values["Minimum"], values["Maximum"], values["Average"]))

    # Print table headers for volume
    print("\n| Volume ID       | Instance ID       | Type  | Size    |")
    print("|-----------------|-------------------|-------|---------|")
    for volume in volumes:
        volume_id = volume["VolumeId"]
        volume_type = volume["Type"]
        volume_size = volume["Size"]
        # Print table data for volume
        print("| {:<15} | {:<17} | {:<6} | {:<8} |".format(volume_id, instance_id, volume_type, volume_size))

        # Print volume metrics
        print("\nVolume Metrics:")
        print("| Metric          | Min           | Max           | Avg           |")
        print("|-----------------|---------------|---------------|---------------|")
        volume_metrics = volume["VolumeMetrics"]
        for metric, values in volume_metrics.items():
            print("| {:<15} | {:<13} | {:<13} | {:<13} |".format(metric, values["Minimum"], values["Maximum"], values["Average"]))

        print()  # Empty line between volumes

    print()  # Empty line after instance

# Iterate over instances
for instance in data:
    region = instance["Region"]
    instance_id = instance["InstanceId"]
    instance_type = instance["InstanceType"]
    public_ip = instance["PublicIP"]
    instance_metrics = instance["InstanceMetrics"]
    volumes = instance["Volumes"]

    # Print metrics table for each instance
    print_metrics_table(region, instance_id, instance_type, public_ip, instance_metrics, volumes)
