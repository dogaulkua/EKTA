import os
import requests

def get_gif_from_repo(word, save_path):
    base_url = "https://raw.githubusercontent.com/dogaulkua/Turkish_Sign_Language_Dictionary/main/data/img/"
    first_letter = word[0]  # Kelimenin ilk harfini al
    gif_url = f"{base_url}{first_letter}/{word}.gif"
    response = requests.get(gif_url)
    
    if response.status_code == 200:
        gif_data = response.content
        gif_name = f"{word}.gif"
        with open(os.path.join(save_path, gif_name), 'wb') as gif_file:
            gif_file.write(gif_data)
        print(f"{word} kelimesi için GIF başarıyla indirildi: {gif_name}")
    else:
        print(f"{word} kelimesi için GIF bulunamadı: {gif_url}")
