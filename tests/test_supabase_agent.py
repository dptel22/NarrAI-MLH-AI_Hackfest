import io
import os
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

import main
import supabase_agent


client = TestClient(main.app)


def test_log_upload_does_nothing_when_url_missing():
    with patch.dict(os.environ, {"SUPABASE_KEY": "test-key"}, clear=True):
        with patch("supabase_agent.create_client") as mock_create_client:
            supabase_agent.log_upload("upload_123", 2, ["col1", "col2"])

    mock_create_client.assert_not_called()


def test_log_upload_does_nothing_when_key_missing():
    with patch.dict(os.environ, {"SUPABASE_URL": "https://example.supabase.co"}, clear=True):
        with patch("supabase_agent.create_client") as mock_create_client:
            supabase_agent.log_upload("upload_123", 2, ["col1", "col2"])

    mock_create_client.assert_not_called()


def test_log_upload_inserts_expected_row():
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_insert = MagicMock()

    mock_client.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert

    with patch.dict(
        os.environ,
        {
            "SUPABASE_URL": "https://example.supabase.co",
            "SUPABASE_KEY": "test-key",
        },
        clear=True,
    ):
        with patch("supabase_agent.create_client", return_value=mock_client) as mock_create_client:
            supabase_agent.log_upload("upload_123", 2, ["col1", "col2"])

    mock_create_client.assert_called_once_with("https://example.supabase.co", "test-key")
    mock_client.table.assert_called_once_with("csv_uploads")
    mock_table.insert.assert_called_once_with(
        {
            "session_id": "upload_123",
            "row_count": 2,
            "columns": ["col1", "col2"],
        }
    )
    mock_insert.execute.assert_called_once_with()


def test_log_upload_swallows_client_exceptions():
    with patch.dict(
        os.environ,
        {
            "SUPABASE_URL": "https://example.supabase.co",
            "SUPABASE_KEY": "test-key",
        },
        clear=True,
    ):
        with patch("supabase_agent.create_client", side_effect=RuntimeError("boom")):
            with patch("supabase_agent.logger.exception") as mock_logger:
                supabase_agent.log_upload("upload_123", 2, ["col1", "col2"])

    mock_logger.assert_called_once()


def test_analyze_returns_200_when_log_upload_fails_internally():
    with patch.dict(
        os.environ,
        {
            "SUPABASE_URL": "https://example.supabase.co",
            "SUPABASE_KEY": "test-key",
        },
        clear=True,
    ):
        with patch("main.supabase_agent.get_table_summary", return_value={"summary": "test"}):
            with patch("main.supabase_agent.create_client", side_effect=RuntimeError("boom")):
                with patch("main.gemini_agent.generate_insight") as mock_generate_insight:
                    with patch("main.elevenlabs_agent.text_to_audio", return_value=b"mocked_audio_bytes"):
                        mock_generate_insight.return_value = {
                            "insight": "Mocked insight",
                            "chart_data": None,
                        }
                        main.gemini_agent.ERROR_INSIGHT = "Unable to generate insight."

                        csv_content = "col1,col2\nval1,val2\n"
                        csv_file = io.BytesIO(csv_content.encode("utf-8"))

                        response = client.post(
                            "/analyze",
                            files={"file": ("test.csv", csv_file, "text/csv")},
                        )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["insight"] == "Mocked insight"
    assert json_response["columns"] == ["col1", "col2"]
    assert "audio_b64" in json_response
