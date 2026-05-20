/** @odoo-module **/

const FIELD_CONFIG = {
    hr_critical_min: { min: 20, max: 80, step: 1, unit: "bpm", color: "#ef4444", label: "Critical Min" },
    hr_critical_max: { min: 100, max: 220, step: 1, unit: "bpm", color: "#ef4444", label: "Critical Max" },
    hr_warning_min: { min: 30, max: 90, step: 1, unit: "bpm", color: "#eab308", label: "Warning Min" },
    hr_warning_max: { min: 80, max: 180, step: 1, unit: "bpm", color: "#3b82f6", label: "Warning Max" },

    spo2_critical_min: { min: 50, max: 100, step: 1, unit: "%", color: "#ef4444", label: "Critical Min" },
    spo2_warning_min: { min: 70, max: 100, step: 1, unit: "%", color: "#3b82f6", label: "Warning Min" },

    temp_critical_min: { min: 30, max: 37, step: 0.1, unit: "°C", color: "#ef4444", label: "Critical Min" },
    temp_critical_max: { min: 37, max: 45, step: 0.1, unit: "°C", color: "#ef4444", label: "Critical Max" },
    temp_warning_min: { min: 32, max: 37, step: 0.1, unit: "°C", color: "#eab308", label: "Warning Min" },
    temp_warning_max: { min: 36, max: 42, step: 0.1, unit: "°C", color: "#3b82f6", label: "Warning Max" },
};

function formatValue(v, step) {
    const num = parseFloat(v || 0);
    if (Number.isNaN(num)) return "0";
    return step < 1 ? num.toFixed(1) : String(Math.round(num));
}

function setNativeValue(input, value) {
    input.value = value;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
}

function enhanceField(widget, config) {
    if (!widget || widget.dataset.medSliderReady === "1") return;

    const input = widget.querySelector("input");
    if (!input) return;

    widget.dataset.medSliderReady = "1";
    widget.classList.add("med-hide-original-threshold-input");

    const currentValue = parseFloat(input.value || config.min) || config.min;

    const wrap = document.createElement("div");
    wrap.className = "med-threshold-slider-wrap";

    wrap.innerHTML = `
        <div class="med-threshold-slider-top">
            <div class="med-threshold-slider-current">
                Selected value: <span class="med-current-value"></span>
            </div>
            <div class="med-threshold-slider-badge">
                Threshold: <span class="med-badge-value"></span>
            </div>
        </div>
        <input class="med-threshold-slider" type="range"
               min="${config.min}" max="${config.max}" step="${config.step}" value="${currentValue}">
    `;

    widget.after(wrap);

    const slider = wrap.querySelector(".med-threshold-slider");
    const currentEl = wrap.querySelector(".med-current-value");
    const badgeEl = wrap.querySelector(".med-badge-value");

    function render(value) {
        const v = formatValue(value, config.step);
        currentEl.textContent = `${v}${config.unit}`;
        badgeEl.textContent = `${v}${config.unit}`;

        const min = parseFloat(config.min);
        const max = parseFloat(config.max);
        const val = parseFloat(value);
        const pct = ((val - min) * 100) / (max - min);

        slider.style.background = `linear-gradient(to right, ${config.color} 0%, ${config.color} ${pct}%, #dfe7d8 ${pct}%, #dfe7d8 100%)`;
        slider.style.setProperty("--med-slider-color", config.color);
    }

    slider.addEventListener("input", () => {
        setNativeValue(input, slider.value);
        render(slider.value);
    });

    input.addEventListener("input", () => {
        slider.value = input.value || config.min;
        render(slider.value);
    });

    render(currentValue);
}

function applySettingsSliders() {
    const form = document.querySelector(".o_form_view");
    if (!form) return;

    // full width helper classes
    document.querySelectorAll(".o_form_view .o_form_sheet_bg").forEach((el) => {
        el.classList.add("med-settings-full-bg");
    });
    document.querySelectorAll(".o_form_view .o_form_sheet").forEach((el) => {
        el.classList.add("med-settings-full-sheet");
    });

    Object.entries(FIELD_CONFIG).forEach(([fieldName, config]) => {
        document.querySelectorAll(`.o_form_view .o_field_widget[name="${fieldName}"]`).forEach((widget) => {
            enhanceField(widget, config);
        });
    });
}

function boot() {
    applySettingsSliders();

    const observer = new MutationObserver(() => {
        applySettingsSliders();
    });
    observer.observe(document.body, { childList: true, subtree: true });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
} else {
    boot();
}