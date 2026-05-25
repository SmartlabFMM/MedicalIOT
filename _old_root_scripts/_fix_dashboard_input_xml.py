from pathlib import Path
import re

xml_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\xml\dashboard.xml")
xml = xml_path.read_text(encoding="utf-8")

# Fix malformed: ... style="..."/ t-on-input="...">
xml = re.sub(
    r'(<input\b[^>]*?)\s*/\s+t-on-input="([^"]+)"\s*>',
    r'\1 t-on-input="\2"/>',
    xml,
    count=1
)

xml_path.write_text(xml, encoding="utf-8")
print("dashboard.xml input tag fixed")
