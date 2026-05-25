from pathlib import Path
import re
import xml.etree.ElementTree as ET

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\settings_views.xml")
xml = p.read_text(encoding="utf-8")

marker = "ONBOARD SENSORS"
idx = xml.find(marker)
if idx == -1:
    raise SystemExit("ONBOARD SENSORS block not found")

tag_re = re.compile(r"<(/?)div\b[^>]*?>", re.I)
stack = []
candidates = []

for m in tag_re.finditer(xml):
    if m.group(1) == "":
        stack.append(m)
    else:
        if stack:
            start = stack.pop()
            s, e = start.start(), m.end()
            if s <= idx <= e:
                block = xml[s:e]
                if marker in block and any(x in block for x in ["AD8232", "MAX30102", "DS18B20", "LCD 1602"]):
                    candidates.append((s, e, block))

if not candidates:
    raise SystemExit("Could not safely locate full Onboard Sensors wrapper")

# remove smallest full wrapper containing title + sensor cards
candidates.sort(key=lambda x: x[1] - x[0])
start, end, block = candidates[0]

new_xml = xml[:start] + "\n" + xml[end:]

ET.fromstring(new_xml)
p.write_text(new_xml, encoding="utf-8")

print("ONBOARD SENSORS block removed")
