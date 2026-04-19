import io
import os
import logging

logger = logging.getLogger(__name__)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")  # default: Bella


def _elevenlabs_tts(text: str) -> bytes:
    """Attempt ElevenLabs synthesis. Returns bytes or raises."""
    import requests
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text[:5000],
        "model_id": "eleven_turbo_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    resp.raise_for_status()
    return resp.content


def _gtts_tts(text: str) -> bytes:
    """gTTS fallback. Always works, no API key required."""
    from gtts import gTTS
    buf = io.BytesIO()
    gTTS(text=text[:5000], lang="en", slow=False).write_to_fp(buf)
    return buf.getvalue()


def text_to_audio(text: str, prefix: str = "") -> bytes:
    full_text = f"{prefix} {text}".strip() if prefix else text

    # Try ElevenLabs first if key is configured
    if ELEVENLABS_API_KEY:
        try:
            audio = _elevenlabs_tts(full_text)
            logger.info("TTS: ElevenLabs succeeded")
            return audio
        except Exception as e:
            logger.warning(f"ElevenLabs TTS failed ({e}), falling back to gTTS")

    # Silent fallback — always runs if ElevenLabs is absent or fails
    try:
        audio = _gtts_tts(full_text)
        logger.info("TTS: gTTS succeeded")
        return audio
    except Exception as e:
        logger.warning(f"gTTS also failed: {e}")
        return b""
