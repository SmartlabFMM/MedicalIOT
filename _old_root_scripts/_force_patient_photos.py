from pathlib import Path
import re
import xml.etree.ElementTree as ET

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\patient_views.xml")
xml = p.read_text(encoding="utf-8")

old = r'''<t t-if="record.image_128.raw_value">
                                <img class="mediot_patient_avatar_force"
                                     t-att-src="kanban_image('med.patient', 'image_128', record.id.raw_value)"
                                     alt="Patient"/>
                            </t>
                            <t t-else="">
                                <div class="mediot_patient_avatar_fallback_force">
                                    <t t-esc="record.name.value ? record.name.value[0] : '?'"/>
                                </div>
                            </t>'''

new = r'''<img class="mediot_patient_avatar_force"
                                 t-att-src="'/web/image/med.patient/' + record.id.raw_value + '/image_128'"
                                 alt="Patient"/>'''

if old in xml:
    xml = xml.replace(old, new, 1)
else:
    xml = re.sub(
        r'<t t-if="record\.image_128\.raw_value">[\s\S]*?<t t-else="">[\s\S]*?</t>',
        new,
        xml,
        count=1
    )

ET.fromstring(xml)
p.write_text(xml, encoding="utf-8")

print("Patient photos forced")
