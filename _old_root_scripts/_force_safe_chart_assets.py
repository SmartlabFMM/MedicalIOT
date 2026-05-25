from pathlib import Path
import ast
import pprint

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\__manifest__.py")

txt = p.read_text(encoding="utf-8")
data = ast.literal_eval(txt)

assets = data.setdefault("assets", {})

safe_js = "med_iot_command_center/static/src/js/patient_vital_charts_safe.js"
broken_js = "med_iot_command_center/static/src/js/patient_vital_charts.js"
patient_css = "med_iot_command_center/static/src/css/patient.css"

for bundle in ["web.assets_backend", "web.assets_web"]:
    items = assets.setdefault(bundle, [])

    # remove broken JS and duplicate safe JS
    items = [x for x in items if x not in [broken_js, safe_js]]

    # ensure patient css exists
    if patient_css not in items:
        items.append(patient_css)

    # put safe JS just after patient.css
    idx = items.index(patient_css) + 1
    items.insert(idx, safe_js)

    assets[bundle] = items

new_txt = "# -*- coding: utf-8 -*-\n" + pprint.pformat(data, width=120, sort_dicts=False) + "\n"
p.write_text(new_txt, encoding="utf-8")

print("Manifest fixed: safe JS added to web.assets_backend and web.assets_web")