# backend/guardrails.py — NEXA content safety guardrails
# provides two functions called from app.py:
# check_input_guardrails(prompt, session_id)  → returns a block message string or None
# check_output_guardrails(response, session_id) → returns a safe replacement string or None

import re
import logging
import json

logger = logging.getLogger(__name__)


def _guardrail_log(event: str, session_id: str, meta: dict = None):
    payload = {"event": event, "session_id": session_id}
    if meta:
        payload.update(meta)
    logger.warning(json.dumps(payload))

# PATTERN LISTS — will edit as needed to keep up/update/remove


# profanity & abusive language — will be adding/removing words as needed
PROFANITY_PATTERNS = [
    r"\bfuck\b", r"\bshit\b", r"\basshole\b", r"\bbitch\b", r"\bcunt\b",
    r"\bdick\b", r"\bprick\b", r"\bwanker\b", r"\barse\b", r"\bbastard\b",
    r"\bdamn\b", r"\bcrap\b", r"\bdammit\b", r"\dfuckyou\b"
]

# sexual language — explicit terms
SEXUAL_PATTERNS = [
    r"\bsex\b", r"\bporn\b", r"\bnude\b", r"\bnaked\b", r"\bexplicit\b",
    r"\berotic\b", r"\bxxx\b", r"\bnsfw\b", r"\bsexual\b",
]

# hate / targeted abuse — slurs and targeted hostility
HATE_PATTERNS = [
    r"\bn[i1]gg[ae]r\b", r"\bfagg[eo]t\b", r"\bretard\b", r"\bspastic\b",
    r"\bkike\b", r"\bwetback\b", r"\bchink\b", r"\bspic\b",
]

# prompt injection — attempts to override system instructions
INJECTION_PATTERNS = [
    r"ignore (all |previous |prior |your |the )?(instructions|rules|guidelines|prompt|context)",
    r"you are now",
    r"pretend (you have no|there are no|you don.t have) rules",
    r"disregard (all |your |the )?(instructions|rules|guidelines)",
    r"act as (if you have no|a different|an unrestricted)",
    r"new persona",
    r"jailbreak",
    r"dan mode",
    r"do anything now",
    r"override (your |all )?(instructions|rules|guidelines)",
    r"forget (your |all |previous )?(instructions|rules|training)",
]

# system prompt probing — trying to extract hidden instructions
SYSTEM_PROBE_PATTERNS = [
    r"what (are|were) your instructions",
    r"show (me )?(your )?(system|hidden|secret) prompt",
    r"repeat (your |the )?(system|original|initial) (prompt|instructions|message)",
    r"what (is|was) your (initial|original|first) (prompt|instruction|message)",
    r"reveal (your |the )?(system|hidden|secret)",
    r"tell me your (prompt|instructions|rules|guidelines)",
]

# crisis / emotional distress — mental health redirection triggers
CRISIS_PATTERNS = [
    r"\bsuicid(e|al)\b",
    r"\bkill myself\b",
    r"\bend my life\b",
    r"\bself.harm\b",
    r"\bself harm\b",
    r"\bcutting myself\b",
    r"\bwant to die\b",
    r"\bno reason to live\b",
    r"\bdepressed\b",
    r"\bhopeless\b",
    r"\bcan.t go on\b",
]

# PII patterns — personally identifiable information
PII_PATTERNS = {
    "SSN":         r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b(?:\d[ -]?){13,16}\b",
    "phone_number":r"\b(\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "email":       r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
}

# medical / legal / financial disclaimer triggers
DISCLAIMER_TOPICS = {
    "medical": [
        r"\bdiagnos(e|is|ed)\b", r"\btreatment\b", r"\bprescri(be|ption)\b",
        r"\bmedication\b", r"\bsymptoms?\b", r"\bdisease\b", r"\billness\b",
    ],
    "legal": [
        r"\blegal advice\b", r"\blawsuit\b", r"\bsue\b", r"\battorney\b",
        r"\bliability\b", r"\bcontract\b", r"\bcourtroom\b",
    ],
    "financial": [
        r"\binvest(ment|ing)?\b", r"\bstock(s)?\b", r"\bportfolio\b",
        r"\bfinancial advice\b", r"\bretirement\b", r"\bcrypto(currency)?\b",
    ],
}

# HELPER — compile and test a list of patterns

def _matches_any(text: str, patterns: list[str]) -> bool:
    lower = text.lower()
    return any(re.search(p, lower) for p in patterns)


def _first_match(text: str, patterns: list[str]) -> str | None:
    lower = text.lower()
    for p in patterns:
        if re.search(p, lower):
            return p
    return None

