# from qdrant_client import QdrantClient
# from qdrant_client.models import PointStruct, VectorParams, Distance
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.schema import Document
# from openai import OpenAI
# import pandas as pd
# import uuid  # Để tạo id duy nhất

# # === Khởi tạo Qdrant và OpenAI ===
# qdrant = QdrantClient(path="database")
# client = OpenAI(base_url="http://26.203.51.178:5555/v1", api_key="dont_need")

# collection_name = "my_collection"

# # === Tạo collection nếu chưa tồn tại ===
# if collection_name not in [c.name for c in qdrant.get_collections().collections]:
#     qdrant.create_collection(
#         collection_name=collection_name,
#         vectors_config=VectorParams(size=768, distance=Distance.COSINE)  # Size tùy theo model bạn dùng
#     )
#     print(f"✅ Đã tạo collection `{collection_name}`")

# # === Hàm split văn bản ===
# def text_split(docs):
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=512,
#         chunk_overlap=100,
#         separators=["\n\n", "\n", " ", ""],
#         length_function=len
#     )
#     return text_splitter.split_documents(docs)

# # === Hàm lấy embedding từ API ===
# def embeddingText(text):
#     return client.embeddings.create(
#         model="text-embedding-nomic-embed-text-v1.5",
#         input=text,
#         encoding_format='float'
#     ).data[0].embedding

# # === Đọc file Excel và xử lý ===
# file_path = "data.xlsx"
# all_sheets = pd.read_excel(file_path, sheet_name=None, header=None)

# # === Chuẩn bị danh sách PointStruct để đưa vào Qdrant ===
# points = []

# for sheet_name, df in all_sheets.items():
#     df_text = "\n".join(df.astype(str).apply(lambda row: " ".join(row), axis=1))
#     document = Document(
#         page_content=df_text,
#         metadata={'source': file_path, 'sheet_name': sheet_name}
#     )
#     documents = text_split([document])

#     for doc in documents:
#         embedding = embeddingText(doc.page_content)
#         point = PointStruct(
#             id=str(uuid.uuid4()),  # id ngẫu nhiên duy nhất
#             vector=embedding,
#             payload={
#                 "text": doc.page_content,
#                 "source": doc.metadata.get("source"),
#                 "sheet": doc.metadata.get("sheet_name")
#             }
#         )
#         points.append(point)

# # === Đưa vào Qdrant ===
# if points:
#     qdrant.upsert(collection_name=collection_name, points=points)
#     print(f"✅ Đã upsert {len(points)} điểm vào collection `{collection_name}`")
# else:
#     print("⚠️ Không có dữ liệu nào được upsert vào Qdrant.")


# query.py
# from qdrant_client import QdrantClient
# from openai import OpenAI

# qdrant = QdrantClient(path="database")
# collection_name = "my_collection"

# client = OpenAI(base_url="http://26.203.51.178:5555/v1", api_key="AIzaSyB45BxMcdiViDPeZnW5lz1y9tRL-z3Vckc")

# def embed(text):
#     return client.embeddings.create(
#         model="text-embedding-nomic-embed-text-v1.5",
#         input=text
#     ).data[0].embedding

# # query = input("❓ Nhập câu hỏi: ")
# query = "ScapBot"
# query_vector = embed(query)

# results = qdrant.search(
#     collection_name=collection_name,
#     query_vector=query_vector,
#     limit=5
# )

# print("\n📄 Kết quả liên quan:")
# for r in results:
#     print(r)
    # print(f"- [{r.payload['source']} - trang {r.payload['page']}]")
    # print(r.payload['text'][:300], "\n---\n")
