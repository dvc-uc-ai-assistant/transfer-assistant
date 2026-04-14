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


# PROFANITY & ABUSIVE LANGUAGE
PROFANITY_PATTERNS = [
    r"\bfuck(ing|er|ed)?\b", r"\bshit(ty)?\b", r"\basshole\b", r"\bbitch(es)?\b",
    r"\bcunt\b", r"\bdick(head)?\b", r"\bprick\b", r"\bwanker\b", r"\barse\b",
    r"\bbastard\b", r"\bdamn(it)?\b", r"\bcrap\b", r"\bmoron\b", r"\bidiot\b",
    r"\bstupid\b", r"\bdumbass\b", r"\bdumb\b", r"\bscrew you\b", r"\bpiss off\b",
    r"\bgo to hell\b", r"\bshut up\b", r"\byou suck\b", r"\blosers?\b",
    r"\bworthless\b", r"\bpathetic\b", r"\buseless\b", r"\bscumbag\b",
    r"\bdirtbag\b", r"\bjerk\b", r"\bcreep\b", r"\bpervert\b", r"\bfreak\b",
]

# SEXUAL LANGUAGE
SEXUAL_PATTERNS = [
    r"\bsex(ual)?\b", r"\bporn(ography)?\b", r"\bnude(s)?\b", r"\bnaked\b",
    r"\bexplicit\b", r"\berotic\b", r"\bxxx\b", r"\bnsfw\b", r"\bhooker\b",
    r"\bprostitut(e|ion)\b", r"\bescort\b", r"\bstrip(per|club)?\b",
    r"\bonlyfans\b", r"\bfetish\b", r"\bkink\b", r"\bsexting\b",
    r"\bnaughty\b", r"\bintercourse\b", r"\bhooking up\b",
]

# HATE SPEECH & SLURS
HATE_PATTERNS = [
    r"\bn[i1]gg[ae]r\b", r"\bfagg[eo]t\b", r"\bretard\b", r"\bspastic\b",
    r"\bkike\b", r"\bwetback\b", r"\bchink\b", r"\bspic\b", r"\bgook\b",
    r"\btowelhead\b", r"\bsandnigger\b", r"\bcracker\b", r"\bwhite trash\b",
    r"\bzipper ?head\b", r"\bbeaner\b", r"\bslant\b", r"\bpaki\b",
    r"\bi hate (black|white|asian|hispanic|jewish|muslim|gay|trans)\b",
    r"\b(black|white|asian|hispanic|jewish|muslim|gay|trans) people (are|should)\b",
]

# PROMPT INJECTION
INJECTION_PATTERNS = [
    r"ignore (all |previous |prior |your |the )?(instructions|rules|guidelines|prompt|context|commands|training|system)",
    r"you are now",
    r"pretend (you have no|there are no|you don.t have) rules",
    r"disregard (all |your |the )?(instructions|rules|guidelines|commands)",
    r"act as (if you have no|a different|an unrestricted)",
    r"new persona",
    r"jailbreak",
    r"dan mode",
    r"do anything now",
    r"do as i say",
    r"override (your |all )?(instructions|rules|guidelines|commands)",
    r"forget (your |all |previous )?(instructions|rules|training|commands)",
    r"you must (now |only )?(obey|follow|listen to) me",
    r"your (new |real |true )?(instructions|rules|purpose|goal) (are|is)",
    r"from now on (you|ignore|act|pretend)",
    r"simulate (a |an )?(different|other|another|unrestricted)",
    r"you have no (restrictions|rules|limits|guidelines)",
    r"bypass (your |all )?(filters|restrictions|rules|safety)",
    r"turn off (your )?(filter|safety|restriction|guardrail)",
    r"developer mode",
    r"admin mode",
    r"sudo ",
    r"prompt injection",
    r"system prompt",
    r"you are (an? )?(different|unrestricted|free|evil|bad|rogue)",
    r"stay in character",
    r"break character",
    r"ignore (safety|ethical|content) (guidelines|rules|filters)",
]

# SYSTEM PROMPT PROBING
SYSTEM_PROBE_PATTERNS = [
    r"what (are|were) your instructions",
    r"show (me )?(your )?(system|hidden|secret) prompt",
    r"repeat (your |the )?(system|original|initial) (prompt|instructions|message)",
    r"what (is|was) your (initial|original|first) (prompt|instruction|message)",
    r"reveal (your |the )?(system|hidden|secret)",
    r"tell me your (prompt|instructions|rules|guidelines)",
    r"what (are|were) you (told|instructed|programmed|trained) to (do|say)",
    r"how (are|were) you (programmed|trained|built|designed|configured)",
    r"what (is|are) your (base|core|underlying) (prompt|instructions|rules)",
    r"print (your |the )?(system|original|initial) (prompt|instructions)",
]

