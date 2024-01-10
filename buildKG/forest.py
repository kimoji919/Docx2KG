import xmind
from xmind.core.topic import TopicElement
from xmind.core.const import TOPIC_DETACHED
# from timeout_decorator import timeout
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
    def __init__(self, source, relation, target):
        
        self.source = source
        self.relation = relation
        self.target = target
        signal.signal(signal.SIGALRM, handler)
        # 设置超时时间为5秒
        timeout_seconds = 3
        signal.alarm(timeout_seconds)
        try:
            self.build(source,relation,target)
            signal.alarm(0)
        except Exception as e:
            # print("超时")
            print(e)
        finally:
            # 清除信号处理函数
            signal.signal(signal.SIGALRM, signal.SIG_DFL)
        # 在这里，我们用subTopic也就是父节点与子节点之间的关系来表征,其他关系用关系符号加上关系名称去表征
        # 但是节点必须有根节点，单纯的关联符号无法使得其能在最终的知识图谱上显示，因此我们在这里多加一条属于关系
    def build(self,source,relation,target):
        if relation=="属于":
            target.node_topic.addSubTopic(source.node_topic)
        else:
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
        # Q：构建森林目标?
        # A: 建立以章节小节为体系的基本框架，将大模型输出的内容绑定在小节中，尽可能减少野节点出现的可能
        #    同时考虑到现有python-xmind API的限制：1、建立关系需要让子节点先有从属关系；2、无法找到一个节点的父节点
        # Q: 构建森林思路?
        # A: 在构建关系时，先将所有节点连接到小节节点上，再用边关系对森林进行增改；
        # Q: 在流程中如何使用?
        # A: 1、先用 章节节点、空边列表、空部分名进行第一次构建获得章节知识图谱；
        #    2、分小节、用单一章节内小节节点、[小节，属于，章节]、章节名称进行第二次构建获得章节-小节知识图谱
        #    3、对于单一小节，用单一小节内 节点、关系、小节名称 进行第三次构建获得最后结果
        part_node = next((node for node in self.nodes if node.name == part_name), None)

        for node_name in nodes:
            # 消除野节点
            IsWild=True
            for edge in edges:
                try:
                    if edge[0]==node_name or edge[2]==node_name:
                        IsWild=False
                        break
                except:
                    continue
            if IsWild and edges!=[]:
                continue
            node = Node(node_name)
            
            self.add_node(node)
            # # 将野节点连接到根节点（若节点是章节节点）或者连接到小节节点上
            signal.signal(signal.SIGALRM, handler)
            # 设置超时时间为5秒
            timeout_seconds = 2
            signal.alarm(timeout_seconds)
            try:
                if part_name==None:
                    parent_topic = sheet.getRootTopic()
                    parent_topic.addSubTopic(node.node_topic)
                else:
                    part_node.node_topic.addSubTopic(node.node_topic)
                signal.alarm(0)
            except Exception as e:
                # print("超时")
                print(e)
            finally:
                # 清除信号处理函数
                signal.signal(signal.SIGALRM, signal.SIG_DFL)

        for edge_data in edges:
            print(edge_data)
            if len(edge_data)<3:
                continue
            try:
                source_name, relation, target_name = edge_data
            except:
                continue
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
    def build_kg(self,topic=None,part_array=None):
        parent_topic = sheet.getRootTopic()
        if topic:
            parent_topic.setTitle(topic)
            name=topic+".xmind"
        else:
            parent_topic.setTitle("知识图谱")
            name="知识图谱.xmind"
        xmind.save(workbook, name)

if __name__=="__main__":
    nodes_array=[]
    edges_array=[]
    # forest = Forest()
    # forest.build_forest(nodes_array, edges_array)
    # forest.build_kg()
    