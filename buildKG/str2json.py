import json
import re
def str2json(raw_string):
    # 解码为字符串
    raw_string= raw_string.replace("'", '"')
    decoded_string = raw_string.encode('utf-8').decode('utf-8')

    # 去除字符串内部的"\\"和"\\n"
    cleaned_string = decoded_string.replace("\\", "").replace("\\n", "").replace("```","").replace("json","")
    nodes_array=[]
    edges_array=[]
    try:
        json_data = json.loads(raw_string)
        nodes_array=json_data["point"]
        edges_array=json_data["edge"]
    except json.JSONDecodeError as e:
        # 尝试解析为JSON
        try:
            json_data = json.loads(cleaned_string)
            nodes_array=json_data["point"]
            edges_array=json_data["edge"]
            # print(json.dumps(json_data, indent=2, ensure_ascii=False))  # 打印格式化后的JSON
        except json.JSONDecodeError as e:
            nodes_array=[]
            edges_array=[]
            print(f"Error decoding JSON: {e}")
            # pattern = r'```(.*?)```'
            # cleaned_string = re.findall(pattern, raw_string, re.DOTALL)
            # print(cleaned_string)
            # try:
            #     json_data = json.loads(cleaned_string[0])
            #     nodes_array=json_data["point"]
            #     edges_array=json_data["edge"]
            # except json.JSONDecodeError as e:
            #     nodes_array=[]
            #     edges_array=[]

    return nodes_array,edges_array

def indexstr2json(raw_string):
    # 解码为字符串
    raw_string= raw_string.replace("'", '"')
    decoded_string = raw_string.encode('utf-8').decode('utf-8')
    
    # 去除字符串内部的"\\"和"\\n"
    cleaned_string = decoded_string.replace("\\", "").replace("\\n", "").replace("```","").replace("json","")
    nodes_array=[]
    edges_array=[]
    pages_array=[]
    pages_part_array=[]
    # 尝试解析为JSON
    try:
        json_data = json.loads(cleaned_string)
        slices=json_data["slices"]
        for slice in slices:
            source=slice["chapter_name"]
            nodes_array.append(source)
            # for entrie in slice["entries"]:
            #     if entrie != "总结" and entrie != "小结":
            #         nodes_array.append(entrie)
            #         edges_array.append((entrie,"属于",source))
            for entrie in slice["entries"]:
                pages_array.append(int(entrie["page"]))
                pages_part_array.append(entrie["entry_name"])
                nodes_array.append(entrie["entry_name"])
                edges_array.append((entrie["entry_name"],"属于",source))
        # print(json.dumps(json_data, indent=2, ensure_ascii=False))  # 打印格式化后的JSON
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        nodes_array=[]
        edges_array=[]
        pages_array=[]
    return nodes_array,edges_array,pages_array,pages_part_array
