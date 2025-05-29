from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from qdrant_client.http import models
from openai import OpenAI
from google.genai import Client, types
import pandas as pd
import uuid  # Để tạo id duy nhất
import os
from dotenv import load_dotenv
load_dotenv()
base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")
chat_model = os.getenv("CHAT_MODEL")
embedding_model = os.getenv("EMBEDDING_MODEL")
file_path = "data.xlsx"

# === Khởi tạo Qdrant và OpenAI ===
qdrant = QdrantClient(path="database")
client = OpenAI(base_url=base_url, api_key=api_key)
clients = Client(api_key=api_key)
collection_name = "my_collection"

# === Tạo collection nếu chưa tồn tại ===
if collection_name not in [c.name for c in qdrant.get_collections().collections]:
    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),  # Size tùy theo model bạn dùng
        hnsw_config=models.HnswConfigDiff(
        m=16,           # số liên kết giữa các điểm (cao hơn tăng độ chính xác)
        ef_construct=200  # độ sâu tìm kiếm khi xây chỉ mục
    )
    )
    print(f"✅ Đã tạo collection `{collection_name}`")

# === Hàm split văn bản ===
def text_split(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""],
        length_function=len
    )
    return text_splitter.split_documents(docs)

# === Hàm lấy embedding từ API ===
# def embeddingText(text):
#     return client.embeddings.create(
#         model=embedding_model,
#         input=text,
#         encoding_format='float'
#     ).data[0].embedding
def embeddingText(text):
    embedding = clients.models.embed_content(
        model=embedding_model,
        contents=text,
        config=types.EmbedContentConfig(
          task_type="RETRIEVAL_DOCUMENT",
        )
    )
    return embedding.embeddings[0].values

all_sheets = pd.read_excel(file_path, sheet_name=None, header=None)

# === Chuẩn bị danh sách PointStruct để đưa vào Qdrant ===
points = []

for sheet_name, df in all_sheets.items():
    df_text = "\n".join(df.astype(str).apply(lambda row: " ".join(row), axis=1))
    document = Document(
        page_content=df_text,
        metadata={'source': file_path, 'sheet_name': sheet_name}
    )
    documents = text_split([document])

    for doc in documents:
        embedding = embeddingText(doc.page_content)
        point = PointStruct(
            id=str(uuid.uuid4()),  # id ngẫu nhiên duy nhất
            vector=embedding,
            payload={
                "text": doc.page_content,
                "source": doc.metadata.get("source"),
                "sheet": doc.metadata.get("sheet_name")
            }
        )
        points.append(point)

# === Đưa vào Qdrant ===
if points:
    qdrant.upsert(collection_name=collection_name, points=points)
    print(f"✅ Đã upsert {len(points)} điểm vào collection `{collection_name}`")
else:
    print("⚠️ Không có dữ liệu nào được upsert vào Qdrant.")