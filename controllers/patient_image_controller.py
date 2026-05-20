# -*- coding: utf-8 -*-
import base64

from odoo import http
from odoo.http import request


class MedIoTPatientPhotoController(http.Controller):

    @http.route('/mediot/patient_photo/<int:patient_id>', type='http', auth='user', website=False, csrf=False)
    def mediot_patient_photo(self, patient_id, **kwargs):
        patient = request.env['med.patient'].sudo().browse(patient_id)

        if not patient.exists():
            return request.not_found()

        img = False
        for field_name in ('image_1920', 'image_512', 'image_256', 'image_128', 'image'):
            if field_name in patient._fields and patient[field_name]:
                img = patient[field_name]
                break

        if not img:
            return request.not_found()

        if isinstance(img, str):
            img = img.encode('utf-8')

        raw = base64.b64decode(img)

        content_type = 'image/png'
        if raw.startswith(b'\xff\xd8'):
            content_type = 'image/jpeg'
        elif raw.startswith(b'GIF'):
            content_type = 'image/gif'
        elif raw.startswith(b'RIFF') and b'WEBP' in raw[:20]:
            content_type = 'image/webp'

        return request.make_response(raw, headers=[
            ('Content-Type', content_type),
            ('Cache-Control', 'no-store, max-age=0'),
        ])
