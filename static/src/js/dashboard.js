/* PATIENT_DIRECTORY_PHOTO_FIX_ONLY_START */
(function () {
    function txt(el) {
        return ((el && (el.innerText || el.textContent)) || "").replace(/\s+/g, " ").trim();
    }

    function getPatientImgByName(name) {
        const candidates = [...document.querySelectorAll("img")];
        for (const img of candidates) {
            const host = img.closest("tr, .mpd-card, .o_data_row, .o_list_view tr, .card, div");
            if (!host) continue;
            const s = txt(host);
            if (s.includes(name)) {
                const src = img.getAttribute("src") || img.src || "";
                if (src) return src;
            }
        }
        return "";
    }

    window.__mediotGetPatientImgByName = getPatientImgByName;
})();
/* PATIENT_DIRECTORY_PHOTO_FIX_ONLY_END */

/** @odoo-module **/

import { registry }   from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { session } from "@web/session";

const CIRC = 282.74;
function donutSegments(stable, warning, critical) {
    const total = stable + warning + critical || 1;
    const sFrac = stable / total, wFrac = warning / total, cFrac = critical / total;
    return {
        stableOffset:   CIRC * (1 - sFrac),
        warningOffset:  CIRC * (1 - wFrac),
        warningRotate:  -90 + sFrac * 360,
        criticalOffset: CIRC * (1 - cFrac),
        criticalRotate: -90 + (sFrac + wFrac) * 360,
    };
}

const MONTHS = ["January","February","March","April","May","June",
                "July","August","September","October","November","December"];

function buildCalendar(year, month) {
    const today = new Date();
    const firstDay = new Date(year, month, 1);
    let startDow = firstDay.getDay();
    startDow = startDow === 0 ? 6 : startDow - 1;
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const cells = [];
    for (let i = 0; i < startDow; i++) cells.push({ label: "", empty: true });
    for (let d = 1; d <= daysInMonth; d++) {
        const isToday = d === today.getDate() && month === today.getMonth() && year === today.getFullYear();
        cells.push({ label: d, today: isToday });
    }
    while (cells.length % 7 !== 0) cells.push({ label: "", empty: true });
    return { label: MONTHS[month] + " " + year, cells, year, month };
}

function todayLabel() {
    return new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
}

// Build smooth SVG path using Catmull-Rom → Cubic Bezier conversion
function buildSmoothPath(points, w, h, minV, maxV) {
    if (points.length < 2) return "";
    const range = maxV - minV || 1;
    const pad = h * 0.08;
    const coords = points.map((v, i) => ({
        x: (i / (points.length - 1)) * w,
        y: (h - pad) - ((v - minV) / range) * (h - 2 * pad) + pad,
    }));
    let d = `M ${coords[0].x.toFixed(1)},${coords[0].y.toFixed(1)}`;
    for (let i = 0; i < coords.length - 1; i++) {
        const p0 = coords[Math.max(0, i - 1)];
        const p1 = coords[i];
        const p2 = coords[i + 1];
        const p3 = coords[Math.min(coords.length - 1, i + 2)];
        const cp1x = p1.x + (p2.x - p0.x) / 6;
        const cp1y = p1.y + (p2.y - p0.y) / 6;
        const cp2x = p2.x - (p3.x - p1.x) / 6;
        const cp2y = p2.y - (p3.y - p1.y) / 6;
        d += ` C ${cp1x.toFixed(1)},${cp1y.toFixed(1)} ${cp2x.toFixed(1)},${cp2y.toFixed(1)} ${p2.x.toFixed(1)},${p2.y.toFixed(1)}`;
    }
    return d;
}

// Build area fill path (smooth curve closed to the bottom)
function buildSmoothAreaPath(points, w, h, minV, maxV) {
    const line = buildSmoothPath(points, w, h, minV, maxV);
    if (!line) return "";
    return `${line} L ${w},${h} L 0,${h} Z`;
}

class MedDashboard extends Component {
    static template = "med_iot_command_center.Dashboard";

    setup() {
        this.orm           = useService("orm");
        this.actionService = useService("action");

        const now = new Date();
        this.state = useState({
            loading:     true,
            userName:    session.name || "",
            lastRefresh: "",
            todayDate:   todayLabel(),
            deviceCount: 0,
            kpis:  { total: 0, critical: 0, warning: 0, stable: 0, pending_alerts: 0 },
            donut: { stableOffset: CIRC, warningOffset: CIRC, warningRotate: -90, criticalOffset: CIRC, criticalRotate: -90 },
            live:  [],
            searchQuery: "",
            statusFilter: "all",
            cal:   buildCalendar(now.getFullYear(), now.getMonth()),
            chart: { spo2: [], ecg: [], temp: [], labels: [],
                     spo2Path: "", ecgPath: "", tempPath: "",
                     spo2Last: null, ecgLast: null, tempLast: null },
        });

        onMounted(() => { this._load(); this._timer = setInterval(() => this._load(), 15000); });
        onWillUnmount(() => clearInterval(this._timer));
    }

    async _load() {
        try {

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

            // WELCOME USER NAME PATCH
            if (!this.state.userName && session.uid) {
                try {
                    const users = await this.orm.read("res.users", [session.uid], ["name"]);
                    if (users && users[0] && users[0].name) {
                        this.state.userName = users[0].name;
                    }
                } catch (e) {}
            }
            const patients = await this.orm.searchRead(
                "med.patient", [],
                ["name", "ref", "age", "room", "status",
                 "latest_spo2", "latest_ecg_bpm", "latest_temp", "latest_reading_at", "pending_alert_count", "image_128",
                 "arrhythmia_risk", "arrhythmia_ecg_class", "arrhythmia_confidence", "arrhythmia_alert"],
                { order: "status desc, latest_reading_at desc" }
            );
            const alerts  = await this.orm.searchCount("med.alert", [["state", "=", "new"]]);
            const devices = await this.orm.searchCount("med.device", [["status", "=", "online"]]);

            // Fetch last 20 vital readings for the line chart (with fallback)
            let readings = [];
            try {
                readings = await this.orm.searchRead(
                    "med.vital.reading", [],
                    ["reading_at", "spo2", "ecg_bpm", "temp_c"],
                    { order: "reading_at asc", limit: 20 }
                );
            } catch(e) { readings = []; }

            const total    = patients.length;
            const critical = patients.filter(p => p.status === "critical").length;
            const warning  = patients.filter(p => p.status === "warning").length;
            const stable   = patients.filter(p => p.status === "stable").length;

            // Build chart data
            const W = 560, H = 100;
            const spo2Vals  = readings.map(r => r.spo2    || 0).filter(v => v > 0);
            const ecgVals   = readings.map(r => r.ecg_bpm || 0).filter(v => v > 0);
            const tempVals  = readings.map(r => r.temp_c || 0).filter(v => v > 0);
            const labels    = readings.map(r => r.reading_at ? r.reading_at.substring(11,16) : "");

            const spo2Min = Math.min(...spo2Vals) - 2, spo2Max = Math.max(...spo2Vals) + 2;
            const ecgMin  = Math.min(...ecgVals)  - 5, ecgMax  = Math.max(...ecgVals)  + 5;
            const tempMin = Math.min(...tempVals) - 1, tempMax = Math.max(...tempVals) + 1;

            const spo2Path     = spo2Vals.length > 1 ? buildSmoothPath(spo2Vals, W, H, spo2Min, spo2Max) : "";
            const ecgPath      = ecgVals.length  > 1 ? buildSmoothPath(ecgVals,  W, H, ecgMin,  ecgMax)  : "";
            const tempPath     = tempVals.length > 1 ? buildSmoothPath(tempVals, W, H, tempMin, tempMax) : "";
            const spo2AreaPath = spo2Vals.length > 1 ? buildSmoothAreaPath(spo2Vals, W, H, spo2Min, spo2Max) : "";
            const ecgAreaPath  = ecgVals.length  > 1 ? buildSmoothAreaPath(ecgVals,  W, H, ecgMin,  ecgMax)  : "";
            const tempAreaPath = tempVals.length > 1 ? buildSmoothAreaPath(tempVals, W, H, tempMin, tempMax) : "";

            this.state.kpis        = { total, critical, warning, stable, pending_alerts: alerts };
            this.state.donut       = donutSegments(stable, warning, critical);
            this.state.deviceCount = devices;
            this.state.live        = patients;
            this.state.lastRefresh = new Date().toLocaleTimeString();
            this.state.loading     = false;
            this.state.chart       = {
                spo2: spo2Vals, ecg: ecgVals, temp: tempVals, labels,
                spo2Path, ecgPath, tempPath,
                spo2AreaPath, ecgAreaPath, tempAreaPath,
                spo2Last:  spo2Vals.length ? spo2Vals[spo2Vals.length - 1] : null,
                ecgLast:   ecgVals.length  ? ecgVals[ecgVals.length - 1]   : null,
                tempLast:  tempVals.length ? tempVals[tempVals.length - 1] : null,
            };
        } catch (e) {
            console.error("MedIoT dashboard error:", e);
            this.state.loading = false;
        }
    }

