import pytest
from unittest.mock import patch, MagicMock
import elevenlabs_agent

@patch('elevenlabs_agent.client')
def test_text_to_audio(mock_client):
    mock_response = MagicMock()
    mock_response.audio_content = b"audiodata"
    mock_client.synthesize_speech.return_value = mock_response

    result = elevenlabs_agent.text_to_audio("Hello world")

    assert isinstance(result, bytes)
    assert len(result) > 0
    assert result == b"audiodata"
