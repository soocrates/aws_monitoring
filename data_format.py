# Sample structured data assuming this might be the output format of your existing process
data = [
    {"Region": "ap-northeast-1", "Month": "2024-01-01", "Cost": 858.10},
    {"Region": "ap-northeast-1", "Month": "2024-02-01", "Cost": 4729.00},
    {"Region": "ap-northeast-1", "Month": "2024-03-01", "Cost": 4760.87},
    {"Region": "ap-northeast-1", "Month": "2024-04-01", "Cost": 3834.45},
    {"Region": "ap-northeast-1", "Month": "2024-05-01", "Cost": 1128.83},
    {"Region": "us-east-1", "Month": "2024-04-01", "Cost": 14.12},
    {"Region": "us-east-1", "Month": "2024-05-01", "Cost": 158.03},
    {"Region": "us-east-2", "Month": "2023-10-01", "Cost": 67.08},
    {"Region": "us-east-2", "Month": "2023-11-01", "Cost": 88.93},
    {"Region": "us-east-2", "Month": "2023-12-01", "Cost": 68.25},
    {"Region": "us-east-2", "Month": "2024-03-01", "Cost": 378.98},
    {"Region": "us-east-2", "Month": "2024-04-01", "Cost": 12.94},
    {"Region": "us-east-2", "Month": "2024-05-01", "Cost": 158.67},
    {"Region": "us-west-2", "Month": "2023-10-01", "Cost": 543.25},
    {"Region": "us-west-2", "Month": "2023-11-01", "Cost": 436.85},
    {"Region": "us-west-2", "Month": "2024-02-01", "Cost": 1304.44},
    {"Region": "us-west-2", "Month": "2024-03-01", "Cost": 1542.12},
    {"Region": "us-west-2", "Month": "2024-04-01", "Cost": 2495.79},
    {"Region": "us-west-2", "Month": "2024-05-01", "Cost": 1511.18}
]

# Print the header
print("| Region         | Month       | Cost     |")
print("|----------------|-------------|----------|")

# Print each row
for entry in data:
    region = entry["Region"]
    month = entry["Month"][:7]  # Truncate to show only YYYY-MM
    cost = entry["Cost"]
    print(f"| {region:<14} | {month:<11} | {cost:8.2f} |")
