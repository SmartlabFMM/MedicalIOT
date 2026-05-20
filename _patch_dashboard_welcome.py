from pathlib import Path

js_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\js\dashboard.js")
xml_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\xml\dashboard.xml")

js = js_path.read_text(encoding="utf-8")
xml = xml_path.read_text(encoding="utf-8")

# Add session import
if 'from "@web/session"' not in js:
    js = js.replace(
        'import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";',
        'import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";\nimport { session } from "@web/session";'
    )

# Add userName to state
if 'userName:' not in js:
    js = js.replace(
        'loading:     true,',
        'loading:     true,\n            userName:    session.name || "",'
    )

# Fetch real user name once
if 'WELCOME USER NAME PATCH' not in js:
    js = js.replace(
        'async _load() {\n        try {',
        '''async _load() {
        try {
            // WELCOME USER NAME PATCH
            if (!this.state.userName && session.uid) {
                try {
                    const users = await this.orm.read("res.users", [session.uid], ["name"]);
                    if (users && users[0] && users[0].name) {
                        this.state.userName = users[0].name;
                    }
                } catch (e) {}
            }'''
    )

# Replace Hi!
old = '<div class="med_banner_greeting">Hi!</div>'
new = '''<div class="med_banner_greeting">
                        <t t-if="state.userName">Welcome, Dr <t t-esc="state.userName"/></t>
                        <t t-else="">Welcome, Doctor</t>
                    </div>'''

if old not in xml:
    raise SystemExit("Could not find exact Hi! greeting in dashboard.xml")

xml = xml.replace(old, new, 1)

js_path.write_text(js, encoding="utf-8")
xml_path.write_text(xml, encoding="utf-8")

print("Dashboard greeting patched")
