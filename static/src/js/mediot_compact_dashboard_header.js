(function () {
    function compactHeader() {
        if (!window.location.pathname.startsWith("/web")) return;

        const bodyText = document.body.innerText || "";
        if (!bodyText.includes("Welcome to MedIoT Command Center")) return;
        if (document.getElementById("mediot_compact_header")) return;

        const all = Array.from(document.querySelectorAll("body *"));

        const welcomeEl = all.find(function (el) {
            const txt = (el.innerText || "").trim();
            return txt.includes("Welcome,") &&
                   txt.includes("Welcome to MedIoT Command Center") &&
                   txt.includes("Auto-refreshes");
        });

        if (!welcomeEl) return;

        let hero = welcomeEl;
        for (let i = 0; i < 6 && hero.parentElement; i++) {
            const txt = hero.innerText || "";
            const rect = hero.getBoundingClientRect();
            if (txt.includes("Welcome to MedIoT Command Center") && rect.height > 80) {
                break;
            }
            hero = hero.parentElement;
        }

        const userMatch = bodyText.match(/Welcome,\s*([^\n]+)/);
        const userName = userMatch ? userMatch[1].trim() : "Farah Mehrez";

        const compact = document.createElement("div");
        compact.id = "mediot_compact_header";
        compact.innerHTML = `
            <div style="
                display:flex;
                align-items:center;
                justify-content:space-between;
                gap:16px;
                padding:18px 22px;
                margin:14px 18px 18px 18px;
                background:#ffffff;
                border:1px solid #e6eaf2;
                border-radius:8px;
                box-shadow:0 2px 8px rgba(15,45,78,.06);
                font-family:inherit;
            ">
                <div>
                    <div style="font-size:17px;font-weight:700;color:#1f2937;">
                        Welcome, Doctor
                    </div>
                    <div style="font-size:13px;color:#667085;margin-top:4px;">
                        Bienvenue, Dr ${userName}
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="
                        padding:8px 12px;
                        background:#f3f6fb;
                        border:1px solid #dce4f2;
                        border-radius:6px;
                        color:#344054;
                        font-size:13px;
                        font-weight:600;
                    ">
                        Dashboard Overview
                    </span>
                </div>
            </div>
        `;

        hero.parentElement.insertBefore(compact, hero);
        hero.style.setProperty("display", "none", "important");
    }

    document.addEventListener("DOMContentLoaded", compactHeader);
    window.addEventListener("load", compactHeader);
    setTimeout(compactHeader, 500);
    setTimeout(compactHeader, 1500);
})();