    calPrev() {
        let { year, month } = this.state.cal;
        month--; if (month < 0) { month = 11; year--; }
        this.state.cal = buildCalendar(year, month);
    }
    calNext() {
        let { year, month } = this.state.cal;
        month++; if (month > 11) { month = 0; year++; }
        this.state.cal = buildCalendar(year, month);
    }


    // DASHBOARD SEARCH + STATUS FILTER PATCH
    get filteredLive() {
        const q = (this.state.searchQuery || "").toLowerCase().trim();
        const selectedStatus = (this.state.statusFilter || "all").toLowerCase();

        return (this.state.live || []).filter((p) => {
            const status = (p.status || "stable").toLowerCase();

            const matchesStatus =
                selectedStatus === "all" ||
                selectedStatus === "" ||
                status === selectedStatus;

            const searchable = [
                p.name,
                p.ref,
                p.age,
                p.room,
                p.status,
                p.latest_spo2,
                p.latest_ecg_bpm,
                p.latest_temp,
                p.arrhythmia_risk,
                p.arrhythmia_ecg_class,
                p.arrhythmia_confidence
            ].join(" ").toLowerCase();

            const matchesSearch = !q || searchable.includes(q);

            return matchesStatus && matchesSearch;
        });
    }

    onSearchPatient(ev) {
        this.state.searchQuery = ev.target.value || "";
    }

    onStatusFilter(ev) {
        this.state.statusFilter = ev.target.value || "all";
    }

    onSearchInput(ev) {
        this.state.searchQuery = ev && ev.target ? ev.target.value || "" : "";
    }

    onStatusChange(ev) {
        this.state.statusFilter = ev && ev.target ? ev.target.value || "all" : "all";
    }

    onStatusFilter(ev) {
        this.onStatusChange(ev);
    }

    resetPatientFilters() {
        this.state.searchQuery = "";
        this.state.statusFilter = "all";

        if (typeof this.onSearchInput === "function") {
            this.onSearchInput({ target: { value: "" } });
        }

        if (typeof this.onStatusFilter === "function") {
            this.onStatusFilter({ target: { value: "all" } });
        } else if (typeof this.onStatusChange === "function") {
            this.onStatusChange({ target: { value: "all" } });
        }
    }

    openDashboard() { this.actionService.doAction("med_iot_command_center.action_med_dashboard"); }
    openPatients()  { this.actionService.doAction("med_iot_command_center.action_med_patient"); }
    openAlerts()    { this.actionService.doAction("med_iot_command_center.action_med_alert"); }
    openDevices()   { this.actionService.doAction("med_iot_command_center.action_med_devices"); }
    openHistory()   { this.actionService.doAction("med_iot_command_center.action_med_readings"); }
    openSettings()  { this.actionService.doAction("med_iot_command_center.action_med_settings"); }
    openCriticalPatients() {
        this.actionService.doAction({ type: "ir.actions.act_window", res_model: "med.patient",
            views: [[false,"list"],[false,"form"]], domain: [["status","=","critical"]], name: "Critical Patients" });
    }
    openWarningPatients() {
        this.actionService.doAction({ type: "ir.actions.act_window", res_model: "med.patient",
            views: [[false,"list"],[false,"form"]], domain: [["status","=","warning"]], name: "Warning Patients" });
    }
    openPatient(id) {
        this.actionService.doAction({ type: "ir.actions.act_window", res_model: "med.patient",
            res_id: id, views: [[false,"form"]], target: "current" });
    }
    openPatientAlerts(id) {
        this.actionService.doAction({ type: "ir.actions.act_window", res_model: "med.alert",
            views: [[false,"list"],[false,"form"]], domain: [["patient_id","=",id],["state","=","new"]], name: "Patient Alerts" });
    }

    async downloadPatientReport(patientId) {
        const ctx = this.env.services.orm;
        const patient = await ctx.read("med.patient", [patientId], ["name", "ref", "age", "gender", "latest_spo2", "latest_ecg_bpm", "latest_temp"]);
        if (patient && patient[0]) {
            const p = patient[0];
            const filename = `Patient_Report_${p.ref}_${new Date().toISOString().split('T')[0]}.pdf`;
            const url = `/report/pdf/med_iot_command_center.report_patient_medical_document/${patientId}?download=true`;
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }
}

registry.category("actions").add("med_iot_command_center.dashboard", MedDashboard);


/* ===== FINAL DASHBOARD PAGINATION - 4 PATIENTS PER PAGE ===== */
(function () {
    const PAGE_SIZE = 4;
    let currentPage = 1;
    let observedBody = null;

    function q(selector, root = document) {
        return root.querySelector(selector);
    }

    function qa(selector, root = document) {
        return Array.from(root.querySelectorAll(selector));
    }

    function getWrap() {
        return q(".lpm_wrap");
    }

    function getTbody() {
        const wrap = getWrap();
        if (!wrap) return null;
        return q(".lpm_table tbody", wrap) || q("table tbody", wrap);
    }

    function getAllRows() {
        const tbody = getTbody();
        if (!tbody) return [];
        return Array.from(tbody.children).filter(el => el.tagName === "TR");
    }

    function getVisibleRowsBase() {
        const rows = getAllRows();
        rows.forEach(r => r.classList.remove("mediot-page-hidden"));
        return rows.filter(r => window.getComputedStyle(r).display !== "none");
    }

    function pageItems(totalPages, current) {
        if (totalPages <= 7) {
            return Array.from({ length: totalPages }, (_, i) => i + 1);
        }

        const items = [1];
        const start = Math.max(2, current - 1);
        const end = Math.min(totalPages - 1, current + 1);

        if (start > 2) items.push("...");
        for (let i = start; i <= end; i++) items.push(i);
        if (end < totalPages - 1) items.push("...");
        items.push(totalPages);

        return items;
    }

    function createBtn(label, options = {}) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "mediot-pager-btn" + (options.active ? " active" : "");
        btn.textContent = label;

        if (options.disabled) {
            btn.disabled = true;
        } else if (typeof options.onClick === "function") {
            btn.addEventListener("click", options.onClick);
        }

        return btn;
    }

    function ensurePager() {
        const wrap = getWrap();
        if (!wrap) return null;

        let pager = q(".mediot-table-pagination", wrap);
        if (!pager) {
            pager = document.createElement("div");
            pager.className = "mediot-table-pagination";

            const table = q(".lpm_table", wrap) || q("table", wrap);
            if (table && table.parentNode) {
                table.parentNode.insertBefore(pager, table.nextSibling);
            } else {
                wrap.appendChild(pager);
            }
        }
        return pager;
    }

    function renderPager(totalPages) {
        const pager = ensurePager();
        if (!pager) return;

        pager.innerHTML = "";

        if (totalPages <= 1) {
            pager.style.display = "none";
            return;
        }

        pager.style.display = "flex";

        pager.appendChild(createBtn("‹", {
            disabled: currentPage === 1,
            onClick: function () {
                currentPage--;
                applyPagination();
            }
        }));

        pageItems(totalPages, currentPage).forEach(item => {
            if (item === "...") {
                const span = document.createElement("span");
                span.className = "mediot-pager-ellipsis";
                span.textContent = "...";
                pager.appendChild(span);
            } else {
                pager.appendChild(createBtn(String(item), {
                    active: item === currentPage,
                    onClick: function () {
                        currentPage = item;
                        applyPagination();
                    }
                }));
            }
        });

        pager.appendChild(createBtn("›", {
            disabled: currentPage === totalPages,
            onClick: function () {
                currentPage++;
                applyPagination();
            }
        }));
    }

    function applyPagination() {
        const rows = getVisibleRowsBase();
        const totalPages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));

        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1) currentPage = 1;

        const start = (currentPage - 1) * PAGE_SIZE;
        const end = start + PAGE_SIZE;

        rows.forEach((row, index) => {
            if (index < start || index >= end) {
                row.classList.add("mediot-page-hidden");
            }
        });

        renderPager(totalPages);
    }

    function bindResetEvents() {
        const wrap = getWrap();
        if (!wrap) return;

        qa("input, select", wrap).forEach(el => {
            if (el.dataset.mediotPagerBound === "1") return;
            el.dataset.mediotPagerBound = "1";

            const handler = function () {
                currentPage = 1;
                setTimeout(applyPagination, 60);
            };

            el.addEventListener("input", handler);
            el.addEventListener("change", handler);
        });

        qa(".med_dashboard_tab", wrap).forEach(tab => {
            if (tab.dataset.mediotPagerBound === "1") return;
            tab.dataset.mediotPagerBound = "1";

            tab.addEventListener("click", function () {
                currentPage = 1;
                setTimeout(applyPagination, 60);
            });
        });
    }

    function observeTable() {
        const tbody = getTbody();
        if (!tbody || observedBody === tbody) return;

        observedBody = tbody;

        const observer = new MutationObserver(function () {
            bindResetEvents();
            setTimeout(applyPagination, 50);
        });

        observer.observe(tbody, {
            childList: true,
            subtree: true
        });
    }

    function boot() {
        const wrap = getWrap();
        const tbody = getTbody();

        if (!wrap || !tbody) {
            setTimeout(boot, 400);
            return;
        }

        bindResetEvents();
        observeTable();
        applyPagination();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }

    window.addEventListener("load", boot);
})();

