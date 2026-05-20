/** @odoo-module **/

function animateCounter(el) {
    const target = parseInt(el.dataset.target || "0", 10);
    const suffix = el.dataset.suffix || "";
    const duration = parseInt(el.dataset.duration || "1800", 10);

    if (!target || el.dataset.animated === "true") {
        return;
    }

    el.dataset.animated = "true";

    let startTimestamp = null;

    const step = (timestamp) => {
        if (!startTimestamp) {
            startTimestamp = timestamp;
        }

        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const value = Math.floor(eased * target);

        el.textContent = `${value}${suffix}`;

        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            el.textContent = `${target}${suffix}`;
        }
    };

    window.requestAnimationFrame(step);
}

function initMedCounters() {
    const counters = document.querySelectorAll(".med_video_stat_num[data-target]");

    if (!counters.length) {
        return;
    }

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.35,
        }
    );

    counters.forEach((counter) => observer.observe(counter));
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initMedCounters);
} else {
    initMedCounters();
}