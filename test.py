from buildKG.docx2request import group_paragraphs_by_token_limit
from buildKG.forest import Node,Edge,Forest
from buildKG.str2json import str2json

from http import HTTPStatus
from dashscope import Generation
from dashscope.api_entities.dashscope_response import Role
# export DASHSCOPE_API_KEY=sk-8cdfdc6958a7408492d465269349299f
import time
import random
import os
from collections import OrderedDict
# 指定.docx文件路径
docx_file_path = "./data/（153）商业智能在电子商务中的实践与应用-黄建鹏、徐晓冬、魏宝军-东南大学出版社.docx"
file_name,extension_name=os.path.splitext(os.path.basename(docx_file_path))
contents=group_paragraphs_by_token_limit(docx_file_path,1000)
nodes_array=[]
edges_array=[]
prompt = f"""
    在接下来的对话中，你需要遵循以下规则：
    你是一台用于处理文本数据的AI系统。你的任务是处理我上传的文本，并按照以下要求进行操作：
    - 输出标准JSON格式字符串。
    - 剔除文件中的所有乱码（乱码不包括英文）。
    - 处理英文的时候 请保留英文的原格式，包括括号。
    - 对文本内知识点进行提取，并列成列表，形成json字符串的point字段。
    - 有["属于","递进","实例","关联"]四种关系，对知识点与知识点之间的关系进行提取，有关系的知识点两两之间形成(知识点1,知识点2,关系)的元组，并以列表的形式存进json字符串的edge字段
    - 四种关系中“属于”表示一个知识点是另一个知识点的一部分或属于它的范畴。例如，"狗 属于 动物" 表示狗是动物的一种。
    - 递进关系表示两个知识点之间的逐步发展或层次递进的关系。例如，"初中 递进 高中" 表示初中逐渐发展为高中。
    - 实例关系表示一个知识点是另一个知识点的具体实例。例如，"苹果 实例 水果" 表示苹果是水果的一种具体实例。
    - 关联关系表示两个知识点之间存在某种关联，但不一定是属于或实例的关系。它强调两者之间的相关性，而不一定涉及包含或具体实例。例如，"雨天 关联 雨伞" 表示在雨天时，人们常常会使用雨伞。
    - 格式参考示例:
    {{
        "point": ["数学","线性代数","矩阵","秩","习题：矩阵的定义是什么","线性代数提出者的一生"],
        "edge":[["线性代数","属于","数学"],["矩阵","属于","线性代数"],["秩","递进","矩阵"],["矩阵","实例","习题：矩阵的定义是什么"],["线性代数","关联","线性代数提出者的一生"]]
    }}
    - 同时你可以参考上文中已经提取好的实例和关系,在生成答案的时候，你必须保证这些实例和关系不能改变，只能在这些基础之上新增实体和关系：
    {{
        "point": {nodes_array},
        "edge":  {edges_array}
    }}
    你不需要确认收到，或是做出过多解释，直接开始生成完整准确的输出。
"""
# 发送请求阶段
for content_id,content in enumerate(contents):
    request=""
    print("————————————第"+str(content_id)+"次请求————————————")
    for paragraph_id,paragraph in enumerate(content):
        request+=paragraph
        request+='\n'
    # messages.append({'role': Role.USER, 'content': request})
    messages = [{'role': Role.SYSTEM, 'content': prompt},
              {'role': Role.USER, 'content': request}]
    response = Generation.call(
        Generation.Models.qwen_max_longcontext,
        messages=messages,
        result_format='message',  # set the result to be "message" format.
    )
    if response.status_code == HTTPStatus.OK:
        print(response.output.choices[0]['message']['content'])
        print(response.usage["total_tokens"])
        # append result to messages.
        nodes_array_n,edges_array_n=str2json(response.output.choices[0]['message']['content'])
        nodes_array=list(set(nodes_array_n+nodes_array))
        edges_array=list(set(edges_array_n+edges_array))
    else:
        print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))
        break
    secs = random.normalvariate(70, 0.4)
    if secs <= 60 or secs >= 120:
        secs =60   # 太小则重置为平均值
    print("sleep:"+str(secs)+"秒")
    # time.sleep(secs)

# 构建xmind
forest = Forest()
forest.build_forest(nodes_array, edges_array)
forest.build_kg(file_name)
