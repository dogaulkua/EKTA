import os
import sys
import difflib
import threading
from pathlib import Path

import numpy as np
import pygame
import librosa
from flask import Flask, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO
from gtts import gTTS

# src klasörünü arama yoluna ekleyin
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from speech_to_text import recognize_speech, analyze_sentiment_from_audio

# === Sabit Yollar ===
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / 'static'
GIF_DIR = BASE_DIR / 'Turkish_Sign_Language_Dictionary' / 'data' / 'img'
NEW_GIF_DIR = STATIC_DIR / 'new_gifs'
SOUND_FILE = Path('C:/Users/Lenovo/Desktop/Turkish_Sign_Language_Translator/src/retro-audio-logo-94648.mp3')
LOGO_PATH = Path('C:/Users/Lenovo/Desktop/Turkish_Sign_Language_Translator/src/img/logo.png')

# === Flask ve SocketIO Uygulaması ===
app = Flask(
    __name__,
    static_url_path='/static',
    static_folder=str(STATIC_DIR),
    template_folder=str(BASE_DIR / 'templates')
)
socketio = SocketIO(app)

# new_gifs dizinini oluştur
NEW_GIF_DIR.mkdir(parents=True, exist_ok=True)

# === URL Yönlendirmeleri ===
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/static/new_gifs/<path:filename>')
def serve_gif(filename):
    """new_gifs klasöründeki GIF'leri sunmak için."""
    return send_from_directory(str(NEW_GIF_DIR), filename)

@app.route('/static/logo.png')
def serve_logo():
    """Logo dosyasını sunmak için."""
    return send_from_directory(str(LOGO_PATH.parent), LOGO_PATH.name)

# === Ses Çalma Fonksiyonları ===
def play_sound(sound_file):
    """Ses çalma işlemini (pygame) gerçekleştirir. Bloklayıcıdır."""
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Ses çalma hatası: {e}")
    finally:
        pygame.mixer.quit()

def play_sound_threaded(sound_file):
    """Ses çalma işlemini ayrı bir iş parçacığında (thread) başlatır."""
    threading.Thread(target=play_sound, args=(sound_file,), daemon=True).start()

# === Metin Okuma (TTS) Fonksiyonu ===
def say_text(text):
    """Gelen metni TTS ile oku (gTTS) ve ses dosyasını çal."""
    try:
        speech_file = STATIC_DIR / 'speech.mp3'
        tts = gTTS(text, lang='tr')
        tts.save(str(speech_file))
        play_sound_threaded(str(speech_file))
    except Exception as e:
        print(f"Metin okuma hatası: {e}")

# === GIF Bulma Yardımcı Fonksiyonları ===
def get_word_root(word):
    """Kelime kökünü bulmak için basit ek kesme."""
    suffixes = ["e", "im", "in", "um", "sin", "siniz", "ler", "lar", "dir", "dır", "dur", "mız", "tik", "mek", "mekte"]
    for suffix in sorted(suffixes, key=len, reverse=True):
        if word.endswith(suffix):
            return word[:-len(suffix)]
    return word

def find_similar_word(word, directory_path):
    """Benzer kelimeyi bulmak için difflib kullan."""
    try:
        gif_files = [f.stem for f in Path(directory_path).glob('*.gif')]
        similar_words = difflib.get_close_matches(word, gif_files, n=1, cutoff=0.6)
        return similar_words[0] if similar_words else None
    except Exception as e:
        print(f"Benzer kelime arama hatası: {e}")
        return None

def find_gif(word, gif_dir):
    """Verilen kelime için uygun GIF'i bul."""
    if not word or not word[0].isalpha():
        return None

    first_letter = word[0].lower()
    directory_path = Path(gif_dir) / first_letter

    if not directory_path.exists():
        return None

    # 1) Tam kelime eşleşmesi
    gif_path = directory_path / f"{word}.gif"
    if gif_path.exists():
        return gif_path

    # 2) Kök kelime kontrolü
    word_root = get_word_root(word)
    gif_path = directory_path / f"{word_root}.gif"
    if gif_path.exists():
        return gif_path

    # 3) Benzer kelime kontrolü
    similar_word = find_similar_word(word_root, directory_path)
    if similar_word:
        return directory_path / f"{similar_word}.gif"

    return None

def translate_to_gif(text, gif_dir, new_gif_dir):
    """Tanınan metindeki kelimelerin GIF'lerini bulup kopyalar."""
    words = text.lower().split()
    gif_paths = []

    for word in words:
        gif_path = find_gif(word, gif_dir)
        if gif_path:
            new_gif_path = Path(new_gif_dir) / f"{word}.gif"
            try:
                new_gif_path.write_bytes(gif_path.read_bytes())
                gif_paths.append(new_gif_path)
                print(f"GIF bulundu ve kopyalandı: {new_gif_path}")
            except Exception as e:
                print(f"GIF kopyalama hatası ({word}): {e}")
        else:
            print(f"GIF bulunamadı: {word}")

    return gif_paths

# === Konuşma Tanıma Sonrası Devam Sorusu ===
def ask_for_continuation():
    """Konuşma bitince, devam etmek isteyip istemediğini sorar."""
    # GIF'leri HEMEN temizlemiyoruz; kullanıcı 'Evet' diyene kadar ekranda kalsın.
    status_label = "Konuşmaya devam etmek ister misiniz?"
    socketio.emit('ask_continue', {'status': status_label})

# === Konuşma İşleme ve SocketIO Olayları ===
def process_recognition(gif_dir, new_gif_dir):
    """Arka planda çalışan konuşma tanıma ve işleme fonksiyonu."""
    try:
        text = recognize_speech()
        if text:
            sentiment = analyze_sentiment_from_audio("temp_audio.wav")
            say_text(f"Algılanan metin: {text}")
            # Tanınan metin ve duygu analizi, istemciye gönderiliyor
            socketio.emit('text_recognized', {'text': text, 'sentiment': sentiment})

            # GIF bulma ve istemciye gönderme
            gif_paths = translate_to_gif(text, gif_dir, new_gif_dir)
            gif_urls = [f"/static/new_gifs/{path.name}" for path in gif_paths]
            socketio.emit('update_gifs', {'gifs': gif_urls})

            # Konuşma bitiş sesi
            play_sound_threaded(str(SOUND_FILE))

            # Devam etmek ister misiniz?
            ask_for_continuation()
        else:
            # Metin anlaşılamadıysa da devam sorusuna geçelim
            ask_for_continuation()
    except Exception as e:
        print(f"Konuşma tanıma hatası: {e}")
        ask_for_continuation()
        socketio.emit('recognition_error', {'error': str(e)})

# === Flask Yönlendirmeleri ===
@app.route('/start_recognition', methods=['POST'])
def start_recognition():
    """Mikrofonu açma isteği (istemciden) geldiğinde tetiklenir."""
    try:
        if not SOUND_FILE.exists():
            return jsonify({"error": "Ses dosyası bulunamadı. Lütfen dosyanın doğru yerleştirildiğinden emin olun."})

        # Mikrofon açılış sesini bloklamadan çal
        play_sound_threaded(str(SOUND_FILE))

        # Konuşma işleme fonksiyonunu arka planda çalıştır
        socketio.start_background_task(process_recognition, str(GIF_DIR), str(NEW_GIF_DIR))
        return jsonify({"status": True})
    except Exception as e:
        return jsonify({"error": str(e)})

# === Uygulama Başlatma ===
if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=5000, use_reloader=False)
