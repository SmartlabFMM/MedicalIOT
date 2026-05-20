# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class MedIoTAuthController(http.Controller):

    @http.route(['/mediot', '/mediot/'], type='http', auth='public', website=True, sitemap=False)
    def mediot_landing(self, **kwargs):
        return request.redirect('/mediot/login')

    @http.route(['/mediot/login', '/mediot/login/'], type='http', auth='public', website=True, csrf=False, sitemap=False, methods=['GET', 'POST'])
    def mediot_login_page(self, **kwargs):
        role_title = "MedIoT Access"
        role_desc = "Access your dashboard to manage patients and monitor vitals"
        role_icon = "fa-heartbeat"
        role_class = "mediot"

        if request.httprequest.method == 'POST':
            login = (kwargs.get('login') or kwargs.get('email') or kwargs.get('username') or '').strip()
            password = (kwargs.get('password') or kwargs.get('passwd') or kwargs.get('pwd') or '').strip()

            try:
                credential = {
                    "login": login,
                    "password": password,
                    "type": "password",
                }

                auth_info = request.session.authenticate(request.env, credential)

                if not request.session.uid and hasattr(request.session, "finalize"):
                    import inspect
                    params_count = len(inspect.signature(request.session.finalize).parameters)
                    if params_count == 1:
                        request.session.finalize(request.env)
                    else:
                        request.session.finalize(request.env, auth_info)

                return request.redirect('/mediot/post_login')

            except Exception as e:
                values = {
                    "error": "Login failed: %s: %s" % (type(e).__name__, str(e)),
                    "login": login,
                    "redirect": "/mediot/post_login",
                    "role_title": role_title,
                    "role_desc": role_desc,
                    "role_icon": role_icon,
                    "role_class": role_class,
                }
                return request.render('med_iot_command_center.med_login_page', values)

        values = {
            "error": kwargs.get("error"),
            "login": kwargs.get("login", ""),
            "redirect": "/mediot/post_login",
            "role_title": role_title,
            "role_desc": role_desc,
            "role_icon": role_icon,
            "role_class": role_class,
        }
        return request.render('med_iot_command_center.med_login_page', values)

    @http.route(['/mediot/post_login'], type='http', auth='user', website=False, sitemap=False)
    def mediot_post_login(self, **kwargs):
        user = request.env.user.sudo()

        def redirect_to(action_xmlid, menu_xmlid):
            action = request.env.ref(action_xmlid, raise_if_not_found=False)
            menu = request.env.ref(menu_xmlid, raise_if_not_found=False)

            if action and menu:
                return request.redirect(f"/web#action={action.id}&menu_id={menu.id}")
            if action:
                return request.redirect(f"/web#action={action.id}")
            return request.redirect("/web")

        # Admin login -> Admin interface
        if user.login == "admin" or user.has_group("med_iot_command_center.group_med_admin"):
            return redirect_to(
                "med_iot_command_center.action_med_admin_dashboard",
                "med_iot_command_center.menu_med_admin_dashboard",
            )

        # Doctor login -> Doctor interface
        if user.login == "mhfarah242@gmail.com" or user.has_group("med_iot_command_center.group_med_senior_doctor"):
            return redirect_to(
                "med_iot_command_center.action_med_dashboard",
                "med_iot_command_center.menu_med_dashboard",
            )

        return request.redirect("/web")

    @http.route(['/mediot/signup', '/mediot/signup/'], type='http', auth='public', website=True, sitemap=False)
    def mediot_signup_page(self, **kwargs):
        values = {
            "error": kwargs.get("error"),
            "success": kwargs.get("success"),
            "form_data": kwargs,
            "website": getattr(request, "website", False),
        }
        return request.render("med_iot_command_center.med_signup_page", values)

    @http.route(['/mediot/signup/submit'], type='http', auth='public', website=True, methods=['POST'], csrf=True, sitemap=False)
    def mediot_signup_submit(self, **post):
        Users = request.env['res.users'].sudo()
        email = (post.get('email') or '').strip().lower()
        password = (post.get('password') or '').strip()
        first_name = (post.get('first_name') or '').strip()
        last_name = (post.get('last_name') or '').strip()

        if not email:
            return request.render('med_iot_command_center.med_signup_page', {
                "error": "Email is required.",
                "form_data": post,
                "website": getattr(request, "website", False),
            })

        if not password:
            return request.render('med_iot_command_center.med_signup_page', {
                "error": "Password is required.",
                "form_data": post,
                "website": getattr(request, "website", False),
            })

        if Users.search_count([('login', '=', email)]) > 0:
            return request.render('med_iot_command_center.med_signup_page', {
                "error": "An account with this email already exists.",
                "form_data": post,
                "website": getattr(request, "website", False),
            })

        doctor_group = request.env.ref('med_iot_command_center.group_med_senior_doctor').sudo()
        internal_user_group = request.env.ref('base.group_user').sudo()

        new_user = Users.create({
            'name': f"{first_name} {last_name}".strip() or email,
            'login': email,
            'email': email,
            'password': password,
            'group_ids': [(6, 0, [internal_user_group.id, doctor_group.id])],
        })

        if new_user.partner_id:
            new_user.partner_id.sudo().write({
                'phone': post.get('phone', ''),
                'city': post.get('city', ''),
            })

        return request.render('med_iot_command_center.med_signup_page', {
            "success": "Your account has been created successfully. You can sign in now.",
            "form_data": {},
            "website": getattr(request, "website", False),
        })

    @http.route(['/mediot/reset', '/mediot/reset/'], type='http', auth='public', website=True, sitemap=False)
    def mediot_reset_redirect(self, **kwargs):
        return request.redirect('/web/reset_password')

    @http.route(['/mediot/logout', '/mediot/logout/'], type='http', auth='user', website=True, sitemap=False)
    def mediot_logout(self, **kwargs):
        request.session.logout(keep_db=False)
        return request.redirect('/mediot/login')

    @http.route(['/mediot/role', '/mediot/role/'], type='http', auth='public', website=True, sitemap=False)
    def mediot_role_select(self, **kwargs):
        return request.redirect('/mediot/login')

    @http.route(['/mediot/current_user_greeting'], type='json', auth='user', website=False, sitemap=False)
    def mediot_current_user_greeting(self, **kwargs):
        user = request.env.user.sudo()
        full_name = user.name or "User"
        first_name = full_name.split()[0] if full_name else "User"

        is_admin = user.has_group('med_iot_command_center.group_med_admin')
        is_doctor = user.has_group('med_iot_command_center.group_med_senior_doctor')

        if is_admin:
            greeting = f"Welcome back Admin {first_name}"
            subtitle = "Manage MedIoT operations, users, patients, and system settings."
        elif is_doctor:
            greeting = f"Welcome back Dr. {first_name}"
            subtitle = "Your patient monitoring dashboard is ready."
        else:
            greeting = f"Welcome back {first_name}"
            subtitle = "Welcome to MedIoT Command Center."

        return {
            "greeting": greeting,
            "subtitle": subtitle,
        }

