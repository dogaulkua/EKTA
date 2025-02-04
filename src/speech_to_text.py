import speech_recognition as sr
import numpy as np
import librosa

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
    # Ses özelliklerini analiz et
    rms = librosa.feature.rms(y=y)[0]
    pitch = librosa.yin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
    
    # Ortalama rms ve pitch değerlerini hesapla
    mean_rms = np.mean(rms)
    mean_pitch = np.mean(pitch)
    
    # Duygu analiz sonucunu belirle
    if mean_pitch > 150:
        sentiment = "positive"
    elif mean_pitch < 100:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    return {"mean_rms": mean_rms, "mean_pitch": mean_pitch, "sentiment": sentiment}

if __name__ == "__main__":
    text = recognize_speech()
    if text:
        sentiment = analyze_sentiment_from_audio("temp_audio.wav")
        print("Duygu Analizi:", sentiment)
