from pathlib import Path
import re
import xml.etree.ElementTree as ET

xml_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\patient_views.xml")
css_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\css\patient.css")

xml = xml_path.read_text(encoding="utf-8")

spo2_idx = xml.find(">SpO2<")
hr_idx = xml.find(">Heart Rate<")
temp_idx = xml.find(">Temperature<")

if spo2_idx == -1 or hr_idx == -1 or temp_idx == -1:
    raise SystemExit("Could not find SpO2 / Heart Rate / Temperature labels in patient_views.xml")

# Find the parent grid containing the 3 old metric cards
start = xml.rfind('<div style="display:grid', 0, spo2_idx)
if start == -1:
    raise SystemExit("Could not find parent metric grid before SpO2")

# Find matching closing div for that grid
tag_re = re.compile(r'<(/?)div\b[^>]*>', re.I)
depth = 0
end = None

for m in tag_re.finditer(xml, start):
    if m.group(1) == "":
        depth += 1
    else:
        depth -= 1
        if depth == 0:
            end = m.end()
            break

if end is None:
    raise SystemExit("Could not find end of metric grid")

new_grid = r'''
<div class="mediot-real-vitals-grid">

    <div class="mediot-real-chart-card mediot-spo2-card">
        <div class="mediot-real-chart-head">
            <div class="mediot-real-chart-icon">💧</div>
            <div class="mediot-real-chart-title">SpO2</div>
            <div class="mediot-real-chart-current">
                curr. <field name="latest_spo2" nolabel="1" readonly="1" class="mediot-inline-field"/>%
            </div>
        </div>

        <div class="mediot-real-chart-value">
            <field name="latest_spo2" nolabel="1" readonly="1" class="mediot-main-field"/>
            <span>%</span>
        </div>

        <svg class="mediot-real-chart-svg" viewBox="0 0 350 120" preserveAspectRatio="none">
            <line x1="35" y1="22" x2="335" y2="22" class="mediot-real-grid"/>
            <line x1="35" y1="58" x2="335" y2="58" class="mediot-real-grid"/>
            <line x1="35" y1="94" x2="335" y2="94" class="mediot-real-grid"/>

            <text x="2" y="25" class="mediot-real-axis">100%</text>
            <text x="2" y="61" class="mediot-real-axis">95%</text>
            <text x="2" y="97" class="mediot-real-axis">90%</text>

            <path d="M35 68 C65 66, 78 54, 98 64 C118 74, 135 57, 158 61 C185 64, 200 52, 224 57 C248 62, 260 76, 282 66 C300 58, 318 62, 330 60 L330 104 L35 104 Z" class="mediot-spo2-fill"/>
            <path d="M35 68 C65 66, 78 54, 98 64 C118 74, 135 57, 158 61 C185 64, 200 52, 224 57 C248 62, 260 76, 282 66 C300 58, 318 62, 330 60" class="mediot-spo2-line"/>
            <circle cx="330" cy="60" r="4" class="mediot-spo2-dot"/>

            <text x="45" y="116" class="mediot-real-axis">00h</text>
            <text x="125" y="116" class="mediot-real-axis">06h</text>
            <text x="210" y="116" class="mediot-real-axis">12h</text>
            <text x="292" y="116" class="mediot-real-axis">18h</text>
        </svg>
    </div>

    <div class="mediot-real-chart-card mediot-hr-card">
        <div class="mediot-real-chart-head">
            <div class="mediot-real-chart-icon">💚</div>
            <div class="mediot-real-chart-title">Heart Rate</div>
            <div class="mediot-real-chart-current">
                curr. <field name="latest_ecg_bpm" nolabel="1" readonly="1" class="mediot-inline-field"/> bpm
            </div>
        </div>

        <div class="mediot-real-chart-value">
            <field name="latest_ecg_bpm" nolabel="1" readonly="1" class="mediot-main-field"/>
            <span>bpm</span>
        </div>

        <svg class="mediot-real-chart-svg" viewBox="0 0 350 120" preserveAspectRatio="none">
            <line x1="35" y1="22" x2="335" y2="22" class="mediot-real-grid"/>
            <line x1="35" y1="58" x2="335" y2="58" class="mediot-real-grid"/>
            <line x1="35" y1="94" x2="335" y2="94" class="mediot-real-grid"/>

            <text x="2" y="25" class="mediot-real-axis">100</text>
            <text x="2" y="61" class="mediot-real-axis">80</text>
            <text x="2" y="97" class="mediot-real-axis">60</text>

            <path d="M35 80 C65 79, 75 78, 88 68 C103 55, 125 72, 138 64 C150 56, 151 35, 174 42 C195 50, 205 62, 225 58 C245 54, 250 72, 272 73 C295 74, 305 61, 330 65 L330 104 L35 104 Z" class="mediot-hr-fill"/>
            <path d="M35 80 C65 79, 75 78, 88 68 C103 55, 125 72, 138 64 C150 56, 151 35, 174 42 C195 50, 205 62, 225 58 C245 54, 250 72, 272 73 C295 74, 305 61, 330 65" class="mediot-hr-line"/>
            <circle cx="330" cy="65" r="4" class="mediot-hr-dot"/>

            <text x="45" y="116" class="mediot-real-axis">00h</text>
            <text x="125" y="116" class="mediot-real-axis">06h</text>
            <text x="210" y="116" class="mediot-real-axis">12h</text>
            <text x="292" y="116" class="mediot-real-axis">18h</text>
        </svg>
    </div>

    <div class="mediot-real-chart-card mediot-temp-card">
        <div class="mediot-real-chart-head">
            <div class="mediot-real-chart-icon">🌡️</div>
            <div class="mediot-real-chart-title">Temperature</div>
            <div class="mediot-real-chart-current">
                curr. <field name="latest_temp" nolabel="1" readonly="1" class="mediot-inline-field"/> °C
            </div>
        </div>

        <div class="mediot-real-chart-value">
            <field name="latest_temp" nolabel="1" readonly="1" class="mediot-main-field"/>
            <span>°C</span>
        </div>

        <svg class="mediot-real-chart-svg" viewBox="0 0 350 120" preserveAspectRatio="none">
            <line x1="35" y1="22" x2="335" y2="22" class="mediot-real-grid"/>
            <line x1="35" y1="58" x2="335" y2="58" class="mediot-real-grid"/>
            <line x1="35" y1="94" x2="335" y2="94" class="mediot-real-grid"/>

            <text x="2" y="25" class="mediot-real-axis">38.0</text>
            <text x="2" y="61" class="mediot-real-axis">37.0</text>
            <text x="2" y="97" class="mediot-real-axis">36.0</text>

            <path d="M35 62 C52 55, 62 68, 78 60 C94 51, 110 62, 132 64 C152 66, 164 64, 180 62 C196 60, 200 47, 220 50 C240 53, 250 70, 274 68 C294 66, 305 60, 330 64 L330 104 L35 104 Z" class="mediot-temp-fill"/>
            <path d="M35 62 C52 55, 62 68, 78 60 C94 51, 110 62, 132 64 C152 66, 164 64, 180 62 C196 60, 200 47, 220 50 C240 53, 250 70, 274 68 C294 66, 305 60, 330 64" class="mediot-temp-line"/>
            <circle cx="330" cy="64" r="4" class="mediot-temp-dot"/>

            <text x="45" y="116" class="mediot-real-axis">00h</text>
            <text x="125" y="116" class="mediot-real-axis">06h</text>
            <text x="210" y="116" class="mediot-real-axis">12h</text>
            <text x="292" y="116" class="mediot-real-axis">18h</text>
        </svg>
    </div>

</div>
'''

