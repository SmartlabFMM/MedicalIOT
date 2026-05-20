/** @odoo-module **/
(function () {
    "use strict";

    let cachedGreeting = null;
    let isFetching = false;
    let applied = false;

    async function fetchGreeting() {
        if (cachedGreeting || isFetching) return cachedGreeting;
        isFetching = true;
        try {
            const response = await fetch("/mediot/current_user_greeting", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "same-origin",
                body: JSON.stringify({ jsonrpc: "2.0", method: "call", params: {}, id: Date.now() }),
            });
            const payload = await response.json();
            cachedGreeting = payload.result || null;
            return cachedGreeting;
        } catch (error) {
            console.warn("MedIoT greeting failed:", error);
            return null;
        } finally {
            isFetching = false;
        }
    }

    function normalize(text) {
        return (text || "").replace(/\s+/g, " ").trim();
    }

    function applyGreeting(data) {
        if (!data || !data.greeting || applied) return;
        const titles = document.querySelectorAll("h1, h2, .med-dashboard-title, .med_dashboard_title");
        for (const title of titles) {
            const txt = normalize(title.textContent);
            if ((txt === "Hi!" || txt === "Hi") && title.dataset.mediotGreetingApplied !== "1") {
                title.textContent = data.greeting;
                title.dataset.mediotGreetingApplied = "1";
                applied = true;
            }
        }
    }

    async function updateGreeting() {
        if (applied) return;
        const data = await fetchGreeting();
        applyGreeting(data);
    }

    // Only run once on load - no MutationObserver loop
    document.addEventListener("DOMContentLoaded", updateGreeting);
    window.addEventListener("load", updateGreeting);
    setTimeout(updateGreeting, 500);
})();