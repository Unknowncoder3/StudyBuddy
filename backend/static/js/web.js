const scrapeBtn = document.getElementById("scrapeBtn");
const askBtn = document.getElementById("askBtn");
const loader = document.getElementById("loader");

const previewBox = document.getElementById("previewBox");
const answerBox = document.getElementById("answerBox");

scrapeBtn.addEventListener("click", async () => {
    const url = document.getElementById("urlInput").value;

    if (!url) {
        alert("Please enter a URL");
        return;
    }

    loader.classList.remove("hidden");
    previewBox.innerHTML = "⏳ Scraping website...";

    try {
        const res = await fetch("/web/scrape", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({ url })
        });

        const data = await res.json();

        // ✅ SHOW PREVIEW (FIRST 1000 CHARS)
        previewBox.innerText =
            data.preview && data.preview.length > 0
                ? data.preview
                : "No preview available";

    } catch (err) {
        previewBox.innerText = "❌ Error scraping website";
        console.error(err);
    }

    loader.classList.add("hidden");
});

askBtn.addEventListener("click", async () => {
    const question = document.getElementById("questionInput").value;

    if (!question) {
        alert("Enter a question");
        return;
    }

    loader.classList.remove("hidden");
    answerBox.value = "Thinking...";

    try {
        const res = await fetch("/web/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({ question })
        });

        const data = await res.json();
        answerBox.value = data.answer || "No answer returned";

    } catch (err) {
        answerBox.value = "❌ Error getting answer";
        console.error(err);
    }

    loader.classList.add("hidden");
});
