# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class MedIoTAdminRedirectController(http.Controller):

    @http.route("/mediot/admin", type="http", auth="user", website=False, sitemap=False)
    def mediot_admin_redirect(self, **kw):
        if not request.env.user.has_group("med_iot_command_center.group_med_admin"):
            return request.redirect("/mediot")

        action = request.env.ref("med_iot_command_center.action_med_admin_dashboard").sudo()
        return request.redirect("/odoo/action-%s" % action.id)