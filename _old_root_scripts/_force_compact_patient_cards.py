from pathlib import Path
import re
import xml.etree.ElementTree as ET

xml_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\patient_views.xml")
css_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\css\patient.css")

xml = xml_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")

# Remove ugly Command Center wording only in patient view
xml = xml.replace("Command Center Patients", "Patients")
xml = xml.replace("Command Center\nPatients", "Patients")
xml = xml.replace("Command Center", "")

compact_kanban = r'''<record id="view_med_patient_kanban" model="ir.ui.view">
    <field name="name">med.patient.kanban</field>
    <field name="model">med.patient</field>
    <field name="arch" type="xml">
        <kanban records_draggable="0" class="mediot_patient_kanban_force">
            <field name="id"/>
            <field name="name"/>
            <field name="ref"/>
            <field name="room"/>
            <field name="status"/>
            <field name="latest_spo2"/>
            <field name="latest_ecg_bpm"/>
            <field name="latest_temp"/>
            <field name="image_128"/>
            <field name="pending_alert_count"/>
            <field name="age"/>
            <field name="gender"/>
            <field name="smoker"/>
            <field name="sporty"/>

            <templates>
                <t t-name="card">
                    <div class="mediot_patient_card_force">
                        <div class="mediot_patient_avatar_box_force">
                            <t t-if="record.image_128.raw_value">
                                <img class="mediot_patient_avatar_force"
                                     t-att-src="kanban_image('med.patient', 'image_128', record.id.raw_value)"
                                     alt="Patient"/>
                            </t>
                            <t t-else="">
                                <div class="mediot_patient_avatar_fallback_force">
                                    <t t-esc="record.name.value ? record.name.value[0] : '?'"/>
                                </div>
                            </t>

                            <t t-if="record.pending_alert_count.raw_value &gt; 0">
                                <div class="mediot_patient_alert_force">
                                    <t t-esc="record.pending_alert_count.raw_value"/>
                                </div>
                            </t>
                        </div>

                        <div class="mediot_patient_body_force">
                            <div class="mediot_patient_top_force">
                                <div>
                                    <div class="mediot_patient_name_force">
                                        <t t-esc="record.name.value"/>
                                    </div>
                                    <div class="mediot_patient_meta_force">
                                        <t t-esc="record.gender.value"/> · Age <t t-esc="record.age.raw_value or '—'"/>
                                    </div>
                                </div>

                                <span t-att-class="'mediot_patient_status_force ' + (record.status.raw_value or 'stable')">
                                    <t t-esc="record.status.value"/>
                                </span>
                            </div>

                            <div class="mediot_patient_line_force">
                                <i class="fa fa-id-card-o"/>
                                <t t-esc="record.ref.value"/>
                            </div>

                            <div class="mediot_patient_line_force">
                                <i class="fa fa-bed"/>
                                <t t-esc="record.room.value or '—'"/>
                            </div>

                            <div class="mediot_patient_divider_force"/>

                            <div class="mediot_patient_vitals_force">
                                <div>
                                    <strong><t t-esc="record.latest_spo2.raw_value or '—'"/><t t-if="record.latest_spo2.raw_value">%</t></strong>
                                    <span>SpO2</span>
                                </div>
                                <div>
                                    <strong><t t-esc="record.latest_ecg_bpm.raw_value or '—'"/><t t-if="record.latest_ecg_bpm.raw_value"><small>bpm</small></t></strong>
                                    <span>HR</span>
                                </div>
                                <div>
                                    <strong><t t-esc="record.latest_temp.raw_value or '—'"/><t t-if="record.latest_temp.raw_value">°C</t></strong>
                                    <span>Temp</span>
                                </div>
                            </div>

                            <div class="mediot_patient_bottom_force">
                                <span class="mediot_patient_green_dot_force"></span>
                                <button name="action_print_medical_report"
                                        type="object"
                                        class="btn btn-primary mediot_patient_download_force">
                                    <i class="fa fa-download"/> Download
                                </button>
                            </div>
                        </div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>'''

# Replace every med.patient kanban record
pattern = r'<record\b[^>]*id="[^"]*patient[^"]*kanban[^"]*"[^>]*>[\s\S]*?</record>'
matches = list(re.finditer(pattern, xml, flags=re.I))

if not matches:
    raise SystemExit("No patient kanban record found")

# Replace first kanban record with forced one, remove extra duplicate patient kanban records if any
first = matches[0]
xml = xml[:first.start()] + compact_kanban + xml[first.end():]

# Validate XML
ET.fromstring(xml)
xml_path.write_text(xml, encoding="utf-8")

