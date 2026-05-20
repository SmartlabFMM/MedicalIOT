document.addEventListener("DOMContentLoaded", function () {
    const counters = Array.from(document.querySelectorAll(".med_video_stat_num"));
    if (!counters.length) return;

    function parseCounterText(text) {
        const raw = (text || "").trim();
        const match = raw.match(/(\d+(?:\.\d+)?)/);
        if (!match) {
            return null;
        }
        const numberText = match[1];
        const target = parseFloat(numberText);
        const startIndex = match.index;
        const prefix = raw.slice(0, startIndex);
        const suffix = raw.slice(startIndex + numberText.length);
        const decimals = numberText.includes(".") ? numberText.split(".")[1].length : 0;

        return { raw, target, prefix, suffix, decimals };
    }

    function animateCounter(el, delay) {
        if (el.dataset.counterAnimated === "1") return;

        const parsed = parseCounterText(el.textContent);
        if (!parsed) return;

        el.dataset.counterAnimated = "1";

        const duration = parsed.target >= 100 ? 1800 : 1400;

        setTimeout(function () {
            const start = performance.now();

            function step(now) {
                const progress = Math.min((now - start) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                const current = parsed.target * eased;

                let displayValue;
                if (parsed.decimals > 0) {
                    displayValue = current.toFixed(parsed.decimals);
                } else {
                    displayValue = Math.round(current).toString();
                }

                el.textContent = parsed.prefix + displayValue + parsed.suffix;

                if (progress < 1) {
                    requestAnimationFrame(step);
                } else {
                    el.textContent = parsed.raw;
                }
            }

            requestAnimationFrame(step);
        }, delay);
    }

    let started = false;

    function startCounters() {
        if (started) return;
        started = true;
        counters.forEach(function (counter, index) {
            animateCounter(counter, index * 180);
        });
    }

    const statsSection = document.querySelector(".med_video_stats") || counters[0].closest("section") || counters[0].parentElement;

    if (!statsSection) {
        startCounters();
        return;
    }

    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                startCounters();
                observer.disconnect();
            }
        });
    }, {
        threshold: 0.35
    });

    observer.observe(statsSection);
});