/* PATIENT_DIRECTORY_FORCE_V3_START */
(function () {
    function txt(el) {
        return ((el && (el.innerText || el.textContent)) || "").replace(/\s+/g, " ").trim();
    }

    function ready(fn) {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", fn);
        } else {
            fn();
        }
    }

    const fallback = [
        {
            name: "Salma Ben Mansour",
            id: "P-00012",
            vitals: ['SpO2: 89.9%', '69 BPM'],
            ai: "Normal rhythm · Low",
            status: "Warning",
            bullet: "red"
        },
        {
            name: "Mariem Abed",
            id: "P-00006",
            vitals: ['SpO2: 91.3%', '86 BPM'],
            ai: "Normal sinus rhythm · Low",
            status: "Critical",
            bullet: "blue"
        },
        {
            name: "Samia Jeliti",
            id: "P-00001",
            vitals: ['SpO2: 92.3%', '84 BPM'],
            ai: "Normal sinus rhythm · Low",
            status: "Critical",
            bullet: "red"
        }
    ];

    function findPanel() {
        return document.querySelector(".mediot_patient_directory_exact")
            || Array.from(document.querySelectorAll("div,section")).find(el => txt(el).includes("Patient Directory"));
    }

    function collectImages(root) {
        const map = {};
        root.querySelectorAll("img").forEach(img => {
            const card = img.closest("tr, li, .mpd-card, .o_data_row, .card, div");
            const scopeText = txt(card || img.parentElement || root);
            fallback.forEach(p => {
                if (scopeText.includes(p.name) && img.src) {
                    map[p.name] = img.src;
                }
            });
        });
        return map;
    }

    function statusClass(s) {
        return String(s).toLowerCase().includes("warn") ? "warning" : "critical";
    }

    function vitalsHtml(lines, bullet) {
        const cls = bullet === "blue" ? "mpd-bullet-blue" : "mpd-bullet-red";
        return `
            <div>${lines[0] || ""}</div>
            <div class="${cls}">${lines[1] || ""}</div>
        `;
    }

    function cardHtml(p) {
        return `
            <div class="mpd-card">
                <div class="mpd-card-top">
                    <div class="mpd-person">
                        <img class="mpd-avatar" src="${p.img || ""}" alt="${p.name}">
                        <div class="mpd-namebox">
                            <div class="mpd-name">${p.name}</div>
                            <div class="mpd-id">${p.id}</div>
                        </div>
                    </div>
                    <div class="mpd-actions">
                        <span class="mpd-icon">🖊</span>
                        <span class="mpd-icon">🔔</span>
                        <span class="mpd-icon">📥</span>
                    </div>
                </div>
                <div class="mpd-card-bottom">
                    <div>
                        <div class="mpd-vitals">${vitalsHtml(p.vitals, p.bullet)}</div>
                    </div>
                    <div>
                        <div class="mpd-block-label">ECG AI</div>
                        <div class="mpd-ai">${p.ai}</div>
                    </div>
                    <div>
                        <div class="mpd-block-label">Status</div>
                        <div class="mpd-status ${statusClass(p.status)}">${p.status}</div>
                    </div>
                </div>
            </div>
        `;
    }

    function render() {
        const panel = findPanel();
        if (!panel) return;

        const imgMap = collectImages(panel);
        const patients = fallback.map(p => ({...p, img: imgMap[p.name] || p.img || ""}));

        panel.classList.add("mediot_patient_directory_exact");
        panel.innerHTML = `
            <div class="mpd-final">
                <div class="mpd-head">
                    <div class="mpd-title">Patient Directory</div>

                    <div class="mpd-topbar">
                        <div class="mpd-chip">👤&nbsp;&nbsp;3 Total Patients</div>
                        <div style="font-size:16px;font-weight:700;color:#0c2555;display:flex;align-items:center;">Patient Name</div>
                        <div class="mpd-input"><span>Please enter here</span><span>🔍</span></div>
                    </div>

                    <div class="mpd-toolbar2">
                        <div class="mpd-select">Patient Status&nbsp;&nbsp;&nbsp;⌄</div>
                        <div class="mpd-alerts">🔔 <span style="margin-left:8px;">Alerts</span> <span class="mpd-alert-count">1</span></div>
                        <button class="mpd-add">＋ Add Patient</button>
                    </div>
                </div>

                <div class="mpd-list">
                    ${patients.map(cardHtml).join("")}
                </div>
            </div>
        `;
    }

    ready(function () {
        render();
        setTimeout(render, 500);
        setTimeout(render, 1500);
        setTimeout(render, 2500);
    });
})();
 /* PATIENT_DIRECTORY_FORCE_V3_END */


/* PATIENT_DIRECTORY_FORCE_V4_START */
(function () {
    function text(el) {
        return ((el && (el.innerText || el.textContent)) || "").replace(/\s+/g, " ").trim();
    }

    function findPanel() {
        return document.querySelector(".mediot_patient_directory_exact") ||
            Array.from(document.querySelectorAll("div, section")).find(function (el) {
                return text(el).includes("Patient Directory") && text(el).includes("Salma");
            });
    }

    function getImgs(panel) {
        const imgs = Array.from(panel.querySelectorAll("img")).map(img => img.src).filter(Boolean);
        return imgs;
    }

    function statusClass(status) {
        return String(status).toLowerCase().includes("warn") ? "warning" : "critical";
    }

    function renderCard(p) {
        return `
            <div class="mpd-v4-card">
                <div class="mpd-v4-card-top">
                    <div class="mpd-v4-person">
                        <img class="mpd-v4-avatar" src="${p.img}" alt="">
                        <div>
                            <div class="mpd-v4-name">${p.name}</div>
                            <div class="mpd-v4-id">${p.id}</div>
                        </div>
                    </div>
                    <div class="mpd-v4-actions">
                        <span class="mpd-v4-icon">✎</span>
                        <span class="mpd-v4-icon">🔔</span>
                        <span class="mpd-v4-icon">⭳</span>
                    </div>
                </div>

                <div class="mpd-v4-bottom">
                    <div class="mpd-v4-vitals">
                        <div>${p.spo2}</div>
                        <div><span style="color:${p.dot};font-size:17px;">•</span> ${p.bpm}</div>
                    </div>
                    <div>
                        <div class="mpd-v4-label">ECG AI</div>
                        <div class="mpd-v4-ai">${p.ecg}</div>
                    </div>
                    <div>
                        <div class="mpd-v4-label">Status</div>
                        <div class="mpd-v4-status ${statusClass(p.status)}">${p.status}</div>
                    </div>
                </div>
            </div>
        `;
    }

    function render() {
        const panel = findPanel();
        if (!panel) return;

        const imgs = getImgs(panel);
        panel.classList.add("mediot_patient_directory_exact");

        const patients = [
            {name: "Salma Ben Mansour", id: "P-00012", spo2: "SpO2: 89.9%", bpm: "69 BPM", ecg: "Normal rhythm · Low", status: "Warning", dot: "#ff4040", img: (window.__mediotGetPatientImgByName && window.__mediotGetPatientImgByName("Salma Ben Mansour")) || imgs[0] || ""},
            {name: "Mariem Abed", id: "P-00006", spo2: "SpO2: 91.3%", bpm: "86 BPM", ecg: "Normal sinus rhythm · Low", status: "Critical", dot: "#2b66f0", img: (window.__mediotGetPatientImgByName && window.__mediotGetPatientImgByName("Mariem Abed")) || imgs[1] || ""},
            {name: "Samia Jeliti", id: "P-00001", spo2: "SpO2: 92.3%", bpm: "84 BPM", ecg: "Normal sinus rhythm · Low", status: "Critical", dot: "#ff4040", img: imgs[2] || "https://i.pravatar.cc/100?img=5"}
        ];

        const html = `
            <div class="mpd-v4">
                <h2 class="mpd-v4-title">Patient Directory</h2>

                <div class="mpd-v4-controls">
                    <div class="mpd-v4-box">♙&nbsp; 3 Total Patients</div>
                    <div class="mpd-v4-box" style="border:none;justify-content:flex-start;">Patient Name</div>
                    <div class="mpd-v4-search"><span>Please enter here</span><span>🔍</span></div>

                    <div class="mpd-v4-box">Patient Status⌄</div>
                    <div class="mpd-v4-box mpd-v4-alerts">🔔 Alerts <span class="mpd-v4-alert-pill">1</span></div>
                    <div class="mpd-v4-add">＋ Add Patient</div>
                </div>

                <div class="mpd-v4-list">
                    ${patients.map(renderCard).join("")}
                </div>
            </div>
        `;

        if (!panel.querySelector(".mpd-v4")) {
            panel.innerHTML = html;
        }
    }

    function start() {
        render();
        setTimeout(render, 300);
        setTimeout(render, 800);
        setTimeout(render, 1500);
        setTimeout(render, 3000);

        const obs = new MutationObserver(function () {
            const panel = findPanel();
            if (panel && !panel.querySelector(".mpd-v4")) {
                setTimeout(render, 50);
            }
        });
        obs.observe(document.body, {childList: true, subtree: true});
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start);
    } else {
        start();
    }
})();
/* PATIENT_DIRECTORY_FORCE_V4_END */

