from pathlib import Path
import re
import xml.etree.ElementTree as ET

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\settings_views.xml")
xml = p.read_text(encoding="utf-8")

# Restore small MEDIOT COMMAND CENTER label
xml = re.sub(
    r'<div style="font-size:[^"]*?;">MedIoT Command Center</div>',
    '<div style="font-size:.6rem;font-weight:700;text-transform:uppercase;color:rgba(255,255,255,.6);margin-bottom:4px;letter-spacing:.08em;">MedIoT Command Center</div>',
    xml,
    count=1
)

# Restore Alert Threshold Settings title
xml = re.sub(
    r'<div style="font-size:[^"]*?;">Alert Threshold Settings</div>',
    '<div style="font-size:1.2rem;font-weight:700;color:#fff;">Alert Threshold Settings</div>',
    xml,
    count=1
)

# Restore right text
xml = re.sub(
    r'<div style="font-size:[^"]*?;">Configure vital sign alert limits</div>',
    '<div style="font-size:.75rem;color:rgba(255,255,255,.7);">Configure vital sign alert limits</div>',
    xml,
    count=1
)

ET.fromstring(xml)
p.write_text(xml, encoding="utf-8")

print("Top banner restored only")
