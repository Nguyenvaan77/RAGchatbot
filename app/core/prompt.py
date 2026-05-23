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