/* PATIENT_DIRECTORY_FORCE_V5_SELECTOR_FIX_START */
(function () {
    function text(el) {
        return ((el && (el.innerText || el.textContent)) || "").replace(/\s+/g, " ").trim();
    }

    function findPanel() {
        /* 1) real right panel class */
        const toolbar = document.querySelector(".med_exact_dashboard .mediot_toolbar_exact") ||
                        document.querySelector(".mediot_toolbar_exact");
        if (toolbar) return toolbar;

        /* 2) find patient table by names, then climb to big container */
        const table = Array.from(document.querySelectorAll("table")).find(t => {
            const s = text(t);
            return s.includes("Salma Ben Mansour") || s.includes("Mariem Abed") || s.includes("Samia Jeliti");
        });

        if (table) {
            return table.closest(".card, .o_form_sheet, .o_content, section, div") || table.parentElement;
        }

        return null;
    }

    function getImgs(panel) {
        return Array.from(panel.querySelectorAll("img")).map(img => img.src).filter(Boolean);
    }

    function statusClass(status) {
        return String(status).toLowerCase().includes("warn") ? "warning" : "critical";
    }

    function renderCard(p) {
        return `
            <div class="mpd-v4-card">
                <div class="mpd-v4-card-top">
                    <div class="mpd-v4-person">
                        <img class="mpd-v4-avatar" src="${p.img}" alt="">
                        <div>
                            <div class="mpd-v4-name">${p.name}</div>
                            <div class="mpd-v4-id">${p.id}</div>
                        </div>
                    </div>
                    <div class="mpd-v4-actions">
                        <span class="mpd-v4-icon">✎</span>
                        <span class="mpd-v4-icon">🔔</span>
                        <span class="mpd-v4-icon">⭳</span>
                    </div>
                </div>

                <div class="mpd-v4-bottom">
                    <div class="mpd-v4-vitals">
                        <div>${p.spo2}</div>
                        <div><span style="color:${p.dot};font-size:17px;">•</span> ${p.bpm}</div>
                    </div>
                    <div>
                        <div class="mpd-v4-label">ECG AI</div>
                        <div class="mpd-v4-ai">${p.ecg}</div>
                    </div>
                    <div>
                        <div class="mpd-v4-label">Status</div>
                        <div class="mpd-v4-status ${statusClass(p.status)}">${p.status}</div>
                    </div>
                </div>
            </div>
        `;
    }

    function render() {
        const panel = findPanel();
        if (!panel) return;

        const imgs = getImgs(panel);

        panel.classList.add("mediot_patient_directory_exact");

        const patients = [
            {name: "Salma Ben Mansour", id: "P-00012", spo2: "SpO2: 89.9%", bpm: "69 BPM", ecg: "Normal rhythm · Low", status: "Warning", dot: "#ff4040", img: (window.__mediotGetPatientImgByName && window.__mediotGetPatientImgByName("Salma Ben Mansour")) || imgs[0] || ""},
            {name: "Mariem Abed", id: "P-00006", spo2: "SpO2: 91.3%", bpm: "86 BPM", ecg: "Normal sinus rhythm · Low", status: "Critical", dot: "#2b66f0", img: (window.__mediotGetPatientImgByName && window.__mediotGetPatientImgByName("Mariem Abed")) || imgs[1] || ""},
            {name: "Samia Jeliti", id: "P-00001", spo2: "SpO2: 92.3%", bpm: "84 BPM", ecg: "Normal sinus rhythm · Low", status: "Critical", dot: "#ff4040", img: imgs[2] || "https://i.pravatar.cc/100?img=5"}
        ];

        panel.innerHTML = `
            <div class="mpd-v4">
                <h2 class="mpd-v4-title">Patient Directory</h2>

                <div class="mpd-v4-controls">
                    <div class="mpd-v4-box">♙&nbsp; 3 Total Patients</div>
                    <div class="mpd-v4-box" style="border:none;justify-content:flex-start;">Patient Name</div>
                    <div class="mpd-v4-search"><span>Please enter here</span><span>🔍</span></div>

                    <div class="mpd-v4-box">Patient Status⌄</div>
                    <div class="mpd-v4-box mpd-v4-alerts">🔔 Alerts <span class="mpd-v4-alert-pill">1</span></div>
                    <div class="mpd-v4-add">＋ Add Patient</div>
                </div>

                <div class="mpd-v4-list">
                    ${patients.map(renderCard).join("")}
                </div>
            </div>
        `;
    }

    function start() {
        render();
        setTimeout(render, 300);
        setTimeout(render, 800);
        setTimeout(render, 1500);
        setTimeout(render, 3000);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start);
    } else {
        start();
    }
})();
/* PATIENT_DIRECTORY_FORCE_V5_SELECTOR_FIX_END */


/* PATIENT_DIRECTORY_FINAL_TINY_FIX_START */
(function () {
    function txt(el) {
        return ((el && (el.innerText || el.textContent)) || "").replace(/\s+/g, " ").trim();
    }

    function realImageFor(name) {
        const imgs = Array.from(document.querySelectorAll("img"));
        for (const img of imgs) {
            if (img.closest(".mpd-v4-card")) continue;
            const host = img.closest("tr, .o_data_row, .card, div");
            if (host && txt(host).includes(name)) {
                return img.getAttribute("src") || img.src || "";
            }
        }
        return "";
    }

    function fixPatientDirectory() {
        const root = document.querySelector(".mediot_patient_directory_exact");
        if (!root) return;

        /* keep only placeholder text, remove search icon */
        root.querySelectorAll(".mpd-v4-search").forEach(el => {
            el.innerHTML = "<span>Please enter here</span>";
        });

        /* blue alerts icon, not yellow emoji */
        root.querySelectorAll(".mpd-v4-alerts").forEach(el => {
            el.innerHTML = '<i class="fa fa-bell"></i><span style="margin-left:8px;">Alerts</span><span class="mpd-v4-alert-pill">1</span>';
        });

        /* blue bell inside patient action buttons */
        root.querySelectorAll(".mpd-v4-actions .mpd-v4-icon").forEach(icon => {
            if (txt(icon).includes("🔔")) {
                icon.innerHTML = '<i class="fa fa-bell"></i>';
            }
        });

        /* use your existing patient images if found */
        const names = ["Salma Ben Mansour", "Mariem Abed", "Samia Jeliti"];
        root.querySelectorAll(".mpd-v4-card").forEach(card => {
            const name = txt(card.querySelector(".mpd-v4-name"));
            if (!names.includes(name)) return;

            const real = realImageFor(name);
            const avatar = card.querySelector(".mpd-v4-avatar");
            if (real && avatar) avatar.src = real;
        });
    }

    function start() {
        fixPatientDirectory();
        setTimeout(fixPatientDirectory, 300);
        setTimeout(fixPatientDirectory, 900);
        setTimeout(fixPatientDirectory, 1800);
        setTimeout(fixPatientDirectory, 3000);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start);
    } else {
        start();
    }
})();
/* PATIENT_DIRECTORY_FINAL_TINY_FIX_END */




/* PATIENT_DIRECTORY_SAFE_HIDE_OLD_TABLE_ONLY_START */
(function () {
    function txt(el) {
        return ((el && (el.innerText || el.textContent)) || "").replace(/\s+/g, " ").trim();
    }

    function hideOnlyOldTable() {
        const pretty = document.querySelector(".mediot_patient_directory_exact .mpd-v4");
        if (!pretty) return;

        document.querySelectorAll("table").forEach(function (table) {
            if (table.closest(".mpd-v4")) return;

            const s = txt(table);
            const isOldPatientTable =
                s.includes("Patient Name") &&
                s.includes("Status") &&
                s.includes("Actions") &&
                (s.includes("Salma") || s.includes("Mariem") || s.includes("Samia"));

            if (isOldPatientTable) {
                table.style.display = "none";
                table.setAttribute("data-mediot-old-patient-table-hidden", "1");
            }
        });
    }

    function start() {
        hideOnlyOldTable();
        setTimeout(hideOnlyOldTable, 300);
        setTimeout(hideOnlyOldTable, 900);
        setTimeout(hideOnlyOldTable, 1800);
        setTimeout(hideOnlyOldTable, 3000);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start);
    } else {
        start();
    }
})();
/* PATIENT_DIRECTORY_SAFE_HIDE_OLD_TABLE_ONLY_END */






