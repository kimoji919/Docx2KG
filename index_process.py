# 将目录数据转成实体关系数据以及切片数据
from buildKG.str2json import indexstr2json,str2json
from buildKG.docx2request import group_paragraphs_by_token_limit,extract_text_from_pages,group_page_by_token_limit
from buildKG.forest import Node,Edge,Forest

from http import HTTPStatus
from dashscope import Generation
from dashscope.api_entities.dashscope_response import Role
import dashscope
import time
import random
import os

dashscope.api_key = "sk-8cdfdc6958a7408492d465269349299f"
# 目录起始页
start_page = 7
end_page = 10
pdf_output_path = './data/（153）商业智能在电子商务中的实践与应用-黄建鹏、徐晓冬、魏宝军-东南大学出版社.pdf'
# 执行目录提取
request=extract_text_from_pages(pdf_output_path, start_page, end_page)

nodes_array=[]
edges_array=[]
pages_array=[]
log=[]
prompt = """
    在接下来的对话中，你需要遵循以下规则：
    你是一台用于处理文本数据的AI系统。你的任务是处理我上传的文本文件，并按照以下要求进行操作：
    - 输出标准JSON格式的切片结果。
    - 剔除文件中的所有乱码（乱码不包括英文）。
    - 处理英文的时候 请保留英文的原格式，包括括号。
    - 根据你的判断，可以筛选无意义的、与目录无关的句子。但是要确保没有改变原意，保留了原本的信息量。
    - 确保没有信息遗漏，不要缺省任何有效信息。
    - 按照章节、条目，划分条目到最细，对内容进行切片，构建树状JSON结构，请确保你输出的JSON的格式规范。
    - 格式参考示例:
    {
      "slices": [
        {
          "chapter_name": "(章节去除章节号对应名称)",
          "entries": [
                "(第一节去除章节号对应名称)",
                "(第二节去除章节号对应名称)",
          ] ,
          "page":"(章节页码)"
        }
      ]
    }
    - 确保每一个条目都被完整地处理，不漏切片。
    - 对chapter_name、entries中的属性，请不要带上任何标号性质的前缀
    - 你不需要确认收到，请从第一条讯息开始，直接开始生成完整准确的输出，不允许输出json之外的内容
"""

messages = [{'role': Role.SYSTEM, 'content': prompt},
            {'role': Role.USER, 'content': request}]
response = Generation.call(
    Generation.Models.qwen_max_longcontext,
    messages=messages,
    result_format='message',  # set the result to be "message" format.
)
if response.status_code == HTTPStatus.OK:
    # append result to messages.
    nodes_array,edges_array,pages_array=indexstr2json(response.output.choices[0]['message']['content'])
else:
    print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
        response.request_id, response.status_code,
        response.code, response.message
    ))
pages_array=[page+end_page for page in pages_array]
print(nodes_array)
# prompt = f"""
#     在接下来的对话中，你需要遵循以下规则：
#     你是一台用于处理文本数据的AI系统。你的任务是处理我上传的文本，并按照以下要求进行操作：
#     - 输出标准JSON格式字符串。
#     - 剔除文件中的所有乱码（乱码不包括英文）。
#     - 处理英文的时候 请保留英文的原格式，包括括号。
#     - 对文本内知识点进行提取，并列成列表，形成json字符串的point字段。
#     - 有["属于","递进","实例","关联"]四种关系，对知识点与知识点之间的关系进行提取，有关系的知识点两两之间形成(知识点1,知识点2,关系)的元组，并以列表的形式存进json字符串的edge字段
#     - 四种关系中“属于”表示一个知识点是另一个知识点的一部分或属于它的范畴。例如，"狗 属于 动物" 表示狗是动物的一种。
#     - 递进关系表示两个知识点之间的逐步发展或层次递进的关系。例如，"初中 递进 高中" 表示初中逐渐发展为高中。
#     - 实例关系表示一个知识点是另一个知识点的具体实例。例如，"苹果 实例 水果" 表示苹果是水果的一种具体实例。
#     - 关联关系表示两个知识点之间存在某种关联，但不一定是属于或实例的关系。它强调两者之间的相关性，而不一定涉及包含或具体实例。例如，"雨天 关联 雨伞" 表示在雨天时，人们常常会使用雨伞。
#     - 我们发现通常会有像"一"、"二"或是"第一"、"第二"等形式的序号字符，可用于帮助定位实体。标题之间的层级结构，也可以帮助构建属于关系。
#     - 请尽可能深层次的提取每一个实体和关系
#     - 格式参考示例:
#     {{
#         "point": ["数学","线性代数","矩阵","秩","习题：矩阵的定义是什么","线性代数提出者的一生"],
#         "edge":[["线性代数","属于","数学"],["矩阵","属于","线性代数"],["秩","递进","矩阵"],["矩阵","实例","习题：矩阵的定义是什么"],["线性代数","关联","线性代数提出者的一生"]]
#     }}
#     - 同时你可以参考上下文中已经提取好的实例和关系,在生成答案的时候，你必须保证这些实例和关系不能改变，只能在这些基础之上新增实体和关系：
#     {{
#         "point": {nodes_array},
#         "edge":  {edges_array}
#     }}
#     你不需要确认收到，或是做出过多解释，直接开始生成完整准确的输出。
# """
# for i in range(0,len(pages_array)-1):
#     start=pages_array[i]
#     end=pages_array[i+1]
#     contents=group_page_by_token_limit(pdf_output_path,1000, start, end)
#     for content_id,content in enumerate(contents):
#         request=""
#         print("————————————第"+str(content_id)+"次请求————————————")
#         for paragraph_id,paragraph in enumerate(content):
#             request+=paragraph
#             request+='\n'
#         # messages.append({'role': Role.USER, 'content': request})
#         messages = [{'role': Role.SYSTEM, 'content': prompt},
#                 {'role': Role.USER, 'content': request}]
#         response = Generation.call(
#             Generation.Models.qwen_max_longcontext,
#             messages=messages,
#             result_format='message',  # set the result to be "message" format.
#         )
#         if response.status_code == HTTPStatus.OK:
#             print(response.output.choices[0]['message']['content'])
#             print(response.usage["total_tokens"])
#             # append result to messages.
#             nodes_array_n,edges_array_n=str2json(response.output.choices[0]['message']['content'])
#             nodes_array+=[node for node in nodes_array_n if node not in nodes_array]
#             edges_array+=[edge for edge in edges_array_n if edge not in edges_array]
#             log.append((content_id,nodes_array_n,edges_array_n))
#         else:
#             print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
#                 response.request_id, response.status_code,
#                 response.code, response.message
#             ))
#             break
#         secs = random.normalvariate(80, 0.4)
#         if secs <= 60 or secs >= 120:
#             secs =80   # 太小则重置为平均值
#         print("sleep:"+str(secs)+"秒")
#         time.sleep(secs)       
# # 构建xmind
# forest = Forest()
# forest.build_forest(nodes_array, edges_array)
# forest.build_kg()