#------Imports Section-------
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.lang import Builder
#-----------------------------

class StartingScreen(Widget):
    #def __init__(self, **kwargs):
        #super().__init__(**kwargs)

    #def select_file(self):
    pass
class CowApp(App):
    def build(self):
        return StartingScreen()
    
if __name__ == '__main__':
    CowApp().run()