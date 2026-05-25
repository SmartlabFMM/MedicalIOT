# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


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

# HISTORY_STATUS_VERIFY_PREDICT_SAFE_START
class MedVitalReadingHistoryStatusSafe(models.Model):
    _inherit = "med.vital.reading"

    history_status = fields.Selection(
        [
            ("normal", "Normal"),
            ("warning", "Warning"),
            ("critical", "Critical"),
        ],
        string="Status",
        compute="_compute_history_status_safe",
        store=True,
    )

    verification_state = fields.Selection(
        [
            ("not_verified", "Not Verified"),
            ("verified", "Verified"),
        ],
        string="Verification",
        default="not_verified",
        required=True,
        copy=False,
    )

    @api.depends("spo2", "ecg_bpm", "temp_c")
    def _compute_history_status_safe(self):
        for rec in self:
            status = "normal"

            if (
                (rec.spo2 and rec.spo2 < 90)
                or (rec.ecg_bpm and rec.ecg_bpm > 120)
                or (rec.temp_c and rec.temp_c > 38.5)
            ):
                status = "critical"
            elif (
                (rec.spo2 and rec.spo2 < 94)
                or (rec.ecg_bpm and rec.ecg_bpm > 100)
                or (rec.temp_c and rec.temp_c > 37.5)
            ):
                status = "warning"

            rec.history_status = status

    def action_verify_reading(self):
        self.write({"verification_state": "verified"})
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Verification"),
                "message": _("Reading verified successfully."),
                "type": "success",
                "sticky": False,
            },
        }

    def action_predict_reading(self):
        self.ensure_one()

        if not self.patient_id:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Predict"),
                    "message": _("No patient linked to this reading."),
                    "type": "warning",
                    "sticky": False,
                },
            }

        view = self.env["ir.ui.view"].sudo().search([
            ("name", "=", "med.patient.ai.choice.popup.form"),
            ("model", "=", "med.patient"),
        ], limit=1)

        # Clear previous CVD prediction when opening the popup
        self.patient_id.sudo().write({
            "cvd_risk": "unknown",
            "cvd_probability": 0.0,
            "cvd_alert": False,
            "cvd_message": False,
            "cvd_last_checked": False,
            "heart_risk": "unknown",
            "heart_probability": 0.0,
            "heart_alert": False,
            "heart_message": False,
            "heart_last_checked": False,
        })

        return {
            "type": "ir.actions.act_window",
            "name": _("Predictive AI - %s") % self.patient_id.display_name,
            "res_model": "med.patient",
            "res_id": self.patient_id.id,
            "view_mode": "form",
            "views": [(view.id if view else False, "form")],
            "target": "new",
            "context": dict(self.env.context or {}),
        }

# HISTORY_STATUS_VERIFY_PREDICT_SAFE_END

