import os
import sys
import difflib
from gtts import gTTS
import pygame
from tkinter import Tk, Label, Button, Frame, messagebox, PhotoImage
from PIL import Image, ImageTk, ImageSequence
import threading
from time import sleep

# `src` klasörünü arama yoluna ekleyin
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from speech_to_text import recognize_speech, process_text

class GifApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Erişilebilir Konuşma - Tercüme Asistanı (EKTA)")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f4fefe")  

        self.title_frame = Frame(root, bg="#f4fefe")
        self.title_frame.pack(anchor="nw", padx=10, pady=10)

        self.logo_image = PhotoImage(file=r"C:\Users\Lenovo\Desktop\Turkish_Sign_Language_Translator\src\img\logo.png")
        self.logo_label = Label(self.title_frame, image=self.logo_image, bg="#f4fefe")
        self.logo_label.pack(side="left", padx=10)

        self.title_label = Label(self.title_frame, text="Erişilebilir Konuşma - Tercüme Asistanı (EKTA)", font=("Arial", 20, "bold"), fg="#2abef4", bg="#f4fefe")
        self.title_label.pack(side="left", padx=10)

        self.start_button = Button(root, text="Başla", font=("Arial", 14), command=self.start_recognition, bg="#f4fefe", fg="#000000")
        self.start_button.pack(pady=10)

        self.status_label = Label(root, text="", font=("Arial", 14), fg="#000000", bg="#f4fefe")
        self.status_label.pack(pady=10)

        self.detected_text_label = Label(root, text="", font=("Arial", 14), fg="#000000", bg="#f4fefe")
        self.detected_text_label.pack(pady=10)

        self.gif_frame = Frame(root, bg="#f4fefe")
        self.gif_frame.pack(pady=25)

    def play_sound(self, sound_file):
        pygame.mixer.init()
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.quit()

    def say_text(self, text):
        tts = gTTS(text, lang='tr')
        tts.save("speech.mp3")
        self.play_sound("speech.mp3")
        os.remove("speech.mp3")

    def get_word_root(self, word):
        suffixes = ["e", "im", "in", "um", "sin", "siniz", "ler", "lar", "dir", "dır", "dur", "mız", "tik", "mek", "mekte"]
        for suffix in suffixes:
            if word.endswith(suffix):
                return word[:-len(suffix)]
        return word

    def find_similar_word(self, word, directory_path):
        gif_files = os.listdir(directory_path)
        similar_word = difflib.get_close_matches(word, [f.split('.')[0] for f in gif_files], n=1, cutoff=0.6)
        if similar_word:
            return similar_word[0]
        return None

    def find_gif(self, word, gif_dir):
        first_letter = word[0]
        if not first_letter.isalpha():
            return None  # Sayısal kelimeler için GIF bulunmuyor
        directory_path = os.path.join(gif_dir, first_letter)
        gif_path = os.path.join(directory_path, f"{word}.gif")
        if os.path.exists(gif_path):
            return gif_path
        word_root = self.get_word_root(word)
        gif_path = os.path.join(directory_path, f"{word_root}.gif")
        if os.path.exists(gif_path):
            return gif_path
        similar_word = self.find_similar_word(word_root, directory_path)
        if similar_word:
            return os.path.join(directory_path, f"{similar_word}.gif")
        return None

    def translate_to_gif(self, text, gif_dir, new_gif_dir):
        words = text.lower().split()
        os.makedirs(new_gif_dir, exist_ok=True)
        gif_paths = []
        for word in words:
            gif_path = self.find_gif(word, gif_dir)
            if gif_path:
                new_gif_path = os.path.join(new_gif_dir, f"{word}.gif")
                with open(gif_path, 'rb') as source, open(new_gif_path, 'wb') as dest:
                    dest.write(source.read())
                gif_paths.append(new_gif_path)
                print(f"GIF bulundu ve kopyalandı: {new_gif_path}")
            else:
                print(f"GIF bulunamadı: {word}")
        return gif_paths

    def display_gifs(self, gif_paths):
        for widget in self.gif_frame.winfo_children():
            widget.destroy()
        for gif_path in gif_paths:
            print(f"GIF gösteriliyor: {gif_path}")
            self.show_gif(gif_path)

    def show_gif(self, gif_path):
        img = Image.open(gif_path)
        frames = [ImageTk.PhotoImage(img.copy().resize((150, 150), Image.Resampling.LANCZOS)) for img in ImageSequence.Iterator(img)]
        label = Label(self.gif_frame, bg="#f4fefe")
        label.pack(side="left", padx=10)

        def animate(counter):
            label.config(image=frames[counter])
            self.root.update()
            self.root.after(50, animate, (counter + 1) % len(frames))

        animate(0)

    def start_recognition(self):
        gif_dir = r'C:\Users\Lenovo\Desktop\Turkish_Sign_Language_Translator\Turkish_Sign_Language_Dictionary\data\img'
        new_gif_dir = r'C:\Users\Lenovo\Desktop\Turkish_Sign_Language_Translator\new_gifs'

        start_sound_path = r'C:\Users\Lenovo\Desktop\Turkish_Sign_Language_Translator\src\retro-audio-logo-94648.mp3'
        end_sound_path = r'C:\Users\Lenovo\Desktop\Turkish_Sign_Language_Translator\src\retro-audio-logo-94648.mp3'

        if not os.path.exists(start_sound_path) or not os.path.exists(end_sound_path):
            print("Ses dosyaları bulunamadı. Lütfen dosyaların doğru yerleştirildiğinden emin olun.")
            return

        self.play_sound(start_sound_path)

        self.status_label.config(text="Mikrofon açılacaktır. Lütfen birkaç saniye bekleyin 😊")
        self.root.update()
        sleep(3)  # Kullanıcının mikrofon açılmadan önce birkaç saniye beklemesi için

        self.status_label.config(text="Mikrofon açıldı. Konuşabilirsiniz.")
        self.root.update()

        threading.Thread(target=self.recognize_and_process_speech, args=(gif_dir, new_gif_dir, end_sound_path)).start()

    def recognize_and_process_speech(self, gif_dir, new_gif_dir, end_sound_path):
        text = recognize_speech()
        if text:
            self.detected_text_label.config(text=f"Algılanan metin: {text}")
            self.say_text(f"Algılanan metin: {text}")
            process_text(text)  # Metin işleme ve analiz işlemleri
            gif_paths = self.translate_to_gif(text, gif_dir, new_gif_dir)
            self.display_gifs(gif_paths)
        else:
            self.status_label.config(text="Konuşma algılanamadı. Lütfen tekrar deneyin.")
            self.root.update()

        self.play_sound(end_sound_path)

        self.ask_continue()

    def ask_continue(self):
        answer = messagebox.askyesno("Devam?", "Konuşmak ve tercüme etmeye devam etmek ister misiniz?")
        if answer:
            self.start_recognition()
        else:
            messagebox.showinfo("Görüşmek üzere!", "Çok teşekkür ederiz. Bir sonraki görüşmemizde görüşmek üzere!")
            self.root.quit()

if __name__ == "__main__":
    root = Tk()
    app = GifApp(root)
    root.mainloop()
