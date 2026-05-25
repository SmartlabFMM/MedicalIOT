# -*- coding: utf-8 -*-
import logging
from datetime import timedelta
from html import escape
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class MedAlert(models.Model):
    _name = "med.alert"
    _description = "Patient Alert"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    patient_id = fields.Many2one("med.patient", required=True, ondelete="cascade", index=True)
    reading_id = fields.Many2one("med.vital.reading", index=True)

    alert_type = fields.Selection(
        [("temp", "Temperature"), ("spo2", "SpO2"), ("ecg", "ECG"), ("cvd", "CVD Risk")],
        required=True,
        index=True,
    )
    severity = fields.Selection([("warning", "Warning"), ("critical", "Critical")], required=True, index=True)

    message = fields.Char(required=True)
    state = fields.Selection([("new", "New"), ("ack", "Acknowledged"), ("resolved", "Resolved")],
                             default="new", tracking=True, index=True)

    ai_email_sent = fields.Boolean(string="AI Alert Email Sent", default=False, readonly=True)
    ai_email_sent_on = fields.Datetime(string="AI Alert Email Sent On", readonly=True)

    acknowledged_by = fields.Many2one("res.users", readonly=True)
    acknowledged_on = fields.Datetime(readonly=True)
    resolved_by = fields.Many2one("res.users", readonly=True)
    resolved_on = fields.Datetime(readonly=True)


    # PREDICTIVE_EMAIL_ALERT_START
    def _get_alert_email_recipient(self):
        self.ensure_one()
        patient = self.patient_id
        doctor = getattr(patient, "assigned_doctor_id", False)

        if doctor and doctor.email:
            return doctor.email
        if self.env.user.email:
            return self.env.user.email
        if self.env.company.email:
            return self.env.company.email
        return False

    def _build_predictive_alert_email_body(self):
        self.ensure_one()
        patient = self.patient_id

        patient_name = escape(patient.display_name or patient.name or "Unknown patient")
        room = escape(patient.room or "Not specified")
        status = escape(dict(patient._fields["status"].selection).get(patient.status, patient.status or "Unknown"))
        severity = escape(dict(self._fields["severity"].selection).get(self.severity, self.severity or "Unknown"))
        alert_message = escape(self.message or "No details available")

        spo2 = getattr(patient, "latest_spo2", False)
        bpm = getattr(patient, "latest_ecg_bpm", False)
        temp = getattr(patient, "latest_temp", False)

        vitals_html = ""
        if spo2 not in (False, None):
            vitals_html += "<li>SpO?: %.2f %%</li>" % spo2
        if bpm not in (False, None):
            vitals_html += "<li>Heart rate: %.0f BPM</li>" % bpm
        if temp not in (False, None):
            vitals_html += "<li>Temperature: %.2f ?C</li>" % temp
        if not vitals_html:
            vitals_html = "<li>No latest vital signs available.</li>"

        prediction_blocks = ""

        if getattr(patient, "cvd_last_checked", False):
            prediction_blocks += """
                <p><b>Model used:</b> Cardiovascular Disease Risk Prediction</p>
                <ul>
                    <li><b>Prediction:</b> %s</li>
                    <li><b>Probability:</b> %.2f %%</li>
                    <li><b>Clinical message:</b> %s</li>
                </ul>
            """ % (
                escape(dict(patient._fields["cvd_risk"].selection).get(patient.cvd_risk, patient.cvd_risk or "Unknown")),
                patient.cvd_probability or 0.0,
                escape(patient.cvd_message or "No CVD message available.")
            )

        if getattr(patient, "heart_last_checked", False):
            prediction_blocks += """
                <p><b>Model used:</b> Heart Disease Prediction</p>
                <ul>
                    <li><b>Prediction:</b> %s</li>
                    <li><b>Probability:</b> %.2f %%</li>
                    <li><b>Clinical message:</b> %s</li>
                </ul>
            """ % (
                escape(dict(patient._fields["heart_risk"].selection).get(patient.heart_risk, patient.heart_risk or "Unknown")),
                patient.heart_probability or 0.0,
                escape(patient.heart_message or "No heart disease message available.")
            )

        if not prediction_blocks:
            prediction_blocks = "<p>No AI prediction result has been generated yet for this patient.</p>"

        return """
            <p>Dear Doctor,</p>

            <p>A MedIoT alert concerning patient <b>%s</b> has not been acknowledged within the expected delay and requires your attention.</p>

            <p><b>Patient information:</b></p>
            <ul>
                <li><b>Room:</b> %s</li>
                <li><b>Current status:</b> %s</li>
                <li><b>Alert severity:</b> %s</li>
            </ul>

            <p><b>Detected alert:</b></p>
            <ul>
                <li>%s</li>
            </ul>

            <p><b>Latest vital signs:</b></p>
            <ul>
                %s
            </ul>

            <p><b>AI prediction result:</b></p>
            %s

            <p>Please review the patient's monitoring history, check the AI prediction results, and take the necessary medical action if required.</p>

            <p>Best regards,<br/>
            MedIoT Command Center</p>
        """ % (patient_name, room, status, severity, alert_message, vitals_html, prediction_blocks)

    def action_send_predictive_email(self):
        for rec in self:
            recipient = rec._get_alert_email_recipient()
            if not recipient:
                raise ValidationError(_("No recipient email found. Please configure the doctor or company email."))

            patient_name = rec.patient_id.display_name or rec.patient_id.name or "Unknown patient"
            subject = "MedIoT Unacknowledged Predictive Alert - Patient %s" % patient_name

            mail = self.env["mail.mail"].sudo().create({
                "subject": subject,
                "body_html": rec._build_predictive_alert_email_body(),
                "email_to": recipient,
                "auto_delete": False,
            })
            mail.send()

            rec.write({
                "ai_email_sent": True,
                "ai_email_sent_on": fields.Datetime.now(),
            })

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Predictive alert email sent"),
                "message": _("The personalized MedIoT alert email has been sent successfully."),
                "type": "success",
                "sticky": False,
            },
        }

    @api.model
    def _cron_send_unconsulted_predictive_emails(self):
        delay_minutes = 2
        limit_date = fields.Datetime.now() - timedelta(minutes=delay_minutes)

        alerts = self.sudo().search([
            ("state", "=", "new"),
            ("severity", "in", ["warning", "critical"]),
            ("ai_email_sent", "=", False),
            ("create_date", "<=", limit_date),
            ("patient_id", "!=", False),
        ], limit=50)

        for alert in alerts:
            try:
                alert.action_send_predictive_email()
            except Exception as exc:
                _logger.warning("Could not send predictive email for alert %s: %s", alert.id, exc)

    # PREDICTIVE_EMAIL_ALERT_END

    def action_acknowledge(self):
        now = fields.Datetime.now()
        for rec in self:
            rec.write({
                "state": "ack",
                "acknowledged_by": self.env.user.id,
                "acknowledged_on": now,
            })

    def action_resolve(self):
        now = fields.Datetime.now()
        for rec in self:
            rec.write({
                "state": "resolved",
                "resolved_by": self.env.user.id,
                "resolved_on": now,
            })

