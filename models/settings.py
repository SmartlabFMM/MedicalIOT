# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MedSettings(models.Model):
    _rec_name = "name"

    name = fields.Char(string="Name", default="Alert Threshold Settings")
    _name = "med.settings"
    _description = "Monitoring Settings (Singleton)"

    # DEVICE SETTINGS EMBED FIELDS
    device_id = fields.Many2one(
        "med.device",
        string="Device",
        compute="_compute_embedded_device",
        store=True,
        readonly=True,
    )
    device_name = fields.Char(
        string="Device Name",
        related="device_id.name",
        readonly=False,
    )
    device_status = fields.Selection(
        string="Status",
        related="device_id.status",
        readonly=False,
    )
    device_uid = fields.Char(
        string="MQTT Topic",
        related="device_id.device_uid",
        readonly=False,
    )
    device_room = fields.Char(
        string="Room / Bed",
        related="device_id.room",
        readonly=False,
    )
    device_patient_id = fields.Many2one(
        "med.patient",
        string="Monitoring Patient",
        related="device_id.patient_id",
        readonly=False,
    )
    device_last_seen = fields.Datetime(
        string="Last Seen",
        related="device_id.last_seen",
        readonly=True,
    )

    def _compute_embedded_device(self):
        device = self.env["med.device"].sudo().search([], order="id asc", limit=1)
        for rec in self:
            rec.device_id = device


    # Heart rate
    hr_critical_min = fields.Integer(default=40)
    hr_critical_max = fields.Integer(default=130)
    hr_warning_min = fields.Integer(default=50)
    hr_warning_max = fields.Integer(default=110)

    # SpO2
    spo2_critical_min = fields.Float(default=85.0)
    spo2_warning_min = fields.Float(default=90.0)

    # Temperature
    temp_critical_min = fields.Float(default=35.0)
    temp_critical_max = fields.Float(default=39.0)
    temp_warning_min = fields.Float(default=36.0)
    temp_warning_max = fields.Float(default=37.8)

    check_interval_seconds = fields.Integer(default=30)

    @api.model
    def get_settings(self):
        rec = self.search([], limit=1)
        if not rec:
            rec = self.create({})
        return rec  # Remove the comma, it was causing a tuple return
