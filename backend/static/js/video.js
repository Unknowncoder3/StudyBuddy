const analyzeBtn = document.getElementById("analyzeBtn");
const loader = document.getElementById("loader");

const transcriptBox = document.getElementById("transcriptBox");
const summaryBox = document.getElementById("summaryBox");
const timelineList = document.getElementById("timelineList");
const captionPreview = document.getElementById("captionPreview");

analyzeBtn.addEventListener("click", async () => {
    const fileInput = document.getElementById("videoInput");

    if (!fileInput.files.length) {
        alert("Please select a video file");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    // Reset UI
    transcriptBox.value = "";
    summaryBox.innerHTML = "<p class='muted'>Processing...</p>";
    timelineList.innerHTML = "<li class='muted'>Processing...</li>";
    captionPreview.innerHTML = "<li class='muted'>Processing...</li>";

    loader.classList.remove("hidden");

    try {
        const res = await fetch("/video/upload", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        /* =========================
           TRANSCRIPT
        ========================= */
        transcriptBox.value = data.transcript || "No transcript generated.";

        /* =========================
           SUMMARY
        ========================= */
        summaryBox.innerHTML = data.summary
            ? data.summary
            : "<p class='muted'>No summary available.</p>";

        /* =========================
           TIMELINE
        ========================= */
        timelineList.innerHTML = "";
        if (data.timeline && data.timeline.length) {
            data.timeline.forEach(item => {
                const li = document.createElement("li");
                li.textContent = item;
                timelineList.appendChild(li);
            });
        } else {
            timelineList.innerHTML = "<li class='muted'>No timeline data</li>";
        }

        /* =========================
           SAMPLED CAPTIONS
        ========================= */
        captionPreview.innerHTML = "";
        if (data.sampled_captions && data.sampled_captions.length) {
            data.sampled_captions.forEach(item => {
                const li = document.createElement("li");
                li.textContent = item;
                captionPreview.appendChild(li);
            });
        } else {
            captionPreview.innerHTML = "<li class='muted'>No sampled captions</li>";
        }

    } catch (err) {
        console.error(err);
        alert("Error analyzing video. Check server logs.");
    }

    loader.classList.add("hidden");
});
