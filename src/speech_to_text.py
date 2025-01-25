import speech_recognition as sr
import pygame
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import BertTokenizer, BertModel
import os
import torch

# NLTK resources
if not os.path.exists('C:/Users/Lenovo/nltk_data'):
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('vader_lexicon')

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
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Mikrofon açıldı. Konuşabilirsiniz.")

        while True:
            try:
                print("Ses algılanıyor...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
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

def process_text(text):
    # Kelime tokenizasyonu
    tokens = word_tokenize(text)
    print("Kelime Tokenleri:", tokens)

    # Stop words çıkarımı
    stop_words = set(stopwords.words('turkish'))
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
    print("Filtrelenmiş Tokenler:", filtered_tokens)

    # Sentiment analizi
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)
    print("Sentiment Analizi:", sentiment)

    # Transformers ile metin işleme
    tokenizer = BertTokenizer.from_pretrained("dbmdz/bert-base-turkish-cased")
    model = BertModel.from_pretrained("dbmdz/bert-base-turkish-cased")
    
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    print("Transformers ile Metin İşleme Tamamlandı.")

    return {
        'tokens': tokens,
        'filtered_tokens': filtered_tokens,
        'sentiment': sentiment
    }

if __name__ == "__main__":
    text = recognize_speech()
    if text:
        process_text(text)