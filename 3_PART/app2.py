# ==============================
# 🔹 IMPORTS & SETUP
# ==============================

import os  # Used for environment variables and file handling
import streamlit as st  # Streamlit is used to build the web UI
from dotenv import load_dotenv  # Loads environment variables from .env file

# Load environment variables (like OPENAI_API_KEY)
load_dotenv()


# ==============================
# 🔹 LANGCHAIN IMPORTS
# ==============================

# Used to load and read PDF files
from langchain_community.document_loaders import PyPDFLoader

# Used to split large text into smaller chunks
from langchain_text_splitters import RecursiveCharacterTextSplitter

# OpenAI embeddings + chat model
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# FAISS is a vector database for similarity search
from langchain_community.vectorstores import FAISS

# Memory to store conversation history
from langchain.memory import ConversationBufferMemory

# Chain that combines retrieval + LLM + memory
from langchain.chains import ConversationalRetrievalChain


# ==============================
# 🔹 STREAMLIT PAGE CONFIG
# ==============================

# Set page title and layout
st.set_page_config(page_title="Chat with PDF", layout="wide")

# Display title on UI
st.title("📄🤖 Chat with your PDF")


# ==============================
# 🔹 SESSION STATE (IMPORTANT)
# ==============================

# Store QA chain (RAG pipeline) so it doesn't reset on every interaction
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None

# Store chat history (user + bot messages)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ==============================
# 🔹 FILE UPLOAD
# ==============================

# UI component to upload PDF file
uploaded_file = st.file_uploader("Upload your PDF", type="pdf")


# ==============================
# 🔹 PDF PROCESSING (RAG PIPELINE)
# ==============================

if uploaded_file is not None:

    # Save uploaded file temporarily to disk
    # This is required because PyPDFLoader works with file paths
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    # -----------------------------
    # 🔹 LOAD PDF
    # -----------------------------

    # Initialize PDF loader
    loader = PyPDFLoader("temp.pdf")

    # Load PDF into list of documents (each page becomes a document)
    documents = loader.load()

    # -----------------------------
    # 🔹 TEXT SPLITTING
    # -----------------------------

    # Create text splitter
    # chunk_size = max size of each chunk
    # chunk_overlap = overlapping text between chunks (helps context continuity)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    # Split documents into smaller chunks
    docs = text_splitter.split_documents(documents)

    # -----------------------------
    # 🔹 EMBEDDINGS + VECTOR DB
    # -----------------------------

    # Initialize OpenAI embeddings model
    embeddings = OpenAIEmbeddings()

    # Convert text chunks into vectors and store in FAISS database
    vector_db = FAISS.from_documents(docs, embeddings)

    # -----------------------------
    # 🔹 MEMORY (CHAT HISTORY)
    # -----------------------------

    # ConversationBufferMemory stores full conversation
    # memory_key = key used internally in chain
    # return_messages = returns structured messages instead of plain text
    # output_key = tells memory where answer is stored
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    # -----------------------------
    # 🔹 LLM SETUP
    # -----------------------------

    # Initialize ChatGPT model
    # temperature=0 → more factual, less creative
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4o-mini"
    )

    # -----------------------------
    # 🔹 RETRIEVER CONFIG
    # -----------------------------

    # Convert FAISS into retriever
    # k=3 → top 3 relevant chunks will be retrieved
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})

    # -----------------------------
    # 🔹 CREATE RAG CHAIN
    # -----------------------------

    # This chain connects:
    # 1. Retriever (search relevant chunks)
    # 2. LLM (generate answer)
    # 3. Memory (chat history)
    st.session_state.qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True  # Return source chunks for transparency
    )

    # Show success message
    st.success("✅ PDF processed! You can now ask questions.")


# ==============================
# 🔹 CHAT INTERFACE
# ==============================

# Only show chat if QA chain is ready
if st.session_state.qa_chain:

    # Input box for user question
    user_input = st.chat_input("Ask something about your PDF...")

    # If user enters a question
    if user_input:

        # Pass question to RAG pipeline
        result = st.session_state.qa_chain.invoke({
            "question": user_input
        })

        # Extract answer from result
        answer = result["answer"]

        # Extract source documents (used for answer)
        sources = result["source_documents"]

        # -----------------------------
        # 🔹 STORE CHAT HISTORY
        # -----------------------------

        # Save user message
        st.session_state.chat_history.append(("You", user_input))

        # Save bot response
        st.session_state.chat_history.append(("Bot", answer))

    # -----------------------------
    # 🔹 DISPLAY CHAT MESSAGES
    # -----------------------------

    for role, msg in st.session_state.chat_history:

        # Streamlit chat message UI
        with st.chat_message(role.lower()):
            st.write(msg)

    # -----------------------------
    # 🔹 DISPLAY SOURCES
    # -----------------------------

    if st.session_state.chat_history:

        st.subheader("📚 Sources (last answer)")

        # Show top 2 source chunks
        for doc in sources[:2]:

            # Metadata contains page number and source file
            st.write(
                f"- {doc.metadata.get('source', 'N/A')} | Page: {doc.metadata.get('page', 'N/A')}"
            )