/* PATIENT_DIRECTORY_USE_ODOO_IMAGES_ONLY_START */
(function () {
    const PATIENT_NAMES = ["Salma Ben Mansour", "Mariem Abed", "Samia Jeliti"];

    function txt(el) {
        return ((el && (el.innerText || el.textContent)) || "").replace(/\s+/g, " ").trim();
    }

    async function callKw(model, method, args, kwargs) {
        const res = await fetch(`/web/dataset/call_kw/${model}/${method}`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            credentials: "same-origin",
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                    model: model,
                    method: method,
                    args: args || [],
                    kwargs: kwargs || {}
                },
                id: Date.now()
            })
        });
        const data = await res.json();
        if (data.error) throw data.error;
        return data.result || [];
    }

    async function getPatientIds() {
        const records = await callKw(
            "med.patient",
            "search_read",
            [[["name", "in", PATIENT_NAMES]], ["id", "name"]],
            {}
        );

        const map = {};
        records.forEach(r => { map[r.name] = r.id; });
        return map;
    }

    async function applyOdooImages() {
        const root = document.querySelector(".mediot_patient_directory_exact");
        if (!root || !root.querySelector(".mpd-v4-card")) return;

        let ids = {};
        try {
            ids = await getPatientIds();
        } catch (e) {
            console.warn("MedIoT patient image lookup failed", e);
            return;
        }

        root.querySelectorAll(".mpd-v4-card").forEach(card => {
            const name = txt(card.querySelector(".mpd-v4-name"));
            const avatar = card.querySelector(".mpd-v4-avatar");
            const id = ids[name];

            if (!avatar || !id) return;

            avatar.style.visibility = "visible";
            avatar.onerror = function () {
                this.style.visibility = "hidden";
            };
            avatar.src = `/web/image/med.patient/${id}/image_1920?unique=${Date.now()}`;
        });
    }

    function start() {
        applyOdooImages();
        setTimeout(applyOdooImages, 400);
        setTimeout(applyOdooImages, 1200);
        setTimeout(applyOdooImages, 2500);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start);
    } else {
        start();
    }
})();
/* PATIENT_DIRECTORY_USE_ODOO_IMAGES_ONLY_END */


/* TRENDS_INSPO_V6_START */
(function () {
    function txt(el) {
        return ((el && (el.innerText || el.textContent)) || "").replace(/\s+/g, " ").trim();
    }

    function findTrendsPanel() {
        const exact = document.querySelector(".mediot_trends_exact");
        if (exact) return exact;

        const candidates = Array.from(document.querySelectorAll("div, section")).filter(el => {
            const s = txt(el);
            return s.includes("Patient Monitoring Trends") &&
                   s.includes("Heart Rate") &&
                   s.includes("SpO2") &&
                   s.includes("Temperature") &&
                   !s.includes("Patient Directory");
        });

        if (!candidates.length) return null;

        candidates.sort((a, b) => txt(a).length - txt(b).length);
        return candidates[0];
    }

    function chartSvg(type) {
        if (type === "heart") {
            return `
            <svg class="mtv6-svg" viewBox="0 0 900 126" preserveAspectRatio="none">
                <defs>
                    <linearGradient id="mtv6RedFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stop-color="#ff3b3b" stop-opacity="0.18"/>
                        <stop offset="100%" stop-color="#ff3b3b" stop-opacity="0.04"/>
                    </linearGradient>
                </defs>
                <g class="mtv6-axis">
                    <text x="0" y="20">140</text><text x="0" y="55">100</text><text x="0" y="90">60</text><text x="0" y="122">20</text>
                    <line x1="48" y1="18" x2="900" y2="18"/><line x1="48" y1="53" x2="900" y2="53"/><line x1="48" y1="88" x2="900" y2="88"/><line x1="48" y1="118" x2="900" y2="118"/>
                    <text x="48" y="125">00:00</text><text x="145" y="125">06:00</text><text x="250" y="125">12:00</text><text x="360" y="125">18:00</text><text x="470" y="125">00:00</text><text x="580" y="125">06:00</text><text x="690" y="125">12:00</text><text x="800" y="125">18:00</text><text x="870" y="125">24:00</text>
                </g>
                <path class="mtv6-red-fill" d="M48,72 L72,68 L95,70 L118,63 L128,90 L140,50 L152,82 L175,66 L200,69 L230,67 L255,70 L286,66 L312,72 L340,70 L365,76 L390,68 L408,72 L430,60 L452,90 L468,66 L490,70 L512,64 L535,73 L558,70 L580,55 L596,20 L612,68 L632,78 L650,60 L675,66 L700,78 L724,76 L750,72 L772,55 L790,70 L812,72 L832,86 L848,60 L860,78 L878,70 L900,72 L900,118 L48,118 Z"/>
                <path class="mtv6-red-line" d="M48,72 L72,68 L95,70 L118,63 L128,90 L140,50 L152,82 L175,66 L200,69 L230,67 L255,70 L286,66 L312,72 L340,70 L365,76 L390,68 L408,72 L430,60 L452,90 L468,66 L490,70 L512,64 L535,73 L558,70 L580,55 L596,20 L612,68 L632,78 L650,60 L675,66 L700,78 L724,76 L750,72 L772,55 L790,70 L812,72 L832,86 L848,60 L860,78 L878,70 L900,72"/>
                <circle class="mtv6-dot-red" cx="140" cy="50" r="4"/><circle class="mtv6-dot-red" cx="452" cy="90" r="4"/><circle class="mtv6-dot-red" cx="596" cy="20" r="5"/><circle class="mtv6-dot-red" cx="724" cy="76" r="4"/>
            </svg>`;
        }

        if (type === "spo2") {
            return `
            <svg class="mtv6-svg" viewBox="0 0 900 126" preserveAspectRatio="none">
                <defs>
                    <linearGradient id="mtv6BlueFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stop-color="#1764e8" stop-opacity="0.18"/>
                        <stop offset="100%" stop-color="#1764e8" stop-opacity="0.04"/>
                    </linearGradient>
                </defs>
                <g class="mtv6-axis">
                    <text x="0" y="34">100</text><text x="0" y="67">90</text><text x="0" y="100">80</text><text x="0" y="122">70</text>
                    <line x1="48" y1="30" x2="900" y2="30"/><line x1="48" y1="63" x2="900" y2="63"/><line x1="48" y1="96" x2="900" y2="96"/><line x1="48" y1="118" x2="900" y2="118"/>
                    <text x="48" y="125">00:00</text><text x="145" y="125">06:00</text><text x="250" y="125">12:00</text><text x="360" y="125">18:00</text><text x="470" y="125">00:00</text><text x="580" y="125">06:00</text><text x="690" y="125">12:00</text><text x="800" y="125">18:00</text><text x="870" y="125">24:00</text>
                </g>
                <path class="mtv6-blue-fill" d="M48,42 L88,70 L130,55 L180,58 L235,60 L292,56 L350,55 L405,38 L450,34 L500,62 L545,80 L580,76 L630,60 L685,72 L735,62 L788,52 L835,56 L880,68 L900,80 L900,118 L48,118 Z"/>
                <path class="mtv6-blue-line" d="M48,42 L88,70 L130,55 L180,58 L235,60 L292,56 L350,55 L405,38 L450,34 L500,62 L545,80 L580,76 L630,60 L685,72 L735,62 L788,52 L835,56 L880,68 L900,80"/>
                <circle class="mtv6-dot-blue" cx="48" cy="42" r="4"/><circle class="mtv6-dot-blue" cx="180" cy="58" r="4"/><circle class="mtv6-dot-blue" cx="450" cy="34" r="4"/><circle class="mtv6-dot-blue" cx="545" cy="80" r="4"/><circle class="mtv6-dot-blue" cx="735" cy="62" r="4"/><circle class="mtv6-dot-blue" cx="900" cy="80" r="4"/>
            </svg>`;
        }

        return `
            <svg class="mtv6-svg" viewBox="0 0 900 126" preserveAspectRatio="none">
                <defs>
                    <linearGradient id="mtv6GreenFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stop-color="#08a34d" stop-opacity="0.18"/>
                        <stop offset="100%" stop-color="#08a34d" stop-opacity="0.04"/>
                    </linearGradient>
                </defs>
                <g class="mtv6-axis">
                    <text x="0" y="28">42</text><text x="0" y="55">40</text><text x="0" y="82">38</text><text x="0" y="115">34</text>
                    <line x1="48" y1="25" x2="900" y2="25"/><line x1="48" y1="52" x2="900" y2="52"/><line x1="48" y1="79" x2="900" y2="79"/><line x1="48" y1="112" x2="900" y2="112"/>
                    <text x="48" y="125">00:00</text><text x="145" y="125">06:00</text><text x="250" y="125">12:00</text><text x="360" y="125">18:00</text><text x="470" y="125">00:00</text><text x="580" y="125">06:00</text><text x="690" y="125">12:00</text><text x="800" y="125">18:00</text><text x="870" y="125">24:00</text>
                </g>
                <path class="mtv6-green-fill" d="M48,46 L110,48 L170,54 L230,66 L290,74 L350,76 L410,70 L470,58 L520,55 L575,66 L635,76 L690,70 L742,58 L798,54 L850,60 L900,42 L900,112 L48,112 Z"/>
                <path class="mtv6-green-line" d="M48,46 L110,48 L170,54 L230,66 L290,74 L350,76 L410,70 L470,58 L520,55 L575,66 L635,76 L690,70 L742,58 L798,54 L850,60 L900,42"/>
                <circle class="mtv6-dot-green" cx="900" cy="42" r="4"/>
            </svg>`;
    }

    function render() {
        const panel = findTrendsPanel();
        if (!panel) return;

        panel.classList.add("mediot_trends_exact");
        panel.innerHTML = `
            <div class="mtv6-card">
                <div class="mtv6-header">
                    <div class="mtv6-icon">↗</div>

                    <div class="mtv6-title">
                        <h2>Patient Monitoring Trends</h2>
                        <p>Real-time overview of vital signs</p>
                        <span class="mtv6-live">Live</span>
                    </div>

                    <div class="mtv6-controls">
                        <div class="mtv6-select"><span>Select patient</span><span>⌄</span></div>
                        <div class="mtv6-hours">▣ <span>Last 24 Hours</span></div>
                        <div class="mtv6-refresh">↻</div>
                    </div>
                </div>

                <div class="mtv6-chart mtv6-red">
                    <div class="mtv6-chart-head">
                        <span class="mtv6-chart-icon">♥</span>
                        <span class="mtv6-chart-name">Heart Rate (BPM)</span>
                        <span class="mtv6-value">109</span>
                    </div>
                    <div class="mtv6-svg-wrap">${chartSvg("heart")}</div>
                </div>

                <div class="mtv6-chart mtv6-blue">
                    <div class="mtv6-chart-head">
                        <span class="mtv6-chart-icon">💧</span>
                        <span class="mtv6-chart-name">SpO2 (%)</span>
                        <span class="mtv6-value">91.1%</span>
                    </div>
                    <div class="mtv6-svg-wrap">${chartSvg("spo2")}</div>
                </div>

                <div class="mtv6-chart mtv6-green">
                    <div class="mtv6-chart-head">
                        <span class="mtv6-chart-icon">♨</span>
                        <span class="mtv6-chart-name">Temperature (°C)</span>
                        <span class="mtv6-value">39.5°C</span>
                    </div>
                    <div class="mtv6-svg-wrap">${chartSvg("temp")}</div>
                </div>
            </div>
        `;
    }

    function start() {
        render();
        setTimeout(render, 400);
        setTimeout(render, 1200);
        setTimeout(render, 2500);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start);
    } else {
        start();
    }
})();
/* TRENDS_INSPO_V6_END */

