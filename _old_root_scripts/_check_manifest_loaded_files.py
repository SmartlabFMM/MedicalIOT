import ast
import pathlib
import sys
import xml.etree.ElementTree as ET

module = pathlib.Path(r"D:\odoo-19\custom_addons\med_iot_command_center")
manifest_path = module / "__manifest__.py"

manifest = ast.literal_eval(manifest_path.read_text(encoding="utf-8"))

loaded = []

for key in ("data", "demo", "qweb"):
    for item in manifest.get(key, []) or []:
        loaded.append(item)

assets = manifest.get("assets", {}) or {}
for bundle, items in assets.items():
    for item in items:
        if isinstance(item, str):
            loaded.append(item)

xml_files = [x for x in loaded if x.lower().endswith(".xml")]

print("\nManifest-loaded XML files:")
for x in xml_files:
    print(" -", x)

ok = True

print("\nXML parse result:")
for rel in xml_files:
    path = module / rel
    if not path.exists():
        print("FALSE - MISSING:", rel)
        ok = False
        continue

    try:
        ET.parse(path)
        print("TRUE  - XML OK:", rel)
    except Exception as e:
        print("FALSE - XML ERROR:", rel, "::", e)
        ok = False

print("\nImportant broken backup files from previous check should NOT be loaded:")
danger = [
    "med_iot_command_center/views/vital_reading_views.xml",
    "static/src/css/patient_BACKUP_before_alert_tiny_cards.xml",
    "static/src/xml/dashboard_BACKUP_before_apply_clean_filters.xml",
    "static/src/xml/dashboard_BACKUP_before_search_status_fix.xml",
    "static/src/xml/dashboard_BROKEN_before_input_fix.xml",
]

for rel in danger:
    normalized = rel.replace("\\", "/")
    loaded_normalized = [x.replace("\\", "/") for x in loaded]
    if normalized in loaded_normalized:
        print("FALSE - BROKEN FILE IS LOADED:", rel)
        ok = False
    else:
        print("TRUE  - Not loaded:", rel)

print("\n=== MANIFEST-ONLY RESULT ===")
if ok:
    print("TRUE  - SAFE FROM MANIFEST XML SIDE")
else:
    print("FALSE - DO NOT UPDATE YET")
    sys.exit(1)