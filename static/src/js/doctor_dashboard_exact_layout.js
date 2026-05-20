(function () {
    function text(el) {
        return (el?.textContent || "").replace(/\s+/g, " ").trim();
    }

    function byExactText(selector, label) {
        return [...document.querySelectorAll(selector)].find(el => text(el) === label);
    }

    function byIncludes(selector, label) {
        return [...document.querySelectorAll(selector)].find(el => text(el).includes(label));
    }

    function closestLargeBlock(el) {
        let cur = el;
        while (cur && cur !== document.body) {
            const hasChart = cur.querySelector && cur.querySelector("canvas, svg");
            const hasTable = cur.querySelector && cur.querySelector("table");
            if (hasChart || hasTable || (cur.children && cur.children.length >= 3)) return cur;
            cur = cur.parentElement;
        }
        return el?.parentElement || null;
    }

    function findPatientTable() {
        return [...document.querySelectorAll("table")].find(t => {
            const headers = [...t.querySelectorAll("th")].map(th => text(th).toLowerCase());
            return headers.some(h => h.includes("patient name")) && headers.some(h => h.includes("actions"));
        });
    }

    function findToolbarBlock(root) {
        if (!root) return null;
        const all = [...root.querySelectorAll("div, section")];
        return all.find(el => {
            const s = text(el);
            return s.includes("Total Patients") && s.includes("Add Patient");
        }) || null;
    }

    function nearestCardFromTitle(titleEl) {
        let cur = titleEl;
        while (cur && cur !== document.body) {
            const hasChart = cur.querySelector && cur.querySelector("canvas, svg");
            if (hasChart) return cur;
            cur = cur.parentElement;
        }
        return titleEl?.parentElement || null;
    }

    function collectRows(table) {
        return [...table.querySelectorAll("tbody tr")].map(row => {
            const tds = [...row.querySelectorAll("td")];
            const img = row.querySelector("img")?.src || "";
            return {
                name: text(tds[0]) || "Patient",
                id: text(tds[1]) || "",
                condition: text(tds[3]) || "",
                ecg: text(tds[4]) || "",
                status: text(tds[5]) || "",
                actionsHtml: tds[6]?.innerHTML || "",
                avatar: img
            };
        }).filter(r => r.name);
    }

    function statusClass(status) {
        const s = (status || "").toLowerCase();
        if (s.includes("critical")) return "critical";
        if (s.includes("warning")) return "warning";
        if (s.includes("stable")) return "stable";
        if (s.includes("normal")) return "normal";
        return "stable";
    }

    function buildPatientCard(row) {
        const wrap = document.createElement("div");
        wrap.className = "mediot-patient-card";
        wrap.innerHTML = `
            <div class="mediot-patient-main">
                ${row.avatar ? `<img class="mediot-patient-avatar" src="${row.avatar}" alt="">` : `<div class="mediot-patient-avatar"></div>`}
                <div>
                    <div class="mediot-patient-name">${row.name}</div>
                    <div class="mediot-patient-id">${row.id}</div>
                    <div class="mediot-patient-meta">${row.condition || ""}</div>
                    <div class="mediot-patient-ecg">${row.ecg || ""}</div>
                </div>
            </div>
            <div class="mediot-status-wrap">
                <span class="mediot-status-badge ${statusClass(row.status)}">${row.status || "Stable"}</span>
            </div>
            <div class="mediot-actions-wrap">${row.actionsHtml}</div>
        `;
        return wrap;
    }

    function buildExactDashboard() {
        if (document.querySelector(".mediot-exact-shell")) return;
        if (!(location.pathname.startsWith("/web") || location.pathname.startsWith("/odoo"))) return;

        const table = findPatientTable();
        const trendTitle = byExactText("h1,h2,h3,h4,h5,div,span,strong", "Patient Monitoring Trends");
        if (!table || !trendTitle) return;

        const trendSource = closestLargeBlock(trendTitle);
        const patientSource = closestLargeBlock(table);
        const welcomeTitle = byIncludes("h1,h2,h3,h4,h5,div,span,strong", "Welcome, Doctor");
        const welcomeSource = welcomeTitle ? closestLargeBlock(welcomeTitle) : null;
        const dashboardHost = (welcomeSource || trendSource || patientSource)?.parentElement;
        if (!dashboardHost) return;

        const rows = collectRows(table);
        const toolbarSource = findToolbarBlock(patientSource);

        const shell = document.createElement("div");
        shell.className = "mediot-exact-shell";

        if (welcomeSource) {
            const top = document.createElement("div");
            top.className = "mediot-exact-top mediot-exact-panel mediot-exact-welcome";
            top.appendChild(welcomeSource.cloneNode(true));
            shell.appendChild(top);
        }

        const main = document.createElement("div");
        main.className = "mediot-exact-main";

        const left = document.createElement("div");
        left.className = "mediot-exact-panel mediot-exact-vitals";
        const right = document.createElement("div");
        right.className = "mediot-exact-panel mediot-exact-directory";

        /* ---------- LEFT: VITALS ---------- */
        const trendSubtitle = byIncludes("p,div,span", "Real-time overview of vital signs");
        const selectPatient = byIncludes("button,a,div,span,label", "Select patient");
        const last24 = byIncludes("button,a,div,span,label", "Last 24");
        const liveBadge = byIncludes("div,span", "Live");

        const head = document.createElement("div");
        head.className = "mediot-section-head";
        head.innerHTML = `
            <div class="mediot-section-head-left">
                <div class="mediot-head-icon">📈</div>
                <div>
                    <h3 class="mediot-section-title">Patient Monitoring Trends</h3>
                    <p class="mediot-section-subtitle">Real-time overview of vital signs</p>
                </div>
            </div>
            <div class="mediot-top-controls"></div>
        `;
        left.appendChild(head);

        const live = document.createElement("div");
        live.className = "mediot-live-badge";
        live.innerHTML = `<span class="mediot-live-dot"></span><span>Live</span>`;
        left.appendChild(live);

        const controlsWrap = head.querySelector(".mediot-top-controls");
        const controls = [];
        const allPossibleControls = [...document.querySelectorAll("button, a, input, select, .btn, .dropdown, .form-control")];
        allPossibleControls.forEach(el => {
            const s = text(el);
            if (
                s.includes("Select patient") ||
                s.includes("Last 24") ||
                s.includes("Hours") ||
                (el.tagName === "SELECT") ||
                (el.tagName === "INPUT" && (el.placeholder || "").toLowerCase().includes("patient"))
            ) {
                controls.push(el.cloneNode(true));
            }
        });

        const added = new Set();
        controls.forEach(el => {
            const key = text(el) + "|" + (el.placeholder || "") + "|" + el.tagName;
            if (!added.has(key)) {
                controlsWrap.appendChild(el);
                added.add(key);
            }
        });

        const stack = document.createElement("div");
        stack.className = "mediot-vitals-stack";

        const vitalTitles = [
            byIncludes("h1,h2,h3,h4,h5,div,span,strong", "Heart Rate"),
            byIncludes("h1,h2,h3,h4,h5,div,span,strong", "SpO2"),
            byIncludes("h1,h2,h3,h4,h5,div,span,strong", "Temperature")
        ].filter(Boolean);

        const uniqueBlocks = [];
        vitalTitles.forEach(t => {
            const block = nearestCardFromTitle(t);
            if (block && !uniqueBlocks.includes(block)) uniqueBlocks.push(block);
        });

        uniqueBlocks.forEach(block => {
            const box = document.createElement("div");
            box.className = "mediot-vital-box";

            const titleEl = [...block.querySelectorAll("h1,h2,h3,h4,h5,div,span,strong")].find(el => {
                const s = text(el);
                return s.includes("Heart Rate") || s.includes("SpO2") || s.includes("Temperature");
            });

            const valueEl = [...block.querySelectorAll("h1,h2,h3,h4,h5,div,span,strong")].find(el => {
                const s = text(el);
                return /\d/.test(s) && (s.includes("BPM") || s.includes("%") || s.includes("°C"));
            });

            const chart = block.querySelector("canvas, svg");
            const row = document.createElement("div");
            row.className = "mediot-vital-row";
            row.innerHTML = `
                <div class="mediot-vital-title">${titleEl ? text(titleEl) : ""}</div>
                <div class="mediot-vital-value">${valueEl ? text(valueEl) : ""}</div>
            `;
            box.appendChild(row);

            if (chart) box.appendChild(chart.cloneNode(true));
            stack.appendChild(box);
        });

        left.appendChild(stack);

        /* ---------- RIGHT: DIRECTORY ---------- */
        const title = document.createElement("h3");
        title.className = "mediot-directory-title";
        title.textContent = "Patient Directory";
        right.appendChild(title);

        const toolbar = document.createElement("div");
        toolbar.className = "mediot-directory-toolbar";

        const toolbarItems = [];
        [...document.querySelectorAll("button,a,input,select,.btn,.form-control")].forEach(el => {
            const s = text(el);
            const ph = (el.placeholder || "");
            if (
                s.includes("Total Patients") ||
                s.includes("Patient Status") ||
                s.includes("Alerts") ||
                s.includes("Add Patient") ||
                ph.toLowerCase().includes("enter here") ||
                ph.toLowerCase().includes("search")
            ) {
                toolbarItems.push(el.cloneNode(true));
            }
        });

        const toolbarSeen = new Set();
        toolbarItems.forEach(el => {
            const key = text(el) + "|" + (el.placeholder || "") + "|" + el.tagName;
            if (!toolbarSeen.has(key)) {
                toolbar.appendChild(el);
                toolbarSeen.add(key);
            }
        });
        right.appendChild(toolbar);

        const list = document.createElement("div");
        list.className = "mediot-patient-list";
        rows.slice(0, 8).forEach(r => list.appendChild(buildPatientCard(r)));
        right.appendChild(list);

        main.appendChild(left);
        main.appendChild(right);
        shell.appendChild(main);

        dashboardHost.prepend(shell);

        if (welcomeSource) welcomeSource.classList.add("mediot-hide-original");
        if (trendSource) trendSource.classList.add("mediot-hide-original");
        if (patientSource) patientSource.classList.add("mediot-hide-original");
    }

    function run() {
        try { buildExactDashboard(); } catch (e) { console.log("doctor_dashboard_exact_layout:", e); }
    }

    document.addEventListener("DOMContentLoaded", run);
    window.addEventListener("load", run);
    setTimeout(run, 500);
    setTimeout(run, 1500);
})();
