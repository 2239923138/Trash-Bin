import os
from py2neo import Graph, Node, Relationship, NodeMatcher

# 连接 Neo4j 数据库
graph = Graph("bolt://localhost:7687", auth=("neo4j", "yourpassword"))

# 路径到你的 CSV 文件
file_name = "algorithm_knowledge_graph.csv"

# 初始化 matcher（用于查找数据库中已有节点）
matcher = NodeMatcher(graph)

# 读取 CSV 内容
name_list = []
relation_list = []
point_list = []

with open(file_name, 'r', encoding="utf-8") as csvfile:
    for line in csvfile:
        line = line.strip()
        if not line or ',' not in line:
            continue  # 跳过无效行
        parts = line.split(',')
        if len(parts) != 3:
            continue  # 确保每行3列
        name_list.append(parts[0])
        relation_list.append(parts[1])
        point_list.append(parts[2])

# 创建并合并节点
unique_names = set(name_list)
unique_points = set(point_list)

for name in unique_names:
    node = Node("algorithm", name=name)
    graph.merge(node, "algorithm", "name")  # merge 可避免重复插入

for point in unique_points:
    node = Node("relation", name=point)
    graph.merge(node, "relation", "name")

print(" 所有节点创建完成！")

# 创建关系
created_count = 0
for name, rel, point in zip(name_list, relation_list, point_list):
    node1 = matcher.match("algorithm", name=name).first()
    node2 = matcher.match("relation", name=point).first()
    if node1 and node2:
        relationship = Relationship(node1, rel, node2)
        graph.create(relationship)
        created_count += 1
    else:
        print(f" 无法找到节点: {name} 或 {point}")

print(f" 共创建关系: {created_count} 条")
