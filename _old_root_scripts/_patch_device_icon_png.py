from pathlib import Path
import re
import xml.etree.ElementTree as ET

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\settings_views.xml")
xml = p.read_text(encoding="utf-8")

img = '<img src="/med_iot_command_center/static/description/s.png" alt="Device" style="width:72px;height:72px;object-fit:contain;"/>'

# replace the big ?? inside the device circle
xml = re.sub(
    r'(<div[^>]*border-radius:50%[^>]*>)[\s\S]*?(\s*</div>\s*<div[^>]*>\s*Device\s*</div>)',
    r'\1' + img + r'\2',
    xml,
    count=1
)

ET.fromstring(xml)
p.write_text(xml, encoding="utf-8")

print("Device icon replaced with s.png")
