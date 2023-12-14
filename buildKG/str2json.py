import json
import re
def str2json(raw_string):
    # 解码为字符串
    decoded_string = raw_string.encode('utf-8').decode('utf-8')

    # 去除字符串内部的"\\"和"\\n"
    cleaned_string = decoded_string.replace("\\", "").replace("\\n", "").replace("```","").replace("json","")
    nodes_array=[]
    edges_array=[]
    # 尝试解析为JSON
    try:
        json_data = json.loads(cleaned_string)
        nodes_array=json_data["point"]
        edges_array=json_data["edge"]
        # print(json.dumps(json_data, indent=2, ensure_ascii=False))  # 打印格式化后的JSON
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        pattern = r'```(.*?)```'
        cleaned_string = re.findall(pattern, raw_string, re.DOTALL)
        print(cleaned_string)
        if len(cleaned_string)==1:
            json_data = json.loads(cleaned_string[0])
            nodes_array=json_data["point"]
            edges_array=json_data["edge"]
        else:
            nodes_array=[]
            edges_array=[]

    return nodes_array,edges_array