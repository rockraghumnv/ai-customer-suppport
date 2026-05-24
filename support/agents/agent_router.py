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
    agent_scores = []

    intent_result = classify_intent(query)
    intent = intent_result["intent"]
    intent_confidence = intent_result["confidence"]

    responses = {}

    # 1. FAQ Agent
    faq_agent = FAQAgent(company)
    faq_response = faq_agent.handle_query(query, context=context)
    agent_scores.append(("FAQ", faq_response, get_confidence_score(faq_response)))
    responses["FAQ"] = faq_response

    # 2. Info Agent
    info_agent = InfoAgent(company)
    info_response = info_agent.handle_query(query, context=context)
    agent_scores.append(("Info", info_response, get_confidence_score(info_response)))
    responses["INFO"] = info_response

    # 3. Troubleshooting Agent
    troubleshooting_agent = TroubleshootingAgent(company)
    troubleshooting_response = troubleshooting_agent.handle_query(query, context=context)
    agent_scores.append(("Troubleshooting", troubleshooting_response, get_confidence_score(troubleshooting_response)))
    responses["TROUBLESHOOTING"] = troubleshooting_response

    # 4. General Purpose Agent
    general_agent = GeneralPurposeAgent(company)
    general_response = general_agent.handle_query(query, context=context)
    agent_scores.append(("General", general_response, get_confidence_score(general_response)))
    responses["GENERAL"] = general_response

    # Prefer classifier intent if confident and strong
    selected = responses.get(intent)
    if selected and not selected.get("fallback", False) and not is_weak_response(selected):
        if intent_confidence >= 0.6 and get_confidence_score(selected) >= 0.7:
            update_context(user_email, {"role": "agent", "content": selected["response"]})
            reset_failed_attempts(user_email)
            return selected["response"]

    # Otherwise pick the strongest agent response
    best_name = None
    best_resp = None
    best_score = 0.0
    for name, resp, score in agent_scores:
        if not resp or resp.get("fallback", False) or is_weak_response(resp):
            continue
        if score > best_score:
            best_name = name
            best_resp = resp
            best_score = score

    if best_resp and best_score >= 0.7:
        if not should_handoff_to_human(query, best_resp, best_score, failed_attempts(user_email)):
            update_context(user_email, {"role": "agent", "content": best_resp["response"]})
            reset_failed_attempts(user_email)
            return best_resp["response"]
        record_failed_attempt(user_email)
    else:
        record_failed_attempt(user_email)

    if should_handoff_to_human(query, best_resp, best_score, failed_attempts(user_email)):
        pass

    # 5. Fallback: Create a ticket
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
