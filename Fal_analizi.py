import os
import base64
import openai
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.properties import StringProperty
from kivy.core.window import Window
from kivy.lang import Builder
from dotenv import load_dotenv

Window.size = (360, 540)

### API KEY LOAD ###

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

### Converting image to Base64 ###

def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")



### Prompt Logic and OpenAI api call ###

def analyze_image(image_path, fal_type="el"):
    try:
        base64_img = image_to_base64(image_path)

        prompt_texts = {
            "el": """
Aşağıda bir el fotoğrafı paylaşıyorum. Lütfen bu eldeki çizgilere göre genel geçer, eğlenceli, motive edici kısa yorumlar yaz.

Format şu şekilde olsun:
- Kalp çizgisi:
- Akıl çizgisi:
- Yaşam çizgisi:
- Kader çizgisi:

Lütfen her biri için pozitif ve yaratıcı birer cümle kur. Bu sadece kişisel gelişim temalı bir eğlencedir.
""",
            "kahve": """
Aşağıda bir kahve fincanı fotoğrafı paylaşıyorum. Bu görsele bakarak eğlenceli, gizemli ve olumlu bir kahve falı yorumu yapmanı istiyorum.

Lütfen kısa ve etkileyici bir fal yorumu yaz. Bu bir eğlence uygulamasıdır.
"""
        }

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_texts[fal_type]},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
                        }
                    ]
                }
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Hata oluştu: {str(e)}"



### Button Functions ###

class BaseFaliScreen(Screen):
    selected_image_path = StringProperty("")

    def open_file_chooser(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        filechooser = FileChooserListView(path='.', filters=['*.png', '*.jpg', '*.jpeg'], size_hint=(1, 0.9))
        choose_button = Button(text="Dosyayı Seç", size_hint=(1, 0.1), background_color=(0.3, 0.6, 1, 1))
        popup = Popup(title="Fotoğraf Yükle", content=layout, size_hint=(0.9, 0.9))

        def choose_file(_):
            if filechooser.selection:
                self.selected_image_path = filechooser.selection[0]
                self.ids.image_label.text = os.path.basename(self.selected_image_path)
                popup.dismiss()

        choose_button.bind(on_release=choose_file)
        layout.add_widget(filechooser)
        layout.add_widget(choose_button)
        popup.open()


class ElFali1Screen(BaseFaliScreen):
    def submit(self):
        if self.selected_image_path:
            result = analyze_image(self.selected_image_path, "el")
            self.manager.get_screen("elfali2").ids.result_box.text = result
            self.manager.current = "elfali2"
        else:
            self.ids.image_label.text = "Lütfen bir fotoğraf seçin"


class KahveFali1Screen(BaseFaliScreen):
    def submit(self):
        if self.selected_image_path:
            result = analyze_image(self.selected_image_path, "kahve")
            self.manager.get_screen("kahvefali2").ids.result_box.text = result
            self.manager.current = "kahvefali2"
        else:
            self.ids.image_label.text = "Lütfen bir fotoğraf seçin"


class ElFali2Screen(Screen): pass
class KahveFali2Screen(Screen): pass
class HomeScreen(Screen): pass
class NavigationScreen(Screen): pass

### UI Call from ui.kv file ###

class MyApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.theme_style = "Light"
        return Builder.load_file("ui.kv")

### App Start ###

if __name__ == '__main__':
    MyApp().run()
