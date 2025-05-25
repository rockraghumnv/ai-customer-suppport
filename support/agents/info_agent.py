from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from django.conf import settings
import os

class InfoAgent:
    def __init__(self, company):
        self.company = company
        self.chroma_dir = os.path.join(settings.BASE_DIR, f'chroma_db_{self.company.id}')
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
        self.vectorstore = Chroma(persist_directory=self.chroma_dir, embedding_function=self.llm.embeddings)
        self.retriever = self.vectorstore.as_retriever()
        self.prompt = ChatPromptTemplate.from_template("""You are an information agent. Use the following context to answer the user's question about company policies, services, or general info.\n{context}\n\nQuestion: {question}""")
        self.chain = ({"context": self.retriever, "question": lambda x: x["query"]} | self.prompt | self.llm | StrOutputParser())

    def handle_query(self, query, context=None):
        try:
            response = self.chain.invoke({"query": query})
            return {"response": response, "fallback": False}
        except Exception as e:
            print(f"InfoAgent error: {e}")
            return {"response": None, "fallback": True}
