from pathlib import Path
import re

xml_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\views\auth_pages.xml")
text = xml_path.read_text(encoding="utf-8")

new_footer = r'''
<footer class="med_video_footer mediot_footer_v2">
    <div class="container">
        <div class="mediot_footer_grid_v2">
            <div class="mediot_footer_col_v2 mediot_footer_brand_v2">
                <div class="mediot_footer_logo_v2">
                    <span>♡</span>
                    <strong>MedIoT</strong>
                </div>
                <p>Smart care. Real-time monitoring. Connected clinical support.</p>
            </div>

            <div class="mediot_footer_col_v2">
                <h4>Services</h4>
                <ul>
                    <li>Vital Monitoring</li>
                    <li>Medical Dashboards</li>
                    <li>Doctor Follow-up</li>
                    <li>Case Management</li>
                </ul>
            </div>

            <div class="mediot_footer_col_v2">
                <h4>Contact</h4>
                <ul class="mediot_footer_contact_v2">
                    <li><i class="fa fa-phone" title="Phone"></i><span>+216 00 000 000</span></li>
                    <li><i class="fa fa-envelope" title="Email"></i><span>contact@mediot.health</span></li>
                    <li><i class="fa fa-map-marker" title="Location"></i><span>Tunis, Tunisia</span></li>
                </ul>
            </div>

            <div class="mediot_footer_col_v2">
                <h4>Follow Us</h4>
                <div class="mediot_footer_socials_v2">
                    <a href="#" aria-label="Instagram"><i class="fa fa-instagram" title="Instagram"></i></a>
                    <a href="#" aria-label="Facebook"><i class="fa fa-facebook" title="Facebook"></i></a>
                    <a href="#" aria-label="Twitter"><i class="fa fa-twitter" title="Twitter"></i></a>
                    <a href="#" aria-label="LinkedIn"><i class="fa fa-linkedin" title="LinkedIn"></i></a>
                </div>

                <div class="mediot_footer_newsletter_v2">
                    <p>Subscribe for platform updates and wellness insights.</p>
                    <div class="mediot_footer_newsletter_box_v2">
                        <input type="email" placeholder="Your email"/>
                        <button type="button">Subscribe</button>
                    </div>
                </div>
            </div>
        </div>

        <div class="mediot_footer_bottom_v2">
            <p>© 2026 MedIoT. All rights reserved.</p>
        </div>
    </div>
</footer>
'''

pattern = re.compile(r'<footer\b.*?</footer>', re.S)
new_text, count = pattern.subn(new_footer, text, count=1)

if count != 1:
    raise SystemExit("Footer block not found in auth_pages.xml")

xml_path.write_text(new_text, encoding="utf-8")
print("FOOTER XML PATCHED:", count)
