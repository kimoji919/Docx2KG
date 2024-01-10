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
import fitz  # PyMuPDF
import copy
dashscope.api_key = "sk-8cdfdc6958a7408492d465269349299f"

# 目录起始页
start_page = 12
end_page = 15
pdf_output_path = './data/（139） 3D打印技术基础（第三版）-朱红,易杰,谢丹-华中科技大学出版社.pdf'
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
    - 按照章节、小节，对内容进行切片，构建树状JSON结构，请确保你输出的JSON的格式规范。
    - 请严格参考格式示例:
    {
      "slices": [
        {
      "chapter_name": "(章节去除编号对应名称）",
      "page": "（章节对应页码）",
      "entries": [
        {
          "entry_name": "（小节去除编号对应名称）",
          "page": "（小节对应页码）",
        }
        {
          "entry_name": "（小节去除编号对应名称）",
          "page": "（小节对应页码）",
        }
      ]
    },
      ]
    }
    - 确保每一个条目都被完整地处理，不漏切片。
    - 对chapter_name、entries中的属性，请不要带上任何标号性质的前缀，并对你提取到的名称进行概括
    - 不要输出subentries
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
    raw_string=response.output.choices[0]['message']['content']
    print(raw_string)
    nodes_array,edges_array,pages_array,pages_part_array=indexstr2json(raw_string)
else:
    print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
        response.request_id, response.status_code,
        response.code, response.message
    ))
# 检查LLM输出是否带有章节号，是否带有小结等会污染节点的内容
part_array=copy.copy(nodes_array)
print(len(part_array))
# 这段代码不能重复跑，pages_array需要重新生成
pages_array=[page+end_page for page in pages_array]
pages_array=sorted(pages_array)
# pages_array=[16, 17, 19, 20, 21, 23, 25, 45, 58, 60, 65, 77, 80, 82, 90, 100, 101, 102, 107, 119, 123, 125, 129, 138, 140, 141, 144, 151, 153, 155, 157, 161, 171, 179, 183, 185, 186, 188]
# 补充尾页信息
# 打开 PDF 文件
pdf_document = fitz.open(pdf_output_path)
    # 获取总页数
total_pages = pdf_document.page_count
pages_array.append(total_pages)
node_array=copy.copy(part_array)
debug_array=[]
part_name=""
prompt = f"""
    在接下来的对话中，你需要遵循以下规则：
    你是一个擅长读书并总结的人，你的任务是处理我上传的课本选段，并按照以下要求进行操作：
    - 输出标准JSON格式字符串。
    - 剔除文件中的所有乱码（乱码不包括英文）。
    - 处理英文的时候 请保留英文的原格式，包括括号。
    - 我会告诉你这段文字的主题，你可以围绕着这个主题开始一层一层地梳理知识结构
    - 你需要对文本内知识点进行提取，并列成列表，形成json字符串的point字段。
    - 当你提取到一个知识点，在上下文寻找与他相关联的知识点，并进行提取
    - 你需要对知识点与知识点之间的属于关系进行提取，将有属于关系的知识点两两之间形成(知识点1,属于，知识点2)的元组，并以列表的形式存进json字符串的edge字段
    - 像"一"、"二"或是"第一"、"第二"等形式的序号字符，可用于帮助定位实体。标题之间的层级结构，也可以帮助构建属于关系。
    - 这一节的名字叫{part_name},请围绕{part_name}进行知识点提取和属于关系识别
    - 格式参考示例:
    {{
        "point": ["数学","线性代数","矩阵"],
        "edge":[["线性代数","属于","数学"],["矩阵","属于","线性代数"]]
    }}
    - 请保证仅提取属于关系，被提取出的知识点一定有相应的关系。
    你不需要确认收到，或是做出过多解释，直接开始生成完整准确的输出。
"""
    # 下面这段原本是写在提示词里面的，表征上下文，但是由于我们将提取目录中，构建关系的部分删去了，这部分写入提示词会导致边生成不出来，故注释掉
    # - 同时你可以参考上下文中已经提取好的实例和关系,在生成答案的时候，你必须保证这些实例和关系不能改变，只能在这些基础之上新增实体和关系：
    # {{
    #     "point": {nodes_array},
    #     "edge":  {edges_array}
    # }}
    # 实测加了这段话生成的内容边多了，但是很杂，影响最后生成结果且会造成各种生成的答案格式不正确等问题；但是理论上来说，我们需要上下文提示，下一期工程再改吧
