import os
import sys
import difflib
import requests
from gtts import gTTS
import pygame
import threading
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from pathlib import Path

# src klasörünü arama yoluna ekleyin
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from speech_to_text import recognize_speech

# Sabit yolları tanımla
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / 'static'
GIF_DIR = BASE_DIR / 'Turkish_Sign_Language_Dictionary' / 'data' / 'img'
NEW_GIF_DIR = STATIC_DIR / 'new_gifs'
SOUND_FILE = Path('C:/Users/Lenovo/Desktop/Turkish_Sign_Language_Translator/src/retro-audio-logo-94648.mp3')
LOGO_PATH = Path('C:/Users/Lenovo/Desktop/Turkish_Sign_Language_Translator/src/img/logo.png')

# Flask uygulamasını oluştur
app = Flask(__name__,
    static_url_path='/static',
    static_folder=str(STATIC_DIR),
    template_folder=str(BASE_DIR / 'templates'))
socketio = SocketIO(app)

# Dizinleri oluştur
NEW_GIF_DIR.mkdir(parents=True, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/static/new_gifs/<path:filename>')
def serve_gif(filename):
    return send_from_directory(str(NEW_GIF_DIR), filename)

@app.route('/static/logo.png')
def serve_logo():
    return send_from_directory(str(LOGO_PATH.parent), LOGO_PATH.name)

def play_sound(sound_file):
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

def say_text(text):
    try:
        speech_file = STATIC_DIR / 'speech.mp3'
        tts = gTTS(text, lang='tr')
        tts.save(str(speech_file))
        play_sound(str(speech_file))
        speech_file.unlink(missing_ok=True)
    except Exception as e:
        print(f"Metin okuma hatası: {e}")

def get_word_root(word):
    suffixes = ["e", "im", "in", "um", "sin", "siniz", "ler", "lar", "dir", "dır", "dur", "mız", "tik", "mek", "mekte"]
    for suffix in sorted(suffixes, key=len, reverse=True):
        if word.endswith(suffix):
            return word[:-len(suffix)]
    return word

def find_similar_word(word, directory_path):
    try:
        gif_files = [f.stem for f in Path(directory_path).glob('*.gif')]
        similar_words = difflib.get_close_matches(word, gif_files, n=1, cutoff=0.6)
        return similar_words[0] if similar_words else None
    except Exception as e:
        print(f"Benzer kelime arama hatası: {e}")
        return None

def find_gif(word, gif_dir):
    if not word or not word[0].isalpha():
        return None

    first_letter = word[0].lower()
    directory_path = Path(gif_dir) / first_letter

    if not directory_path.exists():
        return None

    # Tam kelime eşleşmesi
    gif_path = directory_path / f"{word}.gif"
    if gif_path.exists():
        return gif_path

    # Kök kelime kontrolü
    word_root = get_word_root(word)
    gif_path = directory_path / f"{word_root}.gif"
    if gif_path.exists():
        return gif_path

    # Benzer kelime kontrolü
    similar_word = find_similar_word(word_root, directory_path)
    if similar_word:
        return directory_path / f"{similar_word}.gif"

    return None

def translate_to_gif(text, gif_dir, new_gif_dir):
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

def analyze_sentiment(text):
    API_URL = "https://api-inference.huggingface.co/models/dbmdz/bert-base-turkish-uncased"
    headers = {"Authorization": "Bearer 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"}
    
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    result = response.json()
    
    return result

@app.route('/start_recognition', methods=['POST'])
def start_recognition():
    try:
        if not SOUND_FILE.exists():
            return jsonify({
                "error": "Ses dosyası bulunamadı. Lütfen dosyanın doğru yerleştirildiğinden emin olun."
            })

        play_sound(str(SOUND_FILE))
        recognition_thread = threading.Thread(
            target=process_recognition,
            args=(str(GIF_DIR), str(NEW_GIF_DIR))
        )
        recognition_thread.start()

        return jsonify({"status": True})
    except Exception as e:
        return jsonify({"error": str(e)})

def process_recognition(gif_dir, new_gif_dir):
    try:
        text = recognize_speech()
        if text:
            sentiment = analyze_sentiment(text)
            say_text(f"Algılanan metin: {text}")
            socketio.emit('text_recognized', {'text': text, 'sentiment': sentiment})
            gif_paths = translate_to_gif(text, gif_dir, new_gif_dir)
            gif_urls = [f"/static/new_gifs/{path.name}" for path in gif_paths]
            socketio.emit('update_gifs', {'gifs': gif_urls})
            play_sound(str(SOUND_FILE))
        else:
            ask_for_continuation()
    except Exception as e:
        print(f"Konuşma tanıma hatası: {e}")
        ask_for_continuation()
        socketio.emit('recognition_error', {'error': str(e)})

def ask_for_continuation():
    socketio.emit('update_gifs', {'gifs': []})  # Clear GIFs
    status_label = "Google Speech Recognition konuşmayı anlayamadı. Konuşmaya devam etmek ister misiniz?"
    socketio.emit('ask_continue', {'status': status_label})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)
