from pathlib import Path
import re

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\models\settings.py")
txt = p.read_text(encoding="utf-8")

# Add real field only if exact "name =" does not exist
if not re.search(r'^\s+name\s*=\s*fields\.Char\(', txt, re.M):
    txt = re.sub(
        r'(_rec_name\s*=\s*"name"\s*\n)',
        r'\1    name = fields.Char(string="Name", default="Alert Threshold Settings")\n',
        txt,
        count=1
    )

p.write_text(txt, encoding="utf-8")
print("Real name field added")
