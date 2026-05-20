(function () {
    function runLayoutV2() {
        const root = document.querySelector(".med_exact_dashboard");
        const header = document.querySelector(".mediot_compact_source_header");
        const trends = document.querySelector(".mediot_trends_exact");
        const directory = document.querySelector(".mediot_toolbar_exact");

        if (!root || !header || !trends || !directory) return;
        if (document.querySelector(".mediot_layout_v2")) return;

        const shell = document.createElement("div");
        shell.className = "mediot_layout_v2";

        const left = document.createElement("div");
        left.className = "mediot_left_v2";

        const right = document.createElement("div");
        right.className = "mediot_right_v2";

        root.insertBefore(shell, header);
        shell.appendChild(left);
        shell.appendChild(right);

        left.appendChild(header);
        left.appendChild(trends);
        right.appendChild(directory);
    }

    function start() {
        runLayoutV2();
        setTimeout(runLayoutV2, 300);
        setTimeout(runLayoutV2, 1000);
        setTimeout(runLayoutV2, 2500);

        const obs = new MutationObserver(runLayoutV2);
        obs.observe(document.body, { childList: true, subtree: true });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start);
    } else {
        start();
    }

    window.addEventListener("load", start);
})();
