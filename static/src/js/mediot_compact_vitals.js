(function () {
    function compactVitals() {
        if (!window.location.pathname.startsWith("/web")) return;

        const all = Array.from(document.querySelectorAll("body *"));

        const title = all.find(function (el) {
            const txt = (el.innerText || "").trim();
            return txt === "Patient Monitoring Trends";
        });

        if (!title) return;

        let section = title;
        for (let i = 0; i < 8 && section.parentElement; i++) {
            const txt = section.innerText || "";
            const rect = section.getBoundingClientRect();

            if (
                txt.includes("Patient Monitoring Trends") &&
                txt.includes("Heart Rate") &&
                txt.includes("SpO2") &&
                txt.includes("Temperature") &&
                rect.width > window.innerWidth * 0.65
            ) {
                break;
            }
            section = section.parentElement;
        }

        section.classList.add("mediot-vitals-compact");

        const cards = Array.from(section.querySelectorAll("div")).filter(function (el) {
            const txt = el.innerText || "";
            const rect = el.getBoundingClientRect();
            return (
                rect.width > 180 &&
                rect.height > 120 &&
                (
                    txt.includes("Heart Rate") ||
                    txt.includes("SpO2") ||
                    txt.includes("Temperature")
                )
            );
        });

        cards.forEach(function (card) {
            card.classList.add("mediot-vital-card");
            card.style.setProperty("height", "170px", "important");
            card.style.setProperty("min-height", "150px", "important");
            card.style.setProperty("padding", "16px 18px", "important");

            card.querySelectorAll("canvas, svg").forEach(function (chart) {
                chart.style.setProperty("height", "82px", "important");
                chart.style.setProperty("max-height", "82px", "important");
            });
        });

        const bigWhiteCard = section;
        bigWhiteCard.style.setProperty("padding", "18px 22px", "important");
        bigWhiteCard.style.setProperty("margin-top", "12px", "important");
    }

    function start() {
        compactVitals();
        setTimeout(compactVitals, 500);
        setTimeout(compactVitals, 1500);
        setTimeout(compactVitals, 3000);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start);
    } else {
        start();
    }

    window.addEventListener("load", start);
})();
