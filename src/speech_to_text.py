import speech_recognition as sr
import pygame

def play_sound(sound_file):
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    pygame.mixer.quit()

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Ortam gürültüsünü hızlıca ayarlamak için süreyi 1 saniye yapıyoruz
        print("Mikrofon açıldı. Konuşabilirsiniz.")

        while True:
            try:
                print("Ses algılanıyor...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)  # Ses duyulunca algılamaya başlar ve 10 saniye süreyle dinler
                print("Ses kaydedildi, işleniyor...")
                play_sound(r'C:\Users\Lenovo\Desktop\Turkish_Sign_Language_Translator\src\retro-audio-logo-94648.mp3')

                text = recognizer.recognize_google(audio, language="tr-TR")
                print("Algılanan Metin: ", text)
                return text
            except sr.UnknownValueError:
                print("Sesi Anlayamadım. Tekrar deneyin.")
                continue
            except sr.RequestError:
                print("Servis Kullanılamıyor.")
                return None
            except Exception as e:
                print(f"Bir hata oluştu: {e}")
                return None

if __name__ == "__main__":
    recognize_speech()
