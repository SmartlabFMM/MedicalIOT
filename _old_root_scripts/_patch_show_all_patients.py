from pathlib import Path
import re

js_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\js\dashboard.js")
xml_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\xml\dashboard.xml")
css_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\css\dashboard.css")

js = js_path.read_text(encoding="utf-8")
xml = xml_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")

js = re.sub(r"patients\.slice\(\s*0\s*,\s*\d+\s*\)", "patients", js)
xml = re.sub(r"state\.live\.slice\(\s*0\s*,\s*\d+\s*\)", "state.live", xml)

start = js.find('"med.patient"')
if start != -1:
    end = js.find(');', start)
    if end != -1:
        block = js[start:end]
        block2 = re.sub(r",?\s*limit\s*:\s*\d+\s*,?", "", block)
        js = js[:start] + block2 + js[end:]

if "SHOW ALL PATIENTS TABLE FIX" not in css:
    css += r'''

/* SHOW ALL PATIENTS TABLE FIX */
.lpm_wrap,
.lpm_table,
.lpm_table tbody {
    max-height: none !important;
    overflow: visible !important;
}
'''

js_path.write_text(js, encoding="utf-8")
xml_path.write_text(xml, encoding="utf-8")
css_path.write_text(css, encoding="utf-8")

print("Show all patients patch applied")
