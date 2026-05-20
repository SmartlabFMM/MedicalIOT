(function () {
    function norm(s) {
        return (s || "").replace(/\s+/g, " ").trim();
    }

    function textIncludes(el, txt) {
        return norm(el.innerText || el.textContent).includes(txt);
    }

    function findTextNode(txt) {
        return [...document.querySelectorAll("h1,h2,h3,h4,h5,div,span,p,label,button,a,td,th")]
            .find(el => textIncludes(el, txt));
    }

    function findClosestControl(txt) {
        const el = findTextNode(txt);
        return el ? (el.closest("button,a,.btn,div,section,article") || el) : null;
    }

    function commonAncestor(a, b) {
        const seen = new Set();
        let x = a;
        while (x) {
            seen.add(x);
            x = x.parentElement;
        }
        let y = b;
        while (y) {
            if (seen.has(y)) return y;
            y = y.parentElement;
        }
        return null;
    }

    function findChartBlock(title) {
        const candidates = [...document.querySelectorAll("div,section,article")]
            .filter(el => {
                const t = norm(el.innerText);
                const hasChart = el.querySelector("canvas,svg,path,polyline,line");
                return t.includes(title) && hasChart;
            })
            .sort((a, b) => norm(a.innerText).length - norm(b.innerText).length);

        return candidates[0] || null;
    }

    function statusClass(status) {
        const s = norm(status).toLowerCase();
        if (s.includes("critical")) return "critical";
        if (s.includes("warning")) return "warning";
        return "stable";
    }

    function cardFromRow(tr) {
        const tds = [...tr.querySelectorAll("td")];
        if (!tds.length) return "";

        const img = tr.querySelector("img");
        const imgSrc = img ? img.src : "";
        const name = norm(tds[0]?.innerText) || "Patient";
        const patientId = norm(tds[1]?.innerText) || "";
        const condition = norm(tds[3]?.innerText) || "";
        const ecg = norm(tds[4]?.innerText) || "Normal sinus rhythm · Low";
        const status = norm(tds[5]?.innerText) || "Stable";
        const actionsHtml = tds[6] ? tds[6].innerHTML : "";

        return `
            <div class="mxd-patient-card">
                <div class="mxd-patient-top">
                    <div class="mxd-patient-main">
                        ${imgSrc ? `<img class="mxd-avatar" src="${imgSrc}" alt="${name}">` : ""}
                        <div>
                            <h4 class="mxd-patient-name">${name}</h4>
                            <div class="mxd-patient-id">${patientId}</div>
                        </div>
                    </div>
                    <div class="mxd-patient-actions">${actionsHtml}</div>
                </div>
                <div class="mxd-patient-bottom">
                    <div class="mxd-vitals">${condition || "SpO2: -- · -- BPM"}</div>
                    <div class="mxd-ecg">${ecg || "Normal sinus rhythm · Low"}</div>
                    <div class="mxd-status ${statusClass(status)}">${status}</div>
                </div>
            </div>
        `;
    }

    function moveIfExists(target, node, cls) {
        if (!target || !node) return;
        if (cls) node.classList.add(cls);
        target.appendChild(node);
    }

    function runExactDashboard() {
        if (!document.body.innerText.includes("Patient Monitoring Trends")) return;
        if (document.getElementById("mediot-exact-dashboard")) return;

        const welcomeTitle = findTextNode("Welcome, Doctor");
        const welcomeButton = findTextNode("Dashboard Overview");
        const hrBlock = findChartBlock("Heart Rate (BPM)");
        const spo2Block = findChartBlock("SpO2 (%)");
        const tempBlock = findChartBlock("Temperature (°C)");
        const table = document.querySelector("table");

        if (!welcomeTitle || !hrBlock || !spo2Block || !tempBlock || !table) return;

        const welcomeCard = commonAncestor(welcomeTitle, welcomeButton || welcomeTitle) || welcomeTitle.closest("div");
        const originalRoot = commonAncestor(welcomeCard, table) || table.closest("section") || table.parentElement;

        const totalPatients = findClosestControl("Total Patients");
        const addPatient = findClosestControl("Add Patient");
        const alerts = findClosestControl("Alerts");
        const patientStatus = findTextNode("Please choose")?.closest("div,button,a,select") || findClosestControl("Patient Status");
        const searchInput = document.querySelector('input[placeholder*="enter"], input[placeholder*="Please"], input[type="search"]');
        const searchWrap = searchInput ? (searchInput.closest("div,form") || searchInput) : null;

        const selectPatient = findClosestControl("Select patient");
        const last24 = findClosestControl("Last 24 Hours");
        const refreshBtn = [...document.querySelectorAll("button,a,.btn,div,span")]
            .find(el => norm(el.innerText) === "" && /rotate|refresh|sync/i.test(el.className))
            || [...document.querySelectorAll("button,a,.btn,div,span")]
            .find(el => norm(el.innerText).includes("↻"));

        const rows = [...table.querySelectorAll("tbody tr")].slice(0, 5);
        const patientCards = rows.map(cardFromRow).join("");

        const wrap = document.createElement("div");
        wrap.id = "mediot-exact-dashboard";
        wrap.innerHTML = `
            <div class="mxd-grid">
                <div class="mxd-left">
                    <div class="mxd-card mxd-welcome-host"></div>

                    <div class="mxd-card mxd-trends-card">
                        <div class="mxd-trends-top">
                            <div class="mxd-title-wrap">
                                <div class="mxd-iconbox">📈</div>
                                <div class="mxd-title-group">
                                    <h2>Patient Monitoring Trends</h2>
                                    <p>Real-time overview of vital signs</p>
                                    <div class="mxd-live">Live</div>
                                </div>
                            </div>
                            <div class="mxd-toolbar" id="mxd-toolbar"></div>
                        </div>
                        <div class="mxd-charts" id="mxd-charts"></div>
                    </div>
                </div>

                <div class="mxd-right">
                    <div class="mxd-card mxd-right-card">
                        <div class="mxd-right-head">
                            <h2>Patient Directory</h2>
                        </div>
                        <div class="mxd-dir-controls" id="mxd-dir-controls"></div>
                        <div class="mxd-patient-list">${patientCards}</div>
                    </div>
                </div>
            </div>
        `;

        originalRoot.parentElement.insertBefore(wrap, originalRoot);

        const welcomeHost = wrap.querySelector(".mxd-welcome-host");
        const chartsHost = wrap.querySelector("#mxd-charts");
        const toolbarHost = wrap.querySelector("#mxd-toolbar");
        const dirControlsHost = wrap.querySelector("#mxd-dir-controls");

        if (welcomeCard) welcomeHost.appendChild(welcomeCard);

        [selectPatient, last24, refreshBtn].forEach(node => {
            if (node) {
                if (node === selectPatient) node.classList.add("mxd-toolbar-grow");
                toolbarHost.appendChild(node);
            }
        });

        [hrBlock, spo2Block, tempBlock].forEach(node => {
            const outer = document.createElement("div");
            outer.className = "mxd-chart-wrap";
            outer.appendChild(node);
            chartsHost.appendChild(outer);
        });

        [totalPatients, searchWrap, patientStatus, alerts, addPatient].forEach(node => {
            if (!node) return;
            const holder = document.createElement("div");
            if (node === addPatient) holder.className = "mxd-full";
            holder.appendChild(node);
            dirControlsHost.appendChild(holder);
        });

        // hide old dashboard source
        originalRoot.classList.add("mxd-hide-original");
    }

    document.addEventListener("DOMContentLoaded", runExactDashboard);
    window.addEventListener("load", function () {
        setTimeout(runExactDashboard, 300);
        setTimeout(runExactDashboard, 900);
    });
})();
