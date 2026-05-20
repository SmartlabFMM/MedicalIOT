from pathlib import Path
import re

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\__manifest__.py")
txt = p.read_text(encoding="utf-8")

# Remove old broken chart JS if still referenced
txt = re.sub(
    r'\s*["\']med_iot_command_center/static/src/js/patient_vital_charts\.js["\'],?\s*',
    '\n',
    txt
)

# Add safe JS after patient.css if missing
if "patient_vital_charts_safe.js" not in txt:
    txt = txt.replace(
        '"med_iot_command_center/static/src/css/patient.css",',
        '"med_iot_command_center/static/src/css/patient.css",\n            "med_iot_command_center/static/src/js/patient_vital_charts_safe.js",'
    )

p.write_text(txt, encoding="utf-8")
print("Manifest patched with safe chart JS")
