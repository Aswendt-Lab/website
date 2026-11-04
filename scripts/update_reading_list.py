#!/usr/bin/env python3
"""Import linked manuscripts from Telegram into the website data."""
import argparse
import datetime as dt
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
URL_PATTERN = re.compile(r"https?://[^\s<>()]+", re.IGNORECASE)
DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:\w]+", re.IGNORECASE)
TRAILING_URL_PUNCTUATION = ".,;:!?)]}'\""
PAGE_SIZE = 100


def request_json(url, params):
    target = url + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(target, headers={"User-Agent": "AswendtLabWebsite/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=40) as response:
            payload = json.load(response)
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise RuntimeError("Telegram API request failed; existing reading-list data retained") from None
    if not isinstance(payload, dict) or payload.get("ok") is not True:
        raise RuntimeError("Telegram API returned an unsuccessful response")
    return payload


def identify_bot(token, get_json=request_json):
    payload = get_json(f"https://api.telegram.org/bot{token}/getMe", {})
    bot = payload.get("result")
    if not isinstance(bot, dict) or not isinstance(bot.get("username"), str) or not isinstance(bot.get("id"), int):
        raise ValueError("Telegram getMe response is missing bot identity")
    return bot


def fetch_updates(token, offset, get_json=request_json):
    """Fetch one batch; avoid acknowledging a batch before its state is saved."""
    payload = get_json(
        f"https://api.telegram.org/bot{token}/getUpdates",
        {
            "offset": offset,
            "limit": PAGE_SIZE,
            "timeout": 0,
            "allowed_updates": json.dumps(["channel_post", "message"]),
        },
    )
    updates = payload.get("result")
    if not isinstance(updates, list):
        raise ValueError("Telegram response is missing its update list")
    next_offset = offset
    for update in updates:
        if not isinstance(update, dict) or not isinstance(update.get("update_id"), int):
            raise ValueError("Telegram response contains an invalid update")
        next_offset = max(next_offset, update["update_id"] + 1)
    return updates, next_offset


def _safe_url(value):
    value = value.rstrip(TRAILING_URL_PUNCTUATION)
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme.lower() not in ("http", "https") or not parsed.hostname:
        return ""
    return value


def manuscript_links(message, text):
    entities = message.get("entities") or message.get("caption_entities") or []
    candidates = [entity.get("url", "") for entity in entities if isinstance(entity, dict)]
    candidates.extend(URL_PATTERN.findall(text))
    candidates.extend(
        "https://doi.org/" + doi.rstrip(TRAILING_URL_PUNCTUATION)
        for doi in DOI_PATTERN.findall(text)
    )

    links = []
    seen = set()
    for candidate in candidates:
        url = _safe_url(candidate)
        if not url:
            continue
        doi_match = DOI_PATTERN.search(urllib.parse.unquote(urllib.parse.urlsplit(url).path))
        if doi_match:
            doi = doi_match.group(0).rstrip(TRAILING_URL_PUNCTUATION).lower()
            url = "https://doi.org/" + doi
            label = "DOI"
        else:
            label = "Full text" if not any(link["label"] == "Full text" for link in links) else "Link"
        if url not in seen:
            links.append({"label": label, "url": url})
            seen.add(url)
    return links


def parse_channel_post(message):
    text = message.get("text") or message.get("caption") or ""
    links = manuscript_links(message, text)
    if not links:
        return None

    title = message.get("title") or text
    title = URL_PATTERN.sub("", title)
    title = DOI_PATTERN.sub("", title)
    title = re.sub(r"\bdoi\s*:\s*", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s+", " ", title).strip(" \t\r\n-–—:;|")
    if not title:
        title = "Untitled manuscript"

    doi = ""
    for link in links:
        if link["label"] == "DOI":
            doi_match = DOI_PATTERN.search(link["url"])
            if doi_match:
                doi = doi_match.group(0).lower()
                break
    primary_url = next((link["url"] for link in links if link["label"] == "Full text"), links[0]["url"])
    timestamp = message.get("date")
    if isinstance(timestamp, int):
        posted = dt.datetime.fromtimestamp(timestamp, dt.timezone.utc)
    elif isinstance(timestamp, str):
        try:
            posted = dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Telegram channel post has an invalid timestamp") from None
        if posted.tzinfo is None:
            raise ValueError("Telegram channel post timestamp must include a timezone")
        posted = posted.astimezone(dt.timezone.utc)
    else:
        raise ValueError("Telegram channel post is missing its timestamp")
    posted_at = posted.isoformat(timespec="seconds").replace("+00:00", "Z")
    key = "doi:" + doi if doi else "url:" + primary_url
    return {
        "key": key,
        "title": title,
        "links": links,
        "posted_at": posted_at,
        "message_id": message.get("message_id"),
    }


def merge_items(data, incoming):
    known_keys = set()
    for existing in data["items"]:
        if not isinstance(existing, dict):
            raise ValueError("Reading-list data contains an invalid entry")
        key = existing.get("key")
        if key is not None and not isinstance(key, str):
            raise ValueError("Reading-list data contains an invalid entry key")
        if key:
            known_keys.add(key)

    added = []
    for item in incoming:
        key = item.get("key")
        if not isinstance(key, str):
            raise ValueError("Imported reading-list entry has an invalid key")
        if key not in known_keys:
            added.append(item)
            known_keys.add(key)
    if added:
        data["items"].extend(added)
        data["items"].sort(key=lambda entry: (entry["posted_at"], entry.get("message_id") or 0), reverse=True)
        data["updated_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    return data, len(added)


def _flatten_export_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(
            part if isinstance(part, str) else part.get("text", "")
            for part in value
            if isinstance(part, str) or isinstance(part, dict) and isinstance(part.get("text"), str)
        )
    return ""


class TelegramHtmlHistoryParser(HTMLParser):
    """Extract dated Telegram Desktop HTML messages without retaining export markup."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.messages = []
        self.message = None
        self.div_depth = 0
        self.text_depths = []
        self.preview_depths = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()
        if self.message is None:
            if tag == "div" and "message" in classes and "service" not in classes:
                message_id = re.search(r"\d+", attributes.get("id", ""))
                self.message = {
                    "message_id": int(message_id.group()) if message_id else None,
                    "date": "",
                    "text_parts": [],
                    "preview_parts": [],
                    "urls": [],
                }
                self.div_depth = 1
            return

        if tag == "div":
            self.div_depth += 1
            if "date" in classes:
                self.message["date"] = attributes.get("title", "")
            if "text" in classes:
                self.text_depths.append(self.div_depth)
            if "webpage_title" in classes:
                self.preview_depths.append(self.div_depth)
        elif tag == "a":
            href = attributes.get("href", "")
            if href.startswith(("http://", "https://")):
                self.message["urls"].append(href)
        elif tag == "br":
            if self.text_depths:
                self.message["text_parts"].append("\n")
            if self.preview_depths:
                self.message["preview_parts"].append("\n")

    def handle_endtag(self, tag):
        if self.message is None or tag != "div":
            return
        if self.text_depths and self.text_depths[-1] == self.div_depth:
            self.text_depths.pop()
        if self.preview_depths and self.preview_depths[-1] == self.div_depth:
            self.preview_depths.pop()
        if self.div_depth == 1:
            message_id = self.message["message_id"]
            if message_id is not None:
                self.message["message_id"] = message_id
                self.messages.append(self.message)
            self.message = None
            self.div_depth = 0
            self.text_depths.clear()
            self.preview_depths.clear()
            return
        self.div_depth -= 1

    def handle_data(self, data):
        if self.message is None:
            return
        if self.text_depths:
            self.message["text_parts"].append(data)
        if self.preview_depths:
            self.message["preview_parts"].append(data)


def _html_export_messages(path):
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        raise ValueError("Could not read the Telegram Desktop HTML export") from None
    parser = TelegramHtmlHistoryParser()
    parser.feed(content)
    if not parser.messages:
        raise ValueError("Telegram HTML export did not contain any dated messages")

    messages = []
    for message in parser.messages:
        try:
            local_date = dt.datetime.strptime(message["date"], "%d %B %Y, %H:%M:%S")
        except ValueError:
            raise ValueError(
                f"Telegram HTML export has an unsupported date for message {message['message_id']}"
            ) from None
        posted = local_date.astimezone(dt.timezone.utc)
        messages.append({
            "message_id": message["message_id"],
            "date": posted.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "text": "".join(message["text_parts"]),
            "title": "".join(message["preview_parts"]).strip(),
            "entities": [{"url": url} for url in message["urls"]],
        })
    return messages


def import_history_export(path, data):
    """Merge a Telegram Desktop JSON or HTML export into the list."""
    if path.suffix.lower() in {".html", ".htm"}:
        messages = _html_export_messages(path)
    else:
        try:
            export = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raise ValueError("Could not read the Telegram Desktop JSON export") from None
        messages = export.get("messages") if isinstance(export, dict) else None
        if not isinstance(messages, list):
            raise ValueError("Telegram export must be a JSON or HTML Telegram Desktop export")

    incoming = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        if "type" in message and message.get("type") != "message":
            continue
        message_id = message.get("id")
        message_id = message.get("message_id", message_id)
        if not isinstance(message_id, int):
            raise ValueError("Telegram export contains a message without a numeric ID")
        entities = message.get("entities") or message.get("text_entities") or []
        if not isinstance(entities, list):
            raise ValueError("Telegram export contains invalid text entities")
        normalized = {
            "message_id": message_id,
            "date": message.get("date"),
            "text": message.get("text") if isinstance(message.get("text"), str) else _flatten_export_text(message.get("text")),
            "title": message.get("title", ""),
            "entities": [
                {"url": entity.get("href") or entity.get("url", "")}
                for entity in entities
                if isinstance(entity, dict)
            ],
        }
        item = parse_channel_post(normalized)
        if item:
            incoming.append(item)
    return merge_items(data, incoming)


def process_updates(updates, state, data):
    channel_id = state.get("channel_id")
    incoming = []

    for update in updates:
        message = update.get("channel_post") or update.get("message")
        if not isinstance(message, dict):
            continue
        chat = message.get("chat")
        if (
            not isinstance(chat, dict)
            or not isinstance(chat.get("id"), int)
            or chat.get("type") not in {"channel", "group", "supergroup"}
        ):
            continue
        message_channel_id = chat["id"]
        if channel_id is None:
            channel_id = message_channel_id
        if message_channel_id != channel_id:
            continue
        item = parse_channel_post(message)
        if item:
            incoming.append(item)
    data, added = merge_items(data, incoming)
    return {"channel_id": channel_id}, data, added


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--history-export",
        type=Path,
        help="Import a Telegram Desktop JSON or HTML export without contacting the Bot API",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    state_path = root / "_data/reading_list_state.json"
    data_path = root / "_data/reading_list.json"
    data = json.loads(data_path.read_text(encoding="utf-8")) if data_path.exists() else {"items": [], "updated_at": ""}
    if not isinstance(data.get("items"), list):
        raise ValueError("Reading-list data has an invalid format")

    state = None
    channel_post_count = 0
    if args.history_export:
        data, added = import_history_export(args.history_export, data)
        update_count = 0
    else:
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not token:
            raise RuntimeError("Set TELEGRAM_BOT_TOKEN or provide --history-export")
        bot = identify_bot(token)
        print(f"Connected Telegram bot: @{bot['username']} (ID {bot['id']}).")
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {"offset": 0, "channel_id": None}
        if not isinstance(state.get("offset"), int):
            raise ValueError("Telegram update state has an invalid format")
        updates, next_offset = fetch_updates(token, state["offset"])
        state, data, added = process_updates(updates, state, data)
        state["offset"] = next_offset
        update_count = len(updates)
        channel_post_count = sum(
            isinstance(update.get("channel_post"), dict)
            or isinstance(update.get("message"), dict)
            and update["message"].get("chat", {}).get("type") in {"group", "supergroup"}
            for update in updates
        )

    with tempfile.TemporaryDirectory(prefix="lab-reading-list-") as temporary:
        staged_data = Path(temporary) / "reading_list.json"
        _write_json(staged_data, data)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        staged_files = [(staged_data, data_path)]
        if state is not None:
            staged_state = Path(temporary) / "reading_list_state.json"
            _write_json(staged_state, state)
            staged_files.append((staged_state, state_path))
        for source, destination in staged_files:
            pending = destination.with_suffix(destination.suffix + ".pending")
            shutil.copyfile(source, pending)
            pending.replace(destination)
    if state is None:
        print(f"Imported {added} new manuscript(s) from the history export.")
    else:
        print(
            f"Telegram returned {update_count} update(s), including {channel_post_count} "
            f"channel/group post(s); imported {added} new manuscript(s)."
        )


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, OSError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
