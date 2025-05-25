import os
from .faq_agent import FAQAgent
from .info_agent import InfoAgent
from .troubleshooting_agent import TroubleshootingAgent
from .general_purpose_agent import GeneralPurposeAgent
from support.models import Ticket

# In-memory context store for demo/testing
CHAT_CONTEXT = {}

def get_context(user_email):
    return CHAT_CONTEXT.get(user_email, [])

def update_context(user_email, message):
    if user_email not in CHAT_CONTEXT:
        CHAT_CONTEXT[user_email] = []
    CHAT_CONTEXT[user_email].append(message)
    if len(CHAT_CONTEXT[user_email]) > 10:
        CHAT_CONTEXT[user_email] = CHAT_CONTEXT[user_email][-10:]

def route_query_to_agent(query: str, company, user_email):
    context = get_context(user_email)
    update_context(user_email, {"role": "user", "content": query})

    # 1. FAQ Agent
    faq_agent = FAQAgent(company)
    faq_response = faq_agent.handle_query(query, context=context)
    if faq_response and not faq_response.get('fallback', False):
        update_context(user_email, {"role": "agent", "content": faq_response['response']})
        return faq_response['response']

    # 2. Info Agent
    info_agent = InfoAgent(company)
    info_response = info_agent.handle_query(query, context=context)
    if info_response and not info_response.get('fallback', False):
        update_context(user_email, {"role": "agent", "content": info_response['response']})
        return info_response['response']

    # 3. Troubleshooting Agent
    troubleshooting_agent = TroubleshootingAgent(company)
    troubleshooting_response = troubleshooting_agent.handle_query(query, context=context)
    if troubleshooting_response and not troubleshooting_response.get('fallback', False):
        update_context(user_email, {"role": "agent", "content": troubleshooting_response['response']})
        return troubleshooting_response['response']

    # 4. General Purpose Agent
    general_agent = GeneralPurposeAgent(company)
    general_response = general_agent.handle_query(query, context=context)
    if general_response and not general_response.get('fallback', False):
        update_context(user_email, {"role": "agent", "content": general_response['response']})
        return general_response['response']

    # 5. Fallback: Create a ticket
    ticket = Ticket.objects.create(
        company=company,
        user_email=user_email,
        subject=f"Support Request: {query[:100]}",
        description=query,
        assigned_to=None
    )
    print(f"Ticket created: {ticket.id} for {user_email} at {company.name}. Needs human agent attention.")
    return ticket

def route_query_to_agent(query, company, user_email):
    # Example: Try FAQ agent first
    answer, confidence = None, 0.0
    try:
        answer, confidence = faq_agent.get_answer(query, company)
    except Exception:
        pass
    if answer and confidence > 0.7:
        return answer
    # Try info agent
    try:
        answer, confidence = info_agent.get_answer(query, company)
    except Exception:
        pass
    if answer and confidence > 0.7:
        return answer
    # Try troubleshooting agent
    try:
        answer, confidence = troubleshooting_agent.get_answer(query, company)
    except Exception:
        pass
    if answer and confidence > 0.7:
        return answer
    # Try general purpose agent
    try:
        answer, confidence = general_purpose_agent.get_answer(query, company)
    except Exception:
        pass
    if answer and confidence > 0.7:
        return answer
    # Fallback: create ticket and explain
    explanation = "No confident answer found (confidence below threshold or no answer). Escalating to human agent."
    ticket = ticket_creation_agent.create_ticket(query, company, user_email, explanation)
    return ticket