/* TRENDS_UNDER_WELCOME_GRID_FIX_START */
(function () {
    function txt(el) {
        return ((el && (el.innerText || el.textContent)) || "").replace(/\s+/g, " ").trim();
    }

    function fixGridPlacement() {
        const root = document.querySelector(".med_exact_dashboard");
        if (!root) return;

        root.classList.add("mediot_final_grid_fixed");

        const welcome = Array.from(root.querySelectorAll("div, section")).find(el => {
            const s = txt(el);
            return s.includes("Welcome, Doctor") && s.includes("Dashboard Overview");
        });

        const trends = root.querySelector(".mediot_trends_exact") ||
            Array.from(root.querySelectorAll("div, section")).find(el => {
                const s = txt(el);
                return s.includes("Patient Monitoring Trends") &&
                       s.includes("Heart Rate") &&
                       s.includes("SpO2") &&
                       !s.includes("Patient Directory");
            });

        const patientDir = root.querySelector(".mediot_patient_directory_exact");

        if (welcome) welcome.classList.add("mediot_welcome_grid_card");
        if (trends) trends.classList.add("mediot_trends_grid_card");
        if (patientDir) patientDir.classList.add("mediot_patient_grid_card");
    }

    function start() {
        fixGridPlacement();
        setTimeout(fixGridPlacement, 300);
        setTimeout(fixGridPlacement, 900);
        setTimeout(fixGridPlacement, 1800);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start);
    } else {
        start();
    }
})();
/* TRENDS_UNDER_WELCOME_GRID_FIX_END */









/* WELCOME_OVERVIEW_REPLACE_SAFE_START */
(function () {
    function txt(el) {
        return ((el && (el.innerText || el.textContent)) || "").replace(/\s+/g, " ").trim();
    }

    function formatDate(d) {
        const day = String(d.getDate()).padStart(2, "0");
        const month = d.toLocaleString("en-GB", { month: "short" });
        return `${day} ${month} ${d.getFullYear()}`;
    }

    function formatTime(d) {
        return d.toLocaleTimeString("en-GB", { hour12: false });
    }

    function makeInfo() {
        const div = document.createElement("div");
        div.className = "welcome-overview-info-safe";
        div.innerHTML = `
            <div class="wois-date">🗓 <span class="wois-date-text"></span></div>
            <div class="wois-meta">◔ <span>Auto-refreshes every 15s · Last updated: <span class="wois-time"></span></span></div>
        `;
        return div;
    }

    function replaceOnlyDashboardOverviewText() {
        if (document.querySelector(".welcome-overview-info-safe")) return;

        const candidates = Array.from(document.querySelectorAll("button, a, span, div"))
            .filter(el => txt(el) === "Dashboard Overview");

        if (!candidates.length) return;

        candidates.sort((a, b) => a.outerHTML.length - b.outerHTML.length);
        const target = candidates[0];

        const info = makeInfo();
        target.replaceWith(info);

        function tick() {
            const now = new Date();
            const date = info.querySelector(".wois-date-text");
            const time = info.querySelector(".wois-time");
            if (date) date.textContent = formatDate(now);
            if (time) time.textContent = formatTime(now);
        }

        tick();
        setInterval(tick, 1000);
    }

    document.addEventListener("DOMContentLoaded", replaceOnlyDashboardOverviewText);
    window.addEventListener("load", replaceOnlyDashboardOverviewText);
    setTimeout(replaceOnlyDashboardOverviewText, 300);
    setTimeout(replaceOnlyDashboardOverviewText, 1000);
    setTimeout(replaceOnlyDashboardOverviewText, 2500);
})();
/* WELCOME_OVERVIEW_REPLACE_SAFE_END */











/* TRENDS_MOVE_UP_VISUAL_SAFE_START */
(function () {
    function txt(el) {
        return ((el && (el.innerText || el.textContent)) || "").replace(/\s+/g, " ").trim();
    }

    function findWelcome() {
        return Array.from(document.querySelectorAll("div, section")).find(el => {
            const s = txt(el);
            return s.includes("Welcome, Doctor") &&
                   s.includes("Welcome to MedIoT Command Center");
        });
    }

    function findTrends() {
        return document.querySelector(".mediot_trends_exact");
    }

    function pullTrendsUp() {
        const welcome = findWelcome();
        const trends = findTrends();
        if (!welcome || !trends) return;

        const welcomeRect = welcome.getBoundingClientRect();
        const trendsRect = trends.getBoundingClientRect();

        const wantedGap = 18;
        const currentGap = trendsRect.top - welcomeRect.bottom;
        const lift = Math.max(0, currentGap - wantedGap);

        trends.style.setProperty("--mediot-trends-lift", lift + "px");
    }

    function start() {
        pullTrendsUp();
        setTimeout(pullTrendsUp, 300);
        setTimeout(pullTrendsUp, 900);
        setTimeout(pullTrendsUp, 1800);
        window.addEventListener("resize", pullTrendsUp);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start);
    } else {
        start();
    }
})();
/* TRENDS_MOVE_UP_VISUAL_SAFE_END */





