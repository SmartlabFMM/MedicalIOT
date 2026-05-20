# -*- coding: utf-8 -*-
from odoo import fields, models


class MedDevice(models.Model):
    _name = "med.device"
    _description = "IoT Device"
    _order = "name"

    name = fields.Char(required=True)
    device_uid = fields.Char(string="Device UID / Topic", index=True)
    room = fields.Char()

    status = fields.Selection([("online", "Online"), ("offline", "Offline")], default="offline", index=True)
    last_seen = fields.Datetime()

    patient_id = fields.Many2one("med.patient", help="Optional: device bound to patient/bed")
