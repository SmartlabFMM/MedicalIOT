from pathlib import Path
import re
import xml.etree.ElementTree as ET

xml_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\patient_views.xml")
css_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\css\patient.css")

xml = xml_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")

# Add class to any button/link containing Download
def add_small_class(match):
    tag = match.group(1)
    rest = match.group(2)

    if 'mediot-download-sm' in tag:
        return tag + rest

    if 'class="' in tag:
        tag = re.sub(r'class="([^"]*)"', r'class="\1 mediot-download-sm"', tag, count=1)
    else:
        tag = tag[:-1] + ' class="mediot-download-sm">'

    return tag + rest

xml = re.sub(
    r'(<(?:button|a)\b[^>]*>)([\s\S]*?Download[\s\S]*?</(?:button|a)>)',
    add_small_class,
    xml,
    flags=re.I
)

ET.fromstring(xml)
xml_path.write_text(xml, encoding="utf-8")

if "SMALL DOWNLOAD BUTTON FIX" not in css:
    css += r'''

/* SMALL DOWNLOAD BUTTON FIX */
.mediot-download-sm {
    padding: 6px 12px !important;
    min-height: 32px !important;
    height: 32px !important;
    font-size: 12px !important;
    line-height: 1 !important;
    border-radius: 7px !important;
    width: auto !important;
    max-width: 110px !important;
}

.mediot-download-sm i,
.mediot-download-sm .fa {
    font-size: 11px !important;
    margin-right: 5px !important;
}
'''
    css_path.write_text(css, encoding="utf-8")

print("Download button kept, made smaller")
