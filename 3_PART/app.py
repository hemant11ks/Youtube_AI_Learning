import os
import streamlit as st
from dotenv import load_dotenv

# 🔹 Load ENV
load_dotenv()

# 🔹 LangChain Imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# -----------------------------
# 🔹 PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Chat with PDF", layout="wide")

st.title("📄🤖 Chat with your PDF")

# -----------------------------
# 🔹 SESSION STATE
# -----------------------------
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------
# 🔹 FILE UPLOAD
# -----------------------------
uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

if uploaded_file is not None:

    # Save file temporarily
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    # Load PDF
    loader = PyPDFLoader("temp.pdf")
    documents = loader.load()

    # Split
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    docs = text_splitter.split_documents(documents)

    # Embeddings + FAISS
    embeddings = OpenAIEmbeddings()
    vector_db = FAISS.from_documents(docs, embeddings)

    # Memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    # LLM
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4o-mini"
    )

    # Chain
    st.session_state.qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_db.as_retriever(),
        memory=memory,
        return_source_documents=True
    )

    st.success("✅ PDF processed! You can now ask questions.")

# -----------------------------
# 🔹 CHAT UI
# -----------------------------
if st.session_state.qa_chain:

    user_input = st.chat_input("Ask something about your PDF...")

    if user_input:
        result = st.session_state.qa_chain.invoke({"question": user_input})

        answer = result["answer"]
        sources = result["source_documents"]

        # Save chat
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Bot", answer))

    # Display chat
    for role, msg in st.session_state.chat_history:
        with st.chat_message(role.lower()):
            st.write(msg)

    # Show sources (latest response)
    if st.session_state.chat_history:
        st.subheader("📚 Sources (last answer)")
        for doc in sources[:2]:
            st.write(
                f"- {doc.metadata.get('source', 'N/A')} | Page: {doc.metadata.get('page', 'N/A')}"
            )