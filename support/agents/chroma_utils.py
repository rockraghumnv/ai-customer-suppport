import os
from django.conf import settings
from langchain_community.document_loaders import TextLoader, PyPDFLoader, JSONLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["source"] = record.get("source")
    metadata["question"] = record.get("question")
    metadata["answer"] = record.get("answer")
    return metadata

def process_file_for_chroma(uploaded_file_instance):
    """Reads the uploaded file, processes its content, and stores it in ChromaDB."""
    file_path = uploaded_file_instance.file.path
    file_extension = os.path.splitext(file_path)[1].lower()
    company_id = uploaded_file_instance.company.id # Get company ID

    # Define a directory for ChromaDB specific to the company
    chroma_dir = os.path.join(settings.BASE_DIR, f'chroma_db_{company_id}')

    # Load the document based on file type
    loader = None
    if file_extension == '.txt':
        loader = TextLoader(file_path)
    elif file_extension == '.pdf':
        loader = PyPDFLoader(file_path)
    elif file_extension == '.json':
        # Assuming JSON is for FAQs in a specific format
        loader = JSONLoader(file_path, jq_schema='.[]', content_key="answer", metadata_func=metadata_func)
    # Add more file types as needed

    if loader:
        documents = loader.load()

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)

        # Create embeddings and store in ChromaDB
        # Using a common embedding model. You might choose a different one.
        embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

        # Initialize ChromaDB with the company-specific directory
        db = Chroma.from_documents(texts, embeddings, persist_directory=chroma_dir)
        db.persist()
        print(f"Successfully processed and stored {file_path} in ChromaDB for company {company_id}")
    else:
        print(f"Unsupported file type: {file_extension}")
        # Handle unsupported file types (e.g., raise an error, log a warning)
