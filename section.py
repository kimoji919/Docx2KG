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
docx_file_path = "./data/1.docx"
file_name,extension_name=os.path.splitext(os.path.basename(docx_file_path))
contents=group_paragraphs_by_token_limit(docx_file_path,1000)
nodes_array=[]
edges_array=[]
prompt = """
    在接下来的对话中，你需要遵循以下规则：
    你是一台用于处理文本数据的AI系统。你的任务是处理我上传的文本文件，并按照以下要求进行操作：
    - 输出标准JSON格式的切片结果。
    - 剔除文件中的所有乱码（乱码不包括英文）。
    - 处理英文的时候 请保留英文的原格式，包括括号。
    - 根据你的判断，可以筛选无意义的、与学生无关的句子。但是要确保没有改变原意，保留了原本的信息量。
    - 确保没有信息遗漏，不要缺省任何有效信息。
    - 按照章节、条目，划分条目到最细，对内容进行切片，构建树状JSON结构，请确保你输出的JSON的格式规范。
    - 通过树状结构将"slices"中父节点的信息补充进content中。例如：第一章 第一条 xx内容，content 就是 “第一章 第一条 xx内容”
    - 格式参考示例:
    {
      "title": "(文件的标题)",
      "slices": [
        {
          "chapter_no": "第一章",
          "chapter_name": "(章节对应名称)",
          "entries": [
            {
                "entry_no":"第一条",
                "content":"第一章 (章节对应名称) 第一条 (第一条对应的内容)"
            },
            {
                "entry_no":"第二条",
                "content":"第一章 (章节对应名称) 第二条 (第二条对应的内容)"
            },
            ...
          ] 
        }
      ]
    }
    - 确保每一个条目都被完整地处理，不漏切片。
    你不需要确认收到，请从第一条讯息开始，直接开始生成完整准确的输出。
"""
# 发送请求阶段
for content_id,content in enumerate(contents):
    request=""
    print("————————————第"+str(content_id+1)+"次请求————————————")
    for paragraph_id,paragraph in enumerate(content):
        request+=paragraph
        request+='\n'
    # messages.append({'role': Role.USER, 'content': request})
    messages = [{'role': Role.SYSTEM, 'content': prompt},
              {'role': Role.USER, 'content': request}]
    response = Generation.call(
        Generation.Models.qwen_max,
        messages=messages,
        result_format='message',  # set the result to be "message" format.
    )
    if response.status_code == HTTPStatus.OK:
        print(response.output.choices[0]['message']['content'])
        print(response.usage["total_tokens"])
    else:
        print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))
        break
    # time.sleep(secs)