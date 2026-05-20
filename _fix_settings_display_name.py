from pathlib import Path
import re

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\models\settings.py")
txt = p.read_text(encoding="utf-8")

# Add clean record name
if '_rec_name = "name"' not in txt:
    txt = re.sub(
        r'(class\s+MedSettings\(models\.Model\):\s*\n)',
        r'\1    _rec_name = "name"\n\n',
        txt,
        count=1
    )

# Add name field after class/_rec_name if missing
if 'name = fields.Char(' not in txt:
    txt = re.sub(
        r'(_rec_name = "name"\s*\n)',
        r'\1    name = fields.Char(default="Alert Threshold Settings")\n',
        txt,
        count=1
    )

p.write_text(txt, encoding="utf-8")
print("settings.py display name fixed")
