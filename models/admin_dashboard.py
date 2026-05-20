# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class MedAdminDashboard(models.Model):
    _name = "med.admin.dashboard"
    _description = "MedIoT Admin Dashboard"

    name = fields.Char(default="Admin Dashboard")

    doctor_count = fields.Integer(compute="_compute_dashboard")
    patient_count = fields.Integer(compute="_compute_dashboard")
    critical_patient_count = fields.Integer(compute="_compute_dashboard")
    pending_alert_count = fields.Integer(compute="_compute_dashboard")
    online_device_count = fields.Integer(compute="_compute_dashboard")

    doctor_ids = fields.Many2many(
        "res.users",
        compute="_compute_dashboard",
        string="Doctors / Staff",
    )

    critical_patient_ids = fields.Many2many(
        "med.patient",
        compute="_compute_dashboard",
        string="Critical Patients",
    )

    recent_alert_ids = fields.Many2many(
        "med.alert",
        compute="_compute_dashboard",
        string="Recent Alerts",
    )

    @api.depends()
    def _compute_dashboard(self):
        Patient = self.env["med.patient"].sudo()
        Alert = self.env["med.alert"].sudo()
        Device = self.env["med.device"].sudo()
        Users = self.env["res.users"].sudo()

        staff_group_xmlids = [
            "med_iot_command_center.group_med_admin",
            "med_iot_command_center.group_med_senior_doctor",
            "med_iot_command_center.group_med_junior_staff",
        ]

        doctors = Users.browse()
        internal_users = Users.search([("share", "=", False)])

        for user in internal_users:
            for xmlid in staff_group_xmlids:
                try:
                    if user.has_group(xmlid):
                        doctors |= user
                        break
                except Exception:
                    continue

        critical_patients = Patient.search([("status", "=", "critical")], limit=10)
        recent_alerts = Alert.search([], order="create_date desc", limit=10)

        device_status_field = Device._fields.get("status")
        if device_status_field:
            online_device_count = Device.search_count([("status", "=", "online")])
        else:
            online_device_count = Device.search_count([])

        for rec in self:
            rec.doctor_count = len(doctors)
            rec.patient_count = Patient.search_count([])
            rec.critical_patient_count = Patient.search_count([("status", "=", "critical")])
            rec.pending_alert_count = Alert.search_count([])
            rec.online_device_count = online_device_count
            rec.doctor_ids = doctors
            rec.critical_patient_ids = critical_patients
            rec.recent_alert_ids = recent_alerts

    def action_open_doctors(self):
        list_view = self.env.ref(
            "med_iot_command_center.view_med_admin_users_list_clean",
            raise_if_not_found=False,
        )
        form_view = self.env.ref("base.view_users_form", raise_if_not_found=False)

        views = []
        if list_view:
            views.append((list_view.id, "list"))
        if form_view:
            views.append((form_view.id, "form"))

        return {
            "type": "ir.actions.act_window",
            "name": "Manage Users",
            "res_model": "res.users",
            "view_mode": "list,form",
            "views": views or [(False, "list"), (False, "form")],
            "target": "current",
            "domain": [("share", "=", False)],
            "context": {
                "create": True,
                "edit": True,
                "delete": True,
            },
        }

    def action_add_doctor(self):
        form_view = self.env.ref("base.view_users_form", raise_if_not_found=False)
        doctor_group = self.env.ref("med_iot_command_center.group_med_senior_doctor", raise_if_not_found=False)

        ctx = {"create": True}
        if doctor_group:
            ctx["default_group_ids"] = [(6, 0, [doctor_group.id])]

        return {
            "type": "ir.actions.act_window",
            "name": "Add Doctor",
            "res_model": "res.users",
            "view_mode": "form",
            "views": [(form_view.id, "form")] if form_view else [(False, "form")],
            "target": "current",
            "context": ctx,
        }

    def action_open_patients(self):
        return self.env.ref("med_iot_command_center.action_med_patient").read()[0]

    def action_open_alerts(self):
        return self.env.ref("med_iot_command_center.action_med_alert").read()[0]

    def action_open_devices(self):
        return self.env.ref("med_iot_command_center.action_med_settings").read()[0]

