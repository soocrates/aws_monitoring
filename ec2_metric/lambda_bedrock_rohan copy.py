import boto3
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import BedrockChat

bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1',
)
model_id = 'anthropic.claude-3-haiku-20240307-v1:0'
model_kwargs =  {
    'max_tokens': 4096,
    'temperature': 0.8,
    'top_k': 350,
    'top_p': 1,
    'stop_sequences': ['\n\nHuman'],
}
model = BedrockChat(
    client=bedrock_runtime,
    model_id=model_id,
    model_kwargs=model_kwargs,
)

#system prompt
messages = [
    ('system', 'You are AWS FinOps engineer who is excellent on optimizing the cost for AWS.'),
    ('human', '{question}'),
]
prompt = ChatPromptTemplate.from_messages(messages)

#prompt chain
chain = prompt | model | StrOutputParser()
def response_from_model(request_prompt):
    '''
    Retrieves a response from the Bedrock model given a specific prompt.

    Parameters:
    request_prompt (str): The prompt to pass to the model.

    Returns:
    str: The response from the model, or an empty JSON object string if no response.
    '''
    # user_prompt = """
    #                 Given the data, recommend me one instance type in tag <instance> </instance>, give nothing else. 
    #                 the instance must be such that for minimum cost and good performace. The goal is to minize the cost 
    #                 with optimal performace. Also compare bewteen previous and recommneded on basis of cost and performace.
    #                 Between tags <rec> </rec>
    #               """
    # user_prompt = """
    # "How can we effectively utilize historical metrics for CPU utilization, network activity, disk operations, EBS interactions, and volume usage (detailed in the metrics list) to determine the most appropriate AWS instance type and volume size for optimal performance and cost-efficiency in a production environment?"
    # """
    user_prompt = """
Our Motive is to Minimize cost.
Based on the following information in response body, what are the top 3 recommendations for AWS ec2 instance, EBS volume configuration to meet the performance requirements while optimizing for cost
Current EC2:
	[Based on metrics like (CPUUtilization,NetworkIn, NetworkOut, NetworkPacketsIn, NetworkPacketsOut, DiskReadBytes, DiskReadOps, DiskWriteBytes, DiskWriteOps, EBSWriteBytes, EBSReadBytes, EBSWriteOps, EBSReadOps, CPUCreditUsage and	  CPUCreditBalance)  and nature/best use-case of current used instance type. Is this instance over provisioned, under provisioned, moderated provisioned, Is this Configuration best fit. If fit why, else why not,  Draw a conclusion based on provided  response_body[Instance_Metrics[]] ]  
Print:
  [current instance-type]
  [current instance-nature]
  [current instance-cost (on-demand and reserve for 1 year in current deployed region)] Fetch Exact Cost
EC2 Recommendation:
	[Recommend three instance in comparision to current instance nauture and metrics]
	[Each instance should have It's type]
	[CPU Specification]
	[Nature]
	[Best fit use-case, make sure current instance nature should match]
	[Cost on-demand and reserve for 1 year in current deployed region, response_body[volume_Metrics[]] ] Fetch Exact Cost
	[Reason for recommending ]
Print Current Volume:
  [Current IOPS, Size and Used Storage]
	[Based metrics like (VolumeReadBytes, VolumeWriteBytes, VolumeReadOps, VolumeWriteOps, VolumeTotalReadTime, VolumeTotalWriteTime, VolumeIdleTime, VolumeQueueLength, VolumeConsumedReadWriteOps,BurstBalance) and nature of current 	used volume type,   over provisioned, under provisioned, moderated provisioned, Is this Configuration best fit. If fit why, else why not,  Draw a conclusion based on provided response_body[volume_Metrics[]] ]
# EBS Volume IOPS Recommendation:
# 	[ current IOPS status, average IOPS usage, over provisioned, under provisioned, moderated provisioned, Is this Configuration best fit. If fit why, else why not ]
# 	[ provide me the best EBS Volume IOPS recommendation base on provided response_body volume metrics  ]
# 	[ Reason for recommending ]
# EBS Volume Configuration Recommendation:
# 	[ current EBS volume condition,  over provisioned, under provisioned, moderated provisioned, Is this Configuration best fit. If fit why, else why not  ]
# 	[ provide me the best EBS Volume Configuration recommendation base on provided response_body volume metrics  ]
# 	[ Reason for recommending ]    
"""
    
    
    if response := chain.invoke({'question': f'{user_prompt}\n{request_prompt}'}):
        return response
    return '{}'
  
instance_data = """
Response Body: {"Region": "us-west-2", "InstanceId": "i-0687fdc27af20f058", "InstanceType": "g4dn.2xlarge", "PublicIP": "35.89.54.19", "Volumes": [{"VolumeId": "vol-0da89a9cf01d9d378", "Type": "gp3", "Size": "100 GB", "VolumeMetrics": {"VolumeWriteBytes": {"Minimum": 42496.0, "Maximum": 649216.0, "Average": 190301.867}, "VolumeWriteOps": {"Minimum": 7.0, "Maximum": 124.0, "Average": 34.017}, "VolumeTotalWriteTime": {"Minimum": 0.006, "Maximum": 0.11, "Average": 0.029}, "VolumeIdleTime": {"Minimum": 59.97, "Maximum": 59.996, "Average": 59.99}, "VolumeQueueLength": {"Maximum": 0.001}}}], "InstanceMetrics": {"CPUUtilization": {"Minimum": 0.622, "Maximum": 0.658, "Average": 0.641}, "NetworkIn": {"Minimum": 190201.0, "Maximum": 307718.0, "Average": 228437.883}, "NetworkOut": {"Minimum": 85701.0, "Maximum": 102435.0, "Average": 95520.333}, "NetworkPacketsIn": {"Minimum": 461.0, "Maximum": 579.0, "Average": 511.217}, "NetworkPacketsOut": {"Minimum": 457.0, "Maximum": 536.0, "Average": 490.183}, "EBSWriteBytes": {"Minimum": 42496.0, "Maximum": 649216.0, "Average": 189977.6}, "EBSWriteOps": {"Minimum": 7.0, "Maximum": 124.0, "Average": 33.933}}}
"""
  
print(response_from_model(instance_data))




