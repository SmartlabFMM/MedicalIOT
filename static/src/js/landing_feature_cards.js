(function () {
    "use strict";

    function initMedFeatureCards() {
        const cards = document.querySelectorAll(".med_feature_card");

        if (!cards.length) {
            return;
        }

        cards.forEach(function (card) {
            card.setAttribute("tabindex", "0");

            card.addEventListener("mousemove", function (event) {
                const rect = card.getBoundingClientRect();
                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;

                const rotateX = ((y / rect.height) - 0.5) * -5;
                const rotateY = ((x / rect.width) - 0.5) * 5;

                card.style.setProperty("--med-tilt-x", rotateX + "deg");
                card.style.setProperty("--med-tilt-y", rotateY + "deg");
            });

            card.addEventListener("mouseleave", function () {
                card.style.setProperty("--med-tilt-x", "0deg");
                card.style.setProperty("--med-tilt-y", "0deg");
            });

            card.addEventListener("click", function () {
                cards.forEach(function (other) {
                    if (other !== card) {
                        other.classList.remove("med_feature_active");
                    }
                });

                card.classList.toggle("med_feature_active");
                card.classList.remove("med_feature_pop");

                void card.offsetWidth;

                card.classList.add("med_feature_pop");

                window.setTimeout(function () {
                    card.classList.remove("med_feature_pop");
                }, 480);
            });

            card.addEventListener("keydown", function (event) {
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    card.click();
                }
            });
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initMedFeatureCards);
    } else {
        initMedFeatureCards();
    }
})();
