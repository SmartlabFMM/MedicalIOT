from pathlib import Path
import xml.etree.ElementTree as ET

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\settings_views.xml")
xml = p.read_text(encoding="utf-8")

marker = 'Dashboard auto-refresh interval'
idx = xml.find(marker)
if idx == -1:
    raise SystemExit("Polling marker not found")

start = xml.rfind('<div style="background:#fff;border:1px solid #dde0f5;border-radius:16px;padding:18px;">', 0, idx)
if start == -1:
    raise SystemExit("Polling card start not found")

end_marker = '<div data-mediot-device-section="1"'
end = xml.find(end_marker, idx)
if end == -1:
    raise SystemExit("Next device section not found")

new_xml = xml[:start] + xml[end:]

ET.fromstring(new_xml)
p.write_text(new_xml, encoding="utf-8")

print("Polling block removed from settings_views.xml")