for i in range(0,len(pages_array)-1):
    print("————————————第"+str(i+1)+"章————————————")
    start=pages_array[i]
    end=pages_array[i+1]
    part_name=pages_part_array[i]
    prompt = f"""
    在接下来的对话中，你需要遵循以下规则：
    你是一个擅长读书并总结的人，你的任务是处理我上传的课本选段，并按照以下要求进行操作：
    - 输出标准JSON格式字符串。
    - 剔除文件中的所有乱码（乱码不包括英文）。
    - 处理英文的时候 请保留英文的原格式，包括括号。
    - 我会告诉你这段文字的主题，你可以围绕着这个主题开始一层一层地梳理知识结构
    - 你需要对文本内知识点进行提取，并列成列表，形成json字符串的point字段。
    - 当你提取到一个知识点，在上下文寻找与他相关联的知识点，并进行提取
    - 你需要对知识点与知识点之间的属于关系进行提取，将有属于关系的知识点两两之间形成(知识点1,属于，知识点2)的元组，并以列表的形式存进json字符串的edge字段
    - 像"一"、"二"或是"第一"、"第二"等形式的序号字符，可用于帮助定位实体。标题之间的层级结构，也可以帮助构建属于关系。
    - 这一节的名字叫{part_name},请围绕{part_name}进行知识点提取和属于关系识别
    - 格式参考示例:
    {{
        "point": ["数学","线性代数","矩阵"],
        "edge":[["线性代数","属于","数学"],["矩阵","属于","线性代数"]]
    }}
    - 请保证仅提取属于关系，被提取出的知识点一定有相应的关系。
    你不需要确认收到，或是做出过多解释，直接开始生成完整准确的输出。
    """
    # 50000是token数量，可以用来选择单元切片的大小
    # 经过我的测试，小节所表现出的效果不如章节，很乱很杂，当然也有可能是因为上下文提示词的原因
    contents=group_page_by_token_limit(pdf_output_path,50000, start, end)
    for content_id,content in enumerate(contents):
        request=""
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
            raw_string=response.output.choices[0]['message']['content']
            # print(raw_string)
            # print(response.usage["total_tokens"])
            # append result to messages.
            nodes_array_n,edges_array_n=str2json(raw_string)
            nodes_array+=[node for node in nodes_array_n if node not in nodes_array]
            edges_array+=[edge for edge in edges_array_n if edge not in edges_array]
            log.append((i,nodes_array_n,edges_array_n))
            if nodes_array_n ==[] or edges_array_n==[]:
                debug_array.append(i)
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
            debug_array.append(i)
            break
        # api限制是1分钟调用一次
        secs = random.normalvariate(45, 0.4)
        if secs <= 30 or secs >= 70:
            secs =45   # 太小或太大则重置为平均值
        print("sleep:"+str(secs)+"秒")
        time.sleep(secs)       
        
import pickle
with open('node.pkl', 'wb') as f:
    pickle.dump(nodes_array, f)
with open('edge.pkl', 'wb') as f:
    pickle.dump(edges_array, f)
with open('log.pkl', 'wb') as f:
    pickle.dump(log, f)
with open('part_array.pkl', 'wb') as f:
    pickle.dump(part_array, f)

# 构建xmind
forest = Forest()
forest.build_forest(part_array,[],None)
for l in log:
    id,nodes_array_i,edges_array_i=l
    part=part_array[id]
    forest.build_forest(nodes_array_i,edges_array_i,part)
forest.build_kg("3D打印技术基础")