const uploadBtn = document.getElementById("uploadBtn");
const askBtn = document.getElementById("askBtn");
const loader = document.getElementById("loader");

const summaryBox = document.getElementById("summaryBox");
const chatBox = document.getElementById("chatBox");

let uploaded = false;

// UPLOAD PDF
uploadBtn.addEventListener("click", async () => {
    const fileInput = document.getElementById("pdfFile");
    if (!fileInput.files.length) {
        alert("Please upload a PDF");
        return;
    }

    loader.classList.remove("hidden");

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const res = await fetch("/document/upload", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    loader.classList.add("hidden");

    summaryBox.value = data.summary || "Summary generated successfully.";
    uploaded = true;
});

// ASK QUESTION
askBtn.addEventListener("click", async () => {
    if (!uploaded) {
        alert("Upload PDF first");
        return;
    }

    const question = document.getElementById("questionInput").value;
    if (!question) return;

    loader.classList.remove("hidden");

    const res = await fetch("/document/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
    });

    const data = await res.json();
    loader.classList.add("hidden");

    chatBox.innerHTML += `
        <div class="chat-user">You: ${question}</div>
        <div class="chat-ai">AI: ${data.answer}</div>
    `;
});
