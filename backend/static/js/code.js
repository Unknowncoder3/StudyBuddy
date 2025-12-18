document.addEventListener("DOMContentLoaded", () => {

    const analyzeBtn = document.getElementById("analyzeBtn");
    const loader = document.getElementById("loader");
    const outputBox = document.getElementById("analysisOutput");

    if (!analyzeBtn) {
        console.error("❌ analyzeBtn not found");
        return;
    }

    analyzeBtn.addEventListener("click", async () => {
        const code = document.getElementById("codeInput").value;
        const language = document.getElementById("languageSelect").value;

        if (!code.trim()) {
            alert("Please paste some code");
            return;
        }

        loader.classList.remove("hidden");
        outputBox.innerHTML = "";

        try {
            const res = await fetch("/analyze-code", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ code, language })
            });

            const data = await res.json();
            loader.classList.add("hidden");

            if (data.error) {
                outputBox.innerHTML = `<p class="error">❌ ${data.error}</p>`;
                return;
            }

            renderExplanation(data.explanation);
            renderSuggestions(data.suggestions);

        } catch (err) {
            loader.classList.add("hidden");
            outputBox.innerHTML = `<p class="error">❌ Backend error</p>`;
            console.error(err);
        }
    });

    function renderExplanation(text) {
        if (!text) return;

        outputBox.innerHTML += `
            <div class="section">
                <h4>🔍 High-level explanation</h4>
                <pre>${escapeHTML(text)}</pre>
            </div>
        `;
    }

    function renderSuggestions(suggestions) {
        outputBox.innerHTML += `
            <div class="section">
                <h4>💡 Suggestions (rule-based)</h4>
            </div>
        `;

        if (!suggestions || suggestions.length === 0) {
            outputBox.innerHTML += `<p class="muted">No issues detected</p>`;
            return;
        }

        suggestions.forEach(s => {
            outputBox.innerHTML += `
                <div class="suggestion">
                    <strong>Line ${s.line || "-"}</strong>
                    <span class="tag">${s.category}</span>
                    <p>${escapeHTML(s.message)}</p>
                </div>
            `;
        });
    }

    function escapeHTML(str) {
        return str.replace(/[&<>"']/g, m => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        })[m]);
    }
});
