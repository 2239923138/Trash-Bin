from flask import Flask, jsonify, request
from neo4j_service import Neo4jService
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app) # 启用 CORS，允许前端跨域请求

# Neo4j 连接详情 - 请替换为你的实际 Neo4j URI, 用户名和密码
# 在实际应用中，强烈建议使用环境变量来存储这些敏感信息。
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "2239923138") # 请替换为你的密码

neo4j_service = Neo4jService(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)

@app.before_request
def before_request_func():
    """
    在每个请求之前尝试连接 Neo4j。
    """
    if not neo4j_service._driver:
        neo4j_service.connect()

@app.teardown_request
def teardown_request_func(exception=None):
    """
    在每个请求结束后关闭 Neo4j 连接。
    """
    if neo4j_service._driver:
        neo4j_service.close()

@app.route('/api/algorithms', methods=['GET'])
def get_algorithms():
    """
    获取所有算法及其相关数据。
    """
    data = neo4j_service.get_all_algorithms()

    # 将 Neo4j 返回的数据转换为前端更容易处理的扁平结构
    transformed_algorithms = []
    for item in data:
        algorithm_node = item['node']
        related_data = item['related_data']

        # 将节点属性扁平化到主算法对象中
        alg = {
            "id": algorithm_node['id'],
            "labels": algorithm_node['labels'],
            **algorithm_node['properties'], # 展开属性
            "relationships": [] # 用于存储简化的关系信息
        }

        for rel in related_data:
            alg["relationships"].append({
                "type": rel["type"],
                "start_node_id": rel["start_node_id"],
                "end_node_id": rel["end_node_id"],
                "related_node_id": rel["related_node"]["id"],
                "related_node_name": rel["related_node"]["properties"].get("name", "Unknown"),
                "related_node_labels": rel["related_node"]["labels"]
            })
        transformed_algorithms.append(alg)

    return jsonify(transformed_algorithms)

@app.route('/api/algorithm_details/<int:node_id>', methods=['GET'])
def get_algorithm_details_api(node_id):
    """
    根据节点 ID 获取单个节点及其直接关联的数据。
    """
    details = neo4j_service.get_node_details(node_id)
    if details:
        return jsonify(details)
    return jsonify({"error": "Node not found"}), 404

if __name__ == '__main__':
    # 确保服务在启动时连接
    if neo4j_service.connect():
        app.run(debug=True, port=5000) # 在 5000 端口运行，调试模式开启
    else:
        print("Failed to connect to Neo4j, exiting.")

