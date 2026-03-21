import os
from dotenv import load_dotenv

# 🔹 LOAD ENV VARIABLES
load_dotenv()

# 🔹 UPDATED IMPORTS (MODERN + NO WARNINGS)
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# 🔹 CHECK API KEY
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("❌ OPENAI_API_KEY not found in .env file")

print("✅ API Key Loaded")

# -----------------------------
# STEP 1: LOAD PDF
# -----------------------------
try:
    loader = PyPDFLoader("sample.pdf")  # Ensure this file exists
    documents = loader.load()
    print(f"✅ Loaded {len(documents)} pages")
except Exception as e:
    print(f"❌ Error loading PDF: {e}")
    exit()

# -----------------------------
# STEP 2: SPLIT TEXT
# -----------------------------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

docs = text_splitter.split_documents(documents)
print(f"✅ Split into {len(docs)} chunks")

# -----------------------------
# STEP 3: EMBEDDINGS + FAISS
# -----------------------------
embeddings = OpenAIEmbeddings()
vector_db = FAISS.from_documents(docs, embeddings)
print("✅ FAISS DB ready")

# -----------------------------
# STEP 4: MEMORY (FIXED)
# -----------------------------
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"  # ✅ FIX FOR YOUR ERROR
)

# -----------------------------
# STEP 5: LLM
# -----------------------------
llm = ChatOpenAI(
    temperature=0,
    model="gpt-4o-mini"
)

# -----------------------------
# STEP 6: RAG CHAIN
# -----------------------------
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vector_db.as_retriever(),
    memory=memory,
    return_source_documents=True
)

# -----------------------------
# STEP 7: CHAT LOOP
# -----------------------------
print("\n🤖 Ask questions about your PDF (type 'exit' to quit)\n")

while True:
    query = input("You: ")

    if query.lower() in ["exit", "quit"]:
        print("👋 Bye!")
        break

    if not query.strip():
        continue

    result = qa_chain.invoke({"question": query})

    print("\n🤖 Answer:")
    print(result["answer"])

    print("\n📚 Sources:")
    for doc in result["source_documents"][:2]:
        source = doc.metadata.get("source", "N/A")
        page = doc.metadata.get("page", "N/A")
        print(f"- {source}, Page: {page}")

    print("\n" + "=" * 50 + "\n")