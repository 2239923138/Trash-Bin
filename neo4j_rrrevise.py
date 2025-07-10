import csv
import os
from py2neo import Graph, Node, Relationship

# 1. 连接 Neo4j（请替换用户名和密码）
graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))

current_dir = os.path.dirname(__file__)

resource_path = os.path.join(current_dir, "NewerResource.csv")

graph.run("MATCH (n) DETACH DELETE n")

# 2. 从 CSV 读取数据，创建 Category、Algorithm 节点及它们之间的 BELONGS_TO 关系
#    并将非“多变”的 TimeComplexity 拆分为独立节点、与 Algorithm 建立 HAS_TIME_COMPLEXITY 关系
with open(resource_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # 提取字段
        alg_name   = row["AlgorithmName"].strip()
        cat_name   = row["ParentCategory"].strip()
        tc_val     = row["TimeComplexity"].strip()
        eng_name   = row["EnglishName"].strip()
        alg_type   = row["AlgorithmType"].strip()
        sc_val     = row["SpaceComplexity"].strip()
        stability  = row["Stability"].strip()
        use_cases  = row["UseCases"].strip()
        core_idea  = row["CoreIdea"].strip()
        domains    = row["ApplicableDomains"].strip()
        pros_cons  = row["ProsConsAnalysis"].strip()

        # 2.1 合并（创建）Category 节点
        cat_node = Node("Category", name=cat_name)
        graph.merge(cat_node, "Category", "name")

        # 2.2 合并（创建）Algorithm 节点，包含全部属性
        alg_node = Node(
            "Algorithm",
            name                = alg_name,
            类别            = cat_name,
            英文名        = eng_name,
            算法类型      = alg_type,
            时间复杂度     = tc_val,
            空间复杂度    = sc_val,
            稳定性           = stability,
            适用场景           = use_cases,
            核心思想           = core_idea,
            应用领域  = domains,
            优缺点分析  = pros_cons
        )
        graph.merge(alg_node, "Algorithm", "name")

        # 2.3 建立 BELONGS_TO 关系：Algorithm -> Category
        rel_cat = Relationship(alg_node, "属于", cat_node)
        graph.merge(rel_cat)

        # 2.4 如果 TimeComplexity 不是 “多变”，拆分为独立节点并关联
        if tc_val and tc_val != "多变":
            tc_node = Node("TimeComplexity", name=tc_val)
            graph.merge(tc_node, "TimeComplexity", "name")
            rel_tc = Relationship(alg_node, "复杂度", tc_node)
            graph.merge(rel_tc)

print("✅ 数据导入完成：已创建 Category、Algorithm、TimeComplexity 节点及它们的关系。")
