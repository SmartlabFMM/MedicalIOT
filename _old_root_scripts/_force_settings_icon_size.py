from pathlib import Path
import re
import xml.etree.ElementTree as ET

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\settings_views.xml")
xml = p.read_text(encoding="utf-8")

# Make section icon boxes bigger
xml = xml.replace(
    'width:36px;height:36px;border-radius:8px;',
    'width:52px;height:52px;border-radius:12px;'
)

# Make images fill their icon box
xml = re.sub(
    r'style="width:26px;height:26px;object-fit:contain;"',
    'style="width:44px;height:44px;object-fit:contain;"',
    xml
)

ET.fromstring(xml)
p.write_text(xml, encoding="utf-8")

print("Settings icons forced bigger inline")
