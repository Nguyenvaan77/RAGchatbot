from ..core.prompt import RAG_PROMPT
from .retriever_service import retriever
from .llm_service import llm

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