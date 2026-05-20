(function () {
    "use strict";

    const HOME = "/";
    const LOGOUT_URL = "/web/session/logout?redirect=/";

    function isLogoutLoginRedirect() {
        try {
            const params = new URLSearchParams(window.location.search);
            const redirect = params.get("redirect") || "";
            return window.location.pathname === "/web/login" && redirect.includes("/odoo");
        } catch (e) {
            return false;
        }
    }

    // If logout still sends user to /web/login?redirect=/odoo, immediately send home
    if (isLogoutLoginRedirect()) {
        window.location.replace(HOME);
        return;
    }

    function looksLikeLogout(el) {
        if (!el) return false;

        const href = el.getAttribute && (el.getAttribute("href") || "");
        const text = (el.textContent || "").toLowerCase();

        return (
            href.includes("/web/session/logout") ||
            text.includes("log out") ||
            text.includes("logout") ||
            text.includes("se déconnecter") ||
            text.includes("déconnexion") ||
            text.includes("deconnexion")
        );
    }

    function patchLogoutLinks() {
        document.querySelectorAll('a[href*="/web/session/logout"]').forEach(function (a) {
            a.setAttribute("href", LOGOUT_URL);
        });
    }

    document.addEventListener("click", function (ev) {
        const el = ev.target.closest("a, button, .dropdown-item, [role='menuitem'], .o-dropdown-item, .o_user_menu *");
        if (!el) return;

        let node = el;
        for (let i = 0; i < 5 && node; i++) {
            if (looksLikeLogout(node)) {
                ev.preventDefault();
                ev.stopPropagation();
                window.location.href = LOGOUT_URL;
                return;
            }
            node = node.parentElement;
        }
    }, true);

    patchLogoutLinks();
    setInterval(patchLogoutLinks, 800);
})();
