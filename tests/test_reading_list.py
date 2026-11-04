import json
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/update_reading_list.py"
spec = importlib.util.spec_from_file_location("reading_list_updater", SCRIPT)
assert spec is not None
updater = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(updater)


class ReadingListTests(unittest.TestCase):
    def test_identifies_bot_without_exposing_token(self):
        calls = []

        def fake_get_json(url, params):
            calls.append((url, params))
            return {"result": {"id": 123, "username": "readinglistauto_bot"}}

        bot = updater.identify_bot("secret-token", fake_get_json)
        self.assertEqual(bot["username"], "readinglistauto_bot")
        self.assertEqual(calls, [("https://api.telegram.org/botsecret-token/getMe", {})])

    def test_extracts_doi_and_html_link_and_title(self):
        post = {
            "message_id": 12,
            "date": 1793782800,
            "chat": {"id": -100123, "type": "channel"},
            "text": "A useful paper\nDOI: 10.1234/Example.1\nhttps://example.org/full-text",
        }
        item = updater.parse_channel_post(post)
        self.assertEqual(item["title"], "A useful paper")
        self.assertEqual(item["key"], "doi:10.1234/example.1")
        self.assertEqual(
            item["links"],
            [
                {"label": "Full text", "url": "https://example.org/full-text"},
                {"label": "DOI", "url": "https://doi.org/10.1234/example.1"},
            ],
        )

    def test_uses_link_entity_for_embedded_url(self):
        post = {
            "message_id": 1,
            "date": 1793782800,
            "text": "Read the paper",
            "entities": [{"type": "text_link", "url": "https://example.org/article"}],
        }
        self.assertEqual(updater.parse_channel_post(post)["title"], "Read the paper")

    def test_ignores_posts_without_links(self):
        self.assertIsNone(updater.parse_channel_post({"text": "A discussion note"}))

    def test_filters_channel_and_deduplicates_doi(self):
        message = {
            "message_id": 1,
            "date": 1793782800,
            "chat": {"id": -100123, "type": "channel"},
            "text": "A paper https://doi.org/10.1234/one",
        }
        updates = [
            {"update_id": 5, "channel_post": message},
            {"update_id": 6, "channel_post": dict(message, message_id=2)},
            {"update_id": 7, "channel_post": dict(message, chat={"id": -100456, "type": "channel"}, text="Other https://example.org/other")},
        ]
        state, data, added = updater.process_updates(updates, {"channel_id": -100123}, {"items": [], "updated_at": ""})
        self.assertEqual(state["channel_id"], -100123)
        self.assertEqual(added, 1)
        self.assertEqual(len(data["items"]), 1)

    def test_discovers_channel_id_on_first_channel_post(self):
        post = {"message_id": 1, "date": 1793782800, "chat": {"id": -100123, "type": "channel"}, "text": "Paper https://example.org/paper"}
        state, data, added = updater.process_updates(
            [{"update_id": 2, "channel_post": post}], {"channel_id": None}, {"items": [], "updated_at": ""}
        )
        self.assertEqual(state["channel_id"], -100123)
        self.assertEqual(added, 1)

    def test_fetch_updates_reads_one_batch_without_premature_acknowledgement(self):
        calls = []

        def fake_get_json(_url, params):
            calls.append((params["offset"], params["limit"]))
            return {"result": [{"update_id": index} for index in range(updater.PAGE_SIZE)]}

        updates, offset = updater.fetch_updates("not-logged", 0, fake_get_json)
        self.assertEqual(len(updates), updater.PAGE_SIZE)
        self.assertEqual(offset, updater.PAGE_SIZE)
        self.assertEqual(calls, [(0, updater.PAGE_SIZE)])

    def test_subscribes_to_channel_and_group_updates(self):
        requests = []

        def fake_get_json(_url, params):
            requests.append(params)
            return {"result": []}

        updater.fetch_updates("not-logged", 0, fake_get_json)

        self.assertEqual(
            json.loads(requests[0]["allowed_updates"]),
            ["channel_post", "message"],
        )

    def test_imports_group_message_but_ignores_private_bot_chat(self):
        group_post = {
            "message_id": 1,
            "date": 1793782800,
            "chat": {"id": -100123, "type": "supergroup"},
            "text": "Paper https://doi.org/10.1234/group",
        }
        private_message = {
            "message_id": 2,
            "date": 1793782800,
            "chat": {"id": 123, "type": "private"},
            "text": "Private https://doi.org/10.1234/private",
        }
        state, data, added = updater.process_updates(
            [
                {"update_id": 1, "message": private_message},
                {"update_id": 2, "message": group_post},
            ],
            {"channel_id": None},
            {"items": [], "updated_at": ""},
        )

        self.assertEqual(state["channel_id"], -100123)
        self.assertEqual(added, 1)
        self.assertEqual(data["items"][0]["key"], "doi:10.1234/group")

    def test_imports_desktop_history_and_sorts_newest_first(self):
        export = {
            "messages": [
                {
                    "id": 3,
                    "type": "message",
                    "date": "2025-02-01T10:00:00+02:00",
                    "text": ["New paper ", {"type": "link", "text": "read", "href": "https://example.org/new"}],
                    "text_entities": [{"type": "text_link", "text": "read", "href": "https://example.org/new"}],
                },
                {
                    "id": 2,
                    "type": "message",
                    "date": "2025-01-01T10:00:00Z",
                    "text": "Old paper https://doi.org/10.1234/old",
                },
            ]
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "messages.json"
            path.write_text(json.dumps(export), encoding="utf-8")
            data, added = updater.import_history_export(path, {"items": [], "updated_at": ""})

        self.assertEqual(added, 2)
        self.assertEqual([item["title"] for item in data["items"]], ["New paper read", "Old paper"])
        self.assertEqual(data["items"][0]["posted_at"], "2025-02-01T08:00:00Z")

    def test_history_import_deduplicates_an_existing_doi(self):
        export = {
            "messages": [
                {"id": 1, "type": "message", "date": "2025-01-01T10:00:00Z", "text": "Paper https://doi.org/10.1234/same"}
            ]
        }
        existing = updater.parse_channel_post(
            {"message_id": 4, "date": 1735725600, "text": "Paper DOI: 10.1234/same"}
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "messages.json"
            path.write_text(json.dumps(export), encoding="utf-8")
            data, added = updater.import_history_export(path, {"items": [existing], "updated_at": ""})
        self.assertEqual(added, 0)
        self.assertEqual(len(data["items"]), 1)


if __name__ == "__main__":
    unittest.main()
