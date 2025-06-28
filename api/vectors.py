from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Use the enhanced investment vector database
embeddings = OllamaEmbeddings(model="mxbai-embed-large")
vector_db_location = os.path.join(script_dir, "enhanced_investment_vector_db")

# Check if enhanced vector database exists
if not os.path.exists(vector_db_location):
    print("⚠️  Enhanced investment vector database not found!")
    print("💡 Please run 'python update_vector_database.py' to create it.")
    raise FileNotFoundError(f"Enhanced vector database not found at {vector_db_location}")

# Load the enhanced investment vector database
vector_store = Chroma(
    collection_name="enhanced_investment_data",
    persist_directory=vector_db_location,
    embedding_function=embeddings
)

# Create retriever with more results for better context
retriver = vector_store.as_retriever(search_kwargs={"k": 10})

