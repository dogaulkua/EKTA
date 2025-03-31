import speech_recognition as sr
import numpy as np
import librosa

def extract_features(audio, sr):
    """Kısa sinyallerde uyarı olmaması için n_fft'i sinyal uzunluğuna göre ayarla."""
    n_fft = min(1024, len(audio))
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40, n_fft=n_fft)
    chroma = librosa.feature.chroma_stft(y=audio, sr=sr, n_fft=n_fft)
    mel = librosa.feature.melspectrogram(y=audio, sr=sr, n_fft=n_fft)
    contrast = librosa.feature.spectral_contrast(y=audio, sr=sr, n_fft=n_fft)
    tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(audio), sr=sr)
    features = np.concatenate([
        np.mean(mfcc, axis=1),
        np.mean(chroma, axis=1),
        np.mean(mel, axis=1),
        np.mean(contrast, axis=1),
        np.mean(tonnetz, axis=1)
    ])
    return features

def recognize_speech():
    """Mikrofonu dinleyip Google Speech Recognition ile metin döndürür."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Konuşun, sizi dinliyorum...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language='tr-TR')
        print("Algılanan Metin: " + text)
        # Tanınan ses kaydını dosyaya yaz
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
    """temp_audio.wav dosyası üzerinden duygu analizi."""
    y, sr = librosa.load(file_path, sr=None)
    features = extract_features(y, sr)
    
    # Örnek eşik değerleri (kendi modelinize göre düzenleyin)
    threshold_angry = np.array([0.495, 0.148, 0.549, 3.470, 0.87])
    threshold_calm  = np.array([0.447, 0.176, 0.374, 3.613, 0.913])
    threshold_happy = np.array([0.438, 0.159, 0.535, 3.308, 0.912])
    threshold_sad   = np.array([0.446, 0.177, 0.316, 3.043, 0.899])
    
    mean_values = features[:5]
    
    # Basit kıyaslama (örnek). İhtiyaca göre değiştirebilirsiniz.
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
    
    return {"mean_values": mean_values.tolist(), "sentiment": sentiment}

if __name__ == "__main__":
    # Test amaçlı direkt çalıştırma
    text = recognize_speech()
    if text:
        sentiment = analyze_sentiment_from_audio("temp_audio.wav")
        print("Duygu Analizi:", sentiment)
