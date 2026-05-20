from pathlib import Path

p = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\settings_views.xml")
xml = p.read_text(encoding="utf-8")

replacements = [
    # top banner
    ('font-size:.6rem;font-weight:700;text-transform:uppercase;color:rgba(255,255,255,.6);margin-bottom:4px;letter-spacing:.08em;',
     'font-size:.82rem;font-weight:700;text-transform:uppercase;color:rgba(255,255,255,.75);margin-bottom:4px;letter-spacing:.08em;'),
    ('font-size:1.2rem;font-weight:700;color:#fff;',
     'font-size:1.75rem;font-weight:800;color:#fff;'),
    ('font-size:.75rem;color:rgba(255,255,255,.7);',
     'font-size:1rem;color:rgba(255,255,255,.88);'),

    # section titles like Heart Rate (ECG)
    ('font-size:.62rem;font-weight:700;text-transform:uppercase;',
     'font-size:1rem;font-weight:800;text-transform:uppercase;'),

    # section subtitles like Normal range
    ('font-size:.7rem;color:#94a3b8;margin-top:2px;',
     'font-size:.98rem;color:#64748b;margin-top:4px;'),

    # small card labels Critical / Warning
    ('font-size:.58rem;text-transform:uppercase;',
     'font-size:.9rem;text-transform:uppercase;'),

    # field values
    ('font-size:1rem;font-weight:700;',
     'font-size:1.2rem;font-weight:800;'),

    # helper text
    ('font-size:.62rem;color:#94a3b8;margin-top:4px;',
     'font-size:.88rem;color:#64748b;margin-top:6px;'),
]

for old, new in replacements:
    xml = xml.replace(old, new)

p.write_text(xml, encoding="utf-8")
print("settings_views.xml updated: bigger text applied")
