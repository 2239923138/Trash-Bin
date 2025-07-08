import os
import py2neo
from py2neo import Node, Relationship ,Graph, Subgraph

graph = Graph("bolt://localhost:7687", auth=("neo4j", "Zr20060428"))
file_name="algorithm_knowledge_graph.csv"
name_list=[]            #1
relation_list=[]        #2
point_list=[]           #3
lst=[]                  #总数据
Node_list1=[]           #节点列表
Node_list2=[]
Node_list_repeat_1=[]
Node_list_repeat_2=[]
rels=[]                 #关系列表

with open(file_name,'r',encoding="UTF-8") as csvfile:
    for line in csvfile:
        line = line.strip()
        line=line.split(',')
        name_list.append(line[0])
        relation_list.append(line[1])
        point_list.append(line[2])

for Name in name_list:
    node=Node("algorithm",name=Name)
    Node_list_repeat_1.append(node)

for point in point_list:
    node=Node("relation",name=point)
    Node_list_repeat_2.append(node)

for i in range(len(relation_list)):
    relationship=Relationship(Node_list_repeat_1[i],relation_list[i],Node_list_repeat_2[i])
    rels.append(relationship)
#去重
name_list=list(set(name_list))
point_list=list(set(point_list))

for Name in name_list:
    node=Node("algorithm",name=Name)
    Node_list1.append(node)

for point in point_list:
    node=Node("relation",name=point)
    Node_list2.append(node)

Node_list_total=Node_list1+Node_list2
subgraph_nodes = Subgraph(Node_list_total)
graph.create(subgraph_nodes)
print("节点创建完成")

tx = graph.begin()
for rel in rels:
    tx.create(rel)
graph.commit(tx)
print("关系创建完成")
