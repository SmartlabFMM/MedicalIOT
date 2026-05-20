/** @odoo-module **/

function enhanceAdminTables() {
    const root = document.querySelector(".mediot-admin-dashboard-form");
    if (!root) return;

    const panels = root.querySelectorAll(".med_admin_panel");
    panels.forEach((panel) => {
        const table = panel.querySelector("table.o_list_table, table");
        if (!table || panel.dataset.mediotEnhanced === "1") return;

        panel.dataset.mediotEnhanced = "1";

        const title = panel.querySelector(".med_admin_panel_head h2")?.textContent?.trim() || "Table";
        const toolbar = document.createElement("div");
        toolbar.className = "med_admin_table_toolbar";

        const searchWrap = document.createElement("div");
        searchWrap.className = "med_admin_table_search";

        const icon = document.createElement("i");
        icon.className = "fa fa-search";
        icon.setAttribute("title", "Search");

        const input = document.createElement("input");
        input.type = "search";
        input.placeholder = `Search ${title.toLowerCase()}...`;
        input.setAttribute("aria-label", `Search ${title}`);

        const count = document.createElement("span");
        count.className = "med_admin_table_count";

        searchWrap.appendChild(icon);
        searchWrap.appendChild(input);
        toolbar.appendChild(searchWrap);
        toolbar.appendChild(count);

        const fieldWrapper = panel.querySelector(".med_admin_table") || table.parentElement;
        fieldWrapper.parentElement.insertBefore(toolbar, fieldWrapper);

        const updateRows = () => {
            const query = input.value.trim().toLowerCase();
            const rows = Array.from(table.querySelectorAll("tbody tr")).filter((row) => {
                return !row.classList.contains("o_list_footer");
            });

            let visible = 0;
            rows.forEach((row) => {
                const text = row.textContent.toLowerCase();
                const show = !query || text.includes(query);
                row.style.display = show ? "" : "none";
                if (show) visible += 1;
            });

            count.textContent = `${visible} visible`;
            panel.classList.toggle("med_admin_table_filtered", Boolean(query));
        };

        input.addEventListener("input", updateRows);
        updateRows();
    });
}

let scheduled = false;
function scheduleEnhance() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => {
        scheduled = false;
        enhanceAdminTables();
    });
}

document.addEventListener("DOMContentLoaded", scheduleEnhance);

const observer = new MutationObserver(scheduleEnhance);
observer.observe(document.body, { childList: true, subtree: true });