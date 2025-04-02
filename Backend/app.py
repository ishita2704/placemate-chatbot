import os
import json
import time
import gspread
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from google.oauth2.service_account import Credentials
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True,
        "max_age": 86400
    }
})


# Load API keys
service_account_json = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
groq_api_key = os.getenv("GROQ_API_KEY")
os.environ['GOOGLE_API_KEY'] = os.getenv("GOOGLE_API_KEY")

# Google Sheets Authentication
SERVICE_ACCOUNT_FILE = "service_account_googlesheet.json"
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scope)
client = gspread.authorize(creds)

# Initialize LangChain Model
llm = ChatGroq(groq_api_key=groq_api_key, model_name="gemma2-9b-it")

# Store vectors in memory
vector_store = None

def load_google_sheet_data():
    """Fetch data from Google Sheets"""
    try:
        sheet = client.open("survey (Responses)").sheet1
        data = sheet.get_all_records()
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)
    except Exception as e:
        return {"error": f"Error loading Google Sheets: {e}"}

def vector_embedding():
    """Create vector embeddings for the Google Sheets data"""
    global vector_store
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        data_df = load_google_sheet_data()

        # Remove unnecessary columns
        excluded_columns = ["Timestamp", "Name", "Student Enrollment Number"]
        documents = [
            ". ".join(f"{col}: {val}" for col, val in row.items() if col not in excluded_columns)
            for _, row in data_df.iterrows()
        ]

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        final_documents = text_splitter.create_documents(documents)

        if not final_documents:
            return {"error": "No data found in Google Sheets!"}

        vector_store = FAISS.from_documents(final_documents, embeddings)
        return {"message": "Vector Store initialized successfully"}
    
    except Exception as e:
        return {"error": f"Failed to initialize embeddings: {e}"}

@app.route("/initialize-vectors", methods=["GET"])
def initialize_vectors():
    return jsonify(vector_embedding())

@app.route("/ask-question", methods=["OPTIONS"])
def options():
    response = jsonify({"message": "OK"})
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    return response, 200


@app.route("/ask-question", methods=["POST"])
def ask_question():
    """Answer the user's question based on the vector store"""
    global vector_store

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    if vector_store is None:
        return jsonify({"error": "Vector store is not initialized. Call /initialize-vectors first."}), 400

    data = request.get_json()
    question = data["query"]


    retriever = vector_store.as_retriever(search_kwargs={"k": 15})
    
    document_chain = create_stuff_documents_chain(
        llm, 
        ChatPromptTemplate.from_template("""
            Answer the questions based on the provided context if available.
            If no context is available, answer the question to the best of your knowledge.

            <context>
            {context}
            <context>
            Question: {input}
        """)
    )

    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    start = time.process_time()
    retrieved_docs = retriever.invoke(question)

    if retrieved_docs:
        response = retrieval_chain.invoke({'input': question})
        final_answer = response['answer']
    else:
        final_answer = llm.predict(question)

    return jsonify({"answer": final_answer})

if __name__ == "__main__":
    app.run(debug=True)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response