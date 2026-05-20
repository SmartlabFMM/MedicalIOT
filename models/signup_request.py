from odoo import models, fields


class MedSignupRequest(models.Model):
    _name = "med.signup.request"
    _description = "MedIoT Signup Request"
    _order = "create_date desc"

    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    gender = fields.Selection([
        ("male", "Male"),
        ("female", "Female"),
    ])
    age = fields.Integer()
    email = fields.Char(required=True)
    phone = fields.Char()
    password = fields.Char(required=True)
    governorate = fields.Char()
    city = fields.Char()
    zip_code = fields.Char()
    role = fields.Selection([
        ("doctor", "Doctor"),
        ("admin", "Administrator"),
    ], default="doctor")
    specialty = fields.Char()
    verification_file = fields.Binary()
    verification_filename = fields.Char()
    state = fields.Selection([
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ], default="pending")