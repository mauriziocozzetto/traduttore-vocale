import streamlit as st
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import io
from pydub import AudioSegment

def transcribe_audio(audio_bytes, language_code):
    r = sr.Recognizer()
    
    try:
        # 1. Carica i bytes (che arrivano come WebM dal browser) tramite pydub
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        
        # 2. Converti in WAV (PCM) in memoria
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)
        
        # 3. Ora SpeechRecognition può leggerlo correttamente
        with sr.AudioFile(wav_io) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language=language_code)
            return text
    except Exception as e:
        st.error(f"Errore tecnico: {e}")
        return None

# Configurazione Pagina
st.set_page_config(page_title="Traduttore Vocale Cloud", page_icon="🎤")

st.title("🎤 Traduttore Vocale Intelligente")
st.info("Registra la tua voce dal browser. L'app trascriverà, tradurrà e parlerà per te.")

# --- SIDEBAR PER IMPOSTAZIONI ---
st.sidebar.header("Configurazione")
lingua_orig = st.sidebar.selectbox("La tua lingua:", ["it-IT", "en-US", "fr-FR", "es-ES"], index=0)
lingua_dest = st.sidebar.selectbox("Traduci in:", ["en", "it", "es", "fr", "de"], index=0)

# --- COMPONENTE MICROFONO (Browser friendly) ---
st.write("### 1. Registra la tua voce")
audio_input = mic_recorder(
    start_prompt="Avvia Registrazione 🎙️",
    stop_prompt="Ferma e Elabora 🛑",
    key='recorder'
)

if audio_input:
    # Recuperiamo i bytes dell'audio
    audio_bytes = audio_input['bytes']
    st.audio(audio_bytes) # Permette all'utente di riascoltarsi

    # --- ELABORAZIONE ---
    with st.spinner("Trascrizione e traduzione in corso..."):
        
        # A. Trascrizione
        testo_originale = transcribe_audio(audio_bytes, lingua_orig)
        
        if testo_originale:
            st.success(f"**Hai detto:** {testo_originale}")

            # B. Traduzione
            translator = Translator()
            traduzione = translator.translate(testo_originale, dest=lingua_dest)
            st.balloons()
            st.subheader(f"Traduzione ({lingua_dest}):")
            st.write(f"### {traduzione.text}")

            # C. Sintesi Vocale (gTTS)
            tts = gTTS(text=traduzione.text, lang=lingua_dest)
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            
            st.write("### 2. Ascolta la traduzione")
            st.audio(audio_fp)
            
        else:
            st.error("Non ho potuto riconoscere la voce. Riprova parlando più chiaramente.")

st.divider()

st.caption("Sviluppato con Streamlit, SpeechRecognition e gTTS (Senza PyAudio)")
