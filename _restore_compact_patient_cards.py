from pathlib import Path
import xml.etree.ElementTree as ET

xml_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\patient_views.xml")
css_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\css\patient.css")

xml = xml_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")

# Rename ugly title
xml = xml.replace("Command Center Patients", "Patients")
xml = xml.replace("Command Center\nPatients", "Patients")
xml = xml.replace("Command Center", "")

kanban = r'''<record id="view_med_patient_kanban" model="ir.ui.view">
    <field name="name">med.patient.kanban</field>
    <field name="model">med.patient</field>
    <field name="arch" type="xml">
        <kanban records_draggable="0">
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
                    <div class="mediot-patient-card-compact">

                        <div class="mediot-patient-avatar-wrap">
                            <t t-if="record.image_128.raw_value">
                                <img class="mediot-patient-avatar"
                                     t-att-src="'/web/image/med.patient/' + record.id.value + '/image_128'"
                                     alt="Patient"/>
                            </t>
                            <t t-else="">
                                <div class="mediot-patient-avatar-fallback">
                                    <t t-esc="record.name.value ? record.name.value[0].toUpperCase() : '?'"/>
                                </div>
                            </t>

                            <t t-if="record.pending_alert_count.raw_value > 0">
                                <div class="mediot-alert-dot">
                                    <t t-esc="record.pending_alert_count.raw_value"/>
                                </div>
                            </t>
                        </div>

                        <div class="mediot-patient-card-body">
                            <div class="mediot-card-top">
                                <div>
                                    <div class="mediot-patient-name">
                                        <t t-esc="record.name.value"/>
                                    </div>
                                    <div class="mediot-patient-meta">
                                        <t t-esc="record.gender.value"/> · Age <t t-esc="record.age.raw_value or '—'"/>
                                    </div>
                                </div>

                                <span t-att-class="'mediot-status-pill ' + (record.status.raw_value or 'stable')">
                                    <t t-esc="record.status.value"/>
                                </span>
                            </div>

                            <div class="mediot-patient-line">
                                <i class="fa fa-id-badge"/>
                                <t t-esc="record.ref.value"/>
                            </div>

                            <div class="mediot-patient-line">
                                <i class="fa fa-bed"/>
                                <t t-esc="record.room.value or '—'"/>
                            </div>

                            <div class="mediot-card-divider"/>

                            <div class="mediot-vitals-mini">
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

                            <div class="mediot-risk-tags">
                                <t t-if="record.smoker.raw_value">
                                    <span>Smoker</span>
                                </t>
                                <t t-if="record.sporty.raw_value">
                                    <span>Sporty</span>
                                </t>
                            </div>
                        </div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>'''

start = xml.find('<record id="view_med_patient_kanban"')
if start == -1:
    raise SystemExit("Kanban record not found")

end = xml.find('</record>', start)
if end == -1:
    raise SystemExit("Kanban record end not found")
end += len('</record>')

xml = xml[:start] + kanban + xml[end:]

# Validate XML
ET.fromstring(xml)
xml_path.write_text(xml, encoding="utf-8")

compact_css = r'''

/* RESTORED COMPACT PATIENT KANBAN */
.o_kanban_view .mediot-patient-card-compact {
    display: flex !important;
    gap: 16px !important;
    min-height: 210px !important;
    padding: 28px 28px 22px !important;
    background: #fff !important;
    border: 1px solid #dce3ef !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    position: relative !important;
}

.mediot-patient-avatar-wrap {
    position: relative !important;
    width: 76px !important;
    min-width: 76px !important;
}

.mediot-patient-avatar,
.mediot-patient-avatar-fallback {
    width: 76px !important;
    height: 76px !important;
    border-radius: 50% !important;
    object-fit: cover !important;
    border: 3px solid #edf2f7 !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, .08) !important;
}

.mediot-patient-avatar-fallback {
    background: #7766b5 !important;
    color: #fff !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 30px !important;
    font-weight: 900 !important;
}

.mediot-alert-dot {
    position: absolute !important;
    top: -4px !important;
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

.mediot-patient-card-body {
    flex: 1 !important;
    min-width: 0 !important;
}

.mediot-card-top {
    display: flex !important;
    justify-content: space-between !important;
    align-items: flex-start !important;
    gap: 14px !important;
}

.mediot-patient-name {
    font-size: 20px !important;
    font-weight: 900 !important;
    color: #061226 !important;
    margin-bottom: 6px !important;
}

.mediot-patient-meta,
.mediot-patient-line {
    color: #536783 !important;
    font-size: 15px !important;
    line-height: 1.7 !important;
}

.mediot-patient-line i {
    width: 17px !important;
    color: #7f91ad !important;
    margin-right: 6px !important;
}

.mediot-status-pill {
    border-radius: 16px !important;
    padding: 5px 12px !important;
    font-size: 13px !important;
    font-weight: 900 !important;
}

.mediot-status-pill.stable {
    background: #ecfdf5 !important;
    color: #00a85a !important;
}

.mediot-status-pill.critical {
    background: #fff1f2 !important;
    color: #ff3347 !important;
}

.mediot-status-pill.warning {
    background: #fff7ed !important;
    color: #f59e0b !important;
}

.mediot-card-divider {
    height: 1px !important;
    background: #edf2f7 !important;
    margin: 9px 0 12px !important;
}

.mediot-vitals-mini {
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 12px !important;
}

.mediot-vitals-mini > div {
    background: #f8fafc !important;
    border-radius: 8px !important;
    padding: 10px 8px !important;
    text-align: center !important;
}

.mediot-vitals-mini strong {
    display: block !important;
    font-size: 18px !important;
    font-weight: 900 !important;
    color: #07152b !important;
    line-height: 1.1 !important;
}

.mediot-vitals-mini small {
    font-size: 11px !important;
    color: #8da0bd !important;
    margin-left: 1px !important;
}

.mediot-vitals-mini span {
    display: block !important;
    margin-top: 5px !important;
    font-size: 12px !important;
    color: #8da0bd !important;
    text-transform: uppercase !important;
    letter-spacing: .06em !important;
}

.mediot-risk-tags {
    margin-top: 12px !important;
    display: flex !important;
    gap: 6px !important;
}

.mediot-risk-tags span {
    background: #fff7ed !important;
    color: #f97316 !important;
    border-radius: 12px !important;
    padding: 3px 8px !important;
    font-size: 12px !important;
    font-weight: 700 !important;
}

/* hide old/current download buttons if any survived */
.o_kanban_view button:has(.fa-download),
.o_kanban_view a:has(.fa-download),
.o_kanban_view .mediot-download-sm {
    display: none !important;
}
'''

if "RESTORED COMPACT PATIENT KANBAN" not in css:
    css += compact_css

css_path.write_text(css, encoding="utf-8")

print("Compact patient kanban restored")
