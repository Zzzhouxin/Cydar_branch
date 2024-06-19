import json

with open("./Collector.json", mode='r', encoding='utf-8') as f:
    collector = json.load(f)

total_sum = 0

# 遍历每个项目的版本值，累加到总和中
for project in collector:
    project_versions = collector[project]
    for version_value in project_versions.values():
        total_sum += version_value

print("总累加和:", total_sum)
