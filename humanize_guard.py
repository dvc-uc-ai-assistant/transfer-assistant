# backend/humanize_guard.py — NEXA bot/humanizing detection
#
# Provides two functions called from app.py:
#   score_request(session_id, message, timing_ms, honeypot) → (score, flags)
#   handle_trust_score(score, flags) → "ok" | "slow_down" | "captcha" | "blocked"
#
# Uses an in-memory session store to track per-session behaviour.
# All thresholds are tunable via the constants below.

import hashlib
import time
import logging
import json
from collections import defaultdict

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# TUNABLE THRESHOLDS
# ---------------------------------------------------------------------------

# Minimum time (ms) between input focus and submission — below this = suspiciously fast
MIN_HUMAN_TYPING_MS = 1000

# Max messages per session within the velocity window before flagging
VELOCITY_WINDOW_SECS = 60
VELOCITY_MAX_MESSAGES = 10

# Trust score thresholds — actions triggered at each level
THRESHOLD_SLOW_DOWN = 25   # warn and add friction
THRESHOLD_CAPTCHA   = 50   # require CAPTCHA challenge
THRESHOLD_BLOCK     = 100  # hard block (e.g. honeypot filled)

# Penalty weights per flag type
TRUST_PENALTIES = {
    "honeypot_filled":    100,  # instant block — only bots fill hidden fields
    "instant_submit":      30,  # submitted faster than a human can type
    "velocity_breach":     40,  # too many messages in a short window
    "duplicate_message":   20,  # same message sent again this session
    "uniform_interval":    25,  # messages arriving at suspiciously even intervals
}


# ---------------------------------------------------------------------------
# IN-MEMORY SESSION STATE
# (separate from app.py sessions — only stores bot-detection signals)
# ---------------------------------------------------------------------------

# { session_id: { "last_msg_hash": str, "timestamps": [float], "last_interval": float } }
_bot_state: dict = defaultdict(lambda: {
    "last_msg_hash": None,
    "timestamps":    [],
    "last_interval": None,
})


def _guardrail_log(event: str, session_id: str, meta: dict = None):
    payload = {"event": event, "session_id": session_id}
    if meta:
        payload.update(meta)
    logger.warning(json.dumps(payload))


# ---------------------------------------------------------------------------
# CORE SCORING FUNCTION
# ---------------------------------------------------------------------------

def score_request(
    session_id: str,
    message: str,
    timing_ms: int | float,
    honeypot: str,
) -> tuple[int, list[str]]:
    """
    Analyses a single request for bot-like signals.

    Parameters:
        session_id  — current session identifier
        message     — the user's prompt text
        timing_ms   — milliseconds between input focus and form submission (from frontend)
        honeypot    — value of the hidden _confirm field (should always be empty for humans)

    Returns:
        (score, flags) where score is an int and flags is a list of triggered check names.
    """

    score = 0
    flags = []
    state = _bot_state[session_id]
    now   = time.time()

    # ------------------------------------------------------------------
    # CHECK 1: Honeypot field — if filled, it's almost certainly a bot
    # ------------------------------------------------------------------
    if honeypot:
        score += TRUST_PENALTIES["honeypot_filled"]
        flags.append("honeypot_filled")
        _guardrail_log("bot_honeypot_triggered", session_id, {})
        # Return immediately — no point running further checks
        return score, flags

    # ------------------------------------------------------------------
    # CHECK 2: Submission timing — humans take at least ~1 second to type
    # ------------------------------------------------------------------
    try:
        timing_ms = float(timing_ms)
    except (TypeError, ValueError):
        timing_ms = 0

    if timing_ms < MIN_HUMAN_TYPING_MS:
        score += TRUST_PENALTIES["instant_submit"]
        flags.append("instant_submit")
        _guardrail_log("bot_instant_submit", session_id, {"timing_ms": timing_ms})

    # ------------------------------------------------------------------
    # CHECK 3: Duplicate message — same content sent again this session
    # ------------------------------------------------------------------
    msg_hash = hashlib.md5(message.strip().lower().encode()).hexdigest()
    if state["last_msg_hash"] and msg_hash == state["last_msg_hash"]:
        score += TRUST_PENALTIES["duplicate_message"]
        flags.append("duplicate_message")
        _guardrail_log("bot_duplicate_message", session_id, {})
    state["last_msg_hash"] = msg_hash

    # ------------------------------------------------------------------
    # CHECK 4: Velocity — too many messages in the rolling time window
    # ------------------------------------------------------------------
    # Prune timestamps outside the window
    state["timestamps"] = [
        t for t in state["timestamps"]
        if now - t < VELOCITY_WINDOW_SECS
    ]

    if len(state["timestamps"]) >= VELOCITY_MAX_MESSAGES:
        score += TRUST_PENALTIES["velocity_breach"]
        flags.append("velocity_breach")
        _guardrail_log(
            "bot_velocity_breach", session_id,
            {"messages_in_window": len(state["timestamps"]), "window_secs": VELOCITY_WINDOW_SECS}
        )

    state["timestamps"].append(now)

    # ------------------------------------------------------------------
    # CHECK 5: Uniform interval — messages arriving at suspiciously even spacing
    # ------------------------------------------------------------------
    if len(state["timestamps"]) >= 3:
        intervals = [
            state["timestamps"][i] - state["timestamps"][i - 1]
            for i in range(1, len(state["timestamps"]))
        ]
        # If the last two intervals differ by less than 100ms, flag as robotic
        if len(intervals) >= 2 and abs(intervals[-1] - intervals[-2]) < 0.1:
            score += TRUST_PENALTIES["uniform_interval"]
            flags.append("uniform_interval")
            _guardrail_log("bot_uniform_interval", session_id, {"interval_diff_ms": abs(intervals[-1] - intervals[-2]) * 1000})

    return score, flags


# ---------------------------------------------------------------------------
# ACTION DECISION
# ---------------------------------------------------------------------------

def handle_trust_score(score: int, flags: list[str]) -> str:
    """
    Converts a numeric trust score into an action string.

    Returns one of:
        "ok"         — request is fine, proceed normally
        "slow_down"  — suspicious but allow through (add friction on frontend)
        "captcha"    — require the user to complete a CAPTCHA before continuing
        "blocked"    — hard block, return 403
    """
    if score >= THRESHOLD_BLOCK:
        return "blocked"
    elif score >= THRESHOLD_CAPTCHA:
        return "captcha"
    elif score >= THRESHOLD_SLOW_DOWN:
        return "slow_down"
    return "ok"