xml = xml[:start] + new_grid + xml[end:]

ET.fromstring(xml)
xml_path.write_text(xml, encoding="utf-8")

css = css_path.read_text(encoding="utf-8")

if "REAL XML CURVE VITAL CARDS" not in css:
    css += r'''

/* REAL XML CURVE VITAL CARDS */
.mediot-real-vitals-grid {
    display: grid !important;
    grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
    gap: 16px !important;
    margin-bottom: 20px !important;
}

.mediot-real-chart-card {
    background: #fff !important;
    border: 1px solid #dfe6f2 !important;
    border-radius: 14px !important;
    padding: 16px 16px 10px !important;
    height: 190px !important;
    min-height: 190px !important;
    overflow: hidden !important;
    box-shadow: 0 1px 0 rgba(15, 23, 42, 0.02) !important;
}

.mediot-real-chart-head {
    display: grid !important;
    grid-template-columns: 40px 1fr auto !important;
    gap: 10px !important;
    align-items: center !important;
    margin-bottom: 3px !important;
}

.mediot-real-chart-icon {
    width: 38px !important;
    height: 38px !important;
    border-radius: 11px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 18px !important;
}

.mediot-spo2-card .mediot-real-chart-icon { background:#eaf2ff !important; }
.mediot-hr-card .mediot-real-chart-icon { background:#eafbea !important; }
.mediot-temp-card .mediot-real-chart-icon { background:#fff1e8 !important; }

.mediot-real-chart-title {
    font-size: 14px !important;
    font-weight: 800 !important;
    color: #42516b !important;
}

.mediot-real-chart-current {
    font-size: 12px !important;
    color: #7d8daa !important;
    white-space: nowrap !important;
}

.mediot-inline-field,
.mediot-main-field {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    display: inline !important;
}

.mediot-real-chart-value {
    font-size: 28px !important;
    font-weight: 900 !important;
    line-height: 1 !important;
    margin-left: 50px !important;
    margin-bottom: 4px !important;
}

.mediot-spo2-card .mediot-real-chart-value { color:#2563eb !important; }
.mediot-hr-card .mediot-real-chart-value { color:#22a047 !important; }
.mediot-temp-card .mediot-real-chart-value { color:#f97316 !important; }

.mediot-real-chart-value span {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #8da0bd !important;
    margin-left: 4px !important;
}

.mediot-real-chart-svg {
    width: 100% !important;
    height: 112px !important;
    display: block !important;
}

.mediot-real-grid {
    stroke: #d7dfec !important;
    stroke-width: 1 !important;
    stroke-dasharray: 5 5 !important;
}

.mediot-real-axis {
    fill: #6b7280 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
}

.mediot-spo2-line { fill:none !important; stroke:#2563eb !important; stroke-width:3 !important; stroke-linecap:round !important; stroke-linejoin:round !important; }
.mediot-spo2-fill { fill:#2563eb !important; opacity:.08 !important; }
.mediot-spo2-dot { fill:#2563eb !important; }

.mediot-hr-line { fill:none !important; stroke:#22a047 !important; stroke-width:3 !important; stroke-linecap:round !important; stroke-linejoin:round !important; }
.mediot-hr-fill { fill:#22a047 !important; opacity:.08 !important; }
.mediot-hr-dot { fill:#22a047 !important; }

.mediot-temp-line { fill:none !important; stroke:#f97316 !important; stroke-width:3 !important; stroke-linecap:round !important; stroke-linejoin:round !important; }
.mediot-temp-fill { fill:#f97316 !important; opacity:.08 !important; }
.mediot-temp-dot { fill:#f97316 !important; }

@media (max-width: 1200px) {
    .mediot-real-vitals-grid {
        grid-template-columns: 1fr !important;
    }
}
'''
    css_path.write_text(css, encoding="utf-8")

print("Metric cards replaced by real XML curve cards")
