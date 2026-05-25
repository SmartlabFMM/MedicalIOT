from pathlib import Path
import re
import xml.etree.ElementTree as ET

js_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\js\dashboard.js")
xml_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\xml\dashboard.xml")

js = js_path.read_text(encoding="utf-8")
xml = xml_path.read_text(encoding="utf-8")

# Fix report URL
js = re.sub(
    r'const url = `/report/pdf/[^`]+/\$\{patientId\}`;',
    'const url = `/report/pdf/med_iot_command_center.report_patient_medical_document/${patientId}?download=true`;',
    js,
    count=1
)

# Make All Status visible/match state.statusFilter = "all"
xml = xml.replace('<option value="">All Status</option>', '<option value="all">All Status</option>')

# Validate XML
ET.fromstring(xml)

js_path.write_text(js, encoding="utf-8")
xml_path.write_text(xml, encoding="utf-8")

print("PDF download + All Status patched")
