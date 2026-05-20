from pathlib import Path
import re
import xml.etree.ElementTree as ET

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\patient_views.xml")
xml = p.read_text(encoding="utf-8")

# Replace avatar block completely: no initials fallback
pattern = r'<div class="mediot_patient_avatar_box_force">[\s\S]*?<t t-if="record\.pending_alert_count\.raw_value &gt; 0">'
replacement = '''<div class="mediot_patient_avatar_box_force">
                            <img class="mediot_patient_avatar_force"
                                 t-att-src="'/web/image/med.patient/' + record.id.raw_value + '/image_128'"
                                 alt="Patient"/>

                            <t t-if="record.pending_alert_count.raw_value &gt; 0">'''

xml2 = re.sub(pattern, replacement, xml, count=1)

if xml2 == xml:
    raise SystemExit("Avatar block not found / not replaced")

ET.fromstring(xml2)
p.write_text(xml2, encoding="utf-8")
print("Kanban avatar forced to real /web/image URL")
