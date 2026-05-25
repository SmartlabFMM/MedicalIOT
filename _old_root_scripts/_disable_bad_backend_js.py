from pathlib import Path
import ast
import pprint

base = Path(r"D:\odoo-19\custom_addons\med_iot_command_center")
manifest = base / "__manifest__.py"

txt = manifest.read_text(encoding="utf-8")
data = ast.literal_eval(txt)

bad_assets = {
    "med_iot_command_center/static/src/js/logout_redirect_home.js",
    "med_iot_command_center/static/src/js/patient_vital_charts_safe.js",
    "med_iot_command_center/static/src/js/patient_vital_charts.js",
}

assets = data.setdefault("assets", {})
for bundle, items in list(assets.items()):
    if isinstance(items, list):
        assets[bundle] = [x for x in items if x not in bad_assets]

manifest.write_text(
    "# -*- coding: utf-8 -*-\n" + pprint.pformat(data, width=120, sort_dicts=False) + "\n",
    encoding="utf-8"
)

for rel in [
    "static/src/js/logout_redirect_home.js",
    "static/src/js/patient_vital_charts_safe.js",
    "static/src/js/patient_vital_charts.js",
]:
    p = base / rel
    if p.exists():
        disabled = p.with_suffix(p.suffix + ".disabled")
        if disabled.exists():
            disabled.unlink()
        p.rename(disabled)
        print("Disabled:", rel)

print("Manifest cleaned")