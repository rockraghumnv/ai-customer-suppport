import os
from django.conf import settings
from langchain_community.document_loaders import TextLoader, PyPDFLoader, JSONLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from PIL import Image
import io
<<<<<<< HEAD
=======
from docx import Document
>>>>>>> cd67d2aec22586fc568a9a49933775b19793c4b4

def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["source"] = record.get("source")
    metadata["question"] = record.get("question")
    metadata["answer"] = record.get("answer")
    return metadata

def process_file_for_chroma(uploaded_file_instance):
    """Reads the uploaded file or image, processes its content, and stores it in ChromaDB."""
    file_path = uploaded_file_instance.file.path
    file_extension = os.path.splitext(file_path)[1].lower()
    company_id = uploaded_file_instance.company.id # Get company ID

    # Define a directory for ChromaDB specific to the company
    chroma_dir = os.path.join(settings.BASE_DIR, f'chroma_db_{company_id}')

    loader = None
    is_image = False
    if file_extension == '.txt':
        loader = TextLoader(file_path)
    elif file_extension == '.pdf':
        loader = PyPDFLoader(file_path)
    elif file_extension == '.json':
        loader = JSONLoader(file_path, jq_schema='.[]', content_key="answer", metadata_func=metadata_func)
<<<<<<< HEAD
=======
    elif file_extension in ['.docx']:
        # DOCX support
        doc = Document(file_path)
        full_text = '\n'.join([para.text for para in doc.paragraphs])
        # Simulate a loader for docx
        class DocxLoader:
            def load(self):
                return [{"page_content": full_text, "metadata": {"source": file_path}}]
        loader = DocxLoader()
>>>>>>> cd67d2aec22586fc568a9a49933775b19793c4b4
    elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
        is_image = True
    # Add more file types as needed

    if loader:
        documents = loader.load()

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)

        # Use Gemini for text embeddings
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