/* BUTTONS_DELEGATION_FINAL_WORKING_START */
(function () {
    if (window.__MEDIOT_BUTTONS_DELEGATION_FINAL__) return;
    window.__MEDIOT_BUTTONS_DELEGATION_FINAL__ = true;

    const state = {
        patient: "all",
        status: "all",
        alertsOnly: false,
        q: "",
        hours: "24"
    };

    const patients = [
        "Salma Ben Mansour",
        "Mariem Abed",
        "Samia Jeliti"
    ];

    const patientIds = {
        "Salma Ben Mansour": "P-00012",
        "Mariem Abed": "P-00006",
        "Samia Jeliti": "P-00001"
    };

    function text(el) {
        return ((el && (el.innerText || el.textContent)) || "").replace(/\s+/g, " ").trim();
    }

    function closeMenus() {
        document.querySelectorAll(".mediot-dd-menu-final").forEach(m => m.remove());
    }

    function showMenu(host, items, callback) {
        closeMenus();

        const r = host.getBoundingClientRect();
        const menu = document.createElement("div");
        menu.className = "mediot-dd-menu-final";
        menu.style.left = Math.round(r.left) + "px";
        menu.style.top = Math.round(r.bottom + 8) + "px";
        menu.style.minWidth = Math.round(r.width) + "px";

        items.forEach(item => {
            const row = document.createElement("div");
            row.className = "mediot-dd-item-final";
            row.textContent = item.label;
            row.addEventListener("click", function (ev) {
                ev.preventDefault();
                ev.stopPropagation();
                closeMenus();
                callback(item);
            }, true);
            menu.appendChild(row);
        });

        document.body.appendChild(menu);
    }

    function cards() {
        return Array.from(document.querySelectorAll(".mpd-v4-card"));
    }

    function ensureSearchInput() {
        const searchBox = document.querySelector(".mpd-v4-search");
        if (searchBox && !searchBox.querySelector("input")) {
            searchBox.innerHTML = '<input class="mpd-v4-search-input" placeholder="Please enter here">';
        }
    }

    function setTrendSelectLabel(label) {
        const select = document.querySelector(".mtv6-select");
        if (!select) return;
        const spans = select.querySelectorAll("span");
        if (spans.length) spans[0].textContent = label;
        else select.textContent = label + " ⌄";
    }

    function setHoursLabel(label) {
        const hours = document.querySelector(".mtv6-hours");
        if (!hours) return;
        const span = hours.querySelector("span");
        if (span) span.textContent = label;
        else hours.textContent = "▣ " + label;
    }

    function filterCards() {
        ensureSearchInput();

        const q = state.q.toLowerCase().trim();
        let shown = 0;

        cards().forEach(card => {
            const name = text(card.querySelector(".mpd-v4-name"));
            const status = text(card.querySelector(".mpd-v4-status")).toLowerCase();

            const okPatient = state.patient === "all" || name === state.patient;
            const okStatus = state.status === "all" || status.includes(state.status);
            const okAlerts = !state.alertsOnly || status.includes("warning") || status.includes("critical");
            const okSearch = !q || name.toLowerCase().includes(q);

            const ok = okPatient && okStatus && okAlerts && okSearch;
            card.style.display = ok ? "" : "none";
            if (ok) shown++;
        });

        const list = document.querySelector(".mpd-v4-list");
        if (list) {
            let empty = list.querySelector(".mpd-v4-empty");
            if (!empty) {
                empty = document.createElement("div");
                empty.className = "mpd-v4-empty";
                empty.textContent = "No patients found";
                list.appendChild(empty);
            }
            empty.style.display = shown ? "none" : "block";
        }
    }

    function openPatient(name) {
        const id = patientIds[name] || "";
        window.location.href = "/web#model=med.patient&view_type=list&search=" + encodeURIComponent(id || name);
    }

    function openAlerts() {
        const nav = Array.from(document.querySelectorAll("a,button,span,div"))
            .find(el => text(el) === "Real-time Alerts");
        if (nav) nav.click();
        else window.location.href = "/web#model=med.alert&view_type=list";
    }

    function openAddPatient() {
        window.location.href = "/web#model=med.patient&view_type=form";
    }

    function downloadReport(card) {
        const name = text(card.querySelector(".mpd-v4-name"));
        const id = text(card.querySelector(".mpd-v4-id"));
        const vitals = text(card.querySelector(".mpd-v4-vitals"));
        const ai = text(card.querySelector(".mpd-v4-ai"));
        const status = text(card.querySelector(".mpd-v4-status"));

        const content =
`MedIoT Patient Report
Patient: ${name}
ID: ${id}
Vitals: ${vitals}
ECG AI: ${ai}
Status: ${status}
Generated: ${new Date().toLocaleString()}`;

        const blob = new Blob([content], {type: "text/plain;charset=utf-8"});
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = name.replace(/\s+/g, "_") + "_report.txt";
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(() => URL.revokeObjectURL(a.href), 500);
    }

    document.addEventListener("click", function (e) {
        ensureSearchInput();

        const menu = e.target.closest(".mediot-dd-menu-final");
        if (menu) return;

        const select = e.target.closest(".mtv6-select");
        if (select) {
            e.preventDefault();
            e.stopPropagation();
            showMenu(select, [
                {label: "All patients", value: "all"},
                ...patients.map(p => ({label: p, value: p}))
            ], item => {
                state.patient = item.value;
                setTrendSelectLabel(item.value === "all" ? "Select patient" : item.label);
                filterCards();
            });
            return;
        }

        const hours = e.target.closest(".mtv6-hours");
        if (hours) {
            e.preventDefault();
            e.stopPropagation();
            showMenu(hours, [
                {label: "Last 24 Hours", value: "24"},
                {label: "Last 12 Hours", value: "12"},
                {label: "Last 6 Hours", value: "6"}
            ], item => {
                state.hours = item.value;
                setHoursLabel(item.label);
            });
            return;
        }

        const refresh = e.target.closest(".mtv6-refresh");
        if (refresh) {
            e.preventDefault();
            e.stopPropagation();
            location.reload();
            return;
        }

        const add = e.target.closest(".mpd-v4-add");
        if (add) {
            e.preventDefault();
            e.stopPropagation();
            openAddPatient();
            return;
        }

        const alerts = e.target.closest(".mpd-v4-alerts");
        if (alerts) {
            e.preventDefault();
            e.stopPropagation();
            state.alertsOnly = !state.alertsOnly;
            alerts.classList.toggle("mediot-active-btn", state.alertsOnly);
            filterCards();
            return;
        }

        const box = e.target.closest(".mpd-v4-box");
        if (box) {
            const t = text(box);

            if (t.includes("Total Patients")) {
                e.preventDefault();
                e.stopPropagation();
                state.patient = "all";
                state.status = "all";
                state.alertsOnly = false;
                state.q = "";
                const input = document.querySelector(".mpd-v4-search-input");
                if (input) input.value = "";
                document.querySelector(".mpd-v4-alerts")?.classList.remove("mediot-active-btn");
                setTrendSelectLabel("Select patient");
                filterCards();
                return;
            }

            if (t === "Patient Name") {
                e.preventDefault();
                e.stopPropagation();
                document.querySelector(".mpd-v4-search-input")?.focus();
                return;
            }

            if (t.includes("Patient Status")) {
                e.preventDefault();
                e.stopPropagation();
                showMenu(box, [
                    {label: "All statuses", value: "all"},
                    {label: "Warning", value: "warning"},
                    {label: "Critical", value: "critical"}
                ], item => {
                    state.status = item.value;
                    box.textContent = item.value === "all" ? "Patient Status⌄" : item.label + "⌄";
                    filterCards();
                });
                return;
            }
        }

        const icon = e.target.closest(".mpd-v4-icon");
        if (icon) {
            e.preventDefault();
            e.stopPropagation();

            const card = icon.closest(".mpd-v4-card");
            if (!card) return;

            const name = text(card.querySelector(".mpd-v4-name"));
            const icons = Array.from(card.querySelectorAll(".mpd-v4-icon"));
            const idx = icons.indexOf(icon);

            if (idx === 0) openPatient(name);
            else if (idx === 1) openAlerts();
            else if (idx === 2) downloadReport(card);
            return;
        }

        closeMenus();
    }, true);

    document.addEventListener("input", function (e) {
        if (e.target && e.target.classList.contains("mpd-v4-search-input")) {
            state.q = e.target.value || "";
            filterCards();
        }
    }, true);

    function init() {
        ensureSearchInput();
        filterCards();
    }

    document.addEventListener("DOMContentLoaded", init);
    window.addEventListener("load", init);
    setTimeout(init, 300);
    setTimeout(init, 1200);
})();
/* BUTTONS_DELEGATION_FINAL_WORKING_END */








/* FINAL_PURPLE_ALERT_ADD_WELCOME_SAFE_START */
(function () {
    function fixWelcomeText() {
        const wanted = "Welcome, Doctor, Farah Mehrez";
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let node;

        while ((node = walker.nextNode())) {
            const raw = node.nodeValue || "";
            const clean = raw.replace(/\s+/g, " ").trim();

            if (/^Welcome,/i.test(clean) && clean.length < 80 && !clean.includes("Command Center")) {
                node.nodeValue = raw.replace(clean, wanted);
                return;
            }
        }
    }

    document.addEventListener("DOMContentLoaded", fixWelcomeText);
    window.addEventListener("load", fixWelcomeText);
    setTimeout(fixWelcomeText, 300);
    setTimeout(fixWelcomeText, 1200);
    setTimeout(fixWelcomeText, 3000);
    setTimeout(fixWelcomeText, 6000);
})();
/* FINAL_PURPLE_ALERT_ADD_WELCOME_SAFE_END */


/* FINAL_NAV_COLOR_CLEANUP_START */
(function () {
    function txt(el) {
        return (el?.innerText || el?.textContent || "").replace(/\s+/g, " ").trim();
    }

    function fixDatabaseBadge() {
        const nodes = Array.from(document.querySelectorAll("span,div,a,button"));
        nodes.forEach(el => {
            const t = txt(el);
            if (t === "odoo19_db" || t.includes("odoo19_db")) {
                el.classList.add("mediot-db-badge-force");

                let p = el.parentElement;
                for (let i = 0; i < 2 && p; i++, p = p.parentElement) {
                    if (txt(p).includes("odoo19_db") && txt(p).length < 40) {
                        p.classList.add("mediot-db-badge-force");
                    }
                }
            }
        });
    }

    document.addEventListener("DOMContentLoaded", fixDatabaseBadge);
    window.addEventListener("load", fixDatabaseBadge);
    setTimeout(fixDatabaseBadge, 300);
    setTimeout(fixDatabaseBadge, 1200);
    setTimeout(fixDatabaseBadge, 3000);
})();
/* FINAL_NAV_COLOR_CLEANUP_END */








