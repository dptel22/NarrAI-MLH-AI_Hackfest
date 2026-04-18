import os
import json
import tempfile
import logging
from google.cloud import texttospeech
from google.api_core.exceptions import InvalidArgument

logger = logging.getLogger(__name__)

# Load Google Cloud credentials from environment variable if present
creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if creds_json:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w")
    tmp.write(creds_json)
    tmp.close()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp.name

# Initialize client. This will automatically use GOOGLE_APPLICATION_CREDENTIALS if set,
# or Workload Identity if running on GCP.
try:
    client = texttospeech.TextToSpeechClient()
except Exception as e:
    logger.warning(f"Failed to initialize Google Cloud TTS client: {e}")
    client = None

def _synthesize_with_voice(text: str, voice_name: str) -> bytes:
    if not client:
        return b""

    synthesis_input = texttospeech.SynthesisInput(text=text[:5000])
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    return response.audio_content

def text_to_audio(text: str, prefix: str = "") -> bytes:
    full_text = f"{prefix} {text}".strip() if prefix else text

    if client is None:
        logger.warning("Google Cloud TTS client not initialized; skipping audio generation.")
        return b""

    try:
        # Try default voice first
        return _synthesize_with_voice(full_text, "en-US-Neural2-F")
    except InvalidArgument as e:
        # Fallback if voice is unavailable
        logger.warning(f"Default voice failed, falling back: {e}")
        try:
            return _synthesize_with_voice(full_text, "en-US-Standard-C")
        except Exception as fallback_e:
            print(f"Error in text_to_audio (fallback): {fallback_e}")
            return b""
    except Exception as e:
        print(f"Error in text_to_audio: {e}")
        return b""
