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


    # HEART_DISEASE_AI_FIELDS_START
    heart_cp = fields.Selection(
        [("0", "Typical Angina"), ("1", "Atypical Angina"), ("2", "Non-anginal Pain"), ("3", "Asymptomatic")],
        string="Chest Pain Type",
        default="0",
    )
    heart_trestbps = fields.Integer(string="Resting Blood Pressure", default=120)
    heart_chol = fields.Integer(string="Cholesterol", default=200)
    heart_fbs = fields.Selection(
        [("0", "False"), ("1", "True")],
        string="Fasting Blood Sugar > 120 mg/dl",
        default="0",
    )
    heart_restecg = fields.Selection(
        [("0", "Normal"), ("1", "ST-T Abnormality"), ("2", "LV Hypertrophy")],
        string="Resting ECG",
        default="0",
    )
    heart_thalach = fields.Integer(string="Max Heart Rate", default=150)
    heart_exang = fields.Selection(
        [("0", "No"), ("1", "Yes")],
        string="Exercise Angina",
        default="0",
    )
    heart_oldpeak = fields.Float(string="Oldpeak", default=1.0)
    heart_slope = fields.Selection(
        [("0", "Upsloping"), ("1", "Flat"), ("2", "Downsloping")],
        string="Slope",
        default="1",
    )
    heart_ca = fields.Selection(
        [("0", "0"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4")],
        string="Major Vessels",
        default="0",
    )
    heart_thal = fields.Selection(
        [("0", "Unknown"), ("1", "Fixed Defect"), ("2", "Normal"), ("3", "Reversible Defect")],
        string="Thalassemia",
        default="2",
    )

    heart_prediction = fields.Integer(string="Heart Prediction", readonly=True)
    heart_risk = fields.Selection(
        [("unknown", "Unknown"), ("not_detected", "Not Detected"), ("detected", "Detected")],
        string="Heart Disease Risk",
        default="unknown",
        readonly=True,
    )
    heart_probability = fields.Float(string="Heart Disease Probability (%)", readonly=True)
    heart_alert = fields.Boolean(string="Heart Disease Alert", readonly=True)
    heart_message = fields.Char(string="Heart Disease AI Message", readonly=True)
    heart_last_checked = fields.Datetime(string="Heart Disease Last Checked", readonly=True)
    # HEART_DISEASE_AI_FIELDS_END

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

        view = self.env["ir.ui.view"].sudo().search([
            ("name", "=", "med.patient.cvd.predict.popup.form"),
            ("model", "=", "med.patient"),
        ], limit=1)

        return {
            "type": "ir.actions.act_window",
            "name": _("CVD AI Prediction - %s") % self.display_name,
            "res_model": "med.patient",
            "res_id": self.id,
            "view_mode": "form",
            "views": [(view.id if view else False, "form")],
            "target": "new",
            "context": dict(self.env.context or {}),
        }
    # CVD_AI_METHODS_END



    # AI_CHOICE_POPUP_METHODS_START
    def action_open_cvd_prediction_popup(self):
        self.ensure_one()
        self.sudo().write({
            "cvd_risk": "unknown",
            "cvd_probability": 0.0,
            "cvd_alert": False,
            "cvd_message": False,
            "cvd_last_checked": False,
        })
        view = self.env["ir.ui.view"].sudo().search([
            ("name", "=", "med.patient.cvd.predict.popup.form"),
            ("model", "=", "med.patient"),
        ], limit=1)
        return {
            "type": "ir.actions.act_window",
            "name": _("CVD AI Prediction - %s") % self.display_name,
            "res_model": "med.patient",
            "res_id": self.id,
            "view_mode": "form",
            "views": [(view.id if view else False, "form")],
            "target": "new",
            "context": dict(self.env.context or {}),
        }

    def action_open_heart_prediction_popup(self):
        self.ensure_one()
        self.sudo().write({
            "heart_risk": "unknown",
            "heart_probability": 0.0,
            "heart_alert": False,
            "heart_message": False,
            "heart_last_checked": False,
        })
        view = self.env["ir.ui.view"].sudo().search([
            ("name", "=", "med.patient.heart.predict.popup.form"),
            ("model", "=", "med.patient"),
        ], limit=1)
        return {
            "type": "ir.actions.act_window",
            "name": _("Heart Disease AI Prediction - %s") % self.display_name,
            "res_model": "med.patient",
            "res_id": self.id,
            "view_mode": "form",
            "views": [(view.id if view else False, "form")],
            "target": "new",
            "context": dict(self.env.context or {}),
        }
    # AI_CHOICE_POPUP_METHODS_END

    # HEART_DISEASE_AI_METHODS_START
    def _get_heart_disease_payload(self):
        self.ensure_one()
        sex_value = 1 if self.gender == "male" else 0
        return {
            "age": int(self.age or 0),
            "sex": int(sex_value),
            "cp": int(self.heart_cp or 0),
            "trestbps": int(self.heart_trestbps or 120),
            "chol": int(self.heart_chol or 200),
            "fbs": int(self.heart_fbs or 0),
            "restecg": int(self.heart_restecg or 0),
            "thalach": int(self.heart_thalach or 150),
            "exang": int(self.heart_exang or 0),
            "oldpeak": float(self.heart_oldpeak or 0.0),
            "slope": int(self.heart_slope or 1),
            "ca": int(self.heart_ca or 0),
            "thal": int(self.heart_thal or 2),
        }

    def action_compute_heart_disease(self):
        for rec in self:
            payload = rec._get_heart_disease_payload()
            url = "http://localhost:8000/predict/heart_disease"

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
                raise ValidationError(_("Heart Disease AI service is not reachable. Start FastAPI on port 8000 first. Error: %s") % exc)

            probability = float(result.get("probability") or 0.0)
            if probability <= 1:
                probability = probability * 100

            prediction = int(result.get("heart_prediction") or 0)
            heart_risk = "detected" if prediction == 1 else "not_detected"
            alert = bool(result.get("alert") or prediction == 1)

            message = result.get("message")
            if not message:
                message = "Heart disease signs detected based on clinical parameters." if prediction == 1 else "No major heart disease signs detected based on clinical parameters."

            rec.write({
                "heart_prediction": prediction,
                "heart_risk": heart_risk,
                "heart_probability": probability,
                "heart_alert": alert,
                "heart_message": message,
                "heart_last_checked": fields.Datetime.now(),
            })

        view = self.env["ir.ui.view"].sudo().search([
            ("name", "=", "med.patient.heart.predict.popup.form"),
            ("model", "=", "med.patient"),
        ], limit=1)

        return {
            "type": "ir.actions.act_window",
            "name": _("Heart Disease AI Prediction - %s") % self.display_name,
            "res_model": "med.patient",
            "res_id": self.id,
            "view_mode": "form",
            "views": [(view.id if view else False, "form")],
            "target": "new",
            "context": dict(self.env.context or {}),
        }
    # HEART_DISEASE_AI_METHODS_END

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












# PATIENT_PROFILE_VITAL_CURVES_SAFE_START
class MedPatientVitalCurvesSafe(models.Model):
    _inherit = "med.patient"

    spo2_chart_html = fields.Html(
        string="SpO2 Chart",
        compute="_compute_mediot_vital_curves_html_safe",
        sanitize=False,
    )
    hr_chart_html = fields.Html(
        string="Heart Rate Chart",
        compute="_compute_mediot_vital_curves_html_safe",
        sanitize=False,
    )
    temp_chart_html = fields.Html(
        string="Temperature Chart",
        compute="_compute_mediot_vital_curves_html_safe",
        sanitize=False,
    )
    vitals_curves_html = fields.Html(
        string="Vital Curves",
        compute="_compute_mediot_vital_curves_html_safe",
        sanitize=False,
    )

    def _mediot_svg_curve_safe(self, readings, field_name, title, unit, color="#f2b544"):
        points = []
        values = []

        for rec in readings:
            value = getattr(rec, field_name, 0) or 0
            if value:
                values.append(float(value))

        if not values:
            return """
            <div class="mediot_curve_card">
                <div class="mediot_curve_title">%s</div>
                <div class="mediot_curve_empty">No readings yet</div>
            </div>
            """ % title

        vmin = min(values)
        vmax = max(values)
        if vmin == vmax:
            vmin = vmin - 1
            vmax = vmax + 1

        width = 520
        height = 145
        pad_x = 28
        pad_y = 22

        used = []
        for rec in readings:
            value = getattr(rec, field_name, 0) or 0
            if value:
                used.append(rec)

        total = max(len(used) - 1, 1)

        for idx, rec in enumerate(used):
            value = float(getattr(rec, field_name, 0) or 0)
            x = pad_x + (idx / total) * (width - 2 * pad_x)
            y = pad_y + (1 - ((value - vmin) / (vmax - vmin))) * (height - 2 * pad_y)
            points.append("%.1f,%.1f" % (x, y))

        label_min = "%.1f" % vmin
        label_max = "%.1f" % vmax
        label_last = "%.1f%s" % (values[-1], unit)

        return """
        <div class="mediot_curve_card">
            <div class="mediot_curve_head">
                <div class="mediot_curve_title">%s</div>
                <div class="mediot_curve_last">%s</div>
            </div>
            <svg viewBox="0 0 %s %s" class="mediot_curve_svg" preserveAspectRatio="none">
                <line x1="28" y1="22" x2="492" y2="22" class="mediot_curve_grid"/>
                <line x1="28" y1="72" x2="492" y2="72" class="mediot_curve_grid"/>
                <line x1="28" y1="123" x2="492" y2="123" class="mediot_curve_grid"/>
                <polyline points="%s" fill="none" stroke="%s" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>
                %s
            </svg>
            <div class="mediot_curve_axis">
                <span>%s</span>
                <span>%s</span>
            </div>
        </div>
        """ % (
            title,
            label_last,
            width,
            height,
            " ".join(points),
            color,
            "".join(
                '<circle cx="%s" cy="%s" r="3.8" fill="%s"></circle>' % (
                    point.split(",")[0],
                    point.split(",")[1],
                    color,
                )
                for point in points
            ),
            label_min,
            label_max,
        )

    def _compute_mediot_vital_curves_html_safe(self):
        Reading = self.env["med.vital.reading"].sudo()

        for patient in self:
            readings = Reading.search(
                [("patient_id", "=", patient.id)],
                order="reading_at desc",
                limit=18,
            )
            readings = readings.sorted(lambda r: r.reading_at or r.create_date)

            hr = patient._mediot_svg_curve_safe(
                readings, "ecg_bpm", "Heart Rate (bpm)", " bpm", "#f2b544"
            )
            spo2 = patient._mediot_svg_curve_safe(
                readings, "spo2", "O₂ Saturation (%)", "%", "#f2b544"
            )
            temp = patient._mediot_svg_curve_safe(
                readings, "temp_c", "Temperature (°C)", "°C", "#f2b544"
            )

            patient.hr_chart_html = hr
            patient.spo2_chart_html = spo2
            patient.temp_chart_html = temp
            patient.vitals_curves_html = """
            <div class="mediot_vital_curves_panel">
                <div class="mediot_vital_curves_badge">MONITORING</div>
                <div class="mediot_vital_curves_grid">
                    %s
                    %s
                    %s
                </div>
            </div>
            """ % (hr, spo2, temp)
# PATIENT_PROFILE_VITAL_CURVES_SAFE_END



# PATIENT_PROFILE_VITAL_CURVES_NUMBERED_SAFE_START
class MedPatientVitalCurvesNumberedSafe(models.Model):
    _inherit = "med.patient"

    def _mediot_svg_curve_safe(self, readings, field_name, title, unit, color="#f2b544"):
        values = []
        used = []

        for rec in readings:
            value = getattr(rec, field_name, 0) or 0
            if value:
                values.append(float(value))
                used.append(rec)

        if not values:
            return """
            <div class="mediot_curve_card">
                <div class="mediot_curve_title">%s</div>
                <div class="mediot_curve_empty">No readings yet</div>
            </div>
            """ % title

        vmin = min(values)
        vmax = max(values)
        if vmin == vmax:
            vmin = vmin - 1
            vmax = vmax + 1

        vmid = (vmin + vmax) / 2.0

        width = 560
        height = 170
        pad_left = 52
        pad_right = 20
        pad_top = 22
        pad_bottom = 34

        total = max(len(used) - 1, 1)
        points = []

        for idx, rec in enumerate(used):
            value = float(getattr(rec, field_name, 0) or 0)
            x = pad_left + (idx / total) * (width - pad_left - pad_right)
            y = pad_top + (1 - ((value - vmin) / (vmax - vmin))) * (height - pad_top - pad_bottom)
            points.append("%.1f,%.1f" % (x, y))

        def fmt(v):
            if field_name == "ecg_bpm":
                return "%d" % round(v)
            return "%.1f" % v

        def time_label(rec):
            dt = rec.reading_at or rec.create_date
            return dt.strftime("%H:%M") if dt else "--:--"

        first_time = time_label(used[0])
        mid_time = time_label(used[len(used)//2])
        last_time = time_label(used[-1])
        label_last = fmt(values[-1]) + unit

        dots = "".join(
            '<circle cx="%s" cy="%s" r="3.6" fill="%s"></circle>' % (
                p.split(",")[0], p.split(",")[1], color
            )
            for p in points
        )

        return """
        <div class="mediot_curve_card mediot_curve_numbered_card">
            <div class="mediot_curve_head">
                <div class="mediot_curve_title">%s</div>
                <div class="mediot_curve_last">%s</div>
            </div>

            <svg viewBox="0 0 %s %s" class="mediot_curve_svg mediot_curve_numbered_svg" preserveAspectRatio="none">
                <text x="8" y="28" class="mediot_curve_y_label">%s</text>
                <text x="8" y="82" class="mediot_curve_y_label">%s</text>
                <text x="8" y="136" class="mediot_curve_y_label">%s</text>

                <line x1="52" y1="24" x2="540" y2="24" class="mediot_curve_grid"/>
                <line x1="52" y1="82" x2="540" y2="82" class="mediot_curve_grid"/>
                <line x1="52" y1="136" x2="540" y2="136" class="mediot_curve_grid"/>

                <polyline points="%s" fill="none" stroke="%s" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>
                %s

                <text x="52" y="164" class="mediot_curve_x_label">%s</text>
                <text x="280" y="164" class="mediot_curve_x_label" text-anchor="middle">%s</text>
                <text x="540" y="164" class="mediot_curve_x_label" text-anchor="end">%s</text>
            </svg>
        </div>
        """ % (
            title,
            label_last,
            width,
            height,
            fmt(vmax),
            fmt(vmid),
            fmt(vmin),
            " ".join(points),
            color,
            dots,
            first_time,
            mid_time,
            last_time,
        )
# PATIENT_PROFILE_VITAL_CURVES_NUMBERED_SAFE_END



# PATIENT_ALERTS_HTML_TABLE_SAFE_START
class MedPatientAlertsHtmlTableSafe(models.Model):
    _inherit = "med.patient"

    patient_alerts_table_html = fields.Html(
        string="Alerts Table",
        compute="_compute_patient_alerts_table_html_safe",
        sanitize=False,
    )

    def _compute_patient_alerts_table_html_safe(self):
        from markupsafe import escape

        type_labels = {
            "spo2": "SpO2",
            "temp": "Temperature",
            "ecg": "ECG",
            "cvd": "CVD",
        }

        for patient in self:
            alerts = self.env["med.alert"].sudo().search(
                [("patient_id", "=", patient.id)],
                order="create_date desc",
                limit=5,
            )

            rows = []
            for alert in alerts:
                date_txt = ""
                if alert.create_date:
                    try:
                        date_txt = fields.Datetime.context_timestamp(patient, alert.create_date).strftime("%b %d, %I:%M %p")
                    except Exception:
                        date_txt = str(alert.create_date)

                severity = alert.severity or ""
                state = alert.state or ""
                alert_type = type_labels.get(alert.alert_type or "", alert.alert_type or "")

                sev_class = "critical" if severity == "critical" else "warning"
                state_class = "resolved" if state == "resolved" else "new"

                rows.append("""
                    <tr class="mediot_alert_html_row %s">
                        <td>%s</td>
                        <td>%s</td>
                        <td><span class="mediot_alert_badge %s">%s</span></td>
                        <td class="mediot_alert_msg">%s</td>
                        <td><span class="mediot_state_badge %s">%s</span></td>
                    </tr>
                """ % (
                    sev_class,
                    escape(date_txt),
                    escape(alert_type),
                    sev_class,
                    escape(severity.title() if severity else ""),
                    escape(alert.message or ""),
                    state_class,
                    escape(state.title() if state else ""),
                ))

            if not rows:
                rows.append("""
                    <tr>
                        <td colspan="5" class="mediot_alert_empty">No alerts for this patient.</td>
                    </tr>
                """)

            patient.patient_alerts_table_html = """
                <div class="mediot_alert_html_table_wrap">
                    <table class="mediot_alert_html_table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Type</th>
                                <th>Severity</th>
                                <th>Message</th>
                                <th>State</th>
                            </tr>
                        </thead>
                        <tbody>
                            %s
                        </tbody>
                    </table>
                </div>
            """ % "".join(rows)
# PATIENT_ALERTS_HTML_TABLE_SAFE_END
