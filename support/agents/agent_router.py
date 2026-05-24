import json
from langchain_google_genai import ChatGoogleGenerativeAI
from .faq_agent import FAQAgent
from .info_agent import InfoAgent
from .troubleshooting_agent import TroubleshootingAgent
from .general_purpose_agent import GeneralPurposeAgent
from tickets.models import Ticket

# In-memory context store for demo/testing
CHAT_CONTEXT = {}
FAILED_ATTEMPTS = {}

INTENTS = ["FAQ", "INFO", "TROUBLESHOOTING", "GENERAL"]

def get_context(user_email):
    return CHAT_CONTEXT.get(user_email, [])

def update_context(user_email, message):
    if user_email not in CHAT_CONTEXT:
        CHAT_CONTEXT[user_email] = []
    CHAT_CONTEXT[user_email].append(message)
    if len(CHAT_CONTEXT[user_email]) > 10:
        CHAT_CONTEXT[user_email] = CHAT_CONTEXT[user_email][-10:]
def record_failed_attempt(user_email):
    FAILED_ATTEMPTS[user_email] = FAILED_ATTEMPTS.get(user_email, 0) + 1

def reset_failed_attempts(user_email):
    FAILED_ATTEMPTS[user_email] = 0

def failed_attempts(user_email):
    return FAILED_ATTEMPTS.get(user_email, 0)
def get_confidence_score(response):
    # Placeholder: In production, use LLM logprobs or RAG similarity scores
    # Here, we use a simple heuristic: longer, more specific answers are more confident
    if isinstance(response, str):
        text = response
    elif isinstance(response, dict) and response.get('response'):
        text = response['response']
    else:
        return 0.0
    if len(text) > 100:
        return 0.9
    elif len(text) > 30:
        return 0.7
    elif len(text) > 10:
        return 0.5
    return 0.2

def is_weak_response(response):
    if not response or not isinstance(response, dict):
        return True
    text = response.get("response")
    if not text or len(text.strip()) < 20:
        return True
    lowered = text.lower()
    if "sorry" in lowered or "couldn't" in lowered or "could not" in lowered:
        return True
    return False

def user_says_not_helpful(query: str) -> bool:
    lowered = (query or "").lower()
    triggers = [
        "not helpful",
        "not useful",
        "doesn't help",
        "does not help",
        "didn't help",
        "did not help",
        "not solved",
        "still not working",
        "still broken",
    ]
    return any(trigger in lowered for trigger in triggers)

def should_handoff_to_human(query, response, confidence, attempts):
    if user_says_not_helpful(query):
        return True
    if response is None:
        return True
    if confidence < 0.5:
        return True
    if is_weak_response(response):
        return True
    if attempts >= 2:
        return True
    return False

def classify_intent(query: str) -> dict:
    llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", temperature=0)
    prompt = (
        "Classify the user query into one of the following intents: FAQ, INFO, TROUBLESHOOTING, GENERAL. "
        "Return JSON only with keys intent and confidence (0 to 1).\n\n"
        f"Query: {query}"
    )
    try:
        result = llm.invoke(prompt)
        content = getattr(result, "content", str(result))
        data = json.loads(content)
        intent = str(data.get("intent", "GENERAL")).upper()
        confidence = float(data.get("confidence", 0.0))
        if intent not in INTENTS:
            intent = "GENERAL"
            confidence = 0.0
        return {"intent": intent, "confidence": max(0.0, min(confidence, 1.0))}
    except Exception:
        return {"intent": "GENERAL", "confidence": 0.0}

def route_query_to_agent(query: str, company, user_email):
    context = get_context(user_email)
    update_context(user_email, {"role": "user", "content": query})
    intent_result = classify_intent(query)
    intent = intent_result["intent"]
    intent_confidence = intent_result["confidence"]
    agent_scores = []

    # Immediate human fallback if user explicitly says prior answer was not helpful
    if user_says_not_helpful(query):
        record_failed_attempt(user_email)
        return _create_human_fallback_ticket(query, company, user_email, agent_scores)

    # If intent classifier itself is not confident, handoff to human
    if intent_confidence < 0.6:
        record_failed_attempt(user_email)
        return _create_human_fallback_ticket(query, company, user_email, agent_scores)

    # Route only to the selected intent agent (do not call all agents)
    if intent == "FAQ":
        selected_agent_name = "FAQ"
        selected_agent = FAQAgent(company)
    elif intent == "INFO":
        selected_agent_name = "INFO"
        selected_agent = InfoAgent(company)
    elif intent == "TROUBLESHOOTING":
        selected_agent_name = "TROUBLESHOOTING"
        selected_agent = TroubleshootingAgent(company)
    else:
        selected_agent_name = "GENERAL"
        selected_agent = GeneralPurposeAgent(company)

    selected_response = selected_agent.handle_query(query, context=context)
    selected_score = get_confidence_score(selected_response)
    agent_scores.append((selected_agent_name, selected_response, selected_score))

    if (
        selected_response
        and not selected_response.get("fallback", False)
        and not should_handoff_to_human(
            query,
            selected_response,
            selected_score,
            failed_attempts(user_email),
        )
    ):
        update_context(user_email, {"role": "agent", "content": selected_response["response"]})
        reset_failed_attempts(user_email)
        return selected_response["response"]

    record_failed_attempt(user_email)
    return _create_human_fallback_ticket(query, company, user_email, agent_scores)


def _create_human_fallback_ticket(query: str, company, user_email: str, agent_scores):
    # Fallback: Create a ticket for human agent
    ticket = Ticket.objects.create(
        company=company,
        user_email=user_email,
        subject=f"Support Request: {query[:100]}",
        description=query,
        assigned_to=None
    )
    print(f"Ticket created: {ticket.id} for {user_email} at {company.name}. Needs human agent attention.")

    # Log agent scores for performance monitoring
    from support.models import AgentPerformanceLog
    for agent_name, resp, score in agent_scores:
        AgentPerformanceLog.objects.create(
            ticket=ticket,
            agent_name=agent_name,
            confidence_score=score,
            fallback=resp.get('fallback', True) if resp else True
        )
    return ticket
