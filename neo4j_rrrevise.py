import csv
from py2neo import Graph, Node, Relationship

# 1. 连接 Neo4j（请替换用户名和密码）
graph = Graph("bolt://localhost:7687", auth=("neo4j", "Zr20060428"))

# 2. 从 CSV 读取数据，创建 Category、Algorithm 节点及它们之间的 BELONGS_TO 关系
#    并将非“多变”的 TimeComplexity 拆分为独立节点、与 Algorithm 建立 HAS_TIME_COMPLEXITY 关系
with open(r"NewerResource.csv", encoding="utf-8") as f:
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
            category            = cat_name,
            english_name        = eng_name,
            algorithm_type      = alg_type,
            time_complexity     = tc_val,
            space_complexity    = sc_val,
            stability           = stability,
            use_cases           = use_cases,
            core_idea           = core_idea,
            applicable_domains  = domains,
            pros_cons_analysis  = pros_cons
        )
        graph.merge(alg_node, "Algorithm", "name")

        # 2.3 建立 BELONGS_TO 关系：Algorithm -> Category
        rel_cat = Relationship(alg_node, "BELONGS_TO", cat_node)
        graph.merge(rel_cat)

        # 2.4 如果 TimeComplexity 不是 “多变”，拆分为独立节点并关联
        if tc_val and tc_val != "多变":
            tc_node = Node("TimeComplexity", value=tc_val)
            graph.merge(tc_node, "TimeComplexity", "value")
            rel_tc = Relationship(alg_node, "HAS_TIME_COMPLEXITY", tc_node)
            graph.merge(rel_tc)

print("✅ 数据导入完成：已创建 Category、Algorithm、TimeComplexity 节点及它们的关系。")