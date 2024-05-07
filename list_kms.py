import boto3

def list_aws_regions():
    """List all available AWS regions."""
    ec2 = boto3.client('ec2')
    response = ec2.describe_regions()
    return [region['RegionName'] for region in response['Regions']]

def list_kms_keys(region):
    """List all KMS keys for a given AWS region."""
    kms = boto3.client('kms', region_name=region)
    paginator = kms.get_paginator('list_keys')
    keys = []
    for page in paginator.paginate():
        keys.extend(page['Keys'])
    return keys

def get_key_aliases(kms_client, key_id):
    """Retrieve aliases for a given Key ID using a KMS client."""
    paginator = kms_client.get_paginator('list_aliases')
    for page in paginator.paginate(KeyId=key_id):
        for alias_info in page['Aliases']:
            yield alias_info['AliasName']


regions = list_aws_regions()
print("| Region | Key ID | Aliases |")
print("|--------|--------|---------|")
for region in regions:
    kms_client = boto3.client('kms', region_name=region)
    keys = list_kms_keys(region)
    for key in keys:
        key_id = key['KeyId']
        aliases = list(get_key_aliases(kms_client, key_id))
        aliases_str = ', '.join(aliases)
        print(f"|{region} | {key_id} | {aliases_str}|")
