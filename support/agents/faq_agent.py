import os
from django.conf import settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

class FAQAgent:
    def __init__(self, company):
        self.company = company
        self.chroma_dir = os.path.join(settings.BASE_DIR, f'chroma_db_{self.company.id}')
        self.embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = self._load_vectorstore()
        if self.vectorstore:
            self.retriever = self.vectorstore.as_retriever()
        else:
            self.retriever = None

        # Use Gemini LLM
        # Ensure GOOGLE_API_KEY environment variable is set
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
        self.chain = self._build_rag_chain()

    def _load_vectorstore(self):
        """Loads the company-specific ChromaDB vectorstore."""
        if not os.path.exists(self.chroma_dir):
            # Handle case where knowledge base doesn't exist for the company
            print(f"ChromaDB directory not found for company {self.company.id}")
            return None # Or raise an error
        return Chroma(persist_directory=self.chroma_dir, embedding_function=self.embeddings)

    def _build_rag_chain(self):
        """Builds the RAG chain for querying the knowledge base."""
        if not self.vectorstore:
            return None

        template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
        prompt = ChatPromptTemplate.from_template(template)

        # RAG chain
        chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        return chain

    def handle_query(self, query: str) -> str:
        """Handles the user query using the RAG chain."""
        if not self.chain:
            return "Sorry, the knowledge base is not available for this company."

        try:
            response = self.chain.invoke(query)
            return response
        except Exception as e:
            print(f"Error during RAG chain invocation: {e}")
            return "Sorry, I couldn't retrieve an answer from the knowledge base."