force_css = r'''

/* FORCE COMPACT PATIENT KANBAN */
.mediot_patient_kanban_force .o_kanban_record,
.o_kanban_view .o_kanban_record:has(.mediot_patient_card_force) {
    padding: 0 !important;
    margin: 8px !important;
    border: 1px solid #dce3ef !important;
    box-shadow: none !important;
    background: #fff !important;
    min-height: 245px !important;
}

.mediot_patient_card_force {
    display: flex !important;
    gap: 16px !important;
    min-height: 245px !important;
    padding: 24px 26px 18px !important;
    background: #fff !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

.mediot_patient_avatar_box_force {
    position: relative !important;
    width: 76px !important;
    min-width: 76px !important;
}

.mediot_patient_avatar_force,
.mediot_patient_avatar_fallback_force {
    width: 76px !important;
    height: 76px !important;
    border-radius: 50% !important;
    object-fit: cover !important;
    border: 3px solid #edf2f7 !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, .10) !important;
}

.mediot_patient_avatar_fallback_force {
    background: #7766b5 !important;
    color: #fff !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 30px !important;
    font-weight: 900 !important;
}

.mediot_patient_alert_force {
    position: absolute !important;
    top: -5px !important;
    right: -5px !important;
    width: 20px !important;
    height: 20px !important;
    border-radius: 50% !important;
    background: #ff4d4f !important;
    color: #fff !important;
    font-size: 12px !important;
    font-weight: 900 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    border: 2px solid #fff !important;
}

.mediot_patient_body_force {
    flex: 1 !important;
    min-width: 0 !important;
}

.mediot_patient_top_force {
    display: flex !important;
    justify-content: space-between !important;
    align-items: flex-start !important;
    gap: 12px !important;
}

.mediot_patient_name_force {
    font-size: 20px !important;
    font-weight: 900 !important;
    color: #061226 !important;
    margin-bottom: 5px !important;
}

.mediot_patient_meta_force,
.mediot_patient_line_force {
    color: #536783 !important;
    font-size: 15px !important;
    line-height: 1.65 !important;
}

.mediot_patient_line_force i {
    width: 17px !important;
    margin-right: 6px !important;
    color: #7f91ad !important;
}

.mediot_patient_status_force {
    border-radius: 16px !important;
    padding: 5px 12px !important;
    font-size: 13px !important;
    font-weight: 900 !important;
}

.mediot_patient_status_force.stable {
    background: #ecfdf5 !important;
    color: #00a85a !important;
}

.mediot_patient_status_force.critical {
    background: #fff1f2 !important;
    color: #ff3347 !important;
}

.mediot_patient_status_force.warning {
    background: #fff7ed !important;
    color: #f59e0b !important;
}

.mediot_patient_divider_force {
    height: 1px !important;
    background: #edf2f7 !important;
    margin: 9px 0 12px !important;
}

.mediot_patient_vitals_force {
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 10px !important;
}

.mediot_patient_vitals_force > div {
    background: #f8fafc !important;
    border-radius: 8px !important;
    padding: 9px 8px !important;
    text-align: center !important;
}

.mediot_patient_vitals_force strong {
    display: block !important;
    font-size: 17px !important;
    font-weight: 900 !important;
    color: #07152b !important;
    line-height: 1.1 !important;
}

.mediot_patient_vitals_force small {
    font-size: 10px !important;
    color: #8da0bd !important;
    margin-left: 1px !important;
}

.mediot_patient_vitals_force span {
    display: block !important;
    margin-top: 5px !important;
    font-size: 11px !important;
    color: #8da0bd !important;
    text-transform: uppercase !important;
    letter-spacing: .06em !important;
}

.mediot_patient_bottom_force {
    margin-top: 16px !important;
    padding-top: 12px !important;
    border-top: 1px solid #edf2f7 !important;
    display: flex !important;
    align-items: center !important;
    gap: 18px !important;
}

.mediot_patient_green_dot_force {
    width: 12px !important;
    height: 12px !important;
    border-radius: 50% !important;
    background: #12bd7a !important;
    display: inline-block !important;
}

.mediot_patient_download_force {
    padding: 6px 12px !important;
    height: 32px !important;
    min-height: 32px !important;
    border-radius: 6px !important;
    font-size: 12px !important;
    font-weight: 800 !important;
    line-height: 1 !important;
    width: auto !important;
    max-width: 110px !important;
}

.mediot_patient_download_force i {
    font-size: 11px !important;
    margin-right: 4px !important;
}
'''

# Remove old force block if exists then append fresh
css = re.sub(r'/\* FORCE COMPACT PATIENT KANBAN \*/[\s\S]*$', '', css).rstrip()
css += "\n\n" + force_css

css_path.write_text(css, encoding="utf-8")

print("FORCED compact patient cards applied")
