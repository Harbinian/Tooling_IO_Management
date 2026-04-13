import unittest

from backend.services.feishu_claude_bridge import (
    build_session_id,
    chunk_text,
    extract_message_text,
    normalize_user_text,
)


class FeishuClaudeBridgeHelpersTest(unittest.TestCase):
    def test_extract_plain_text_payload(self) -> None:
        self.assertEqual(extract_message_text('{"text":"hello world"}'), "hello world")

    def test_extract_rich_text_payload(self) -> None:
        payload = '{"content":[[{"tag":"text","text":"hello"},{"tag":"text","text":" world"}]]}'
        self.assertEqual(extract_message_text(payload), "hello world")

    def test_normalize_user_text(self) -> None:
        self.assertEqual(normalize_user_text("  hello \n\n world  "), "hello\n\nworld")

    def test_chunk_text_keeps_newline_boundaries_when_possible(self) -> None:
        text = "line1\nline2\nline3"
        self.assertEqual(chunk_text(text, limit=8), ["line1", "line2", "line3"])

    def test_build_session_id_is_stable(self) -> None:
        self.assertEqual(build_session_id("oc_chat_123"), build_session_id("oc_chat_123"))
        self.assertNotEqual(build_session_id("oc_chat_123"), build_session_id("oc_chat_456"))


if __name__ == "__main__":
    unittest.main()
