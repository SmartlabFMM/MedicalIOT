from pathlib import Path
import re

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\models\settings.py")
txt = p.read_text(encoding="utf-8")

pattern = r'(device_id\s*=\s*fields\.Many2one\(\s*"med\.device",[\s\S]*?compute="_compute_embedded_device",)([\s\S]*?\))'

def patch(m):
    block = m.group(0)
    if "store=True" in block:
        return block
    return block.replace('compute="_compute_embedded_device",', 'compute="_compute_embedded_device",\n        store=True,')

txt2 = re.sub(pattern, patch, txt, count=1)

if txt2 == txt:
    raise SystemExit("device_id block not patched")

p.write_text(txt2, encoding="utf-8")
print("device_id patched with store=True")
