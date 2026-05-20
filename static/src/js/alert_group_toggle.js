
/** @odoo-module **/

function normalizeAlertPills(root) {
    root.querySelectorAll(".o_med_alert_card").forEach((card) => {
        const badge = card.querySelector(".o_med_alert_badge");
        if (badge) {
            const txt = (badge.textContent || "").trim().toLowerCase();
            if (txt.includes("warning")) {
                badge.classList.add("badge-warning", "med_force_warning_badge");
            } else if (txt.includes("critical")) {
                badge.classList.add("badge-critical", "med_force_critical_badge");
            }
        }

        const state = card.querySelector(".o_med_alert_state");
        if (state) {
            const txt = (state.textContent || "").trim().toLowerCase();
            if (txt.includes("new")) {
                state.classList.add("state-new", "med_force_state_new");
                if (!state.querySelector(".o_med_alert_dot")) {
                    const dot = document.createElement("span");
                    dot.className = "o_med_alert_dot";
                    state.prepend(dot);
                }
            }
        }
    });
}

function setupAlertGroupToggles(root) {
    const groups = root.querySelectorAll(".o_med_alert_kanban .o_kanban_group");

    groups.forEach((group) => {
        const header = group.querySelector(".o_kanban_group_header, .o_kanban_header");
        if (!header) return;

        const cards = Array.from(group.querySelectorAll(".o_kanban_record"))
            .filter((record) => record.querySelector(".o_med_alert_card"));

        const existingBtn = header.querySelector(".med_alert_group_toggle");

        if (cards.length <= 1) {
            cards.forEach((record) => record.classList.remove("med_alert_extra_hidden"));
            if (existingBtn) existingBtn.remove();
            group.dataset.medAlertCount = String(cards.length);
            group.dataset.medAlertExpanded = "1";
            return;
        }

        if (!group.dataset.medAlertExpanded) {
            group.dataset.medAlertExpanded = "0";
        }

        const expanded = group.dataset.medAlertExpanded === "1";
        const extraCards = cards.slice(1);

        extraCards.forEach((record) => {
            record.classList.toggle("med_alert_extra_hidden", !expanded);
        });

        let btn = existingBtn;

        if (!btn) {
            btn = document.createElement("button");
            btn.type = "button";
            btn.className = "med_alert_group_toggle";
            header.appendChild(btn);

            btn.addEventListener("click", (ev) => {
                ev.preventDefault();
                ev.stopPropagation();

                const isExpanded = group.dataset.medAlertExpanded === "1";
                group.dataset.medAlertExpanded = isExpanded ? "0" : "1";

                const nowExpanded = group.dataset.medAlertExpanded === "1";
                const currentCards = Array.from(group.querySelectorAll(".o_kanban_record"))
                    .filter((record) => record.querySelector(".o_med_alert_card"));

                currentCards.slice(1).forEach((record) => {
                    record.classList.toggle("med_alert_extra_hidden", !nowExpanded);
                });

                btn.textContent = nowExpanded ? "?" : "+";
                btn.setAttribute("title", nowExpanded ? "Hide extra alerts" : "Show more alerts");
            });
        }

        const wantedText = expanded ? "?" : "+";
        if (btn.textContent !== wantedText) {
            btn.textContent = wantedText;
        }

        btn.setAttribute("title", expanded ? "Hide extra alerts" : "Show more alerts");
        group.dataset.medAlertCount = String(cards.length);
    });
}

let scheduled = false;

function applyAlertEnhancements() {
    if (scheduled) return;

    scheduled = true;

    window.requestAnimationFrame(() => {
        scheduled = false;
        normalizeAlertPills(document);
        setupAlertGroupToggles(document);
    });
}

function boot() {
    applyAlertEnhancements();

    const observer = new MutationObserver(() => {
        applyAlertEnhancements();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
} else {
    boot();
}
