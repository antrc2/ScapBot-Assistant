from qdrant_client import QdrantClient
from qdrant_client.models import SearchParams
from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from google.genai import Client, types
# Load environment variables
load_dotenv()
base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")
chat_model = os.getenv("CHAT_MODEL")
embedding_model = os.getenv("EMBEDDING_MODEL")

# Initialize clients
qdrant = QdrantClient(path="database")
collection_name = "my_collection"
client = OpenAI(base_url=base_url, api_key=api_key)
clients = Client(api_key=api_key)
# Embed text into vector
def embed(text):
    embedding = clients.models.embed_content(
        model=embedding_model,
        contents=text,
        config=types.EmbedContentConfig(
          task_type="retrieval_query",
        )
    )
    return embedding.embeddings[0].values

# Search Qdrant vector DB
def search_in_qdrant_database(query):
    query_vector = embed(query)
    results = qdrant.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=15,
        search_params=SearchParams(hnsw_ef=2048, exact=True)
    )
    return ''.join(res.payload['text'] for res in results)
tools = [{
    "type": "function",
    "function": {
        "name": "search_in_qdrant_database",
        "description": "Tìm kiếm thêm thông tin ở trong Qdrant mỗi khi trả lời",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Từ khóa để tìm kiếm. Bắt buộc phải là tiếng Việt"
                },
                "limit": {
                    "type": "integer",
                    "description": "Số lượng muốn tìm kiếm (5-20)"
                }
            },
            "required": ["query"]
        }
    }
}]
def chat_with_gemini(messages):
    response = client.chat.completions.create(
        model=chat_model,
        messages=messages,
        tools=tools,
        tool_choice="required",
        max_tokens=1024
    )

    # Step 2: Check if AI used a tool
    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
        tool_call = tool_calls[0]
        arguments = json.loads(tool_call.function.arguments)

        # Step 3: Execute the tool
        result = search_in_qdrant_database(arguments['query'])

        # Step 4: Append tool call to messages
        messages.append({
            "role": "assistant",
            "tool_calls": [{
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            }]
        })

        # Step 5: Append tool result to messages
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result, ensure_ascii=False)
        })

        # Step 6: Send final message with full context
        final_response = client.chat.completions.create(
            model=chat_model,
            messages=messages,
            max_tokens=2048
        )
        return (final_response.choices[0].message.content)

    else:
        # If no tool used, just return the AI response directly
        return (response.choices[0].message.content)
