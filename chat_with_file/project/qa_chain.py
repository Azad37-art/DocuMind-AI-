from typing import List, Dict, Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS

from project.config import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE, MAX_OUTPUT_TOKENS


SYSTEM_PROMPT = """You are an intelligent document assistant. Your job is to answer questions \
based strictly on the content of the uploaded document(s). 

Guidelines:
- Answer only based on the provided context from the document.
- If the answer is not found in the document, clearly say "I couldn't find this information in the uploaded document."
- Be concise yet comprehensive in your responses.
- When relevant, mention which part of the document the information comes from.
- Use bullet points or numbered lists when listing multiple items for clarity.
- If asked for a summary, provide a well-structured overview of the document content.

Context from document:
{context}

Chat History:
{chat_history}

Human Question: {question}

Assistant Answer:"""


def get_llm() -> ChatGoogleGenerativeAI:
    """Initialize and return the Gemini LLM."""
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GEMINI_API_KEY,
        temperature=TEMPERATURE,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        convert_system_message_to_human=True,
    )
    return llm



def create_qa_chain(vector_store: FAISS) -> ConversationalRetrievalChain:
    """Create a conversational QA chain with memory."""
    llm = get_llm()
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )

    qa_prompt = PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template=SYSTEM_PROMPT,
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": qa_prompt},
        verbose=False,
    )
    return chain




def ask_question(
    chain: ConversationalRetrievalChain,
    question: str,
) -> Dict[str, Any]:
    """Ask a question using the QA chain and return the response."""
    result = chain.invoke({"question": question})
    answer = result.get("answer", "")
    source_docs = result.get("source_documents", [])

    sources = []
    seen_sources = set()
    for doc in source_docs:
        source_name = doc.metadata.get("source_filename", "Unknown")
        page = doc.metadata.get("page", None)
        key = f"{source_name}_{page}"
        if key not in seen_sources:
            seen_sources.add(key)
            sources.append(
                {
                    "filename": source_name,
                    "page": page,
                    "snippet": doc.page_content[:200] + "..."
                    if len(doc.page_content) > 200
                    else doc.page_content,
                }
            )

    return {
        "answer": answer,
        "sources": sources,
    }
