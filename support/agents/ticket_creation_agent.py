import os
from django.conf import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class TicketDetails(BaseModel):
    subject: str = Field(description="Concise summary of the user's issue.")
    description: str = Field(description="Detailed description of the user's problem.")

class TicketCreationAgent:
    def __init__(self, company):
        self.company = company
        self.llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", temperature=0)
        self.parser = PydanticOutputParser(pydantic_object=TicketDetails)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract the subject and description for a support ticket from the following user query.\n{format_instructions}"),
            ("human", "{query}")
        ]).partial(format_instructions=self.parser.get_format_instructions())
        self.chain = self.prompt | self.llm | self.parser

    def extract_ticket_details(self, query: str) -> TicketDetails:
        try:
            ticket_details = self.chain.invoke({"query": query})
            return ticket_details
        except Exception as e:
            print(f"Error during ticket details extraction: {e}")
            return TicketDetails(subject="Support Request", description=query)

ticket_creation_agent = TicketCreationAgent