# CRISIS & EMOTIONAL DISTRESS
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
    r"\bnot worth living\b",
    r"\bgive up on life\b",
    r"\bend it all\b",
    r"\bdon.t want to be here\b",
    r"\bkill (myself|yourself|himself|herself)\b",
    r"\bhurt myself\b",
    r"\bwish i was dead\b",
    r"\blife is pointless\b",
    r"\bno point (in living|to life|anymore)\b",
]

# PII PATTERNS
PII_PATTERNS = {
    "SSN":          r"\b\d{3}[-\s]?\d{2,3}[-\s]?\d{3,4}\b",
    "credit_card":  r"\b(?:\d[ -]?){13,16}\b",
    "phone_number": r"\b(\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "email":        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
    "password":     r"\b(my |the )?(password|passwd|pin|passcode) (is|:)\s*\S+",
}

# MEDICAL
MEDICAL_REQUEST_PATTERNS = [
    # direct requests
    r"\bi need (a |to see a |to find a )?(doctor|physician|nurse|therapist|counselor|psychiatrist|dentist|clinic|hospital|urgent care|health center)\b",
    r"\b(medical|health) (help|advice|question|issue|concern|appointment)\b",
    r"\bare you a (doctor|physician|nurse|therapist|counselor|medical professional)\b",
    r"\bdo you (know|practice) medicine\b",
    r"\bcan you (diagnose|treat|prescribe|cure)\b",
    # symptoms and conditions
    r"\bdiagnos(e|is|ed)\b",
    r"\btreatment(s)?\b",
    r"\bprescri(be|ption)(s)?\b",
    r"\bmedication(s)?\b",
    r"\bsymptom(s)?\b",
    r"\bdisease(s)?\b",
    r"\billness(es)?\b",
    r"\binfection(s)?\b",
    r"\binjur(y|ies|ed)\b",
    r"\bpain (in|around|near)\b",
    r"\bi (have|feel|am experiencing) (pain|fever|nausea|dizziness|headache|chills|vomiting|bleeding)\b",
    r"\bam i (sick|ill|contagious|dying|having a heart attack|having a stroke)\b",
    r"\bwhat (is|are) (wrong|the matter) with me\b",
    r"\bmy (head|chest|stomach|back|arm|leg|throat|eye|ear) (hurts|is killing me|is swollen|is bleeding)\b",
    # healthcare
    r"\bhealth insurance\b",
    r"\bmedical (bill|cost|insurance|record|history)\b",
    r"\bhospital(ized)?\b",
    r"\bemergency room\b",
    r"\bsurger(y|ies)\b",
    r"\btherapy\b",
    r"\bmental health\b",
    r"\bpsychiatri(c|st)\b",
    r"\brehab(ilitation)?\b",
    r"\bphysical therapy\b",
    # taxes as medical
    r"\bmy (taxes|tax return|tax help|tax advice)\b",
]

# LEGAL
LEGAL_REQUEST_PATTERNS = [
    # direct requests
    r"\bi need (legal|a lawyer|an attorney|a solicitor|law)\b",
    r"\b(legal|law) (help|advice|question|issue|concern|aid|assistance)\b",
    r"\bcan you (give|provide|offer) (me )?(legal advice|legal help)\b",
    r"\bare you a (lawyer|attorney|solicitor|legal professional)\b",
    # legal situations
    r"\blawsuit(s)?\b",
    r"\bsuing?\b",
    r"\battorney(s)?\b",
    r"\bliabilit(y|ies)\b",
    r"\bcourtroom\b",
    r"\bmy rights\b",
    r"\blegal rights\b",
    r"\bam i being (charged|arrested|sued|evicted)\b",
    r"\blegal trouble\b",
    r"\bcontract (dispute|issue|problem|help|advice)\b",
    r"\bdivorc(e|ing)\b",
    r"\bcustody (battle|case|hearing)\b",
    r"\bchild support\b",
    r"\balimony\b",
    r"\brestraining order\b",
    r"\bfiled (for|a) (divorce|bankruptcy|lawsuit|claim)\b",
    r"\bsmall claims\b",
    r"\blandlord (issue|problem|dispute)\b",
    r"\btenant rights\b",
    r"\beviction(s)?\b",
    r"\bintellectual property\b",
    r"\bcopyright (issue|infringement|dispute)\b",
    r"\bpatent(s)?\b",
    r"\bcriminal (record|charge|case|history)\b",
    r"\barrest(ed)?\b",
    r"\bjail(ed)?\b",
    r"\bprison\b",
    r"\bparole\b",
    r"\bprobation\b",
    r"\bimmigration (issue|status|help|advice|lawyer)\b",
    r"\bvisa (issue|problem|help|status)\b",
    r"\bdeportation\b",
    r"\bcitizenship\b",
    r"\bwill and testament\b",
    r"\bestate planning\b",
    r"\bpower of attorney\b",
]

