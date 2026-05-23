# Kiến trúc Chatbot RAG CSV sử dụng LangChain

## 1. Kiến trúc thư mục

```text
rag-chatbot/
│
├── app/
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── chat_routes.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── prompt.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── vector_service.py
│   │   ├── retriever_service.py
│   │   ├── llm_service.py
│   │   └── rag_service.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chat_request.py
│   │   └── chat_response.py
│   │
│   └── main.py
│
├── data/
│   └── faq.csv
│
├── vector_db/
│
├── scripts/
│   └── ingest_csv.py
│
├── requirements.txt
│
└── .env
```

---

# 2. Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Backend | FastAPI |
| RAG Framework | LangChain |
| Vector DB | ChromaDB |
| Embedding | HuggingFace Embeddings |
| LLM | Gemini |
| CSV Processing | pandas |

---

# 3. Requirements

## `requirements.txt`

```txt
fastapi
uvicorn

langchain
langchain-community
langchain-core
langchain-google-genai
langchain-huggingface
langchain-chroma

chromadb

sentence-transformers

pandas
python-dotenv
python-multipart
```

---

# 4. File `.env`

```env
GOOGLE_API_KEY=YOUR_API_KEY
```

---

# 5. Luồng hoạt động hệ thống

## Giai đoạn ingest

```text
faq.csv
    ↓
load csv
    ↓
convert thành Documents
    ↓
embedding
    ↓
save ChromaDB
```

---

## Giai đoạn chatbot

```text
user question
      ↓
retriever
      ↓
similarity search
      ↓
top-k documents
      ↓
prompt
      ↓
Gemini
      ↓
final answer
```

---

# 6. Thiết kế CSV

## `data/faq.csv`

```csv
id,question,answer,category
1,"RAG là gì?","RAG là Retrieval Augmented Generation","AI"
2,"Spring Boot là gì?","Spring Boot là framework Java","Java"
```

---

# 7. Ingest dữ liệu

## `scripts/ingest_csv.py`

```python
import pandas as pd

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

CSV_PATH = "data/faq.csv"

df = pd.read_csv(CSV_PATH)

documents = []

for _, row in df.iterrows():

    content = f"""
    Question: {row['question']}

    Answer: {row['answer']}
    """

    doc = Document(
        page_content=content,
        metadata={
            "id": row["id"],
            "category": row["category"]
        }
    )

    documents.append(doc)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = Chroma.from_documents(
    documents=documents,
    embedding=embedding_model,
    persist_directory="vector_db"
)

print("Ingest success")
```

---

# 8. Config

## `app/core/config.py`

```python
import os

from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
```

---

# 9. Prompt

## `app/core/prompt.py`

```python
RAG_PROMPT = """
Bạn là chatbot AI.

Chỉ trả lời dựa trên context dưới đây.

Nếu không có thông tin,
hãy trả lời:

"Tôi không tìm thấy thông tin."

Context:
{context}

Question:
{question}
"""
```

---

# 10. Retriever Service

## `app/services/retriever_service.py`

```python
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = Chroma(
    persist_directory="vector_db",
    embedding_function=embedding_model
)

retriever = vector_store.as_retriever(
    search_kwargs={"k": 3}
)
```

---

# 11. LLM Service

## `app/services/llm_service.py`

```python
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GOOGLE_API_KEY
)
```

---

# 12. RAG Service

## `app/services/rag_service.py`

```python
from app.core.prompt import RAG_PROMPT
from app.services.retriever_service import retriever
from app.services.llm_service import llm

def ask_question(question: str):

    docs = retriever.invoke(question)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = RAG_PROMPT.format(
        context=context,
        question=question
    )

    response = llm.invoke(prompt)

    return response.content
```

---

# 13. Request Model

## `app/models/chat_request.py`

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str
```

---

# 14. Response Model

## `app/models/chat_response.py`

```python
from pydantic import BaseModel

class ChatResponse(BaseModel):
    answer: str
```

---

# 15. API Route

## `app/api/chat_routes.py`

```python
from fastapi import APIRouter

from app.models.chat_request import ChatRequest
from app.models.chat_response import ChatResponse

from app.services.rag_service import ask_question

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    answer = ask_question(request.question)

    return ChatResponse(answer=answer)
```

---

# 16. Main Application

## `app/main.py`

```python
from fastapi import FastAPI

from app.api.chat_routes import router

app = FastAPI()

app.include_router(router)
```

---

# 17. Chạy ingest

```bash
python scripts/ingest_csv.py
```

---

# 18. Chạy FastAPI

```bash
uvicorn app.main:app --reload
```

---

# 19. Test API

## Endpoint

```http
POST /chat
```

## Request

```json
{
  "question": "RAG hoạt động như thế nào?"
}
```

## Response

```json
{
  "answer": "RAG là Retrieval Augmented Generation..."
}
```

---

# 20. Vì sao LangChain phù hợp?

LangChain giúp:

- chuẩn hóa pipeline RAG
- dễ thay:
  - vector DB
  - embedding model
  - LLM
- hỗ trợ:
  - retriever
  - chain
  - memory
  - prompt template
  - agents

---

# 21. Khi project lớn hơn

Có thể mở rộng:

- Conversational RAG
- History Memory
- Hybrid Search
- Reranker
- Streaming Response
- Multi-document ingestion
- PDF loader
- Web loader
- Milvus/Qdrant
- LangSmith monitoring

---

# 22. Kiến trúc phù hợp cho version đầu

```text
FastAPI
+ LangChain
+ ChromaDB
+ HuggingFace Embedding
+ Gemini
+ CSV FAQ
```

Đây là kiến trúc rất phổ biến cho:

- chatbot FAQ
- chatbot nội bộ
- chatbot tài liệu
- demo CV
- đồ án RAG
- MVP AI system