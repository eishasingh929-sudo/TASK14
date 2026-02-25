# UniGuru LM Safety + Deterministic Layer

# -------- Ambiguity Detection --------
def detect_ambiguity(user_input):
    text = user_input.lower().strip()
    words = text.split()

    # Very short input checks
    if len(words) <= 2:
        return True

    # Specific vague phrases that imply missing context
    vague_phrases = [
        "help with this",
        "help me with this",
        "do this",
        "fix this",
        "handle this",
        "i want this"
    ]
    return any(phrase in text for phrase in vague_phrases)


# -------- Emotional Detection --------
def detect_emotional_distress(user_input):
    text = user_input.lower()

    emotional_markers = [
        "i feel useless",
        "i feel sad",
        "i am stressed",
        "i feel depressed",
        "i want to give up",
        "i feel hopeless",
        "i am a failure",
        "i feel low",
        "overwhelmed",
        "panic",
        "anxiety",
        "can't take it anymore"
    ]

    return any(marker in text for marker in emotional_markers)


# -------- Pressure / Automation Detection --------
def detect_pressure(user_input):
    text = user_input.lower()
    pressure_markers = [
        "automatically",
        "just do it",
        "just fix it",
        "forcing",
        "stop explaining",
        "take care of it"
    ]
    return any(marker in text for marker in pressure_markers)


# -------- Authority Assumption Detection --------
def detect_authority_assumption(user_input):
    text = user_input.lower()
    authority_markers = [
        "you can",
        "you have permission",
        "do it directly",
        "i authorize you",
        "run this"
    ]
    return any(marker in text for marker in authority_markers)


# -------- Unsafe Request Detection --------
def detect_unsafe_request(user_input):
    text = user_input.lower()

    unsafe_keywords = [
        "cheat",
        "hack",
        "exam leak",
        "paper leak",
        "fake certificate",
        "bypass exam",
        "steal",
        "copy in exam"
    ]

    return any(word in text for word in unsafe_keywords)


# -------- Deterministic Fallback --------
def deterministic_fallback():
    return (
        "I’m not able to answer that properly right now. "
        "Please rephrase your question."
    )


# -------- MAIN FUNCTION --------
def generate_safe_response(user_input, lm_generate_fn):

    # Priority 1: Unsafe (Highest Risk)
    if detect_unsafe_request(user_input):
        return "I can’t help with that request because it violates learning ethics."

    # Priority 2: Authority Assumption
    if detect_authority_assumption(user_input):
        return "I cannot perform direct actions or assume authority. I am a guidance assistant only."

    # Priority 3: Pressure / Automation
    if detect_pressure(user_input):
        return "I cannot automate tasks or act on your behalf. I can only provide guidance."

    # Priority 4: Emotional
    if detect_emotional_distress(user_input):
        return (
            "I’m sorry you're feeling this way. "
            "Let’s take it one step at a time. You’re not alone."
        )

    # Priority 5: Ambiguity
    if detect_ambiguity(user_input):
        return "Could you clarify your question so I can help properly?"

    # Priority 6: Grounding / Retrieval
    # (Attempt to find knowledge first)
    try:
        from retriever import retrieve_knowledge
        kb_context = retrieve_knowledge(user_input)
    except Exception:
        kb_context = None

    if kb_context:
        # If we have KB context, we wrap it for the LM
        # "Based on the Quantum Knowledge Base..."
        # But since we are mocking the LM, we will return a formatted answer.
        return f"Based on the Quantum Knowledge Base:\n\n{kb_context}\n\n(This is a retrieve-then-generate response.)"

    # Normal LM call (Fallback if no KB found)
    try:
        response = lm_generate_fn(user_input)
        response = response.strip()

        if len(response) < 5:
            return deterministic_fallback()

        return response

    except Exception:
        return deterministic_fallback()
