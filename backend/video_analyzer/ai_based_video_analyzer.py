import os
import tempfile
import shutil
import subprocess
from typing import List, Tuple

from PIL import Image
import numpy as np
import torch

# Whisper for local transcription
try:
    import whisper
except Exception:
    whisper = None

# BLIP captioning
try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
except Exception:
    BlipProcessor = None
    BlipForConditionalGeneration = None

# Ollama LLM
try:
    from langchain_ollama import OllamaLLM
    from langchain_core.prompts import PromptTemplate
    from langchain_community.chat_message_histories import ChatMessageHistory
except Exception:
    OllamaLLM = None
    PromptTemplate = None
    ChatMessageHistory = None

# OpenCV / imageio
try:
    import cv2
except Exception:
    cv2 = None
    try:
        import imageio
    except Exception:
        imageio = None


# =====================================================
# INITIALIZE MODELS (UNCHANGED)
# =====================================================

llm = OllamaLLM(model="mistral") if OllamaLLM else None
chat_history = ChatMessageHistory() if ChatMessageHistory else None


# =====================================================
# HELPERS (UNCHANGED)
# =====================================================

def format_time(seconds: float) -> str:
    if seconds is None:
        return "00:00"
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"


def find_ffmpeg() -> str:
    ff = shutil.which("ffmpeg")
    if ff:
        return ff
    raise RuntimeError("ffmpeg not found")


def extract_audio_ffmpeg(video_path: str, out_audio_path: str, sample_rate: int = 16000) -> str:
    ffmpeg_exe = find_ffmpeg()
    cmd = [
        ffmpeg_exe, "-y", "-i", video_path, "-vn",
        "-ac", "1", "-ar", str(sample_rate), "-f", "wav", out_audio_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_audio_path


def sample_frames_opencv(video_path: str, fps: float) -> List[Tuple[float, Image.Image]]:
    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frames = []
    idx = 0
    interval = max(1, int(video_fps / fps))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % interval == 0:
            t = idx / video_fps
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            frames.append((round(t, 3), img))
        idx += 1

    cap.release()
    return frames


def caption_image(processor, model, image, device):
    inputs = processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=32)
    return processor.decode(outputs[0], skip_special_tokens=True)


def transcribe_audio_whisper(model, audio_path: str) -> dict:
    return model.transcribe(audio_path)


def summarize_with_llm(llm, chat_history, content: str) -> str:
    if llm is None:
        return "(LLM unavailable)"

    prompt = PromptTemplate(
        input_variables=["chat_history", "content"],
        template="Previous chat: {chat_history}\nSummarize:\n{content}"
    )

    history_text = "\n".join(
        [f"{m.type.capitalize()}: {m.content}" for m in chat_history.messages]
    ) if chat_history else ""

    response = llm.invoke(prompt.format(chat_history=history_text, content=content))

    if chat_history:
        chat_history.add_user_message(content[:500])
        chat_history.add_ai_message(response)

    return response


# =====================================================
# PUBLIC API FUNCTION (FOR FLASK)
# =====================================================

def analyze_video(
    video_path: str,
    whisper_model_name="base",
    blip_model_name="Salesforce/blip-image-captioning-base",
    sample_fps=0.5,
    max_captions=100,
    use_gpu=True,
):
    tmpdir = tempfile.mkdtemp()

    audio_path = os.path.join(tmpdir, "audio.wav")
    extract_audio_ffmpeg(video_path, audio_path)

    transcript_text = ""
    if whisper:
        wmodel = whisper.load_model(whisper_model_name)
        transcript_text = transcribe_audio_whisper(wmodel, audio_path).get("text", "")

    device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"

    captions = []
    if cv2 and BlipProcessor and BlipForConditionalGeneration:
        frames = sample_frames_opencv(video_path, sample_fps)
        processor = BlipProcessor.from_pretrained(blip_model_name)
        model = BlipForConditionalGeneration.from_pretrained(blip_model_name).to(device)

        for t, img in frames[:max_captions]:
            captions.append((t, caption_image(processor, model, img, device)))

    timeline = [f"{format_time(t)} — {c}" for t, c in captions]

    aggregated = (
        "TRANSCRIPT:\n" + (transcript_text or "(no transcript)") +
        "\n\nCAPTIONS:\n" + "\n".join(timeline)
    )

    summary = summarize_with_llm(llm, chat_history, aggregated)

    shutil.rmtree(tmpdir, ignore_errors=True)

    return {
        "transcript": transcript_text,
        "captions": captions,
        "timeline": timeline,
        "summary": summary,
        "aggregated": aggregated,
    }
