# chatbot/retriever.py
# RAG (Retrieval-Augmented Generation) setup using FAISS + HuggingFace embeddings
# This lets the bot "look up" relevant menu/FAQ info before answering

import os
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document


# ── Path Constants ─────────────────────────────────────────────────────────────
VECTOR_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "vector_db", "faiss_index")
MENU_PATH      = os.path.join(os.path.dirname(__file__), "..", "data", "menu.csv")
FAQ_PATH       = os.path.join(os.path.dirname(__file__), "..", "data", "faq.csv")

# Using a lightweight model that runs without GPU
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def get_embeddings():
    """Load HuggingFace embedding model (cached after first load)."""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )


def build_documents_from_menu(df: pd.DataFrame) -> list[Document]:
    """
    Convert each menu row into a LangChain Document for indexing.
    Rich text descriptions help the retriever find relevant items.
    """
    documents = []
    for _, row in df.iterrows():
        veg_label = "Vegetarian" if str(row["is_vegetarian"]).lower() == "yes" else "Non-Vegetarian"
        text = (
            f"Item: {row['name']} | Category: {row['category']} | Price: ${row['price']} | "
            f"Calories: {row['calories']} kcal | Protein: {row['protein']}g | "
            f"Carbs: {row['carbs']}g | Fat: {row['fat']}g | "
            f"Health Score: {row['health_score']}/10 | {veg_label} | "
            f"Health Benefits: {row['health_benefits']}"
        )
        documents.append(Document(page_content=text, metadata={"source": "menu", "name": row["name"]}))
    return documents


def build_documents_from_faq(df: pd.DataFrame) -> list[Document]:
    """
    Convert FAQ rows into LangChain Documents.
    """
    documents = []
    for _, row in df.iterrows():
        text = f"Q: {row['question']}\nA: {row['answer']}"
        documents.append(Document(page_content=text, metadata={"source": "faq"}))
    return documents


def build_vector_store():
    """
    Build FAISS index from menu + FAQ data and save to disk.
    Run this once (or when menu changes).
    """
    print("📚 Building vector store from menu and FAQ data...")

    menu_df = pd.read_csv(MENU_PATH)
    faq_df  = pd.read_csv(FAQ_PATH)

    menu_docs = build_documents_from_menu(menu_df)
    faq_docs  = build_documents_from_faq(faq_df)
    all_docs  = menu_docs + faq_docs

    embeddings   = get_embeddings()
    vector_store = FAISS.from_documents(all_docs, embeddings)

    os.makedirs(os.path.dirname(VECTOR_DB_PATH), exist_ok=True)
    vector_store.save_local(VECTOR_DB_PATH)

    print(f"✅ Vector store saved → {VECTOR_DB_PATH}  ({len(all_docs)} documents indexed)")
    return vector_store


def load_vector_store():
    """
    Load FAISS index from disk. Build it first if it doesn't exist.
    Returns a FAISS retriever object.
    """
    embeddings = get_embeddings()

    if not os.path.exists(VECTOR_DB_PATH):
        print("⚠️  Vector store not found. Building now...")
        build_vector_store()

    vector_store = FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True   # safe — we built this file ourselves
    )
    return vector_store


def retrieve_context(query: str, k: int = 5) -> str:
    """
    Given a user query, retrieve the top-k most relevant documents
    and return them as a single formatted string for the LLM prompt.
    
    Args:
        query: The user's question or message
        k: Number of documents to retrieve
        
    Returns:
        Formatted context string
    """
    try:
        vector_store = load_vector_store()
        docs = vector_store.similarity_search(query, k=k)

        if not docs:
            return "No specific context found."

        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "info").upper()
            context_parts.append(f"[{source} {i}]\n{doc.page_content}")

        return "\n\n".join(context_parts)

    except Exception as e:
        print(f"Retriever error: {e}")
        return "Context retrieval unavailable."
