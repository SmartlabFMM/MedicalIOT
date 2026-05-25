from pathlib import Path
import re

base = Path(r"D:\odoo-19\custom_addons\med_iot_command_center")
manifest = base / "__manifest__.py"
vital = base / "models" / "vital_reading.py"

# Manifest assets
txt = manifest.read_text(encoding="utf-8")

assets_to_add = [
    '"med_iot_command_center/static/src/js/patient_vital_charts.js",',
    '"med_iot_command_center/static/src/css/patient.css",',
]

if "patient_vital_charts.js" not in txt:
    txt = txt.replace(
        '"med_iot_command_center/static/src/css/patient.css",',
        '"med_iot_command_center/static/src/css/patient.css",\n            "med_iot_command_center/static/src/js/patient_vital_charts.js",'
    )

manifest.write_text(txt, encoding="utf-8")
print("Manifest patched")

# Full alert logic
vt = vital.read_text(encoding="utf-8")

new_method = r'''    def _evaluate_thresholds_and_create_alerts(self):
        """Create alerts for SpO2, ECG/heart-rate and temperature using settings thresholds."""
        settings = self.env["med.settings"].sudo().get_settings()
        Alert = self.env["med.alert"].sudo()

        for r in self:
            if not r.patient_id:
                continue

            checks = []

            # SpO2
            if r.spo2:
                if r.spo2 <= settings.spo2_critical_min:
                    checks.append(("spo2", "critical", f"Critical SpO2: {r.spo2}%"))
                elif r.spo2 <= settings.spo2_warning_min:
                    checks.append(("spo2", "warning", f"Low SpO2: {r.spo2}%"))

            # Heart Rate / ECG
            if r.ecg_bpm:
                if r.ecg_bpm <= settings.hr_critical_min:
                    checks.append(("ecg", "critical", f"Critical heart rate low: {r.ecg_bpm} bpm"))
                elif r.ecg_bpm >= settings.hr_critical_max:
                    checks.append(("ecg", "critical", f"Critical heart rate high: {r.ecg_bpm} bpm"))
                elif r.ecg_bpm <= settings.hr_warning_min:
                    checks.append(("ecg", "warning", f"Heart rate low: {r.ecg_bpm} bpm"))
                elif r.ecg_bpm >= settings.hr_warning_max:
                    checks.append(("ecg", "warning", f"Heart rate high: {r.ecg_bpm} bpm"))

            # Temperature
            if r.temp_c:
                if r.temp_c <= settings.temp_critical_min:
                    checks.append(("temp", "critical", f"Critical low temperature: {r.temp_c}°C"))
                elif r.temp_c >= settings.temp_critical_max:
                    checks.append(("temp", "critical", f"Critical high temperature: {r.temp_c}°C"))
                elif r.temp_c <= settings.temp_warning_min:
                    checks.append(("temp", "warning", f"Low temperature warning: {r.temp_c}°C"))
                elif r.temp_c >= settings.temp_warning_max:
                    checks.append(("temp", "warning", f"High temperature warning: {r.temp_c}°C"))

            worst = False

            for alert_type, severity, msg in checks:
                exists = Alert.search_count([
                    ("patient_id", "=", r.patient_id.id),
                    ("reading_id", "=", r.id),
                    ("alert_type", "=", alert_type),
                    ("severity", "=", severity),
                ])

                if not exists:
                    Alert.create({
                        "patient_id": r.patient_id.id,
                        "reading_id": r.id,
                        "alert_type": alert_type,
                        "severity": severity,
                        "message": msg,
                        "state": "new",
                    })

                if severity == "critical":
                    worst = "critical"
                elif severity == "warning" and worst != "critical":
                    worst = "warning"

            if worst:
                r.patient_id.sudo().write({"status": worst})
            elif r.patient_id.status != "critical":
                r.patient_id.sudo().write({"status": "stable"})
'''

pattern = r'    def _evaluate_thresholds_and_create_alerts\(self\):[\s\S]*?(?=\n    def |\Z)'
vt2, n = re.subn(pattern, new_method, vt, count=1)

if n == 0:
    raise SystemExit("Could not find _evaluate_thresholds_and_create_alerts")

vital.write_text(vt2, encoding="utf-8")
print("Alert logic patched")