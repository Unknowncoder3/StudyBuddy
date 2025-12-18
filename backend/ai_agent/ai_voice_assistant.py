import speech_recognition as sr
import pyttsx3

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

# =====================================================
# MODEL SETUP (UNCHANGED)
# =====================================================

llm = OllamaLLM(model="mistral")  # or llama3

# =====================================================
# MEMORY (REPLACES st.session_state)
# =====================================================

chat_history = ChatMessageHistory()

# =====================================================
# TEXT TO SPEECH (UNCHANGED)
# =====================================================

engine = pyttsx3.init()
engine.setProperty("rate", 160)

def speak(text: str):
    engine.say(text)
    engine.runAndWait()

# =====================================================
# SPEECH RECOGNITION (UNCHANGED)
# =====================================================

recognizer = sr.Recognizer()

def listen() -> str:
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio)
        return query.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return ""

# =====================================================
# PROMPT (UNCHANGED)
# =====================================================

prompt = PromptTemplate(
    input_variables=["chat_history", "question"],
    template="Previous conversation: {chat_history}\nUser: {question}\nAI:"
)

# =====================================================
# CORE AI LOGIC (UNCHANGED)
# =====================================================

def run_chain(question: str) -> str:
    chat_history_text = "\n".join(
        [f"{msg.type.capitalize()}: {msg.content}" for msg in chat_history.messages]
    )

    response = llm.invoke(
        prompt.format(chat_history=chat_history_text, question=question)
    )

    chat_history.add_user_message(question)
    chat_history.add_ai_message(response)

    return response

# =====================================================
# PUBLIC API FUNCTIONS (FOR FLASK / FRONTEND)
# =====================================================

def voice_assistant_text_api(user_text: str) -> str:
    """
    Call this when text is sent from frontend
    """
    if not user_text or not user_text.strip():
        return "I didn't hear anything. Please try again."

    response = run_chain(user_text)
    return response


def voice_assistant_voice_api() -> str:
    """
    Optional: Call this if you want mic-based interaction on server
    """
    user_query = listen()
    if not user_query:
        return "Sorry, I could not understand you."

    response = run_chain(user_query)
    speak(response)

    return response
