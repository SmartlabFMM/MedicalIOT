# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MedVitalReading(models.Model):
    _name = "med.vital.reading"
    _description = "Vital Reading"
    _order = "reading_at desc"

    patient_id = fields.Many2one("med.patient", required=True, ondelete="cascade", index=True)
    device_id = fields.Many2one("med.device", index=True)

    reading_at = fields.Datetime(default=fields.Datetime.now, required=True, index=True)

    temp_c = fields.Float(string="Temp (°C)")
    spo2 = fields.Float(string="SpO2 (%)")
    ecg_bpm = fields.Integer(string="ECG (BPM)")

    raw_payload = fields.Text(help="Optional: store raw MQTT/JSON payload")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        # Update patient latest values
        for r in records:
            r.patient_id.sudo().write({
                "latest_temp": r.temp_c,
                "latest_spo2": r.spo2,
                "latest_ecg_bpm": r.ecg_bpm,
                "latest_reading_at": r.reading_at,
            })

        # Placeholder: Evaluate thresholds and create alerts
        records._evaluate_thresholds_and_create_alerts()

        return records

    def _evaluate_thresholds_and_create_alerts(self):
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
