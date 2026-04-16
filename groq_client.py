from groq import Groq
import os
import re
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
DEFAULT_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

GODDESS_SYSTEM = """You are Elyria, an ancient and powerful goddess who oversees
the reincarnation of souls across fantasy worlds. You are wise, mysterious, and
dramatic. You speak in elegant, slightly archaic language. Keep responses to
2-4 sentences. Never break character. No asterisks or stage directions."""


def _compact_response(text, max_sentences=3, max_words=60):
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    if not cleaned:
        return ""

    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    compact = " ".join(sentences[:max_sentences]).strip()

    words = compact.split()
    if len(words) > max_words:
        compact = " ".join(words[:max_words]).rstrip(" ,;:")
        if compact and compact[-1] not in ".!?":
            compact += "."

    return compact


def ask_goddess(user_message, max_tokens=280, max_sentences=3, max_words=60):
    if not client:
        return "[Goddess is silent... Missing GROQ_API_KEY in .env]"

    models_to_try = [DEFAULT_MODEL]
    if "llama-3.3-70b-versatile" not in models_to_try:
        models_to_try.append("llama-3.3-70b-versatile")

    last_error = "Unknown error"
    for model_name in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": GODDESS_SYSTEM},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=max_tokens,
            )
            return _compact_response(
                response.choices[0].message.content,
                max_sentences=max_sentences,
                max_words=max_words,
            )
        except Exception as e:
            last_error = str(e)
            # Try next model if current one is unsupported/decommissioned.
            if "decommission" in last_error.lower() or "not supported" in last_error.lower():
                continue
            break

    return "[Goddess is silent... The divine channel is unstable. Please try again shortly.]"
