from .retriever_service import retriever
from .llm_service import llm
from app.repositories.message_repository import get_message_from_session
from langchain.agents import create_agent
from langchain.messages import AIMessageChunk
from langchain_core.messages import HumanMessage

agent = create_agent(
    model=llm,
    tools=[]
)

async def ask_question(question: str, session_id: str, history):
    messages = [
        {
            "role": message.role,
            "content": message.content
        }

        for message in history
    ]

    answer = ""

    stream = agent.astream(
        {
            "messages": [
                *messages
                ,HumanMessage(content=question)
            ]
        },
        stream_mode="messages"
    )

    async for token, metadata in stream:

        if metadata["langgraph_node"] != "model":
            continue

        if not isinstance(token, AIMessageChunk):
            continue

        for block in token.content_blocks:

            if block["type"] == "text":

                text = block["text"]

                answer += text

                # stream token về frontend
                yield text