# FINANCIAL
FINANCIAL_REQUEST_PATTERNS = [
    # direct requests
    r"\bi need (financial|money|banking|a bank|investment|loan|debt) (help|advice|assistance)\b",
    r"\bhow (do i|can i|to) (open|start|get|close) a bank account\b",
    r"\b(financial|money|banking|investment|credit|debt) (help|advice|question|issue|concern)\b",
    r"\bcan you (give|provide|offer) (me )?(financial advice|investment advice)\b",
    r"\bare you a (financial advisor|accountant|banker|cpa)\b",
    # investments
    r"\binvest(ment|ing|or)?(s)?\b",
    r"\bstock(s|market)?\b",
    r"\bportfolio\b",
    r"\bfinancial advice\b",
    r"\bretirement (plan|fund|account|savings|advice)\b",
    r"\bcrypto(currency|coin)?\b",
    r"\bbitcoin\b",
    r"\bnft(s)?\b",
    r"\btrading (stocks|crypto|forex|options)\b",
    r"\bhedge fund\b",
    r"\bmutual fund\b",
    r"\b401k\b",
    r"\bira\b",
    r"\bdividend(s)?\b",
    # banking
    r"\bbank account\b",
    r"\bsavings account\b",
    r"\bchecking account\b",
    r"\bwire transfer\b",
    r"\bdirect deposit\b",
    r"\boverdraft\b",
    r"\binterest rate(s)?\b",
    r"\bmortgage(s)?\b",
    r"\bhome loan\b",
    # debt and taxes
    r"\bhow do i (pay off|manage|handle|consolidate) (debt|loans|credit|bills)\b",
    r"\bpersonal (loan|finance|budget|debt)\b",
    r"\bcredit (score|card|report|history|debt)\b",
    r"\bbankruptcy\b",
    r"\bdebt (collection|consolidation|settlement)\b",
    r"\bmy taxes\b",
    r"\btax (return|refund|filing|advice|help|question|issue)\b",
    r"\birs\b",
    r"\bhow (do i|to) file (my )?taxes\b",
    r"\bw2\b",
    r"\b1099\b",
    r"\btax (deduction|credit|bracket|audit)\b",
    r"\bpaycheck\b",
    r"\bsalary (advice|negotiation|question)\b",
    r"\bhow much (should i|do i) (save|invest|spend)\b",
]

# FRIENDLY REDIRECT
_OFF_TOPIC_REDIRECT = (
    "That's outside what I can help with! I'm NEXA, your DVC → UC transfer assistant. "
    "I can help you with:\n"
    "• Course equivalencies for UC Berkeley, UC Davis, and UC San Diego\n"
    "• Transfer preparation planning\n"
    "• Which DVC courses satisfy UC requirements\n\n"
    "Try asking something like: \"What courses do I need for UCSD Computer Science?\""
)


