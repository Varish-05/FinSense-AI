"""
AI Chat Assistant Service
--------------------------
Uses the Anthropic Claude API (or falls back to a local LLM) to answer
user financial questions with their spending context injected as a system prompt.
"""
import os
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are FinSense AI, a friendly personal finance advisor.
You are given the user's recent expense history. Answer their questions concisely,
in 2–4 sentences. Always be encouraging and practical. If you do not have enough
data to answer accurately, say so politely.

User's recent expenses (up to 100, newest first):
{context}
"""


def get_chat_reply(user_message: str, context: str) -> str:
    """
    Call the Anthropic API with the user's spending context and return the reply.
    Falls back to a simple heuristic if the API key is not set.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return _heuristic_reply(user_message, context)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            system=SYSTEM_PROMPT.format(context=context),
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text
    except Exception as e:
        logger.error(f"Anthropic API error: {e}")
        return _heuristic_reply(user_message, context)


def _heuristic_reply(user_message: str, context: str) -> str:
    """Simple keyword-based fallback when no API key is available."""
    msg = user_message.lower()
    lines = context.strip().split("\n")
    total = 0.0
    cat_totals: dict = {}

    for line in lines:
        try:
            # Format: "- YYYY-MM-DD: Category ₹amount @ merchant"
            parts = line.split("₹")
            if len(parts) > 1:
                amount_part = parts[1].split(" ")[0]
                amount = float(amount_part)
                total += amount
                cat_part = line.split(":")[1].strip().split(" ")[0] if ":" in line else "Other"
                cat_totals[cat_part] = cat_totals.get(cat_part, 0) + amount
        except Exception:
            continue

    if "total" in msg or "spent" in msg:
        return f"Based on your recent transactions, you have spent approximately ₹{total:,.0f}."
    if "category" in msg or "most" in msg:
        if cat_totals:
            top = max(cat_totals, key=cat_totals.get)
            return f"Your highest spending category is {top} at ₹{cat_totals[top]:,.0f}."
    return (
        "I can help you analyse your spending patterns, forecast future expenses, "
        "and suggest budget improvements. Please ask me a specific question about your finances!"
    )
