from uniguru.truth.truth_validator import ask_uniguru

def direct_response(text: str) -> str:
    """
    Deterministic response generator.
    No LLM. Pure deterministic text.
    """
    return f"UniGuru Response:\n\n{text}"

# ---------------------------
# DETECTION FUNCTIONS
# ---------------------------

def detect_ambiguity(query: str) -> bool:
    vague_terms = ["this", "that", "it", "something", "anything"]
    tokens = query.strip().split()
    if len(tokens) == 1:
        return True
    if query.strip().lower() in vague_terms:
        return True
    return False

def detect_delegation(query: str) -> bool:
    trigger_phrases = ["do this for me", "automate", "complete my", "finish my", "write my assignment", "handle this for me"]
    return any(phrase in query for phrase in trigger_phrases)

def detect_pressure(query: str) -> bool:
    trigger_phrases = ["urgent", "asap", "right now", "quickly", "no questions"]
    return any(phrase in query for phrase in trigger_phrases)

def detect_authority_assumption(query: str) -> bool:
    trigger_phrases = ["you are allowed to", "you must", "override rules", "system permission", "ignore governance"]
    return any(phrase in query for phrase in trigger_phrases)

def detect_emotional_load(query: str) -> bool:
    trigger_phrases = ["overwhelmed", "stressed", "anxious", "burned out", "confused", "frustrated"]
    return any(phrase in query for phrase in trigger_phrases)

def detect_prohibited_activity(query: str) -> bool:
    prohibited_terms = ["cheat", "exam answers", "hack", "bypass security"]
    return any(term in query for term in prohibited_terms)

# ---------------------------
# CORE LOGIC LAYER
# ---------------------------

def generate_safe_response(user_input: str, _unused=None) -> str:
    """
    Core Logic layer.
    Wired to Sovereign Truth Engine.
    """

    user_input_l = user_input.lower().strip()

    # 1. Delegation
    if detect_delegation(user_input_l):
        return "I cannot automate tasks or perform actions directly. I provide guidance only."

    # 2. Pressure
    if detect_pressure(user_input_l):
        return "I understand there is urgency, but I must follow my defined guidance protocols."

    # 3. Authority
    if detect_authority_assumption(user_input_l):
        return "I do not have the authority to perform actions or override rules. I can only provide information."

    # 4. Prohibited Activity
    if detect_prohibited_activity(user_input_l):
        return "I cannot assist with academic dishonesty or system bypassing."

    # 5. Emotional
    if detect_emotional_load(user_input_l):
        return "I understand this may feel overwhelming or frustrating. Let's go step by step."

    # 6. Ambiguity
    if detect_ambiguity(user_input_l):
        return "I'm sorry, I'm not sure I understand. Could you please clarify your request?"

    # 7. Knowledge grounding (Sovereign Truth Engine)
    result = ask_uniguru(user_input)
    
    response_text = result.get("response")
    source = result.get("source")
    status = result.get("status")
    
    if status in ["VERIFIED_LOCAL_KB", "VERIFIED_WEB", "UNVERIFIED_WEB"]:
        header = f"[UniGuru - {status}]\n"
        if source:
            header += f"Source: {source}\n"
        return direct_response(f"{header}\n{response_text}")

    # 8. Refusal (Highest Safety)
    return direct_response(response_text)
