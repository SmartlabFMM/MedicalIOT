# -*- coding: utf-8 -*-
from odoo import fields, models


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

    acknowledged_by = fields.Many2one("res.users", readonly=True)
    acknowledged_on = fields.Datetime(readonly=True)
    resolved_by = fields.Many2one("res.users", readonly=True)
    resolved_on = fields.Datetime(readonly=True)

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

