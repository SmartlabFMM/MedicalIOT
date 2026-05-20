from pathlib import Path
import ast
import pprint

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\__manifest__.py")
data = ast.literal_eval(p.read_text(encoding="utf-8"))

assets = data.setdefault("assets", {})

bad = {
    "med_iot_command_center/static/src/js/logout_redirect_home.js",
}
safe = "med_iot_command_center/static/src/js/logout_redirect_home_safe.js"

for bundle in ["web.assets_backend", "web.assets_web"]:
    items = assets.setdefault(bundle, [])
    items = [x for x in items if x not in bad and x != safe]
    items.append(safe)
    assets[bundle] = items

p.write_text(
    "# -*- coding: utf-8 -*-\n" + pprint.pformat(data, width=120, sort_dicts=False) + "\n",
    encoding="utf-8"
)

print("Safe logout redirect configured")