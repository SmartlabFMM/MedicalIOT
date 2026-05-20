(function () {
    function text(el) {
        return ((el && el.innerText) || "").replace(/\s+/g, " ").trim();
    }

    function findByExactText(value) {
        return Array.from(document.querySelectorAll("body *")).find(function (el) {
            return text(el) === value;
        });
    }

    function findAncestor(el, keywords, minWidth, minHeight) {
        let node = el;
        for (let i = 0; i < 12 && node && node !== document.body; i++) {
            const t = text(node);
            const r = node.getBoundingClientRect();
            const okText = keywords.every(function (k) { return t.includes(k); });
            if (okText && r.width >= minWidth && r.height >= minHeight) {
                return node;
            }
            node = node.parentElement;
        }
        return null;
    }

    function applyLayout() {
        if (!(window.location.pathname.startsWith("/web") || window.location.pathname.startsWith("/odoo"))) return;

        const trendTitle = findByExactText("Patient Monitoring Trends");
        if (!trendTitle) return;

        const trendPanel = findAncestor(
            trendTitle,
            ["Patient Monitoring Trends", "Heart Rate", "SpO2", "Temperature"],
            600,
            260
        );

        const addPatient = Array.from(document.querySelectorAll("body *")).find(function (el) {
            return text(el).includes("Add Patient");
        });

        if (!trendPanel || !addPatient) return;

        const directoryPanel = findAncestor(
            addPatient,
            ["Total Patients", "Patient Name", "Patient Status", "Alerts", "Add Patient"],
            500,
            140
        );

        if (!directoryPanel || trendPanel.contains(directoryPanel) || directoryPanel.contains(trendPanel)) return;

        if (document.querySelector(".mediot-inspo-shell")) return;

        const header = document.querySelector(".mediot_compact_source_header") || trendPanel;

        const shell = document.createElement("div");
        shell.className = "mediot-inspo-shell";

        const grid = document.createElement("div");
        grid.className = "mediot-inspo-grid";

        header.parentElement.insertBefore(shell, header.nextSibling);
        shell.appendChild(grid);

        trendPanel.classList.add("mediot-inspo-trends");
        directoryPanel.classList.add("mediot-inspo-directory");

        grid.appendChild(trendPanel);
        grid.appendChild(directoryPanel);

        if (!directoryPanel.querySelector(".mediot-inspo-directory-title")) {
            const title = document.createElement("div");
            title.className = "mediot-inspo-directory-title";
            title.textContent = "Patient Directory";
            directoryPanel.insertBefore(title, directoryPanel.firstChild);
        }

        Array.from(trendPanel.querySelectorAll("div, section, article")).forEach(function (el) {
            const t = text(el);
            const r = el.getBoundingClientRect();
            if (
                r.width > 180 &&
                r.height > 80 &&
                (
                    t.includes("Heart Rate") ||
                    t.includes("SpO2") ||
                    t.includes("Temperature")
                )
            ) {
                el.classList.add("mediot-inspo-vital-card");
            }
        });
    }

    function start() {
        applyLayout();
        setTimeout(applyLayout, 500);
        setTimeout(applyLayout, 1500);
        setTimeout(applyLayout, 3000);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start);
    } else {
        start();
    }

    window.addEventListener("load", start);
})();

