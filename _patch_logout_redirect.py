from pathlib import Path
import ast
import pprint

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\__manifest__.py")
txt = p.read_text(encoding="utf-8")
data = ast.literal_eval(txt)

assets = data.setdefault("assets", {})
logout_js = "med_iot_command_center/static/src/js/logout_redirect_home.js"

for bundle in ["web.assets_backend", "web.assets_web"]:
    items = assets.setdefault(bundle, [])
    items = [x for x in items if x != logout_js]
    items.append(logout_js)
    assets[bundle] = items

p.write_text(
    "# -*- coding: utf-8 -*-\n" + pprint.pformat(data, width=120, sort_dicts=False) + "\n",
    encoding="utf-8"
)

print("logout redirect asset added")