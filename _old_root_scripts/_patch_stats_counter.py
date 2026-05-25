from pathlib import Path

xml_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\auth_pages.xml")
text = xml_path.read_text(encoding="utf-8")

script_tag = '<script type="text/javascript" src="/med_iot_command_center/static/src/js/landing_stats_counter.js"></script>'

if script_tag not in text:
    text = text.replace("</template>", f"    {script_tag}\n</template>", 1)

xml_path.write_text(text, encoding="utf-8")
print("JS SCRIPT TAG READY")
