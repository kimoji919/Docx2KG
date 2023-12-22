import xmind
from xmind.core.topic import TopicElement
from xmind.core.const import TOPIC_DETACHED
from timeout_decorator import timeout
import multiprocessing
import signal
import time

def handler(signum, frame):
    # 超时时触发的处理函数
    raise TimeoutError("任务执行超时")

workbook = xmind.load("empty.xmind")
sheet = workbook.getPrimarySheet()
class Node:
    def __init__(self, name):
        self.name = name
        self.node_topic = TopicElement(ownerWorkbook=workbook)
        self.node_topic.setTitle(name)

class Edge:
    def __init__(self, source, relation, target,part):
        self.source = source
        self.relation = relation
        self.target = target
        signal.signal(signal.SIGALRM, handler)
        # 设置超时时间为5秒
        timeout_seconds = 3
        signal.alarm(timeout_seconds)
        try:
            self.build(source,relation,target,part)
            signal.alarm(0)
        except:
            print("超时")
            # print(e)
        finally:
            # 清除信号处理函数
            signal.signal(signal.SIGALRM, signal.SIG_DFL)
        # 在这里，我们用subTopic也就是父节点与子节点之间的关系来表征,其他关系用关系符号加上关系名称去表征
        # 但是节点必须有根节点，单纯的关联符号无法使得其能在最终的知识图谱上显示，因此我们在这里多加一条属于关系
    def build(self,source,relation,target,part):
        if relation=="属于":
            target.node_topic.addSubTopic(source.node_topic)
        else:
            if not target.node_topic.getParentNode():
                part.node_topic.addSubTopic(source.node_topic)
            sheet.createRelationship(source.node_topic, target.node_topic, relation) 
class Forest:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)
    def print_node(self):
        node=[node.name for node in self.nodes]
        print(node)
    def build_forest(self, nodes, edges,part_name):
        for node_name in nodes:
            node = Node(node_name)
            self.add_node(node)
        i=0
        part_node = next((node for node in self.nodes if node.name == part_name), None)
        print(part_node)
        for edge_data in edges:
            print(edge_data)
            if len(edge_data)<3:
                continue
            source_name, relation, target_name = edge_data
            source_node = next((node for node in self.nodes if node.name == source_name), None)
            target_node = next((node for node in self.nodes if node.name == target_name), None)
            if not source_node:
                source_node = Node(source_name)
                self.add_node(source_node)

            if not target_node:
                target_node = Node(target_name)
                self.add_node(target_node)

            edge = Edge(source_node, relation, target_node,part_node)
            self.add_edge(edge)

        # tree_roots = self.get_tree_roots()
        # signal.signal(signal.SIGALRM, handler)
        # # 设置超时时间为5秒
        # timeout_seconds = 3
        # signal.alarm(timeout_seconds)
        # try:
        #     if part_name!=None:
        #         for root in tree_roots:
        #             part_node.node_topic.addSubTopic(root.node_topic)
        #     signal.alarm(0)
        # except:
        #     print("超时或未找到")
        # finally:
        #     # 清除信号处理函数
        #     signal.signal(signal.SIGALRM, signal.SIG_DFL)
                
    def get_tree_roots(self):
        roots = [node for node in self.nodes if all(edge.source != node for edge in self.edges)]
        return roots
    def build_kg(self,topic=None,part_array=None):
        parent_topic = sheet.getRootTopic()
        if topic:
            parent_topic.setTitle(topic)
            name=topic+".xmind"
        else:
            parent_topic.setTitle("知识图谱")
            name="知识图谱.xmind"
        tree_roots = self.get_tree_roots()
        for root in tree_roots:
            # if root.name in part_array:
            #     try:
                    parent_topic.addSubTopic(root.node_topic)
                # except:
                    print("未找到")
                # print("章节",root.name)
        xmind.save(workbook, name)

if __name__=="__main__":
    nodes_array=[]
    edges_array=[]
    forest = Forest()
    forest.build_forest(nodes_array, edges_array)
    forest.build_kg()
    