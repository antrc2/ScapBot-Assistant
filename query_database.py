from qdrant_client import QdrantClient
from openai import OpenAI
import json
import os
qdrant = QdrantClient(path="database")
collection_name = "my_collection"
base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")
chat_model = os.getenv("CHAT_MODEL")
embedding_model = os.getenv("EMBEDDING_MODEL")

client = OpenAI(base_url=base_url, api_key=api_key)

def embed(text):
    return client.embeddings.create(
        model=embedding_model,
        input=text
    ).data[0].embedding
def search_in_qdrant_database(query):
    query_vector = embed(query)
    results = qdrant.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=5
    )
    result = ''
    for res in results:
        result += res.payload['text']
    return result

import json

tools = [{
    "type": "function",
    "function": {
        "name": "search_in_qdrant_database",
        "description": "Tìm kiếm thêm thông tin ở trong Qdrant",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Từ khóa để tìm kiếm. Bắt buộc phải là tiếng Việt"
                },
            },
            "required": ["query"]
        }
    }
}]

messages = [
    {
        "role": "user",
        "content": "Giới thiệu chi tiết về dịch vụ của ScapBot"
    }
]

# Bước 1: gửi initial prompt
response = client.chat.completions.create(
    model=chat_model,
    messages=messages,
    tools=tools,
    tool_choice="required",
    max_tokens=512,
)

# Bước 2: lấy tool_call từ assistant
tool_call = response.choices[0].message.tool_calls[0]
arguments = json.loads(tool_call.function.arguments)
# print(arguments['query'])
# print(type(arguments))
# Bước 3: thực thi function
result = search_in_qdrant_database(arguments['query'])

# Bước 4: Append assistant function call
messages.append({
    "role": "assistant",
    "tool_calls": [
        {
            "id": tool_call.id,
            "type": "function",
            "function": {
                "name": tool_call.function.name,
                "arguments": tool_call.function.arguments
            }
        }
    ]
})

# Bước 5: Append kết quả trả về từ tool
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": json.dumps(result, ensure_ascii=False)  # nếu result là dict/list
})

# Bước 6: Gửi lại đầy đủ để AI phản hồi
final_response = client.chat.completions.create(
    model="gemini-2.0-flash",
    messages=messages,
    max_tokens=1024,
)

# In kết quả trả lời cuối cùng
print(final_response.choices[0].message.content)
