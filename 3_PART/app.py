# OS module used for operating system related work
import os
# Streamlit is used to create web UI using Python
import streamlit as st
# Load environment variables from .env file
from dotenv import load_dotenv
# This loads OPENAI_API_KEY from .env file
load_dotenv()
# =========================================================
# LANGCHAIN IMPORTS
# =========================================================
# Used to load PDF documents
from langchain_community.document_loaders import PyPDFLoader
# Used to split large text into smaller chunks
from langchain_text_splitters import RecursiveCharacterTextSplitter
# OpenAI Embedding model converts text into vectors
from langchain_openai import OpenAIEmbeddings
# ChatOpenAI is used to communicate with GPT model
from langchain_openai import ChatOpenAI
# FAISS is a vector database used for similarity search
from langchain_community.vectorstores import FAISS
# Stores conversation history
from langchain.memory import ConversationBufferMemory
# Main RAG conversational chain
from langchain.chains import ConversationalRetrievalChain
# =========================================================
# PAGE CONFIGURATION
# =========================================================
# Set webpage title and layout
st.set_page_config(
    page_title="Chat with PDF",
    layout="wide"
)
# Main heading on webpage
st.title("📄🤖 Chat with your PDF")
# =========================================================
# SESSION STATE
# =========================================================
# Session state stores variables during app runtime
# Store QA chain object
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
# Store complete chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
# =========================================================
# FILE UPLOAD SECTION
# =========================================================
# Upload PDF file
uploaded_file = st.file_uploader(
    "Upload your PDF",
    type="pdf"
)
# Check whether user uploaded file
if uploaded_file is not None:
    # =====================================================
    # SAVE PDF TEMPORARILY
    # =====================================================
    # Save uploaded PDF locally
    with open("temp.pdf", "wb") as f:

        # Read uploaded file and write into temp.pdf
        f.write(uploaded_file.read())
    # =====================================================
    # LOAD PDF DOCUMENT
    # =====================================================
    # Create PDF loader object
    loader = PyPDFLoader("temp.pdf")
    # Extract all PDF text
    documents = loader.load()
    # =====================================================
    # TEXT SPLITTING
    # =====================================================
    # Split large text into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        # Maximum chunk size
        chunk_size=1000,

        # Overlap helps maintain context
        chunk_overlap=200
    )
    # Create smaller document chunks
    docs = text_splitter.split_documents(documents)

    # =====================================================
    # CREATE EMBEDDINGS
    # =====================================================
    # OpenAI embedding model
    embeddings = OpenAIEmbeddings()
    # =====================================================
    # STORE IN VECTOR DATABASE
    # =====================================================
    # Convert chunks into vectors and store in FAISS
    vector_db = FAISS.from_documents(
        docs,
        embeddings
    )
    # =====================================================
    # MEMORY
    # =====================================================
    # Conversation memory stores previous chats
    memory = ConversationBufferMemory(
        # Memory variable name
        memory_key="chat_history",
        # Return message format
        return_messages=True,
        # Output key from chain
        output_key="answer"
    )
    # =====================================================
    # LOAD LLM
    # =====================================================
    # GPT model configuration
    llm = ChatOpenAI(

        # Lower temperature = more accurate answers
        temperature=0,

        # OpenAI model
        model="gpt-4o-mini"
    )
    # =====================================================
    # CREATE CONVERSATIONAL RAG CHAIN
    # =====================================================
    # Main AI pipeline
    st.session_state.qa_chain = (
        ConversationalRetrievalChain.from_llm(
            # LLM model
            llm=llm,
            # Vector retriever
            retriever=vector_db.as_retriever(),
            # Conversation memory
            memory=memory,
            # Return source chunks
            return_source_documents=True
        )
    )

    # Success message
    st.success(
        "✅ PDF processed! You can now ask questions."
    )
# =========================================================
# CHAT SECTION
# =========================================================
# Check whether chain exists
if st.session_state.qa_chain:
    # Chat input box
    user_input = st.chat_input(
        "Ask something about your PDF..."
    )
    # When user enters question
    if user_input:
        # Send question to RAG chain
        result = st.session_state.qa_chain.invoke({

            # User question
            "question": user_input
        })
        # Extract answer
        answer = result["answer"]
        # Extract source documents
        sources = result["source_documents"]
        # =================================================
        # SAVE CHAT HISTORY
        # =================================================
        st.session_state.chat_history.append(
            ("You", user_input)
        )

        st.session_state.chat_history.append(
            ("Bot", answer)
        )
    # =====================================================
    # DISPLAY CHAT HISTORY
    # =====================================================
    for role, msg in st.session_state.chat_history:
        # Create chat message UI
        with st.chat_message(role.lower()):

            # Display message
            st.write(msg)
    # =====================================================
    # SHOW SOURCES
    # =====================================================
    if st.session_state.chat_history:

        st.subheader("📚 Sources (last answer)")

        # Display top 2 matching chunks
        for doc in sources[:2]:

            st.write(
                f"- {doc.metadata.get('source', 'N/A')} "
                f"| Page: {doc.metadata.get('page', 'N/A')}"
            )
