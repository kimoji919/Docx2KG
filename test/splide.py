import os
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
import re
import docx2txt
from transformers import AutoTokenizer
from typing import List, Dict, Union


def clean_text(text: str) -> str:
    regex = re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9。，“”‘’！？【】《》：；……,.!? ]')
    cleaned_text = re.sub(regex, '', text)
    return cleaned_text


def extract_text(file_path: str) -> str:
    text = ''
    if file_path.endswith('.doc') or file_path.endswith('.docx'):
        try:
            text = docx2txt.process(file_path)
        except FileNotFoundError:
            print(f"文件不存在：{file_path}")
        except IsADirectoryError:
            print(f"文件是一个目录：{file_path}")
    elif file_path.endswith('.pdf'):
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    try:
                        page_text = page.extract_text()
                        if page_text is not None:
                            text += page_text
                    except:
                        print(f"无法提取{file_path}的{page}页面文本。")
        except FileNotFoundError:
            print(f"文件不存在：{file_path}")
        except IsADirectoryError:
            print(f"文件是一个目录：{file_path}")
    else:
        print(f"{file_path}的文件格式不符合要求。")
    text = text.replace('\n', '')
    return text


def split_text(doc: str, chunk_size: int, chunk_overlap: int) -> List[Dict[str, Union[str, Dict]]]:
    model_path = os.environ.get("BAICHUAN_PATH", "baichuan-inc/Baichuan2-13B-Chat")
    tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False, trust_remote_code=True)

    def length_function(text: str) -> int:
        return len(tokenizer.tokenize(text))

    splitter = RecursiveCharacterTextSplitter(
        separators=["，", "。", '\\n\\n', '\\n'],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=length_function
    )

    text_splits = splitter.split_text(doc)
    # print(text_splits)
    return [{"content": text, "metadata": {}} for text in text_splits]


def extract_texts_from_file(
        file_path: str,
        chunk_size: int = 256,
        chunk_overlap: int = 32
) -> Dict[str, Union[str, List[Dict[str, Union[str, Dict]]]]]:
    file_type_handlers = ['.pdf', '.doc', '.docx']
    file_name = os.path.basename(os.path.splitext(file_path)[0])
    file_type = os.path.splitext(file_path)[1]
    if file_type in file_type_handlers:
        text = extract_text(file_path)
        cleaned_text = clean_text(text)
        texts = split_text(cleaned_text, chunk_size, chunk_overlap)
        return {"title": file_name, "slices": texts}
    else:
        raise Exception(f"不支持的{file_name}文件格式：{file_type}")


if __name__ == "__main__":
    DOCS_FOLDER = '.\\规章制度-学生类'
    output_dir = 'outputs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    all_splits = []
    for root, dirs, files in os.walk(DOCS_FOLDER):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_path = os.path.join(root, file)
            print(file_name)
            splits = extract_texts_from_file(file_path, 256, 32)
            all_splits.append(splits)

    json_output = json.dumps(all_splits, ensure_ascii=False, indent=4)
    with open('automation_outputs.json', 'w', encoding='utf-8') as f:
        json.dump(all_splits, f, ensure_ascii=False, indent=4)
