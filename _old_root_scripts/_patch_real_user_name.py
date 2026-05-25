from pathlib import Path

js_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\js\dashboard.js")
js = js_path.read_text(encoding="utf-8")

# Ensure userName exists
if "userName:" not in js:
    js = js.replace(
        "loading:     true,",
        "loading:     true,\n            userName:    '',"
    )

patch = r'''
            // REAL LOGGED USER NAME PATCH
            try {
                const response = await fetch("/web/session/get_session_info", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        jsonrpc: "2.0",
                        method: "call",
                        params: {}
                    })
                });
                const sessionData = await response.json();
                const userName = sessionData?.result?.name || sessionData?.result?.username || "";
                if (userName) {
                    this.state.userName = userName;
                }
            } catch (e) {}
'''

if "REAL LOGGED USER NAME PATCH" not in js:
    js = js.replace(
        "async _load() {\n        try {",
        "async _load() {\n        try {\n" + patch
    )

js_path.write_text(js, encoding="utf-8")
print("Real user name patch added")
