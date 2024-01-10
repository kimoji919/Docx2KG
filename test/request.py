from buildKG.docx2request import group_paragraphs_by_token_limit
from buildKG.forest import Node,Edge,Forest
from buildKG.str2json import str2json

from http import HTTPStatus
from dashscope import Generation
from dashscope.api_entities.dashscope_response import Role
import dashscope
# export DASHSCOPE_API_KEY=sk-8cdfdc6958a7408492d465269349299f
import time
import random
import os
from collections import OrderedDict

dashscope.api_key = "sk-8cdfdc6958a7408492d465269349299f"
# 指定.docx文件路径
# docx_file_path = "./data/153/"
docx_file_path = "./data/test/1.docx"
file_name,extension_name=os.path.splitext(os.path.basename(docx_file_path))
contents=group_paragraphs_by_token_limit(docx_file_path,10000)
log=[]
nodes_array=[]
edges_array=[]
prompt = f"""
    在接下来的对话中，你需要遵循以下规则：
    你是一个擅长读书并总结的人，你的任务是处理我上传的课本选段，并按照以下要求进行操作：
    - 输出标准JSON格式字符串。
    - 剔除文件中的所有乱码（乱码不包括英文）。
    - 处理英文的时候 请保留英文的原格式，包括括号。
    - 我会告诉你这段文字的主题，你可以围绕着这个主题开始一层一层地梳理知识结构
    - 你需要对文本内知识点进行提取，并列成列表，形成json字符串的point字段。
    - 当你提取到一个知识点，在上下文寻找与他相关联的知识点，并进行提取
    - 你需要对知识点与知识点之间的从属关系进行提取，有关系的知识点两两之间形成(知识点1,属于，知识点2)的元组，并以列表的形式存进json字符串的edge字段
    - 像"一"、"二"或是"第一"、"第二"等形式的序号字符，可用于帮助定位实体。标题之间的层级结构，也可以帮助构建属于关系。
    - 这一章的名字叫ETC,请围绕ETC进行知识点提取和关系识别
    - 格式参考示例:
    {{
        "point": ["数学","线性代数","矩阵"],
        "edge":[["线性代数","属于","数学"],["矩阵","属于","线性代数"]]
    }}
    - 请保证提取出的关系有且仅有属于，被提取出的知识点，一定有相应的关系。
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
        nodes_array+=[node for node in nodes_array_n if node not in nodes_array]
        edges_array+=[edge for edge in edges_array_n if edge not in edges_array]
        log.append((content_id,nodes_array_n,edges_array_n))
    else:
        print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))
        break
# 构建xmind
forest = Forest()
forest.build_forest(nodes_array, edges_array,"ETC")
forest.build_kg("小节")