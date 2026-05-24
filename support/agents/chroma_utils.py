import io
import json
import os
from django.conf import settings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from PIL import Image
from docx import Document as DocxDocument

def _paragraph_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", " "],
    )

def _load_json_qa(file_path: str):
    with open(file_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    documents = []
    if isinstance(data, list):
        for idx, record in enumerate(data):
            question = str(record.get("question", "")).strip()
            answer = str(record.get("answer", "")).strip()
            content = f"Q: {question}\nA: {answer}".strip()
            if content:
                documents.append(
                    Document(
                        page_content=content,
                        metadata={"source": file_path, "item": idx},
                    )
                )
    return documents

def process_file_for_chroma(uploaded_file_instance):
    """Reads the uploaded file or image, processes its content, and stores it in ChromaDB."""
    file_path = uploaded_file_instance.file.path
    file_extension = os.path.splitext(file_path)[1].lower()
    company_id = uploaded_file_instance.company.id # Get company ID

    # Define a directory for ChromaDB specific to the company
    chroma_dir = os.path.join(settings.BASE_DIR, f'chroma_db_{company_id}')

    loader = None
    is_image = False
    is_json = False
    if file_extension == '.txt':
        loader = TextLoader(file_path)
    elif file_extension == '.pdf':
        loader = PyPDFLoader(file_path)
    elif file_extension == '.json':
        is_json = True
    elif file_extension in ['.docx']:
        # DOCX support
        doc = DocxDocument(file_path)
        full_text = '\n'.join([para.text for para in doc.paragraphs])
        # Simulate a loader for docx
        class DocxLoader:
            def load(self):
                return [Document(page_content=full_text, metadata={"source": file_path})]
        loader = DocxLoader()
    elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
        is_image = True
    # Add more file types as needed

    if is_json:
        documents = _load_json_qa(file_path)
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        db = Chroma.from_documents(documents, embeddings, persist_directory=chroma_dir)
        db.persist()
        print(f"Successfully processed and stored {file_path} in ChromaDB for company {company_id}")
    elif loader:
        documents = loader.load()
        text_splitter = _paragraph_splitter()
        texts = text_splitter.split_documents(documents)
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        db = Chroma.from_documents(texts, embeddings, persist_directory=chroma_dir)
        db.persist()
        print(f"Successfully processed and stored {file_path} in ChromaDB for company {company_id}")
    elif is_image:
        # Process image: get embedding using Gemini
        with open(file_path, 'rb') as img_file:
            img_bytes = img_file.read()
        image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        # Gemini expects bytes for image embedding
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        # The API expects a list of images, so wrap in a list
        image_embedding = embeddings.embed_image([img_bytes])[0]
        # Store as a Chroma document
        doc = {
            "page_content": f"Image file: {os.path.basename(file_path)}",
            "metadata": {"source": file_path, "type": "image"},
        }
        db = Chroma.from_documents([doc], embeddings, persist_directory=chroma_dir, embedding_function=lambda docs: [image_embedding for _ in docs])
        db.persist()
        print(f"Successfully processed and stored image {file_path} in ChromaDB for company {company_id}")
    else:
        print(f"Unsupported file type: {file_extension}")
        # Handle unsupported file types (e.g., raise an error, log a warning)
