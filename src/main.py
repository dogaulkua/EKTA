import os
import sys
import difflib
from gtts import gTTS
from playsound import playsound
from time import sleep

# `src` klasörünü arama yoluna ekleyin
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from speech_to_text import recognize_speech

def play_sound(sound_file):
    playsound(sound_file)

def say_text(text):
    tts = gTTS(text, lang='tr')
    tts.save("speech.mp3")
    play_sound("speech.mp3")
    os.remove("speech.mp3")

def get_word_root(word):
    suffixes = ["e", "im", "in", "um", "sin", "siniz", "ler", "lar", "dir", "dır", "dur", "mız", "tik", "mek", "mekte"]
    for suffix in suffixes:
        if word.endswith(suffix):
            return word[:-len(suffix)]
    return word

def find_similar_word(word, directory_path):
    gif_files = os.listdir(directory_path)
    similar_word = difflib.get_close_matches(word, [f.split('.')[0] for f in gif_files], n=1, cutoff=0.6)
    if similar_word:
        return similar_word[0]
    return None

def find_gif(word, gif_dir):
    first_letter = word[0]
    if not first_letter.isalpha():
        return None  # Sayısal kelimeler için GIF bulunmuyor
    directory_path = os.path.join(gif_dir, first_letter)
    gif_path = os.path.join(directory_path, f"{word}.gif")
    if os.path.exists(gif_path):
        return gif_path
    word_root = get_word_root(word)
    gif_path = os.path.join(directory_path, f"{word_root}.gif")
    if os.path.exists(gif_path):
        return gif_path
    similar_word = find_similar_word(word_root, directory_path)
    if similar_word:
        return os.path.join(directory_path, f"{similar_word}.gif")
    return None

def translate_to_gif(text, gif_dir, new_gif_dir):
    words = text.lower().split()
    os.makedirs(new_gif_dir, exist_ok=True)
    gif_paths = []
    for word in words:
        gif_path = find_gif(word, gif_dir)
        if gif_path:
            new_gif_path = os.path.join(new_gif_dir, f"{word}.gif")
            with open(gif_path, 'rb') as source, open(new_gif_path, 'wb') as dest:
                dest.write(source.read())
            gif_paths.append(new_gif_path)
            print(f"GIF bulundu ve kopyalandı: {new_gif_path}")
        else:
            print(f"GIF bulunamadı: {word}")
    return gif_paths

def display_gifs(gif_paths):
    for gif_path in gif_paths:
        print(f"GIF gösteriliyor: {gif_path}")
        sleep(2)  # 2 saniye duraklama
    continue_recognition = input("Konuşmaya devam etmek ister misiniz? (evet/hayır): ").strip().lower()
    return continue_recognition == "evet"

def main():
    gif_dir = r'C:\Users\Lenovo\Desktop\Turkish_Sign_Language_Translator\Turkish_Sign_Language_Dictionary\data\img'
    new_gif_dir = r'C:\Users\Lenovo\Desktop\Turkish_Sign_Language_Translator\new_gifs'

    start_sound_path = r'C:\Users\Lenovo\Desktop\Turkish_Sign_Language_Translator\src\retro-audio-logo-94648.mp3'
    end_sound_path = r'C:\Users\Lenovo\Desktop\Turkish_Sign_Language_Translator\src\retro-audio-logo-94648.mp3'

    if not os.path.exists(start_sound_path) or not os.path.exists(end_sound_path):
        print("Ses dosyaları bulunamadı. Lütfen dosyaların doğru yerleştirildiğinden emin olun.")
        return

    play_sound(start_sound_path)

    name = input("Lütfen isminizi girin: ")

    while True:
        print("Mikrofon açıldı.")
        text = recognize_speech()
        if text:
            say_text(f"Algılanan metin: {text}")
            gif_paths = translate_to_gif(text, gif_dir, new_gif_dir)
            if not display_gifs(gif_paths):
                break
        else:
            print("Konuşma algılanamadı. Lütfen tekrar deneyin.")

    play_sound(end_sound_path)

if __name__ == "__main__":
    main()
