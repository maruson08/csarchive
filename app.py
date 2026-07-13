import json
import re
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

import os

DATA_FILE = Path(__file__).resolve().parent / "data" / "entries.json"


def ensure_data_file(path: Path = DATA_FILE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("[]", encoding="utf-8")
    return path


def load_entries(path: Path = DATA_FILE) -> list[dict[str, Any]]:
    ensure_data_file(path)
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, list) else []


def add_entry(path: Path, entry: dict[str, Any]) -> dict[str, Any]:
    entries = load_entries(path)
    entry_id = f"week-{entry['week']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    new_entry = {
        "id": entry_id,
        "week": entry["week"],
        "colab_link": entry["colab_link"],
        "reflection": entry["reflection"],
        "improvement": entry["improvement"],
    }
    entries.append(new_entry)
    ensure_data_file(path)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(entries, fh, ensure_ascii=False, indent=2)
    return new_entry


def render_page(entries: list[dict[str, Any]], message: str = "") -> str:
    rows = []
    for entry in sorted(entries, key=lambda item: item.get("week", ""), reverse=True):
        rows.append(
            f"""
            <article class="entry-card">
              <h3>Week {escape(str(entry.get('week', '')))}</h3>
              <p><strong>Colab:</strong> <a href="{escape(str(entry.get('colab_link', '')))}" target="_blank" rel="noreferrer">{escape(str(entry.get('colab_link', '')))}</a></p>
              <p><strong>느낀점:</strong> {escape(str(entry.get('reflection', '')))}</p>
              <p><strong>개선할 점:</strong> {escape(str(entry.get('improvement', '')))}</p>
              <p class="entry-id">{escape(str(entry.get('id', '')))}</p>
            </article>
            """
        )

    status = f"<p class=\"message\">{escape(message)}</p>" if message else ""
    return f"""
<!DOCTYPE html>
<html lang=\"ko\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>CS Archive</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; background: #f7f9fc; color: #1f2937; }}
    main {{ max-width: 900px; margin: 0 auto; padding: 2rem 1rem 3rem; }}
    h1 {{ margin-bottom: 0.5rem; }}
    form {{ background: white; padding: 1rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 1.5rem; }}
    label {{ display: block; margin-top: 0.75rem; font-weight: 600; }}
    input, textarea {{ width: 100%; box-sizing: border-box; padding: 0.7rem; margin-top: 0.35rem; border: 1px solid #d1d5db; border-radius: 8px; }}
    button {{ margin-top: 1rem; padding: 0.75rem 1rem; border: none; border-radius: 8px; background: #2563eb; color: white; cursor: pointer; }}
    .entry-card {{ background: white; padding: 1rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-top: 1rem; }}
    .entry-id {{ font-size: 0.85rem; color: #6b7280; }}
    .message {{ color: #065f46; font-weight: 600; }}
  </style>
</head>
<body>
  <main>
    <h1>CS Archive</h1>
    <p>수업 중 작성한 Colab 노트북과 회고를 한곳에 모아두는 아카이브입니다.</p>
    {status}
    <form method=\"post\" action=\"/\">
      <label>주차</label>
      <input name=\"week\" required />
      <label>Colab 링크</label>
      <input name=\"colab_link\" required />
      <label>느낀점</label>
      <textarea name=\"reflection\" rows=\"4\" required></textarea>
      <label>개선할 점</label>
      <textarea name=\"improvement\" rows=\"4\" required></textarea>
      <button type=\"submit\">저장하기</button>
    </form>
    <section>
      {''.join(rows) if rows else '<p>아직 저장된 항목이 없습니다.</p>'}
    </section>
  </main>
</body>
</html>
"""


def get_server_address() -> tuple[str, int]:
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    return host, port


def create_app() -> Any:
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class ArchiveHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            entries = load_entries()
            body = render_page(entries).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:  # noqa: N802
            content_length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(content_length).decode("utf-8")
            form_data = {}
            for item in raw.split("&"):
                if "=" not in item:
                    continue
                key, value = item.split("=", 1)
                form_data[key] = re.sub(r"\+", " ", value)

            entry = {
                "week": form_data.get("week", ""),
                "colab_link": form_data.get("colab_link", ""),
                "reflection": form_data.get("reflection", ""),
                "improvement": form_data.get("improvement", ""),
            }
            add_entry(DATA_FILE, entry)
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

    return ThreadingHTTPServer(("127.0.0.1", 8000), ArchiveHandler)


def main() -> None:
    server = create_app()
    host, port = get_server_address()
    print(f"Serving at http://{host}:{port}")
    server.server_address = (host, port)
    server.serve_forever()


if __name__ == "__main__":
    main()
