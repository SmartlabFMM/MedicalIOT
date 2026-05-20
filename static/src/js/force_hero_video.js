(function () {
    function forceHeroVideo() {
        const hero = document.querySelector(".med_video_hero");
        if (!hero) return;

        let video = hero.querySelector(".mediot_forced_hero_video");

        if (!video) {
            video = document.createElement("video");
            video.className = "mediot_forced_hero_video";
            video.autoplay = true;
            video.muted = true;
            video.loop = true;
            video.playsInline = true;
            video.preload = "auto";

            const source = document.createElement("source");
            source.src = "/med_iot_command_center/static/description/hero.mp4?v=forcejs";
            source.type = "video/mp4";
            video.appendChild(source);

            hero.insertBefore(video, hero.firstChild);
        }

        hero.style.background = "transparent";
        hero.style.backgroundImage = "none";
        hero.style.backgroundColor = "transparent";
        hero.style.position = "relative";
        hero.style.overflow = "hidden";

        Object.assign(video.style, {
            display: "block",
            visibility: "visible",
            opacity: "1",
            position: "absolute",
            top: "0",
            left: "0",
            width: "100%",
            height: "100%",
            objectFit: "cover",
            zIndex: "1",
            filter: "none",
            transform: "none",
            pointerEvents: "none"
        });

        const overlay = hero.querySelector(".med_video_overlay");
        if (overlay) {
            overlay.style.display = "none";
            overlay.style.opacity = "0";
            overlay.style.background = "none";
        }

        Array.from(hero.children).forEach((child) => {
            if (child !== video && child !== overlay) {
                child.style.position = "relative";
                child.style.zIndex = "5";
            }
        });

        video.muted = true;
        video.loop = true;
        video.playsInline = true;

        try {
            video.load();
            const playPromise = video.play();
            if (playPromise && playPromise.catch) {
                playPromise.catch(function () {});
            }
        } catch (e) {}
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", forceHeroVideo);
    } else {
        forceHeroVideo();
    }

    setTimeout(forceHeroVideo, 500);
    setTimeout(forceHeroVideo, 1500);
})();
