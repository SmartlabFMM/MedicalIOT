(function () {
    function setupMedIoTHeroVideo() {
        const video = document.querySelector('.mediot_hero_video_clean');
        if (!video) return;

        const cleanStart = 0.20;
        const cleanEnd = 4.45; // restart before grey part appears

        video.muted = true;
        video.playsInline = true;
        video.autoplay = true;
        video.loop = false;
        video.preload = 'auto';

        function safePlay() {
            const p = video.play();
            if (p && p.catch) p.catch(function () {});
        }

        video.addEventListener('loadedmetadata', function () {
            try {
                video.currentTime = cleanStart;
            } catch (e) {}
            safePlay();
        });

        video.addEventListener('timeupdate', function () {
            if (video.currentTime >= cleanEnd) {
                try {
                    video.currentTime = cleanStart;
                } catch (e) {}
                safePlay();
            }
        });

        video.addEventListener('ended', function () {
            try {
                video.currentTime = cleanStart;
            } catch (e) {}
            safePlay();
        });

        document.addEventListener('visibilitychange', function () {
            if (!document.hidden) safePlay();
        });

        setTimeout(safePlay, 200);
        setTimeout(safePlay, 800);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupMedIoTHeroVideo);
    } else {
        setupMedIoTHeroVideo();
    }
})();
