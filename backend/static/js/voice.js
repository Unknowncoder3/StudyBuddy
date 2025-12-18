const micBtn = document.getElementById("micBtn");
const sendBtn = document.getElementById("sendBtn");
const input = document.getElementById("voiceInput");
const chatBox = document.getElementById("chatBox");

// ===============================
// 🎤 SPEECH TO TEXT
// ===============================
let recognition;

if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;

    recognition.onstart = () => {
        micBtn.classList.add("listening");
    };

    recognition.onend = () => {
        micBtn.classList.remove("listening");
    };

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        input.value = text;
    };
} else {
    micBtn.disabled = true;
    micBtn.title = "Speech recognition not supported";
}

micBtn.addEventListener("click", () => {
    if (recognition) recognition.start();
});

// ===============================
// 🔊 TEXT TO SPEECH
// ===============================
function speak(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    speechSynthesis.speak(utterance);
}

// ===============================
// 🚀 SEND TO BACKEND
// ===============================
sendBtn.addEventListener("click", async () => {
    const message = input.value.trim();
    if (!message) return;

    chatBox.innerHTML += `<p><b>You:</b> ${message}</p>`;
    input.value = "";

    const res = await fetch("/voice/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: message })
    });

    const data = await res.json();

    chatBox.innerHTML += `<p><b>AI:</b> ${data.response}</p>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    // 🔊 Speak AI response
    speak(data.response);
});
