# neo4j_service.py
from neo4j import GraphDatabase, basic_auth, Result
import neo4j
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Neo4jService:
    """
    Neo4jService 类负责与 Neo4j 数据库进行交互。
    它管理数据库连接并提供执行查询的方法。
    """
    def __init__(self, uri, username, password):
        """
        初始化 Neo4jService。
        :param uri: Neo4j 数据库的 URI (例如 "bolt://localhost:7687")
        :param username: 数据库用户名
        :param password: 数据库密码
        """
        self._uri = uri
        self._username = username
        self._password = password
        self._driver = None
        logging.info(f"Neo4jService initialized, URI: {uri}")

    def connect(self):
        """
        建立与 Neo4j 数据库的连接。
        """
        try:
            self._driver = GraphDatabase.driver(self._uri, auth=basic_auth(self._username, self._password))
            self._driver.verify_connectivity()
            logging.info("Successfully connected to Neo4j database.")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to Neo4j database: {e}")
            self._driver = None
            return False

    def close(self):
        """
        关闭数据库连接。
        """
        if self._driver:
            self._driver.close()
            logging.info("Neo4j database connection closed.")
            self._driver = None

    def search_data(self, keyword: str): # TODO
        """
        根据关键词在 Neo4j 数据库中执行模糊查询，并返回相关的节点和关系。
        """

        if not self._driver:
            logging.warning("Neo4j driver not connected. Please call connect() first.")
            return []

        # 修改后的查询，专门针对你的数据结构
        query = """
        MATCH (n:算法)
        WHERE any(prop IN keys(n) WHERE toLower(toString(n[prop])) CONTAINS toLower($keyword))
        OPTIONAL MATCH (n)-[r]-(related)
        RETURN n, 
            TYPE(r) AS relationship_type,
            r AS relationship,
            related,
            ID(n) AS node_id,
            ID(startNode(r)) AS start_id,
            ID(endNode(r)) AS end_id
        """
        results = []
        try:
            with self._driver.session() as session:
                result_set = session.run(query, keyword=keyword)
                
                processed_nodes = {}
                
                for record in result_set:
                    main_node = record["n"]
                    node_id = record["node_id"]
                    
                    if node_id not in processed_nodes:
                        processed_nodes[node_id] = {
                            "node": {
                                "id": node_id,
                                "labels": list(main_node.labels),
                                "properties": dict(main_node.items())
                            },
                            "related_data": []
                        }
                    
                    if record["relationship_type"]:
                        rel_info = {
                            "type": record["relationship_type"],
                            "properties": dict(record["relationship"].items()),
                            "start_node_id": record["start_id"],
                            "end_node_id": record["end_id"],
                            "related_node": {
                                "id": record["related"].id,
                                "labels": list(record["related"].labels),
                                "properties": dict(record["related"].items())
                            }
                        }
                        processed_nodes[node_id]["related_data"].append(rel_info)
                
                results = list(processed_nodes.values())
                logging.info(f"查询完成，找到 {len(results)} 个匹配节点")
        
        except Exception as e:
            logging.error(f"查询执行失败: {e}")
        
        return results

    def get_node_details(self, node_id: int):
        """
        根据节点 ID 获取单个节点及其直接关联的数据。
        """
        if not self._driver:
            logging.warning("Neo4j driver not connected. Please call connect() first.")
            return None

        query = """
        MATCH (n) WHERE id(n) = $node_id
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN n, r, m
        LIMIT 100
        """
        try:
            with self._driver.session() as session:
                logging.info(f"Executing Neo4j query for node details, ID: {node_id}")
                result_set = session.run(query, node_id=node_id)

                node_details = None
                related_data = []

                for record in result_set:
                    main_node = record["n"]
                    relationship = record["r"]
                    related_node = record["m"]

                    if node_details is None:
                        node_details = {
                            "node": {
                                "id": main_node.id,
                                "labels": list(main_node.labels),
                                "properties": dict(main_node.items())
                            },
                            "related_data": []
                        }

                    if relationship and related_node:
                        rel_info = {
                            "relationship_id": relationship.id,
                            "type": relationship.type,
                            "properties": dict(relationship.items()),
                            "start_node_id": relationship.start_node.id,
                            "end_node_id": relationship.end_node.id,
                            "related_node": {
                                "id": related_node.id,
                                "labels": list(related_node.labels),
                                "properties": dict(related_node.items())
                            }
                        }
                        if rel_info not in node_details["related_data"]:
                            node_details["related_data"].append(rel_info)
                
                logging.info(f"Node details query completed for ID {node_id}.")
                return node_details

        except Exception as e:
            logging.error(f"Failed to get node details for ID {node_id}: {e}")
            return None

    def get_all_algorithms(self):
        """
        获取所有算法节点及其直接关联的数据。
        """
        if not self._driver:
            logging.warning("Neo4j driver not connected. Please call connect() first.")
            return []

        query = """
        MATCH (n:算法)
        OPTIONAL MATCH (n)-[r]-(related)
        RETURN n,
            TYPE(r) AS relationship_type,
            r AS relationship,
            related,
            ID(n) AS node_id,
            ID(startNode(r)) AS start_id,
            ID(endNode(r)) AS end_id
        """
        results = []
        try:
            with self._driver.session() as session:
                result_set = session.run(query)

                processed_nodes = {}

                for record in result_set:
                    main_node = record["n"]
                    node_id = record["node_id"]

                    if node_id not in processed_nodes:
                        processed_nodes[node_id] = {
                            "node": {
                                "id": node_id,
                                "labels": list(main_node.labels),
                                "properties": dict(main_node.items())
                            },
                            "related_data": []
                        }

                    if record["relationship_type"]:
                        rel_info = {
                            "type": record["relationship_type"],
                            "properties": dict(record["relationship"].items()),
                            "start_node_id": record["start_id"],
                            "end_node_id": record["end_id"],
                            "related_node": {
                                "id": record["related"].id,
                                "labels": list(record["related"].labels),
                                "properties": dict(record["related"].items())
                            }
                        }
                        # 确保不添加重复关系
                        if rel_info not in processed_nodes[node_id]["related_data"]:
                            processed_nodes[node_id]["related_data"].append(rel_info)

                results = list(processed_nodes.values())
                logging.info(f"Fetched all algorithms, found {len(results)} algorithm nodes.")

        except Exception as e:
            logging.error(f"Failed to fetch all algorithms: {e}")

        return results
