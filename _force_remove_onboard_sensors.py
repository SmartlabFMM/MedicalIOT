from pathlib import Path
import xml.etree.ElementTree as ET

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\settings_views.xml")
xml = p.read_text(encoding="utf-8")

idx = xml.find("ONBOARD SENSORS")
if idx == -1:
    raise SystemExit("ONBOARD SENSORS not found")

# go back to the big white wrapper before ONBOARD SENSORS
start = xml.rfind('<div style="background:#fff;', 0, idx)
if start == -1:
    start = xml.rfind("<div", 0, idx)

# find LCD 1602 then close the containing wrapper
lcd = xml.find("LCD 1602", idx)
if lcd == -1:
    raise SystemExit("LCD 1602 not found")

# count divs from start until wrapper closes
pos = start
depth = 0
end = None

while pos < len(xml):
    next_open = xml.find("<div", pos)
    next_close = xml.find("</div>", pos)

    if next_open != -1 and next_open < next_close:
        depth += 1
        pos = next_open + 4
    elif next_close != -1:
        depth -= 1
        pos = next_close + len("</div>")
        if pos > lcd and depth == 0:
            end = pos
            break
    else:
        break

if end is None:
    raise SystemExit("Could not find end of ONBOARD SENSORS block")

new_xml = xml[:start] + "\n" + xml[end:]

ET.fromstring(new_xml)
p.write_text(new_xml, encoding="utf-8")

print("ONBOARD SENSORS fully removed")
