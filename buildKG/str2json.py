import json
def str2json(raw_string):
    # 解码为字符串
    decoded_string = raw_string.encode('utf-8').decode('utf-8')

    # 去除字符串内部的"\\"和"\\n"
    cleaned_string = decoded_string.replace("\\", "").replace("\\n", "").replace("```","").replace("json","")


    # 尝试解析为JSON
    try:
        json_data = json.loads(cleaned_string)
        nodes_array=json_data["point"]
        edges_array=json_data["edge"]
        # print(json.dumps(json_data, indent=2, ensure_ascii=False))  # 打印格式化后的JSON
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    
    return nodes_array,edges_array