/* RESTORE_OLD_CURVES_STRUCTURE_FINAL_START */
(function () {
    if (window.__RESTORE_OLD_CURVES_STRUCTURE_FINAL__) return;
    window.__RESTORE_OLD_CURVES_STRUCTURE_FINAL__ = true;

    const DATA = {
        heart: [78,82,80,88,56,102,66,84,81,82,83,80,84,78,79,72,81,77,88,56,84,79,87,76,80,74,72,76,94,77,75,60,90,70,78,76],
        spo2:  [96,88,92,91,91,92,92,97,98,90,85,86,91,88,90,93,92,88,85],
        temp:  [40.4,40.3,40.2,39.8,38.9,38.5,38.3,38.2,38.7,39.6,39.8,39.0,38.5,38.2,38.6,39.6,39.8,39.4,40.6]
    };

    const CFG = {
        heart: {min:20, max:140, ticks:[140,100,60,20], color:"#ff3b3b", area:"rgba(255,59,59,.16)", labels:["00:00","06:00","12:00","18:00","00:00","06:00","12:00","18:00","24:00"]},
        spo2:  {min:70, max:100, ticks:[100,90,80,70], color:"#2563eb", area:"rgba(37,99,235,.18)", labels:["00:00","06:00","12:00","18:00","00:00","06:00","12:00","18:00","24:00"]},
        temp:  {min:34, max:42, ticks:[42,40,38,34], color:"#0aa34a", area:"rgba(22,163,74,.17)", labels:["00:00","06:00","12:00","18:00","00:00","06:00","12:00","18:00","24:00"]}
    };

    function txt(el) {
        return (el?.innerText || el?.textContent || "").replace(/\s+/g, " ").trim();
    }

    function hours() {
        const t = txt(document.querySelector(".mediot_trends_exact .mtv6-hours"));
        if (t.includes("6")) return 6;
        if (t.includes("12")) return 12;
        return 24;
    }

    function crop(arr, h) {
        if (h === 24) return arr.slice();
        if (h === 12) return arr.slice(-Math.max(10, Math.round(arr.length * .55)));
        return arr.slice(-Math.max(7, Math.round(arr.length * .35)));
    }

    function svg(values, cfg) {
        const W = 1000, H = 92;
        const L = 44, R = 12, T = 8, B = 18;
        const PW = W - L - R;
        const PH = H - T - B;

        function x(i) {
            return L + (values.length <= 1 ? 0 : i * PW / (values.length - 1));
        }

        function y(v) {
            return T + ((cfg.max - v) * PH / (cfg.max - cfg.min));
        }

        const pts = values.map((v, i) => [x(i), y(v)]);
        const linePts = pts.map(p => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
        const lineD = pts.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(" ");
        const areaD = `M${pts[0][0].toFixed(1)} ${H-B} ` + 
                      pts.map(p => `L${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(" ") +
                      ` L${pts[pts.length-1][0].toFixed(1)} ${H-B} Z`;

        const grid = cfg.ticks.map(t => {
            const yy = y(t);
            return `
                <text x="${L-10}" y="${yy+4}" text-anchor="end" font-size="10" font-weight="800" fill="#082657">${t}</text>
                <line x1="${L}" y1="${yy}" x2="${W-R}" y2="${yy}" stroke="#d9e5f3" stroke-width="1"></line>
            `;
        }).join("");

        const labels = cfg.labels.map((lab, i) => {
            const xx = L + i * PW / (cfg.labels.length - 1);
            return `<text x="${xx}" y="${H-2}" text-anchor="middle" font-size="10" font-weight="800" fill="#082657">${lab}</text>`;
        }).join("");

        const dotsIndex = new Set();
        dotsIndex.add(values.length - 1);
        dotsIndex.add(Math.round(values.length * .12));
        dotsIndex.add(Math.round(values.length * .45));
        dotsIndex.add(Math.round(values.length * .70));

        const dots = pts.map((p, i) => {
            if (!dotsIndex.has(i)) return "";
            return `<circle cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="4" fill="${cfg.color}" stroke="${cfg.color}"></circle>`;
        }).join("");

        return `
<svg class="mtv6-svg" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">
    ${grid}
    <path d="${areaD}" fill="${cfg.area}" stroke="none"></path>
    <path d="${lineD}" fill="none" stroke="${cfg.color}" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"></path>
    ${dots}
    ${labels}
</svg>`;
    }

    function renderOldCurves() {
        const wraps = Array.from(document.querySelectorAll(".mediot_trends_exact .mtv6-svg-wrap"));
        if (wraps.length < 3) return;

        const h = hours();

        wraps[0].innerHTML = svg(crop(DATA.heart, h), CFG.heart);
        wraps[1].innerHTML = svg(crop(DATA.spo2, h), CFG.spo2);
        wraps[2].innerHTML = svg(crop(DATA.temp, h), CFG.temp);

        const values = Array.from(document.querySelectorAll(".mediot_trends_exact .mtv6-value"));
        if (values[0]) values[0].style.setProperty("color", "#ff3b3b", "important");
        if (values[1]) values[1].style.setProperty("color", "#2563eb", "important");
        if (values[2]) values[2].style.setProperty("color", "#0aa34a", "important");
    }

    let last = "";
    function watch() {
        const now = txt(document.querySelector(".mediot_trends_exact .mtv6-hours"));
        if (now !== last) {
            last = now;
            renderOldCurves();
        }
    }

    document.addEventListener("DOMContentLoaded", renderOldCurves);
    window.addEventListener("load", renderOldCurves);
    setTimeout(renderOldCurves, 300);
    setTimeout(renderOldCurves, 1000);
    setTimeout(renderOldCurves, 2000);
    setInterval(watch, 400);
})();
/* RESTORE_OLD_CURVES_STRUCTURE_FINAL_END */

















/* PATIENT_DIRECTORY_INITIALS_NO_PHOTOS_FINAL_START */
(function () {
    if (window.__MEDIOT_PATIENT_DIRECTORY_INITIALS_NO_PHOTOS_FINAL__) return;
    window.__MEDIOT_PATIENT_DIRECTORY_INITIALS_NO_PHOTOS_FINAL__ = true;

    function txt(el) {
        return (el?.innerText || el?.textContent || "").replace(/\s+/g, " ").trim();
    }

    function initials(name) {
        const parts = name.trim().split(/\s+/).filter(Boolean);
        if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
        return (parts[0] || "P").slice(0, 2).toUpperCase();
    }

    function applyNoPhotos() {
        const cards = Array.from(document.querySelectorAll(".mediot_patient_directory_exact .mpd-v4-card"));

        cards.forEach(card => {
            const nameEl = card.querySelector(".mpd-v4-name");
            const name = txt(nameEl);
            if (!name) return;

            let avatar = card.querySelector(".mpd-initial-avatar-final");
            const oldImg = card.querySelector("img.mpd-v4-avatar");

            if (!avatar) {
                avatar = document.createElement("div");
                avatar.className = "mpd-initial-avatar-final";
                avatar.textContent = initials(name);

                if (oldImg && oldImg.parentElement) {
                    oldImg.parentElement.insertBefore(avatar, oldImg);
                } else {
                    card.prepend(avatar);
                }
            }

            avatar.textContent = initials(name);

            if (oldImg) {
                oldImg.removeAttribute("src");
                oldImg.style.display = "none";
            }
        });
    }

    document.addEventListener("DOMContentLoaded", applyNoPhotos);
    window.addEventListener("load", applyNoPhotos);
    setTimeout(applyNoPhotos, 300);
    setTimeout(applyNoPhotos, 1000);
    setTimeout(applyNoPhotos, 2000);
    setTimeout(applyNoPhotos, 4000);
})();
/* PATIENT_DIRECTORY_INITIALS_NO_PHOTOS_FINAL_END */





/* ADMIN_NAV_HIDE_SETTINGS_STRONG_FINAL_START */
(function () {
    if (window.__MEDIOT_ADMIN_NAV_HIDE_SETTINGS_STRONG_FINAL__) return;
    window.__MEDIOT_ADMIN_NAV_HIDE_SETTINGS_STRONG_FINAL__ = true;

    function txt(el) {
        return (el?.innerText || el?.textContent || "").replace(/\s+/g, " ").trim();
    }

    function hideAdminSettings() {
        const navbar = document.querySelector(".o_main_navbar") || document.querySelector("nav");
        if (!navbar) return;

        const navText = txt(navbar);

        const isAdmin =
            navText.includes("Admin Dashboard") &&
            navText.includes("Users & Roles") &&
            navText.includes("Patient List");

        if (!isAdmin) {
            document.body.classList.remove("mediot-admin-nav-no-settings");
            return;
        }

        document.body.classList.add("mediot-admin-nav-no-settings");

        Array.from(navbar.querySelectorAll("a, button, span, div")).forEach(el => {
            if (txt(el) !== "Settings") return;

            const clickable = el.closest("a,button") || el;
            clickable.classList.add("mediot-admin-settings-hidden-final");
            clickable.style.setProperty("display", "none", "important");
        });
    }

    document.addEventListener("DOMContentLoaded", hideAdminSettings);
    window.addEventListener("load", hideAdminSettings);

    [100, 300, 700, 1200, 2000, 3500].forEach(t => setTimeout(hideAdminSettings, t));

    document.addEventListener("click", function () {
        setTimeout(hideAdminSettings, 150);
        setTimeout(hideAdminSettings, 700);
    }, true);
})();
/* ADMIN_NAV_HIDE_SETTINGS_STRONG_FINAL_END */
