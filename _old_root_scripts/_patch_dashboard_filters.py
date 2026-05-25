from pathlib import Path
import re

js_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\js\dashboard.js")
xml_path = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\xml\dashboard.xml")

js = js_path.read_text(encoding="utf-8")
xml = xml_path.read_text(encoding="utf-8")

# Add filter state
if "searchQuery" not in js:
    js = re.sub(
        r"(live\s*:\s*\[\]\s*,)",
        r'\1\n            searchQuery: "",\n            statusFilter: "all",',
        js,
        count=1
    )

# Add filter methods/getter before openPatients
methods = r'''
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
                p.latest_temp
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

'''

if "DASHBOARD SEARCH + STATUS FILTER PATCH" not in js:
    js = js.replace("    openPatients()", methods + "    openPatients()", 1)

# Make table use filtered data
xml = xml.replace('t-if="state.live.length == 0"', 't-if="this.filteredLive.length == 0"')
xml = xml.replace('t-foreach="state.live"', 't-foreach="this.filteredLive"')

# Fix undefined handlers on search input/select
xml = re.sub(
    r'(<input[^>]*placeholder="Search patient\.\.\."[^>]*?)\s+t-on-[a-zA-Z.-]+="[^"]*"',
    r'\1 t-on-input="(ev) => this.onSearchPatient(ev)"',
    xml,
    count=1
)

xml = re.sub(
    r'(<select[^>]*?)\s+t-on-[a-zA-Z.-]+="[^"]*"',
    r'\1 t-on-change="(ev) => this.onStatusFilter(ev)"',
    xml,
    count=1
)

# If input/select had no handler, add one
xml = re.sub(
    r'(<input[^>]*placeholder="Search patient\.\.\."(?![^>]*t-on-input)[^>]*)(/?>)',
    r'\1 t-on-input="(ev) => this.onSearchPatient(ev)"\2',
    xml,
    count=1
)

xml = re.sub(
    r'(<select(?![^>]*t-on-change)[^>]*)(>)',
    r'\1 t-on-change="(ev) => this.onStatusFilter(ev)"\2',
    xml,
    count=1
)

js_path.write_text(js, encoding="utf-8")
xml_path.write_text(xml, encoding="utf-8")

print("Search/status filter patched")
