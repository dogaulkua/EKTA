import speech_recognition as sr
import numpy as np
import librosa
import pandas as pd

# Belirgin özellikler fonksiyonu
def extract_features(audio, sr):
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40)
    chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
    mel = librosa.feature.melspectrogram(y=audio, sr=sr)
    contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)
    tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(audio), sr=sr)
    features = np.concatenate([np.mean(mfcc, axis=1), np.mean(chroma, axis=1), 
                               np.mean(mel, axis=1), np.mean(contrast, axis=1), 
                               np.mean(tonnetz, axis=1)])
    return features

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Konuşun, sizi dinliyorum...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language='tr-TR')
        print("Algılanan Metin: " + text)
        
        with open("temp_audio.wav", "wb") as f:
            f.write(audio.get_wav_data())
        
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition konuşmayı anlayamadı.")
        return None
    except sr.RequestError as e:
        print("Google Speech Recognition servisine erişim sağlanamıyor; {0}".format(e))
        return None

def analyze_sentiment_from_audio(file_path):
    y, sr = librosa.load(file_path, sr=None)
    features = extract_features(y, sr)
    
    # Belirgin özelliklerin eşikleri
    threshold_angry = [0.495459, 0.147959, 0.549279, 3.470226, 0.87]
    threshold_calm = [0.446611, 0.176167, 0.373689, 3.612745, 0.91277]
    threshold_happy = [0.438491, 0.158663, 0.535074, 3.308123, 0.912297]
    threshold_sad = [0.44646, 0.177271, 0.315748, 3.043478, 0.898509]

    # Duygu analizini gerçekleştirme
    mean_values = features[:5]  # İlk 5 özellik örnek olarak kullanılıyor

    if np.all(mean_values > threshold_angry):
        sentiment = "angry"
    elif np.all(mean_values > threshold_calm):
        sentiment = "calm"
    elif np.all(mean_values > threshold_happy):
        sentiment = "happy"
    elif np.all(mean_values > threshold_sad):
        sentiment = "sad"
    else:
        sentiment = "neutral"
    
    return {"mean_values": mean_values, "sentiment": sentiment}

if __name__ == "__main__":
    text = recognize_speech()
    if text:
        sentiment = analyze_sentiment_from_audio("temp_audio.wav")
        print("Duygu Analizi:", sentiment)
