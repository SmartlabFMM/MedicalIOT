# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class MedIoTLogoutRedirectController(http.Controller):

    @http.route("/web/session/logout", type="http", auth="none", website=False, sitemap=False)
    def logout(self, redirect="/mediot", **kw):
        request.session.logout(keep_db=True)
        return request.redirect("/mediot")