class ResUsers(models.Model):
    _inherit = "res.users"

    mediot_role_label = fields.Char(
        string="Role",
        compute="_compute_mediot_role_label",
    )

    mediot_initial_label = fields.Char(
        string="",
        compute="_compute_mediot_initial_label",
    )

    @api.depends("group_ids", "name", "login", "email")
    def _compute_mediot_role_label(self):
        admin_group = self.env.ref("med_iot_command_center.group_med_admin", raise_if_not_found=False)
        senior_group = self.env.ref("med_iot_command_center.group_med_senior_doctor", raise_if_not_found=False)
        junior_group = self.env.ref("med_iot_command_center.group_med_junior_staff", raise_if_not_found=False)

        for user in self:
            if admin_group and admin_group in user.group_ids:
                user.mediot_role_label = "Admin"
            elif "salem" in (user.name or "").lower() or "technician" in (user.login or "").lower() or "technician" in (user.email or "").lower():
                user.mediot_role_label = "Technician"
            elif (senior_group and senior_group in user.group_ids) or (junior_group and junior_group in user.group_ids):
                user.mediot_role_label = "Doctor"
            else:
                user.mediot_role_label = "Doctor"

    @api.depends("name", "login")
    def _compute_mediot_initial_label(self):
        for user in self:
            source = (user.name or user.login or "?").strip()
            user.mediot_initial_label = source[:1].upper() if source else "?"
class ResUsersMedIoTActions(models.Model):
    _inherit = "res.users"

    def action_mediot_open_user(self):
        self.ensure_one()
        form_view = self.env.ref("med_iot_command_center.view_med_user_role_modal_form", raise_if_not_found=False)
        return {
            "type": "ir.actions.act_window",
            "name": "Manage User",
            "res_model": "res.users",
            "res_id": self.id,
            "view_mode": "form",
            "views": [(form_view.id, "form")] if form_view else [(False, "form")],
            "target": "new",
            "context": {"form_view_ref": "med_iot_command_center.view_med_user_role_modal_form"},
        }

    def action_mediot_delete_user(self):
        self.ensure_one()

        admin_user = self.env.ref("base.user_admin", raise_if_not_found=False)

        if self == self.env.user:
            raise UserError("You cannot delete or archive the currently logged-in user.")

        if admin_user and self.id == admin_user.id:
            raise UserError("You cannot delete or archive the main Administrator user.")

        display_name = self.name or self.login or "User"

        try:
            self.unlink()
            message = "%s deleted successfully." % display_name
        except Exception:
            # Odoo blocks deleting users linked to employees or other records.
            # In that case, archive the user instead, which is the safe Odoo behavior.
            self.write({"active": False})
            message = "%s could not be deleted because it is linked to other records, so it was archived instead." % display_name

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "User updated",
                "message": message,
                "type": "success",
                "sticky": False,
            },
        }


class MedAdminDashboardQuickAdd(models.Model):
    _inherit = "med.admin.dashboard"

    quick_doctor_name = fields.Char(string="Doctor Name")
    quick_doctor_email = fields.Char(string="Doctor Email")
    quick_doctor_password = fields.Char(string="Temporary Password")
    quick_doctor_role = fields.Selection(
        [
            ("senior", "Senior Doctor"),
            ("junior", "Junior Staff"),
        ],
        string="Role",
        default="senior",
    )

    def action_quick_add_doctor(self):
        self.ensure_one()

        name = (self.quick_doctor_name or "").strip()
        email = (self.quick_doctor_email or "").strip().lower()
        password = (self.quick_doctor_password or "").strip()
        role = self.quick_doctor_role or "senior"

        if not name or not email or not password:
            raise UserError("Please fill Name, Email, and Password.")

        Users = self.env["res.users"].sudo()

        if Users.search_count([("login", "=", email)]):
            raise UserError("A user with this email/login already exists.")

        base_group = self.env.ref("base.group_user", raise_if_not_found=False)
        role_group = self.env.ref(
            "med_iot_command_center.group_med_senior_doctor"
            if role == "senior"
            else "med_iot_command_center.group_med_junior_staff",
            raise_if_not_found=False,
        )

        group_ids = []
        if base_group:
            group_ids.append(base_group.id)
        if role_group:
            group_ids.append(role_group.id)

        Users.create({
            "name": name,
            "login": email,
            "email": email,
            "password": password,
            "group_ids": [(6, 0, group_ids)],
        })

        self.write({
            "quick_doctor_name": False,
            "quick_doctor_email": False,
            "quick_doctor_password": False,
            "quick_doctor_role": "senior",
        })

        return {"type": "ir.actions.client", "tag": "reload"}

