import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# -----------------------------
# 🔹 PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="ChatPDF AI", page_icon="🤖", layout="wide")

# -----------------------------
# 🔹 CUSTOM CSS (ChatGPT Style)
# -----------------------------
st.markdown("""
    <style>
    .main {background-color: #0e1117;}
    .stChatMessage {border-radius: 10px; padding: 10px;}
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# 🔹 TITLE
# -----------------------------
st.title("🤖 Chat with your PDF")
st.caption("Upload a PDF and start chatting like ChatGPT 🚀")

# -----------------------------
# 🔹 SESSION STATE
# -----------------------------
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------
# 🔹 SIDEBAR
# -----------------------------
with st.sidebar:
    st.header("📂 Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

    if uploaded_file:
        with st.spinner("Processing PDF... ⏳"):

            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.read())

            loader = PyPDFLoader("temp.pdf")
            documents = loader.load()

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            docs = splitter.split_documents(documents)

            embeddings = OpenAIEmbeddings()
            vector_db = FAISS.from_documents(docs, embeddings)

            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )

            llm = ChatOpenAI(
                temperature=0,
                model="gpt-4o-mini"
            )

            st.session_state.qa_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=vector_db.as_retriever(),
                memory=memory,
                return_source_documents=True
            )

        st.success("✅ PDF ready!")

# -----------------------------
# 🔹 CHAT UI
# -----------------------------
if st.session_state.qa_chain:

    user_input = st.chat_input("Ask anything about your PDF...")

    if user_input:
        result = st.session_state.qa_chain.invoke({"question": user_input})

        answer = result["answer"]
        sources = result["source_documents"]

        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("assistant", answer))

    # Display chat messages
    for role, message in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(message)

    # Show sources
    if "sources" in locals():
        with st.expander("📚 Sources"):
            for doc in sources[:2]:
                st.write(
                    f"- {doc.metadata.get('source', 'N/A')} | Page: {doc.metadata.get('page', 'N/A')}"
                )

else:
    st.info("👈 Upload a PDF from the sidebar to start chatting")