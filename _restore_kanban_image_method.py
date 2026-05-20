from pathlib import Path
import re
import xml.etree.ElementTree as ET

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\patient_views.xml")
xml = p.read_text(encoding="utf-8")

# Replace forced /web/image URL with Odoo kanban_image helper
xml = re.sub(
    r'<img class="mediot_patient_avatar_force"\s+t-att-src="[^"]*"\s+alt="Patient"\s*/>',
    '''<t t-if="record.image_128.raw_value">
                                <img class="mediot_patient_avatar_force"
                                     t-att-src="kanban_image('med.patient', 'image_128', record.id.raw_value)"
                                     alt="Patient"/>
                            </t>
                            <t t-else="">
                                <div class="mediot_patient_avatar_fallback_force">
                                    <t t-esc="record.name.value ? record.name.value[0] : '?'"/>
                                </div>
                            </t>''',
    xml,
    count=1,
    flags=re.S
)

ET.fromstring(xml)
p.write_text(xml, encoding="utf-8")
print("Restored kanban_image avatar method")