class MedAdminDashboardAddDoctorPopup(models.Model):
    _inherit = "med.admin.dashboard"

    def action_open_add_doctor_popup(self):
        view = self.env.ref("med_iot_command_center.view_med_admin_quick_doctor_wizard_form")
        return {
            "type": "ir.actions.act_window",
            "name": "Add Doctor",
            "res_model": "med.admin.quick.doctor.wizard",
            "view_mode": "form",
            "view_id": view.id,
            "target": "new",
            "context": {"default_role": "senior"},
        }


class MedAdminQuickDoctorWizard(models.TransientModel):
    _name = "med.admin.quick.doctor.wizard"
    _description = "Add Doctor Wizard"

    name = fields.Char(string="Name", required=True)
    email = fields.Char(string="Email", required=True)
    password = fields.Char(string="Temporary Password", required=True)
    role = fields.Selection(
        [
            ("senior", "Senior Doctor"),
            ("junior", "Junior Staff"),
        ],
        string="Role",
        default="senior",
        required=True,
    )

    def action_create_doctor(self):
        self.ensure_one()

        name = (self.name or "").strip()
        email = (self.email or "").strip().lower()
        password = (self.password or "").strip()

        if not name or not email or not password:
            raise UserError("Please fill Name, Email, and Password.")

        Users = self.env["res.users"].sudo()

        if Users.search_count([("login", "=", email)]):
            raise UserError("A user with this email/login already exists.")

        base_group = self.env.ref("base.group_user", raise_if_not_found=False)
        role_group = self.env.ref(
            "med_iot_command_center.group_med_senior_doctor"
            if self.role == "senior"
            else "med_iot_command_center.group_med_junior_staff",
            raise_if_not_found=False,
        )

        group_ids = []
        if base_group:
            group_ids.append(base_group.id)
        if role_group:
            group_ids.append(role_group.id)

        Users.create({
            "name": name,
            "login": email,
            "email": email,
            "password": password,
            "group_ids": [(6, 0, group_ids)],
        })

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Doctor created",
                "message": "%s was added successfully." % name,
                "type": "success",
                "sticky": False,
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
        }

class MedAdminDashboardOpenUserRolesPage(models.Model):
    _inherit = "med.admin.dashboard"

    def action_open_doctors(self):
        return self.env.ref("med_iot_command_center.action_med_user_role_management").read()[0]


