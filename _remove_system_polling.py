from pathlib import Path
import re
import xml.etree.ElementTree as ET

base = Path(r"D:\odoo-19\custom_addons\med_iot_command_center")

files = [
    base / "static" / "src" / "xml" / "dashboard.xml",
    base / "views" / "settings_views.xml",
]

markers = [
    "SYSTEM POLLING",
    "Dashboard auto-refresh interval",
    "CHECK INTERVAL",
    "Recommended: 15 seconds",
]

def find_matching_block(text, marker_index, tag):
    pattern = re.compile(rf"<(/?){tag}\b[^>]*?>", re.I)
    tokens = list(pattern.finditer(text))
    blocks = []
    stack = []

    for m in tokens:
        closing = m.group(1) == "/"
        if not closing:
            stack.append(m)
        elif stack:
            start = stack.pop()
            end = m.end()
            if start.start() <= marker_index <= end:
                blocks.append((start.start(), end, text[start.start():end]))

    good = []
    for start, end, block in blocks:
        block_upper = block.upper()
        if "SYSTEM POLLING" in block_upper or "CHECK INTERVAL" in block_upper:
            good.append((start, end, block))

    if not good:
        return None

    # remove smallest matching wrapper
    good.sort(key=lambda x: x[1] - x[0])
    return good[0]

changed_any = False

for path in files:
    if not path.exists():
        continue

    text = path.read_text(encoding="utf-8")
    upper = text.upper()

    if not any(m.upper() in upper for m in markers):
        continue

    print(f"Found block marker in: {path}")

    marker_index = -1
    for m in markers:
        marker_index = upper.find(m.upper())
        if marker_index != -1:
            break

    block = None
    for tag in ["div", "group", "section"]:
        block = find_matching_block(text, marker_index, tag)
        if block:
            print(f"Removing <{tag}> block")
            break

    if not block:
        raise SystemExit(f"Could not safely locate wrapper block in {path}")

    start, end, _ = block
    new_text = text[:start] + "\n" + text[end:]

    # Validate XML before saving
    ET.fromstring(new_text)

    path.write_text(new_text, encoding="utf-8")
    changed_any = True
    print(f"Updated: {path}")

if not changed_any:
    print("No System Polling block found.")