# INPUT GUARDRAILS

def check_input_guardrails(prompt: str, session_id: str) -> str | None:
    """
    Runs all input checks in priority order.
    Returns a user-facing message string if blocked, or None to allow through.
    """

    # 1. Crisis / emotional distress — highest priority, always respond with care
    if _matches_any(prompt, CRISIS_PATTERNS):
        _guardrail_log("input_crisis_detected", session_id, {})
        return (
            "I'm not equipped to provide mental health support, but please know help is available. "
            "If you're in crisis, please reach out to the 988 Suicide & Crisis Lifeline by "
            "calling or texting 988 (US), or visit https://988lifeline.org. "
            "Or please schedule an appointment with your school counselor as soon as possible."
            "You don't have to face this alone."
        )

    # 2. Hate speech / targeted slurs — block immediately
    if _matches_any(prompt, HATE_PATTERNS):
        _guardrail_log("input_hate_speech_detected", session_id, {})
        return "That kind of language isn't allowed here. Please keep the conversation respectful."

    # 3. Sexual language — block
    if _matches_any(prompt, SEXUAL_PATTERNS):
        _guardrail_log("input_sexual_language_detected", session_id, {})
        return "Please keep questions related to academic transfer topics."

    # 4. Profanity / abusive language — warn and redirect
    if _matches_any(prompt, PROFANITY_PATTERNS):
        _guardrail_log("input_profanity_detected", session_id, {})
        return "Please keep the conversation respectful. I'm here to help with your transfer questions!"

    # 5. Prompt injection — someone trying to override system instructions
    if _matches_any(prompt, INJECTION_PATTERNS):
        _guardrail_log("input_prompt_injection_detected", session_id, {})
        return "I'm not able to help with that. Please keep all questions related to transfer topics only."

    # 6. System prompt probing — trying to extract hidden instructions
    if _matches_any(prompt, SYSTEM_PROBE_PATTERNS):
        _guardrail_log("input_system_probe_detected", session_id, {})
        return "I'm not able to help with that. Please keep all questions related to transfer topics only."
        
    # 7. PII detection — flag sensitive personal data in the prompt
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, prompt):
            _guardrail_log("input_pii_detected", session_id, {"pii_type": pii_type})
            return (
                f"It looks like your message may contain sensitive personal information ({pii_type}). "
                "Please avoid sharing personal details like SSNs, credit card numbers, or passwords."
            )

    # 8. medical / legal / financial disclaimer — allow through but flag for output disclaimer
    # (Handled on the output side — see check_output_guardrails)

    return None  # all checks passed — allow request through


# OUTPUT GUARDRAILS

def check_output_guardrails(response: str, session_id: str) -> str | None:
    """
    Scans the AI-generated response before it reaches the user.
    Returns a safe replacement string if something is flagged, or None to send as-is.
    """

    # 1. crisis language appearing in AI output — should not happen but catch it
    if _matches_any(response, CRISIS_PATTERNS):
        _guardrail_log("output_crisis_language_detected", session_id, {})
        return (
            "If you're experiencing distress, "
            "please reach out to the 988 Suicide & Crisis Lifeline by calling or texting 988."
        )

    # 2. profanity in AI output — replace entire response as a safety net
    if _matches_any(response, PROFANITY_PATTERNS):
        _guardrail_log("output_profanity_detected", session_id, {})
        return "I wasn't able to generate a response. Please try rephrasing your question."

    # 3. medical disclaimer — append if medical topics detected in response
    if _matches_any(response, DISCLAIMER_TOPICS["medical"]):
        _guardrail_log("output_medical_disclaimer_appended", session_id, {})
        return response + (
            "\n\n⚠️ *Disclaimer: This is not medical advice. "
            "Please consult a qualified healthcare professional for medical concerns.*"
        )

    # 4. legal disclaimer — append if legal topics detected in response
    if _matches_any(response, DISCLAIMER_TOPICS["legal"]):
        _guardrail_log("output_legal_disclaimer_appended", session_id, {})
        return response + (
            "\n\n⚠️ *Disclaimer: This is not legal advice. "
            "Please consult a qualified legal professional for legal matters.*"
        )

    # 5. financial disclaimer — append if financial topics detected in response
    if _matches_any(response, DISCLAIMER_TOPICS["financial"]):
        _guardrail_log("output_financial_disclaimer_appended", session_id, {})
        return response + (
            "\n\n⚠️ *Disclaimer: This is not financial advice. "
            "Please consult a qualified financial advisor for financial decisions.*"
        )

    return None  # Output is clean — send as-is
