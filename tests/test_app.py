import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import add_entry, get_server_address, load_entries, render_page


class ArchiveAppTests(unittest.TestCase):
    def test_load_entries_returns_empty_list_when_file_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            missing_path = Path(tmpdir) / "entries.json"
            self.assertEqual(load_entries(missing_path), [])

    def test_add_entry_saves_entry_to_json_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "entries.json"
            entry = {
                "week": "3",
                "colab_link": "https://colab.research.google.com/drive/example",
                "reflection": "파이썬 기초를 익혔다.",
                "improvement": "더 자주 복습하겠다.",
            }

            added = add_entry(data_path, entry)
            loaded = load_entries(data_path)

            self.assertTrue(added["id"].startswith("week-3-"))
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["week"], "3")

    def test_render_page_contains_entry_details(self):
        entries = [
            {
                "id": "week-1-001",
                "week": "1",
                "colab_link": "https://example.com",
                "reflection": "좋았다.",
                "improvement": "더 깊게 공부하겠다.",
            }
        ]

        html = render_page(entries, message="저장 완료")
        self.assertIn("CS Archive", html)
        self.assertIn("week-1-001", html)
        self.assertIn("https://example.com", html)

    def test_get_server_address_uses_environment_values(self):
        with patch.dict(os.environ, {"PORT": "9000", "HOST": "0.0.0.0"}, clear=True):
            self.assertEqual(get_server_address(), ("0.0.0.0", 9000))


if __name__ == "__main__":
    unittest.main()
