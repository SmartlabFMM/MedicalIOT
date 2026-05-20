from pathlib import Path
import re
import xml.etree.ElementTree as ET

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\settings_views.xml")
xml = p.read_text(encoding="utf-8")

labels = ["AD8232", "MAX30102", "DS18B20", "LCD 1602"]

def all_div_blocks(text):
    tag_re = re.compile(r"<(/?)div\b[^>]*?>", re.I)
    stack = []
    blocks = []

    for m in tag_re.finditer(text):
        if m.group(1) == "":
            stack.append(m)
        elif stack:
            start = stack.pop()
            blocks.append((start.start(), m.end(), text[start.start():m.end()]))

    return blocks

removed = 0

while True:
    blocks = all_div_blocks(xml)

    candidates = []
    for s, e, block in blocks:
        low = block.lower()
        has_title = "onboard sensors" in low
        has_all_sensors = all(x in block for x in labels)

        if has_title or has_all_sensors:
            candidates.append((s, e, block))

    if not candidates:
        break

    # remove smallest matching block first
    candidates.sort(key=lambda x: x[1] - x[0])
    s, e, block = candidates[0]
    xml = xml[:s] + "\n" + xml[e:]
    removed += 1

# Validate XML
ET.fromstring(xml)

p.write_text(xml, encoding="utf-8")
print(f"Removed {removed} onboard sensor blocks")
