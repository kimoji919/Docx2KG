import xmind
from xmind.core.topic import TopicElement
from xmind.core.const import TOPIC_DETACHED
workbook = xmind.load("empty.xmind")
sheet = workbook.getPrimarySheet()
class Node:
    def __init__(self, name):
        self.name = name
        self.node_topic = TopicElement(ownerWorkbook=workbook)
        self.node_topic.setTitle(name)

class Edge:
    def __init__(self, source, relation, target):
        self.source = source
        self.relation = relation
        self.target = target
        if relation=="属于":
            target.node_topic.addSubTopic(source.node_topic)
        else:
            target.node_topic.addSubTopic(source.node_topic)
            sheet.createRelationship(source.node_topic, target.node_topic, relation) 
class Forest:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def build_forest(self, nodes, edges):
        for node_name in nodes:
            node = Node(node_name)
            self.add_node(node)

        for edge_data in edges:
            source_name, relation, target_name = edge_data
            source_node = next((node for node in self.nodes if node.name == source_name), None)
            target_node = next((node for node in self.nodes if node.name == target_name), None)

            if not source_node:
                source_node = Node(source_name)
                self.add_node(source_node)

            if not target_node:
                target_node = Node(target_name)
                self.add_node(target_node)

            edge = Edge(source_node, relation, target_node)
            self.add_edge(edge)
    def get_tree_roots(self):
        roots = [node for node in self.nodes if all(edge.source != node for edge in self.edges)]
        return roots
    def build_kg(self,topic=None):
        parent_topic = sheet.getRootTopic()
        if topic:
            parent_topic.setTitle(topic)
            name=topic+".xmind"
        else:
            parent_topic.setTitle("知识图谱")
            name="知识图谱.xmind"
        tree_roots = self.get_tree_roots()
        for root in tree_roots:
            print(f"树的头节点: {root.name}")
            parent_topic.addSubTopic(root.node_topic)
        xmind.save(workbook, name)

if __name__=="__main__":
    nodes_array=[]
    edges_array=[]
    forest = Forest()
    forest.build_forest(nodes_array, edges_array)
    forest.build_kg()