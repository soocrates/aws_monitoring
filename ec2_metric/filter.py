import json

def clean_and_round(data):
    if isinstance(data, dict):
        cleaned_dict = {}
        for key, value in data.items():
            if value != "--" and value != 0.0 and value != {}:
                cleaned_value = clean_and_round(value)
                if cleaned_value or isinstance(cleaned_value, dict) and cleaned_value:
                    cleaned_dict[key] = cleaned_value
        return cleaned_dict if cleaned_dict else None
    elif isinstance(data, list):
        cleaned_list = [clean_and_round(item) for item in data if item != "--" and item != 0.0 and item != {}]
        return cleaned_list if cleaned_list else None
    elif isinstance(data, float):
        return round(data, 3) if data != 0.0 else None
    return data

def process_json_file(file_path):
    # Define a mapping of metric names to their units
    metrics_units = {
        'VolumeReadBytes': 'Bytes', 'VolumeWriteBytes': 'Bytes',
        'VolumeReadOps': 'Count', 'VolumeWriteOps': 'Count',
        'VolumeTotalReadTime': 'Seconds', 'VolumeTotalWriteTime': 'Seconds',
        'VolumeIdleTime': 'Seconds', 'VolumeQueueLength': 'Count',
        'VolumeConsumedReadWriteOps': 'Count', 'BurstBalance': '%',
        'CPUUtilization': '%', 'NetworkIn': 'Bytes', 'NetworkOut': 'Bytes',
        'NetworkPacketsIn': 'Count', 'NetworkPacketsOut': 'Count',
        'DiskReadBytes': 'Bytes', 'DiskReadOps': 'Count',
        'DiskWriteBytes': 'Bytes', 'DiskWriteOps': 'Count',
        'EBSWriteBytes': 'Bytes', 'EBSReadBytes': 'Bytes',
        'EBSWriteOps': 'Count', 'EBSReadOps': 'Count',
        'CPUCreditUsage': 'Count', 'CPUCreditBalance': 'Count'
    }

    with open(file_path, 'r') as file:
        data = json.load(file)

    # Process each dictionary in the list
    updated_data = []
    for entry in data:
        processed_entry = {}
        for key, value in entry.items():
            if isinstance(value, dict):
                # Process inner dictionaries
                processed_entry[key] = {k: {"value": clean_and_round(v), "unit": metrics_units.get(k, "")} for k, v in value.items() if k in metrics_units}
            elif isinstance(value, list) and key == 'Volumes':
                # Special handling for 'Volumes' which is a list of dictionaries
                processed_entry[key] = [process_volumes(volume, metrics_units) for volume in value]
            else:
                processed_entry[key] = clean_and_round(value)
        updated_data.append(processed_entry)

    with open(file_path, 'w') as file:
        json.dump(updated_data, file, indent=4)

def process_volumes(volume, metrics_units):
    processed_volume = {}
    for key, value in volume.items():
        if isinstance(value, dict) and key == 'VolumeMetrics':
            processed_volume[key] = {k: {"value": clean_and_round(v), "unit": metrics_units.get(k, "")} for k, v in value.items() if k in metrics_units}
        else:
            processed_volume[key] = value
    return processed_volume

# Example usage
process_json_file('ec2_volume_metrics.json')
