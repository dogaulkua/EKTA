import speech_recognition as sr
from playsound import playsound

def play_sound(sound_file):
    playsound(sound_file)

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Konuşmanızı bekliyorum...")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Mikrofon açıldı.")
        try:
            audio = recognizer.listen(source, timeout=30, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print("Konuşma algılanmadı.")
            return None
        play_sound(r'C:\Users\Lenovo\Desktop\Turkish_Sign_Language_Translator\src\retro-audio-logo-94648.mp3')
        try:
            text = recognizer.recognize_google(audio, language="tr-TR")
            print("Algılanan Metin: ", text)
            return text
        except sr.UnknownValueError:
            print("Sesi Anlayamadım.")
            return None
        except sr.RequestError:
            print("Servis Kullanılamıyor.")
            return None

if __name__ == "__main__":
    recognize_speech()
