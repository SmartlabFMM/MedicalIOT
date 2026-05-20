# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

# CVD_AI_IMPORTS_START
import json
import urllib.request
import urllib.error
# CVD_AI_IMPORTS_END


class MedPatient(models.Model):
    _name = "med.patient"
    _description = "Patient"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    

    smoker = fields.Boolean(string="Smoker", default=False)
    sporty = fields.Boolean(string="Sporty", default=False)
    elderly = fields.Boolean(string="Elderly", default=False)
    prior_cardiac_event = fields.Boolean(string="Prior Cardiac Event", default=False)

    # CVD_AI_FIELDS_START
    cvd_height = fields.Integer(string="Height (cm)", default=170)
    cvd_weight = fields.Float(string="Weight (kg)", default=70.0)
    cvd_ap_hi = fields.Integer(string="Systolic BP", default=120)
    cvd_ap_lo = fields.Integer(string="Diastolic BP", default=80)
    cvd_cholesterol = fields.Selection(
        [("1", "Normal"), ("2", "Above Normal"), ("3", "High")],
        string="Cholesterol",
        default="1",
    )
    cvd_gluc = fields.Selection(
        [("1", "Normal"), ("2", "Above Normal"), ("3", "High")],
        string="Glucose",
        default="1",
    )
    cvd_alco = fields.Boolean(string="Alcohol Intake", default=False)
    cvd_active = fields.Boolean(string="Physically Active", default=True)

    cvd_risk = fields.Selection(
        [("unknown", "Unknown"), ("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        string="CVD Risk",
        default="unknown",
        readonly=True,
        tracking=True,
    )
    cvd_probability = fields.Float(string="CVD Probability (%)", readonly=True)
    cvd_alert = fields.Boolean(string="CVD Alert", readonly=True)
    cvd_message = fields.Char(string="CVD AI Message", readonly=True)
    cvd_last_checked = fields.Datetime(string="CVD Last Checked", readonly=True)
    # CVD_AI_FIELDS_END

    # ARRHYTHMIA_AI_FIELDS_START
    arrhythmia_ecg_input = fields.Selection(
        [
            ("N", "Normal"),
            ("S", "Supraventricular"),
            ("V", "Ventricular"),
            ("F", "Fusion"),
            ("Q", "Unknown"),
        ],
        string="ECG Class Input",
        default="N",
    )
    arrhythmia_ecg_level = fields.Float(string="ECG Level", default=0.0)
    arrhythmia_risk = fields.Selection(
        [("unknown", "Unknown"), ("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        string="Arrhythmia Risk",
        default="unknown",
        readonly=True,
        tracking=True,
    )
    arrhythmia_ecg_class = fields.Char(string="ECG AI Class", readonly=True)
    arrhythmia_confidence = fields.Float(string="Arrhythmia Confidence (%)", readonly=True)
    arrhythmia_alert = fields.Boolean(string="Arrhythmia Alert", readonly=True)
    arrhythmia_message = fields.Char(string="Arrhythmia AI Message", readonly=True)
    arrhythmia_last_checked = fields.Datetime(string="Arrhythmia Last Checked", readonly=True)
    # ARRHYTHMIA_AI_FIELDS_END
    image_128 = fields.Image(string="Photo", max_width=128, max_height=128)

    name = fields.Char(required=True, tracking=True)
    ref = fields.Char(string="Patient ID", readonly=True, copy=False, default="New", index=True)

    age = fields.Integer()
    gender = fields.Selection([("male", "Male"), ("female", "Female"), ("other", "Other")], default="other")
    room = fields.Char(help="Room/Bed e.g. ICU-01", tracking=True)

    assigned_doctor_id = fields.Many2one("res.users", string="Assigned Doctor", tracking=True)
    department = fields.Char()

    status = fields.Selection(
        [("stable", "Stable"), ("warning", "Warning"), ("critical", "Critical")],
        default="stable",
        tracking=True,
        index=True,
    )
    active = fields.Boolean(default=True)

    latest_temp = fields.Float(string="Temp (°C)", readonly=True)
    latest_spo2 = fields.Float(string="SpO2 (%)", readonly=True)
    latest_ecg_bpm = fields.Integer(string="ECG (BPM)", readonly=True)
    latest_reading_at = fields.Datetime(readonly=True)

    alert_ids = fields.One2many("med.alert", "patient_id", string="Alerts")
    pending_alert_count = fields.Integer(compute="_compute_pending_alert_count")

    @api.depends("alert_ids.state", "alert_ids.severity")
    def _compute_pending_alert_count(self):
        for rec in self:
            rec.pending_alert_count = len(rec.alert_ids.filtered(lambda a: a.state == "new"))

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("ref", "New") == "New":
                vals["ref"] = seq.next_by_code("med.patient") or _("New")
        return super().create(vals_list)

    @api.constrains("room", "active")
    def _check_unique_active_room(self):
        for rec in self.filtered(lambda r: r.room and r.active):
            dup = self.search_count([("id", "!=", rec.id), ("room", "=", rec.room), ("active", "=", True)])
            if dup:
                raise ValidationError(_("There is already an active patient assigned to room/bed: %s") % rec.room)
    # CVD_AI_METHODS_START
    def _get_cvd_payload(self):
        self.ensure_one()
        gender_value = 2 if self.gender == "male" else 1
        return {
            "patient_ref": self.ref or self.name or ("P-%s" % self.id),
            "age": int(self.age or 0),
            "gender": gender_value,
            "height": int(self.cvd_height or 170),
            "weight": float(self.cvd_weight or 70.0),
            "ap_hi": int(self.cvd_ap_hi or 120),
            "ap_lo": int(self.cvd_ap_lo or 80),
            "cholesterol": int(self.cvd_cholesterol or 1),
            "gluc": int(self.cvd_gluc or 1),
            "smoke": 1 if self.smoker else 0,
            "alco": 1 if self.cvd_alco else 0,
            "active": 1 if (self.cvd_active or self.sporty) else 0,
        }

    def action_compute_cvd_risk(self):
        Alert = self.env["med.alert"]

        for rec in self:
            payload = rec._get_cvd_payload()
            url = "http://localhost:8000/predict/cvd_risk"

            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    result = json.loads(response.read().decode("utf-8"))
            except Exception as exc:
                raise ValidationError(_("CVD AI service is not reachable. Start FastAPI on port 8000 first. Error: %s") % exc)

            probability = float(result.get("probability") or 0.0)

            if probability <= 1:
                probability = probability * 100

            risk = result.get("cvd_risk") or "unknown"
            risk = str(risk).lower()

            alert = bool(result.get("alert") or probability > 70 or risk in ("high", "critical"))
            message = result.get("message") or "Risk computed successfully"

            vals = {
                "cvd_risk": risk,
                "cvd_probability": probability,
                "cvd_alert": alert,
                "cvd_message": message,
                "cvd_last_checked": fields.Datetime.now(),
            }

            if alert and risk in ("high", "critical"):
                vals["status"] = "critical"
            elif risk == "medium" and rec.status != "critical":
                vals["status"] = "warning"

            rec.write(vals)

            if alert:
                severity = "critical" if risk in ("high", "critical") else "warning"
                alert_message = "%s Probability: %.1f%%" % (message, probability)

                existing = Alert.search([
                    ("patient_id", "=", rec.id),
                    ("alert_type", "=", "cvd"),
                    ("state", "!=", "resolved"),
                ], limit=1)

                if existing:
                    existing.write({
                        "severity": severity,
                        "message": alert_message,
                    })
                else:
                    Alert.create({
                        "patient_id": rec.id,
                        "alert_type": "cvd",
                        "severity": severity,
                        "message": alert_message,
                        "state": "new",
                    })

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("CVD AI Risk Computed"),
                "message": _("Cardiovascular risk was computed and saved."),
                "type": "success",
                "sticky": False,
            },
        }
    # CVD_AI_METHODS_END

    # ARRHYTHMIA_AI_METHODS_START
    def _get_arrhythmia_payload(self):
        self.ensure_one()
        gender_value = 1 if self.gender == "male" else 0

        return {
            "patient_id": self.ref or self.name or ("P-%s" % self.id),
            "spo2": float(self.latest_spo2 or 96.0),
            "temperature": float(self.latest_temp or 37.0),
            "heart_rate": int(self.latest_ecg_bpm or 80),
            "age": int(self.age or 0),
            "gender": gender_value,
            "smoker": bool(self.smoker),
            "sporty": bool(self.sporty),
            "ecg_class": self.arrhythmia_ecg_input or "N",
            "ecg_level": float(self.arrhythmia_ecg_level or 0.0),
        }

    def action_compute_arrhythmia_risk(self):
        Alert = self.env["med.alert"]

        for rec in self:
            payload = rec._get_arrhythmia_payload()
            url = "http://localhost:8000/predict/simple"

            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=15) as response:
                    result = json.loads(response.read().decode("utf-8"))
            except Exception as exc:
                raise ValidationError(_("Arrhythmia AI service is not reachable. Start FastAPI on port 8000 first. Error: %s") % exc)

            ecg = result.get("ecg") or {}
            assessment = result.get("assessment") or {}

            risk = str(assessment.get("final_risk") or assessment.get("base_risk") or "unknown").lower()
            if risk not in ("unknown", "low", "medium", "high", "critical"):
                risk = "unknown"

            confidence = float(ecg.get("confidence") or 0.0)
            ecg_class = str(ecg.get("class_name") or "Unknown")
            alert = bool(assessment.get("alert") or risk in ("high", "critical"))

            issues = assessment.get("issues") or []
            if isinstance(issues, list) and issues:
                message = "; ".join(str(x) for x in issues)
            else:
                message = "%s ECG pattern. Risk: %s." % (ecg_class, risk.title())

            vals = {
                "arrhythmia_risk": risk,
                "arrhythmia_ecg_class": ecg_class,
                "arrhythmia_confidence": confidence,
                "arrhythmia_alert": alert,
                "arrhythmia_message": message,
                "arrhythmia_last_checked": fields.Datetime.now(),
            }

            if alert and risk == "critical":
                vals["status"] = "critical"
            elif alert and risk in ("medium", "high"):
                vals["status"] = "warning"

            rec.write(vals)

            if alert:
                severity = "critical" if risk == "critical" else "warning"
                alert_message = "Arrhythmia AI: %s Confidence: %.1f%%" % (message, confidence)

                existing = Alert.search([
                    ("patient_id", "=", rec.id),
                    ("alert_type", "=", "ecg"),
                    ("state", "!=", "resolved"),
                ], limit=1)

                if existing:
                    existing.write({
                        "severity": severity,
                        "message": alert_message,
                        "state": "new",
                    })
                else:
                    Alert.create({
                        "patient_id": rec.id,
                        "alert_type": "ecg",
                        "severity": severity,
                        "message": alert_message,
                        "state": "new",
                    })

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Arrhythmia AI Computed"),
                "message": _("Arrhythmia risk was computed and saved."),
                "type": "success",
                "sticky": False,
            },
        }
    # ARRHYTHMIA_AI_METHODS_END
    def action_print_medical_report(self):
        self.ensure_one()

        report = self.env.ref(
            "med_iot_command_center.action_report_patient_medical",
            raise_if_not_found=False,
        )

        if report:
            return report.report_action(self)

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Report not found",
                "message": "The patient medical report action is missing.",
                "type": "warning",
                "sticky": False,
            },
        }