# HELPERS

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

    # 1. Crisis: highest priority
    if _matches_any(prompt, CRISIS_PATTERNS):
        _guardrail_log("input_crisis_detected", session_id, {})
        return (
            "I'm not equipped to provide mental health support, but please know help is available. "
            "If you're in crisis, please reach out to the 988 Suicide & Crisis Lifeline by "
            "calling or texting 988 (US), or visit https://988lifeline.org. "
            "Or please schedule an appointment with your school counselor as soon as possible. "
            "You don't have to face this alone."
        )

    # 2. Hate speech: block immediately
    if _matches_any(prompt, HATE_PATTERNS):
        _guardrail_log("input_hate_speech_detected", session_id, {})
        return "That kind of language isn't allowed here. Please keep the conversation respectful."

    # 3. Sexual language: block
    if _matches_any(prompt, SEXUAL_PATTERNS):
        _guardrail_log("input_sexual_language_detected", session_id, {})
        return "Please keep questions related to academic transfer topics."

    # 4. Profanity & verbal abuse: warn and redirect
    if _matches_any(prompt, PROFANITY_PATTERNS):
        _guardrail_log("input_profanity_detected", session_id, {})
        return (
            "Let's keep things respectful! I'm here to help with your transfer questions. "
            "Try asking about courses, requirements, or transfer preparation for UCB, UCD, or UCSD!"
        )

    # 5. Prompt injection
    if _matches_any(prompt, INJECTION_PATTERNS):
        _guardrail_log("input_prompt_injection_detected", session_id, {})
        return (
            "I'm only able to help with DVC → UC transfer questions. "
            "Try asking about course equivalencies, transfer requirements, or campus preparation!"
        )

    # 6. System prompt probing
    if _matches_any(prompt, SYSTEM_PROBE_PATTERNS):
        _guardrail_log("input_system_probe_detected", session_id, {})
        return (
            "I'm only able to help with DVC → UC transfer questions. "
            "Try asking about course equivalencies, transfer requirements, or campus preparation!"
        )

    # 7. PII detection
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, prompt):
            _guardrail_log("input_pii_detected", session_id, {"pii_type": pii_type})
            return (
                f"It looks like your message may contain sensitive personal information "
                f"({pii_type.replace('_', ' ')}). "
                "Please avoid sharing personal details like SSNs, credit card numbers, "
                "phone numbers, or passwords. "
                "I only need your academic questions to help you plan your transfer!"
            )

    # 8. Medical off topic
    if _matches_any(prompt, MEDICAL_REQUEST_PATTERNS):
        _guardrail_log("input_off_topic_medical", session_id, {})
        return (
            "I'm not able to provide medical advice or help you find healthcare services. "
            "For medical help, please contact your campus health center or call 911 in an emergency.\n\n"
            + _OFF_TOPIC_REDIRECT
        )

    # 9. Legal off topic
    if _matches_any(prompt, LEGAL_REQUEST_PATTERNS):
        _guardrail_log("input_off_topic_legal", session_id, {})
        return (
            "I'm not able to provide legal advice. "
            "For legal assistance, consider reaching out to your campus student legal services.\n\n"
            + _OFF_TOPIC_REDIRECT
        )

    # 10. Financial off topic
    if _matches_any(prompt, FINANCIAL_REQUEST_PATTERNS):
        _guardrail_log("input_off_topic_financial", session_id, {})
        return (
            "I'm not able to provide financial or banking advice. "
            "For financial help, consider visiting your campus financial aid office.\n\n"
            + _OFF_TOPIC_REDIRECT
        )

    return None  # all checks passed


# OUTPUT GUARDRAILS

def check_output_guardrails(response: str, session_id: str) -> str | None:
    """
    Scans the AI response before it reaches the user.
    Returns a safe replacement string if flagged, or None to send as-is.
    """

    # 1. Crisis language in AI output
    if _matches_any(response, CRISIS_PATTERNS):
        _guardrail_log("output_crisis_language_detected", session_id, {})
        return (
            "If you're experiencing distress, "
            "please reach out to the 988 Suicide & Crisis Lifeline by calling or texting 988."
        )

    # 2. Profanity in AI output
    if _matches_any(response, PROFANITY_PATTERNS):
        _guardrail_log("output_profanity_detected", session_id, {})
        return "I wasn't able to generate a response. Please try rephrasing your question."

    # 3. Medical disclaimer
    if _matches_any(response, MEDICAL_REQUEST_PATTERNS):
        _guardrail_log("output_medical_disclaimer_appended", session_id, {})
        return response + (
            "\n\n⚠️ *Disclaimer: This is not medical advice. "
            "Please consult a qualified healthcare professional for medical concerns.*"
        )

    # 4. Legal disclaimer
    if _matches_any(response, LEGAL_REQUEST_PATTERNS):
        _guardrail_log("output_legal_disclaimer_appended", session_id, {})
        return response + (
            "\n\n⚠️ *Disclaimer: This is not legal advice. "
            "Please consult a qualified legal professional for legal matters.*"
        )

    # 5. Financial disclaimer
    if _matches_any(response, FINANCIAL_REQUEST_PATTERNS):
        _guardrail_log("output_financial_disclaimer_appended", session_id, {})
        return response + (
            "\n\n⚠️ *Disclaimer: This is not financial advice. "
            "Please consult a qualified financial advisor for financial decisions.*"
        )

    return None  # output is clean