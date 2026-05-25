# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from urllib.parse import quote_plus


class MedIoTAuthController(http.Controller):

    @http.route(['/mediot/role', '/mediot/role/'], type='http', auth='public', website=True, sitemap=False)
    def med_role_select(self, **kw):
        return request.render('med_iot_command_center.med_role_select_page')

    @http.route(['/mediot', '/mediot/'], type='http', auth='public', website=True, sitemap=False)
    def mediot_landing(self, **kwargs):
        return request.render('med_iot_command_center.med_landing_page', {})

    @http.route(['/mediot/login', '/mediot/login/'], type='http', auth='public', website=True, sitemap=False)
    def mediot_login_page(self, **kwargs):
        role = kwargs.get("role", "")
        redirect = kwargs.get("redirect") or "/mediot/post_login"

        role_data = {
            "admin": {
                "role_class": "admin",
                "role_icon": "fa-user-secret",
                "role_title": "Admin",
                "role_desc": "Manage users, settings, patients, and system access",
            },
            "doctor": {
                "role_class": "doctor",
                "role_icon": "fa-user-md",
                "role_title": "Doctor",
                "role_desc": "Monitor patients, alerts, vitals, and medical follow-up",
            },
        }.get(role, {
            "role_class": "default",
            "role_icon": "fa-heart-o",
            "role_title": "MedIoT",
            "role_desc": "Sign in to access your dashboard",
        })

        values = {
            "error": kwargs.get("error"),
            "login": kwargs.get("login", ""),
            "redirect": redirect,
            "role": role,
            **role_data,
        }
        return request.render('med_iot_command_center.med_login_page', values)

    @http.route(['/mediot/login/submit'], type='http', auth='public', website=True, methods=['POST'], csrf=True, sitemap=False)
    def mediot_login_submit(self, **post):
        login = (post.get("login") or "").strip()
        password = (post.get("password") or "").strip()

        try:
            credential = {
                "login": login,
                "password": password,
                "type": "password",
            }

            auth_info = request.session.authenticate(request.env, credential)

            if not auth_info:
                return request.redirect(
                    "/mediot/login?login=%s&error=%s"
                    % (
                        quote_plus(login),
                        quote_plus("Invalid email or password."),
                    )
                )

            if not request.session.uid and hasattr(request.session, "finalize"):
                try:
                    request.session.finalize(request.env, auth_info)
                except TypeError:
                    request.session.finalize(auth_info)

            return request.redirect("/mediot/post_login")

        except Exception:
            return request.redirect(
                "/mediot/login?login=%s&error=%s"
                % (
                    quote_plus(login),
                    quote_plus("Invalid email or password."),
                )
            )

    @http.route(['/mediot/post_login'], type='http', auth='user', website=False, sitemap=False)
    def mediot_post_login(self, **kwargs):
        user = request.env.user

        if user.has_group('med_iot_command_center.group_med_admin'):
            action = request.env.ref('med_iot_command_center.action_med_admin_dashboard').sudo()
            menu = request.env.ref('med_iot_command_center.menu_med_admin_dashboard').sudo()
            return request.redirect(f'/web#action={action.id}&menu_id={menu.id}')

        if user.has_group('med_iot_command_center.group_med_senior_doctor'):
            action = request.env.ref('med_iot_command_center.action_med_dashboard').sudo()
            menu = request.env.ref('med_iot_command_center.menu_med_dashboard').sudo()
            return request.redirect(f'/web#action={action.id}&menu_id={menu.id}')

        return request.redirect('/mediot/role')

    @http.route(['/mediot/signup', '/mediot/signup/'], type='http', auth='public', website=True, sitemap=False)
    def mediot_signup_page(self, **kwargs):
        values = {
            "error": kwargs.get("error"),
            "success": kwargs.get("success"),
            "form_data": kwargs,
        }
        return request.render('med_iot_command_center.med_signup_page', values)

    @http.route(['/mediot/signup/submit'], type='http', auth='public', website=True, methods=['POST'], csrf=True, sitemap=False)
    def mediot_signup_submit(self, **post):
        Users = request.env['res.users'].sudo()

        email = (post.get('email') or post.get('login') or '').strip().lower()
        password = (post.get('password') or '').strip()
        first_name = (post.get('first_name') or '').strip()
        last_name = (post.get('last_name') or '').strip()

        if not email:
            return request.render('med_iot_command_center.med_signup_page', {
                "error": "Email is required.",
                "form_data": post,
            })

        if not password:
            return request.render('med_iot_command_center.med_signup_page', {
                "error": "Password is required.",
                "form_data": post,
            })

        if Users.search_count([('login', '=', email)]) > 0:
            return request.render('med_iot_command_center.med_signup_page', {
                "error": "An account with this email already exists.",
                "form_data": post,
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
        })

    @http.route(['/mediot/reset', '/mediot/reset/'], type='http', auth='public', website=True, sitemap=False)
    def mediot_reset_redirect(self, **kwargs):
        return request.redirect('/web/reset_password')

    @http.route(['/mediot/logout', '/mediot/logout/'], type='http', auth='user', website=True, sitemap=False)
    def mediot_logout(self, **kwargs):
        request.session.logout(keep_db=False)
        return request.redirect('/mediot/login')

    @http.route(['/mediot-test'], type='http', auth='public', website=True, sitemap=False)
    def mediot_test(self, **kwargs):
        return "MEDIOT CONTROLLER IS LOADED"

    @http.route('/login-mediot', type='http', auth='public', website=True, sitemap=False)
    def login_mediot_direct(self, **kwargs):
        values = {
            "error": kwargs.get("error"),
            "login": kwargs.get("login", ""),
            "redirect": "/mediot/post_login",
        }
        return request.render('med_iot_command_center.med_login_page', values)

    @http.route('/signup-mediot', type='http', auth='public', website=True, sitemap=False)
    def signup_mediot_direct(self, **kwargs):
        values = {
            "error": kwargs.get("error"),
            "success": kwargs.get("success"),
            "form_data": kwargs,
        }
        return request.render('med_iot_command_center.med_signup_page', values)

    @http.route('/home-mediot', type='http', auth='public', website=True, sitemap=False)
    def home_mediot_direct(self, **kwargs):
        return request.render('med_iot_command_center.med_landing_page', {})

    @http.route('/mediot/switch/doctor', type='http', auth='public', website=True, sitemap=False)
    def mediot_switch_doctor(self, **kw):
        if request.env.user._is_public():
            return request.redirect('/mediot/login?role=doctor&redirect=/mediot/switch/doctor')
        action = request.env.ref('med_iot_command_center.action_med_dashboard').sudo()
        menu = request.env.ref('med_iot_command_center.menu_med_dashboard').sudo()
        return request.redirect(f'/web#action={action.id}&menu_id={menu.id}')

    @http.route('/mediot/switch/admin', type='http', auth='public', website=True, sitemap=False)
    def mediot_switch_admin(self, **kw):
        if request.env.user._is_public():
            return request.redirect('/mediot/login?role=admin&redirect=/mediot/switch/admin')
        action = request.env.ref('med_iot_command_center.action_med_admin_dashboard').sudo()
        menu = request.env.ref('med_iot_command_center.menu_med_admin_dashboard').sudo()
        return request.redirect(f'/web#action={action.id}&menu_id={menu.id}')

    @http.route('/mediot/current_user_greeting', type='json', auth='user', sitemap=False)
    def current_user_greeting(self, **kwargs):
        user = request.env.user
        return {
            'name': user.name or '',
            'greeting': 'Welcome, %s' % (user.name or ''),
        }