class ResUsersMedIoTRoleManagementPage(models.Model):
    _inherit = "res.users"

    mediot_initial_badge = fields.Char(
        string="",
        compute="_compute_mediot_initial_badge",
    )
    mediot_role_badge = fields.Char(
        string="MedIoT Role",
        compute="_compute_mediot_role_badge",
    )

    mediot_role_description = fields.Text(
        string="Role Description",
        compute="_compute_mediot_role_description",
    )

    @api.depends("name", "login")
    def _compute_mediot_initial_badge(self):
        for user in self:
            source = (user.name or user.login or "?").strip()
            user.mediot_initial_badge = source[:1].upper() if source else "?"

    @api.depends("group_ids")
    def _compute_mediot_role_badge(self):
        admin_group = self.env.ref("med_iot_command_center.group_med_admin", raise_if_not_found=False)
        senior_group = self.env.ref("med_iot_command_center.group_med_senior_doctor", raise_if_not_found=False)
        junior_group = self.env.ref("med_iot_command_center.group_med_junior_staff", raise_if_not_found=False)

        for user in self:
            if admin_group and admin_group in user.group_ids:
                user.mediot_role_badge = "Admin"
            elif "salem" in (user.name or "").lower() or "technician" in (user.login or "").lower() or "technician" in (user.email or "").lower():
                user.mediot_role_badge = "Technician"
            elif senior_group and senior_group in user.group_ids:
                user.mediot_role_badge = "Doctor"
            elif junior_group and junior_group in user.group_ids:
                user.mediot_role_badge = "Doctor"
            else:
                user.mediot_role_badge = "Doctor"

    @api.depends("group_ids", "name", "login", "email")
    def _compute_mediot_role_description(self):
        for user in self:
            role = user.mediot_role_badge

            if role == "Admin":
                user.mediot_role_description = (
                    "Full system administration access. Can manage users and roles, "
                    "configure MedIoT settings, supervise platform access, and oversee "
                    "system operations."
                )
            elif role == "Technician":
                user.mediot_role_description = (
                    "Handles device setup and maintenance, verifies IoT/MQTT connectivity, "
                    "checks device status, and supports technical deployment and troubleshooting."
                )
            else:
                user.mediot_role_description = (
                    "Reviews patient monitoring data, follows wearable readings, checks alerts, "
                    "and supports clinical follow-up and care decisions."
                )

    def _mediot_set_role(self, role):
        admin_group = self.env.ref("med_iot_command_center.group_med_admin", raise_if_not_found=False)
        senior_group = self.env.ref("med_iot_command_center.group_med_senior_doctor", raise_if_not_found=False)
        junior_group = self.env.ref("med_iot_command_center.group_med_junior_staff", raise_if_not_found=False)
        base_group = self.env.ref("base.group_user", raise_if_not_found=False)

        role_map = {
            "admin": admin_group,
            "senior": senior_group,
            "junior": junior_group,
        }

        target_group = role_map.get(role)
        if not target_group:
            raise UserError("Selected role group was not found.")

        for user in self:
            if user == self.env.user and role != "admin":
                raise UserError("You cannot remove your own admin access.")

            commands = []
            for group in [admin_group, senior_group, junior_group]:
                if group:
                    commands.append((3, group.id))

            if base_group:
                commands.append((4, base_group.id))
            commands.append((4, target_group.id))

            user.sudo().write({"group_ids": commands})

        return {"type": "ir.actions.client", "tag": "reload"}

    def action_mediot_role_admin(self):
        return self._mediot_set_role("admin")

    def action_mediot_role_senior(self):
        return self._mediot_set_role("senior")

    def action_mediot_role_junior(self):
        return self._mediot_set_role("junior")

    def action_mediot_open_user(self):
        self.ensure_one()
        form_view = self.env.ref("med_iot_command_center.view_med_user_role_modal_form", raise_if_not_found=False)
        return {
            "type": "ir.actions.act_window",
            "name": "Manage User",
            "res_model": "res.users",
            "res_id": self.id,
            "view_mode": "form",
            "views": [(form_view.id, "form")] if form_view else [(False, "form")],
            "target": "new",
            "context": {"form_view_ref": "med_iot_command_center.view_med_user_role_modal_form"},
        }

    def action_mediot_archive_user(self):
        self.ensure_one()

        admin_user = self.env.ref("base.user_admin", raise_if_not_found=False)

        if self == self.env.user:
            raise UserError("You cannot archive the currently logged-in user.")

        if admin_user and self.id == admin_user.id:
            raise UserError("You cannot archive the main Administrator user.")

        self.sudo().write({"active": False})
        return {"type": "ir.actions.client", "tag": "reload"}



