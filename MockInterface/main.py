#------Imports Section-------
from kivymd.app import MDApp
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.config import Config
from plyer import filechooser
from pathlib import Path
from screeninfo import get_monitors
from kivy.core.window import Window
from requests_t import get_csv_headers, get_recommendations, organize_results  # My implementation of single / homogenouse requests
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
import csv
#-----------------------------

# Set the adaptive fullScreen mode
Window.maximize()

class StartingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        selected_file = ''

    def select_file(self):
        """
        Function select_file that opens filechooser.
        """
        filechooser.open_file(on_selection=self.select_store)
        
    def select_store(self, selection):
        """
        Function selct_store that: 
            1. Stores the selected file path.
            2. Updates the file name label.
        Params:
            selection (arr): array of length 1 with a selected file
        """
        if selection:
            self.selected_file = str(Path(selection[0]))
            file_path_name = str(Path(selection[0]).name)
            self.ids.file_path_label.text = file_path_name

    def switch(self):
        """
        Function switch that 
            1. Switches the screen to converter_screen
            2. Passes the file path to the converter_screen
        """
        converter_screen = self.manager.get_screen("converter")
        converter_screen.display_recommendation(self.selected_file)
        self.manager.current = "converter"

class DataPopup(FloatLayout):
    """
    Class DataPopup that defines a popup page that displays full csv data table
    """
    def __init__(self, column_heads, row_data, **kwargs):
        super().__init__(**kwargs)
        self.build_table(column_heads, row_data)

    def build_table(self, column_heads, row_data):
        """
        Function build_table that builds the table for the whole dataset.

        Params:
            column_heads(arr): list of headers
            row_data(arr): list of data row by row
        """

        # Define the table
        table = MDDataTable(
            column_data=column_heads,
            row_data=row_data,
            size_hint=(0.98, 0.85),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            use_pagination=True,
            rows_num=20
        )

        # Clear the previous table on launch and add the new table to the widget
        self.ids.popup_data_container.clear_widgets()
        self.ids.popup_data_container.add_widget(table)

    def dismiss_popup(self):

        parent = self.parent
        while parent:
            if isinstance(parent, Popup):
                parent.dismiss()
                break
            parent = parent.parent
    
class RecommendationPopup(FloatLayout):
    def __init__(self, header, organized_data, list_titles, **kwargs):
        super().__init__(**kwargs)
        self.build_table(header, organized_data, list_titles)


    def build_table(self, header, organized_data,list_titles):
        """
        Function build_table that builds the table for every header.

        Params:
            column_heads(arr): list of headers
            row_data(arr): list of data row by row
        """

        # Define the table
        table = MDDataTable(
            column_data=list_titles,
            row_data=organized_data,
            size_hint=(0.98, 0.85),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            use_pagination=True,
            rows_num=20
        )

        # Clear the previous table on launch and add the new table to the widget
        self.ids.popup_recommendations.clear_widgets()
        self.ids.popup_recommendations.add_widget(table)

    def dismiss_popup(self):

        parent = self.parent
        while parent:
            if isinstance(parent, Popup):
                parent.dismiss()
                break
            parent = parent.parent
    
class ConverterScreen(Screen):
    def show_popup(self, column_heads, row_data):
        """
        Function show_popup that calls the DataPopup class to display the table 

        Params:
            column_heads(arr): list of headers
            row_data(arr): list of data row by row

        Those parameters are only needed to pass it further to the DataPopup screen
        """

        # Pass the data to the popup
        show = DataPopup(column_heads, row_data)

        # Initialize window
        popupWindow = Popup(title="CSV Data", content=show, size_hint=(1, 1))

        popupWindow.open()
    
    def open_recommendations(self,header, data,list_titles):
        show = RecommendationPopup(header,data,list_titles)
        popupWindow = Popup(title=f'Matches for {header}', content=show,size_hint=(1,1))
        popupWindow.open()
    
    def display_recommendation(self, file_path):
        """
        Function display_recommnedation:
            1. Retreitves the recommendation from the input csv.
            2. Displays the headers on the middle page.
            3. Displays the recommendations on the middle page.
        """
        headers = get_csv_headers(file_path)
        size = 20

        table = self.ids.vocab_recommender

        all_results = {}
        list_titles = [('prefixedName', dp(50)), ('vocabulary.prefix', dp(50)), ('uri',dp(50)), ('type',dp(50)), ('score',dp(50))]

        for header in headers:
            recommendations = get_recommendations(header, size)
            organized_data = organize_results(recommendations)
            table.add_widget(Button(text=f'{header}', on_press=lambda x: self.open_recommendations(header, organized_data, list_titles), bold=True, color=(0, 0, 0, 1)))
            all_results[header] = organized_data
        

        # Load CSV data for table
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            if not rows:
                return

        # Seperate headers and row data
        column_heads = [(header, dp(25)) for header in rows[0]]
        table_rows = rows[1:11] 
        row_data = rows [1:]

        # Remove old tables
        if hasattr(self, 'csv_table'):
            self.remove_widget(self.csv_table)

        # Create MDDataTable
        self.csv_table = MDDataTable(
            column_data=column_heads,
            row_data=table_rows,
            size_hint=(0.9, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            use_pagination=True,
            rows_num = 10
        )

        # Clear the previous table on launch and add the new table to the widget
        self.ids.csv_preview_container.clear_widgets()
        self.ids.csv_preview_container.add_widget(self.csv_table)

        open_popup = Button(text='Load Full Dataset', on_press=lambda x: self.show_popup(column_heads,row_data), size_hint=(None,None), size=(200,50), pos_hint={"center_x": 0.5})
        self.ids.csv_preview_container.add_widget(open_popup)


class CowApp(MDApp):
    def build(self):
        """
        Build app function that runs the Screen Manager.
        """
        sm = ScreenManager()
        sm.add_widget(StartingScreen(name="start"))
        sm.add_widget(ConverterScreen(name="converter"))
        return sm
    
if __name__ == '__main__':
    CowApp().run()