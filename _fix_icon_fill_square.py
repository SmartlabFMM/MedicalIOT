from pathlib import Path
import re

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\css\settings_sliders.css")
txt = p.read_text(encoding="utf-8")

new_block = """
.mediot-icon-box {
    width: 44px !important;
    height: 44px !important;
    min-width: 44px !important;
    min-height: 44px !important;
    border-radius: 12px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    overflow: hidden !important;
    padding: 0 !important;
    box-sizing: border-box !important;
}

.mediot-icon-box img {
    width: 100% !important;
    height: 100% !important;
    max-width: none !important;
    max-height: none !important;
    object-fit: contain !important;
    display: block !important;
    margin: 0 !important;
}
""".strip()

pattern = r"\.mediot-icon-box\s*\{.*?\}\s*\.mediot-icon-box img\s*\{.*?\}"
if re.search(pattern, txt, flags=re.S):
    txt = re.sub(pattern, new_block, txt, flags=re.S)
else:
    txt += "\n\n" + new_block + "\n"

p.write_text(txt, encoding="utf-8")
print("Icon fill CSS fixed")
