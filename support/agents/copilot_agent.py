from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .chroma_utils import GoogleGenerativeAIEmbeddings
<<<<<<< HEAD
from chat.models import ChatMessage
=======
from support.models import ChatMessage
>>>>>>> cd67d2aec22586fc568a9a49933775b19793c4b4

class CopilotAgent:
    def __init__(self, ticket):
        self.ticket = ticket
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
        self.prompt = ChatPromptTemplate.from_template(
            """
            You are a support copilot. Summarize the following conversation between a customer and the AI support system. Then, suggest the next best actions for a human agent to resolve the issue. Be concise and actionable.

            Conversation:
            {conversation}
            """
        )
        self.chain = (self.prompt | self.llm | StrOutputParser())

    def summarize_and_suggest(self):
        messages = ChatMessage.objects.filter(ticket=self.ticket).order_by('created_at')
        conversation = "\n".join([
            f"{msg.sender.title()}: {msg.message or '[Image attached]'}" for msg in messages
        ])
        result = self.chain.invoke({"conversation": conversation})
        return result
