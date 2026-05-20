document.addEventListener("DOMContentLoaded", function () {
    function normalize(str) {
        return (str || "").replace(/\s+/g, " ").trim().toLowerCase();
    }

    function findNodeByExactText(selector, text) {
        const target = normalize(text);
        return [...document.querySelectorAll(selector)].find(el => normalize(el.textContent) === target);
    }

    function findSectionFromBadge(badgeEl) {
        if (!badgeEl) return null;
        return badgeEl.closest("section") || badgeEl.closest("div");
    }

    function findCardContainer(startEl, stopEl) {
        let current = startEl;
        while (current && current !== stopEl) {
            const rect = current.getBoundingClientRect();
            if (rect.width > 260 && rect.height > 220) {
                return current;
            }
            current = current.parentElement;
        }
        return startEl.closest("div");
    }

    const badge = findNodeByExactText("span, p, div, a", "Why MedIoT");
    if (!badge) return;

    let section = findSectionFromBadge(badge);
    if (!section) return;

    while (
        section &&
        section.parentElement &&
        !section.querySelector("*")?.textContent?.includes("Real-Time Patient Progress")
    ) {
        section = section.parentElement;
    }

    if (!section) return;

    section.classList.add("mediot-why-polished");
    badge.classList.add("mediot-why-badge");

    const title = [...section.querySelectorAll("h1, h2, h3")].find(el =>
        normalize(el.textContent).includes("healthcare intelligence designed for real-time monitoring")
    );
    if (title) title.classList.add("mediot-why-title");

    const subtitle = [...section.querySelectorAll("p, div")].find(el =>
        normalize(el.textContent).includes("mediot combines ai")
    );
    if (subtitle) subtitle.classList.add("mediot-why-subtitle");

    const cardNames = [
        "Real-Time Patient Progress",
        "AI-Powered Personalization",
        "IoT Integration"
    ];

    const cards = [];

    cardNames.forEach(name => {
        const heading = [...section.querySelectorAll("h1, h2, h3, h4, h5, h6, div, p")].find(el =>
            normalize(el.textContent) === normalize(name)
        );
        if (!heading) return;

        const card = findCardContainer(heading, section);
        if (!card) return;

        card.classList.add("mediot-why-card", "mediot-why-reveal");
        cards.push(card);

        const iconHolder =
            card.querySelector("img")?.parentElement ||
            card.querySelector("svg")?.parentElement ||
            card.querySelector("i")?.parentElement ||
            card.querySelector("div");

        if (iconHolder) {
            iconHolder.classList.add("mediot-why-icon-wrap");
        }

        card.style.cursor = "pointer";

        card.addEventListener("click", function () {
            cards.forEach(c => c.classList.remove("is-active"));
            card.classList.add("is-active");
        });
    });

    if (cards.length) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.classList.add("is-visible");
                    }, index * 120);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.18 });

        cards.forEach(card => observer.observe(card));
    }
});
