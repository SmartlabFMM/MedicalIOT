/** @odoo-module **/

(function () {
    "use strict";

    function ready(fn) {
        if (document.readyState !== "loading") {
            fn();
        } else {
            document.addEventListener("DOMContentLoaded", fn);
        }
    }

    function addBodyAnimationFlag() {
        setTimeout(() => {
            document.body.classList.add("med-animated");
        }, 80);
    }

    function animateRoleCards() {
        const cards = document.querySelectorAll(".med_role_card, .role-card, .med_role_option");
        if (!cards.length) return;

        cards.forEach((card, index) => {
            card.style.transitionDelay = `${index * 90}ms`;

            card.addEventListener("mouseenter", () => {
                card.classList.add("med-active");
            });

            card.addEventListener("mouseleave", () => {
                if (!card.classList.contains("med-selected")) {
                    card.classList.remove("med-active");
                }
            });

            card.addEventListener("click", () => {
                cards.forEach(c => {
                    c.classList.remove("med-selected");
                    c.classList.remove("med-active");
                });
                card.classList.add("med-selected");
                card.classList.add("med-active");
            });
        });
    }

    function enhanceLoginForm() {
        const form = document.querySelector('.med_login_right form, form[action="/web/login"]');
        if (!form) return;

        const button = form.querySelector(".med_btn, button[type='submit']");
        const inputs = form.querySelectorAll("input");

        inputs.forEach((input) => {
            input.addEventListener("invalid", () => {
                input.classList.add("med-invalid");
                setTimeout(() => input.classList.remove("med-invalid"), 450);
            });

            input.addEventListener("input", () => {
                input.classList.remove("med-invalid");
            });
        });

        form.addEventListener("submit", function () {
            if (!form.checkValidity()) return;

            if (button) {
                button.classList.add("is-loading");
                button.disabled = true;
                if (!button.dataset.originalText) {
                    button.dataset.originalText = button.textContent.trim();
                }
                button.textContent = "Signing In";
            }
        });
    }

    function addParallax() {
        const left = document.querySelector(".med_login_left");
        const hero = document.querySelector(".med_hero");
        const badge = document.querySelector(".med_top_badge");

        if (!left || !hero) return;

        left.addEventListener("mousemove", (e) => {
            const rect = left.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width - 0.5) * 10;
            const y = ((e.clientY - rect.top) / rect.height - 0.5) * 10;

            hero.style.transform = `translate(${x * 0.6}px, ${y * 0.6}px)`;
            if (badge) {
                badge.style.transform = `translate(${x * 0.35}px, ${y * 0.35}px)`;
            }
        });

        left.addEventListener("mouseleave", () => {
            hero.style.transform = "";
            if (badge) badge.style.transform = "";
        });
    }

    ready(function () {
        addBodyAnimationFlag();
        animateRoleCards();
        enhanceLoginForm();
        addParallax();
    });
})();
