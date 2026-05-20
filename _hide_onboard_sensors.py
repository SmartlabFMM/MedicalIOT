from pathlib import Path
import re
import xml.etree.ElementTree as ET

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\settings_views.xml")
xml = p.read_text(encoding="utf-8")

idx = xml.find("ONBOARD SENSORS")
if idx == -1:
    raise SystemExit("ONBOARD SENSORS not found in settings_views.xml")

# Find nearest outer card before ONBOARD SENSORS
start = xml.rfind('<div style="background:#fff;border:1px solid #dde0f5;border-radius:', 0, idx)
if start == -1:
    raise SystemExit("Could not find Onboard Sensors card start")

tag_end = xml.find(">", start)
if tag_end == -1:
    raise SystemExit("Could not find opening tag end")

open_tag = xml[start:tag_end+1]

if "display:none" not in open_tag:
    if 'style="' in open_tag:
        new_open_tag = open_tag.replace('style="', 'style="display:none !important;', 1)
    else:
        new_open_tag = open_tag[:-1] + ' style="display:none !important;">'
    xml = xml[:start] + new_open_tag + xml[tag_end+1:]

ET.fromstring(xml)
p.write_text(xml, encoding="utf-8")

print("ONBOARD SENSORS card hidden")
