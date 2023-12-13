from docx import Document
from nltk.tokenize import word_tokenize
import nltk

# nltk.download('punkt')  # 下载必要的数据，只需要运行一次
def count_tokens(paragraph):
    tokens = word_tokenize(paragraph)
    return len(tokens)

def read_paragraphs(file_path):
    doc = Document(file_path)

    paragraphs = []
    for paragraph in doc.paragraphs:
        paragraphs.append(paragraph.text)

    return paragraphs

def group_paragraphs_by_token_limit(file_path, token_limit):
    doc = Document(file_path)

    current_group = []
    total_tokens = 0
    groups = []

    for paragraph in doc.paragraphs:
        tokens_count = count_tokens(paragraph.text)

        if total_tokens + tokens_count > token_limit and current_group:
            # Start a new group when adding the current paragraph exceeds the token limit
            groups.append(current_group)
            current_group = []
            total_tokens = 0

        current_group.append(paragraph.text)
        total_tokens += tokens_count

    # Add the last group if it's not empty
    if current_group:
        groups.append(current_group)

    return groups