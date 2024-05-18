import customtkinter
import configparser
import os
from PIL import Image
from tkinter import messagebox
import assemblyai as aai
import threading
import requests
import time
from datetime import datetime
from datetime import timedelta
from torch import cuda
from faster_whisper import WhisperModel
import subprocess
from languages import texts
from win10toast import ToastNotifier

customtkinter.set_default_color_theme("themes\\theme.json")

class NavigationFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=0, width=150, **kwargs)

        self.grid(row=0, column=0, sticky='nsew')
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")

        # Download Navigation logo image
        self.navigation_logo = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "navigation_dark.png")), 
                                                      dark_image=Image.open(os.path.join(image_path, "navigation_light.png")), size=(128,128))

        # Navigation menu
        self.navigation_img = customtkinter.CTkLabel(self, text="", image=self.navigation_logo)
        self.navigation_img.grid(row=0, column=0, pady=20)

        self.home_button = customtkinter.CTkButton(self, text=texts[master.language_value]['home_button'], width=120, command=self.home_button_event)
        self.home_button.grid(row=1, column=0, pady=10)

        self.history_button = customtkinter.CTkButton(self, text=texts[master.language_value]['history_button'], width=120, command=self.history_button_event)
        self.history_button.grid(row=2, column=0, pady=10)

        self.settings_button = customtkinter.CTkButton(self, text=texts[master.language_value]['settings_button'], width=120, command=self.settings_button_event)
        self.settings_button.grid(row=3, column=0, pady=10)

    def home_button_event(self):
        self.master.show_frame(self.master.home_frame)

    def history_button_event(self):
        self.master.show_frame(self.master.history_frame)

    def settings_button_event(self):
        self.master.show_frame(self.master.settings_frame)

class HomeFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        """Ініціалізує рамку домашньої сторінки."""
        super().__init__(master, fg_color=("#E8D1B3", "#6D5143"), **kwargs)
        self.grid(row=0, column=1, sticky='nsew')
        self.grid_columnconfigure(0, weight=1)

        self.path_to_file = ""
        self.path_to_folder = ""
        self.original_file_name = ""

        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")

        self.import_button_img = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "import.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "import.png")), size=(48, 48))

        self.export_button_img = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "export.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "export.png")), size=(48, 48))

        self.label = customtkinter.CTkLabel(self, text=texts[master.language_value]['home'], font=("Helvetica", 28, "bold"))
        self.label.grid(row=0, column=0, pady=10, sticky='nsew')

        self.main_buttons_frame = customtkinter.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.main_buttons_frame.grid_columnconfigure(0, weight=1)
        self.main_buttons_frame.grid_columnconfigure(1, weight=1)
        self.main_buttons_frame.grid(row=1, column=0, sticky='nsew', pady=15)

        self.left_main_buttons_frame = customtkinter.CTkFrame(self.main_buttons_frame, corner_radius=0, fg_color='transparent')
        self.left_main_buttons_frame.grid_rowconfigure(0, weight=1)
        self.left_main_buttons_frame.grid_columnconfigure(0, weight=1)
        self.left_main_buttons_frame.grid_columnconfigure(1, weight=1)
        self.left_main_buttons_frame.grid(row=0, column=0, sticky='nsew')

        self.import_button = customtkinter.CTkButton(self.left_main_buttons_frame, text=texts[master.language_value]['import_button'], compound="top", image=self.import_button_img, command=self.select_file)
        self.import_button.grid(row=0, column=0, sticky='ns')
        self.export_button = customtkinter.CTkButton(self.left_main_buttons_frame, text=texts[master.language_value]['export_button'], compound="top", image=self.export_button_img, command=self.select_folder)
        self.export_button.grid(row=0, column=1, sticky='ns')

        self.right_main_buttons_frame = customtkinter.CTkFrame(self.main_buttons_frame, corner_radius=0, fg_color='transparent')
        self.right_main_buttons_frame.grid(row=0, column=1, sticky='nsew')

        self.radio_var = customtkinter.IntVar(value=0)
        self.radiobutton_1 = customtkinter.CTkRadioButton(self.right_main_buttons_frame, text=texts[master.language_value]['radio_button_1'], variable= self.radio_var, value=1)
        self.radiobutton_1.grid(row=0, column=2, sticky='w', pady=10)
        self.radiobutton_2 = customtkinter.CTkRadioButton(self.right_main_buttons_frame, text=texts[master.language_value]['radio_button_2'], variable= self.radio_var, value=2)
        self.radiobutton_2.grid(row=1, column=2, sticky='w', pady=10)

        self.under_main_buttons_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color='transparent', height=100)
        self.under_main_buttons_frame.grid(row=2, column=0, sticky='nsew')

        self.language_mode_menu = customtkinter.CTkOptionMenu(self.under_main_buttons_frame, values=["English"])
        self.language_mode_menu.grid(row=0, column=0, padx=15, pady=20)
        self.start_subtitles_button = customtkinter.CTkButton(self.under_main_buttons_frame, text=texts[master.language_value]['start_subtitles_button'], command=self.start_subtitles_button_event)
        self.start_subtitles_button.grid(row=0, column=1, padx=15, pady=20)


        self.file_label= customtkinter.CTkLabel(self, text=texts[master.language_value]['import_label'])
        self.file_label.grid(row=3, column=0, sticky='w', padx=15)
        self.path_to_file_label =  customtkinter.CTkLabel(self.file_label, text="None")
        self.path_to_file_label.grid(row=0,column=1)

        self.folder_label = customtkinter.CTkLabel(self, text=texts[master.language_value]['export_label'])
        self.folder_label.grid(row=4, column=0, sticky='w', padx=15)
        self.path_to_folder_label =  customtkinter.CTkLabel(self.folder_label, text="None")
        self.path_to_folder_label.grid(row=0,column=1)


        self.status_label = customtkinter.CTkLabel(self, text=texts[master.language_value]['status_label'])
        self.status_label.grid(row=5, column=0, sticky='w', padx=15)
        self.status_progress_label = customtkinter.CTkLabel(self.status_label, text="None")
        self.status_progress_label.grid(row=0, column=1)

        self.delete_event = threading.Event()

    def select_file(self):
        """Вибирає файл для обробки."""
        self.path_to_file = customtkinter.filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.flac"), ("Video Files", "*.mkv *.mp4")])
        self.original_file_name = self.path_to_file
        if self.path_to_file:
            self.path_to_file_label.configure(text=self.path_to_file)

    def select_folder(self):
        """Вибирає папку для збереження файлу."""
        self.path_to_folder = customtkinter.filedialog.askdirectory(title="Select a folder to save the file")
        if self.path_to_folder:
            self.path_to_folder_label.configure(text=self.path_to_folder)

    def start_subtitles_button_event(self):
        """Обробляє натискання кнопки запуску створення субтитрів."""
        if self.path_to_file and self.path_to_folder:
            if self.radio_var.get() == 1:
                if self.master.api_token_validation:
                    threading.Thread(target=self.delete_video_track).start()
                    threading.Thread(target=self.transcribe_and_save_subtitles_online).start()

                else:
                    messagebox.showerror(texts[self.master.language_value]['error_topic'], texts[self.master.language_value]['api_error_description'])
            elif self.radio_var.get() == 2:
                threading.Thread(target=self.delete_video_track).start()
                threading.Thread(target=self.transcribe_and_save_subtitles_offline).start()
            else:
                 messagebox.showerror(texts[self.master.language_value]['error_topic'], texts[self.master.language_value]['error_radio_button'])
        else:
             messagebox.showerror(texts[self.master.language_value]['error_topic'], texts[self.master.language_value]['error_path_to_files'])

    def transcribe_and_save_subtitles_online(self):
        """Транскрибування та збереження субтитрів онлайн."""
        self.delete_event.wait()
        try:
            mode = "Online"
            self.status_progress_label.configure(text=texts[self.master.language_value]['status_progress_label_working'], text_color='blue')
            
            start_process_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            start_date = datetime.now().strftime("%Y-%m-%d")

            aai.settings.api_key = self.master.api_value
            config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best, language_code="en")
            transcriber = aai.Transcriber(config=config)
            transcript = transcriber.transcribe(self.path_to_file)
            srt = transcript.export_subtitles_srt()


            output_path = f"{self.path_to_folder}/generated_subtitles.srt"

            with open(output_path, "w", encoding="utf-8") as file:
                file.write(srt)
            file.close()
            end_process_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_translation_history(self.original_file_name, start_process_time, start_date, end_process_time, mode)

            if self.master.notifications_value:
                self.show_notification(texts[self.master.language_value]['notification_title'], texts[self.master.language_value]['notification_description'])

            self.status_progress_label.configure(text=texts[self.master.language_value]['status_progress_label_done'], text_color='green')

        except Exception:
            self.status_progress_label.configure(text=texts[self.master.language_value]['error_topic'], text_color='red')
            messagebox.showerror(texts[self.master.language_value]['error_topic'], texts[self.master.language_value]['save_subtitles_error'])

    def has_video_track(self):
        """Перевіряє наявність відеодоріжки у файлі."""
        command = [
        "files\\ffprobe.exe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=codec_type",
        "-of", "csv=p=0",
        self.path_to_file 
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return "video" in result.stdout

    def delete_video_track(self):
        """Видаляє відеодоріжку з файлу."""
        if self.has_video_track():
            self.status_progress_label.configure(text=texts[self.master.language_value]['status_progress_preparing'], text_color='blue')
            time.sleep(3)
            command = [
            'files\\ffmpeg.exe', '-i', self.path_to_file, '-vn', 
            '-acodec', 'copy', '-y',
            f'{self.path_to_folder}temporary.mp4'
            ]
            subprocess.run(command, check=True)
            print(f'{self.path_to_folder}temporary.mp4')
            self.path_to_file = f'{self.path_to_folder}temporary.mp4'
        self.delete_event.set()

    def transcribe_and_save_subtitles_offline(self, model_size="medium.en"):
        """Транскрибування та збереження субтитрів офлайн."""
        self.delete_event.wait()
        try:
            mode = "Offline"
            self.status_progress_label.configure(text=texts[self.master.language_value]['status_progress_label_working'], text_color='blue')
            start_process_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            start_date = datetime.now().strftime("%Y-%m-%d")
            if cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"
            
            if cuda.is_bf16_supported():
                compute_type = "float16"
            else:
                compute_type = "float32"

            model = WhisperModel(model_size, device=device, compute_type=compute_type)
            segments, _ = model.transcribe(self.path_to_file, language="en")
            output_path = f"{self.path_to_folder}generated_subtitles.srt"

            with open(output_path, "w", encoding="utf-8") as file:
                for i, segment in enumerate(segments, start=1):
                    start_time = self.format_srt_time(segment.start)
                    end_time = self.format_srt_time(segment.end)
                    text = segment.text
                    file.write(f"{i}\n")
                    file.write(f"{start_time} --> {end_time}\n")
                    file.write(f"{text}\n\n")
                    print(f"{start_time} --> {end_time}\n{text}\n")
            
            end_process_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_translation_history(self.original_file_name, start_process_time, start_date, end_process_time, mode)

            if self.master.notifications_value:
                self.show_notification(texts[self.master.language_value]['notification_title'], texts[self.master.language_value]['notification_description'])

            self.status_progress_label.configure(text=texts[self.master.language_value]['status_progress_label_done'], text_color='green')

        except Exception as e:
            self.status_progress_label.configure(text=texts[self.master.language_value]['error_topic'], text_color='red')
            messagebox.showerror(texts[self.master.language_value]['error_topic'], texts[self.master.language_value]['save_subtitles_error'])

    def format_srt_time(self, seconds):
        """Форматує час у формат SRT."""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = td.microseconds // 1000
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

    def save_translation_history(self, input_file, start_time, start_date, end_time, mode):
        """Зберігає історію перекладів у файл."""
        config = configparser.ConfigParser()
        ini_file = "translation_history.ini"
        if os.path.exists(ini_file):
            config.read(ini_file)

        if "history" not in config:
            config["history"] = {}

        time1 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        time2 = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

        total_time = time2 - time1

        history_entry = {
            'mode' : mode,
            'input_file': os.path.basename(input_file), 
            'start_time': start_date,
            'total_time': str(total_time)
        }

        entry_key = f"translation_{len(config['history']) + 1}"
        config["history"][entry_key] = str(history_entry)

        with open(ini_file, 'w') as configfile:
            config.write(configfile)

    def show_notification(self, title, message):
        """Показує сповіщення."""
        toast = ToastNotifier()
        toast.show_toast(
            title=title,
            msg=message,
            duration=10,
            icon_path="images\\logo_app.ico",
            threaded=True
        )

class HistoryFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        """Ініціалізує рамку історії."""
        super().__init__(master, fg_color=("#E8D1B3", "#6D5143"), **kwargs)
        self.grid(row=0, column=1, sticky='nsew')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.label = customtkinter.CTkLabel(self, text=texts[master.language_value]['history'], font=("Helvetica", 24, "bold"))
        self.label.grid(row=0, column=0, pady=10, sticky='nsew')

        self.history_information = customtkinter.CTkScrollableFrame(self,  corner_radius=0, fg_color="transparent")
        self.history_information.grid(row=2, column=0, sticky="nsew")

        self.file_name_title_label = customtkinter.CTkLabel(self.history_information, text=texts[master.language_value]['file_input_label'])
        self.file_name_title_label.grid(row=0, column=0, padx=20, sticky='w')

        self.mode_title_label = customtkinter.CTkLabel(self.history_information, text=texts[master.language_value]['mode_label'])
        self.mode_title_label.grid(row=0, column=1, padx=20, sticky='w')

        self.date_time_label = customtkinter.CTkLabel(self.history_information, text=texts[master.language_value]['start_time_lable'])
        self.date_time_label.grid(row=0, column=2, padx=20, sticky='w')

        self.total_title_time_label = customtkinter.CTkLabel(self.history_information, text=texts[master.language_value]['total_time_label'])
        self.total_title_time_label.grid(row=0, column=3, padx=20, sticky='w')

        self.load_history()

    def load_history(self):
        """Завантажує історію транскрибування з конфігураційного файлу."""
        config = configparser.ConfigParser()
        ini_file = "translation_history.ini"
        if os.path.exists(ini_file):
            config.read(ini_file)
            if "history" in config:
                for idx, key in enumerate(config["history"]):
                    history_entry = eval(config["history"][key])
                    self.add_history_entry(idx + 1, history_entry)
        
    def add_history_entry(self, row, entry):
        """Додає запис історії транскрибування до прокручуваної рамки."""
        input_file_label = customtkinter.CTkLabel(self.history_information, text=f"{entry['input_file']}", anchor="w")
        input_file_label.grid(row=row, column=0, padx=20, pady=5, sticky="nsew")

        mode_label = customtkinter.CTkLabel(self.history_information, text=f"{entry['mode']}", anchor="w")
        mode_label.grid(row=row, column=1, padx=20, pady=5, sticky="nsew")

        date_time_label = customtkinter.CTkLabel(self.history_information, text=f"{entry['start_time']}", anchor="w")
        date_time_label.grid(row=row, column=2, padx=20, pady=5, sticky="nsew")

        total_time_label = customtkinter.CTkLabel(self.history_information, text=f"{entry['total_time']}", anchor="w")
        total_time_label.grid(row=row, column=3, padx=20, pady=5, sticky="nsew")

class SettingsFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=("#E8D1B3", "#6D5143"), **kwargs)
        """Ініціалізує рамку налаштувань."""
        self.grid(row=0, column=1, sticky='nsew')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.label = customtkinter.CTkLabel(self, text=texts[master.language_value]['settings'], font=("Helvetica", 28, "bold"))
        self.label.grid(row=0, column=0, pady=10, sticky='nsew')

        # Frame For Settings
        self.inner_frame = customtkinter.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.inner_frame.grid(row=1, column=0, sticky='nsew')

        # API Settings
        self.api_label = customtkinter.CTkLabel(self.inner_frame, text=texts[master.language_value]['api_label'], font=("Helvatica", 20))
        self.api_label.grid(row=0, column=0, padx=20, pady=5, sticky='w')
        self.api_input = customtkinter.CTkEntry(self.inner_frame, width=240)
        self.api_input.insert(0, master.api_value)
        self.api_input.grid(row=0, column=1, sticky='w')

        # Focus API Input binds
        self.api_input.bind("<FocusIn>", self.on_focus_in)
        self.api_input.bind("<FocusOut>", self.on_focus_out)

        # Notifications Settings
        self.notifications_label = customtkinter.CTkLabel(self.inner_frame, text=texts[master.language_value]['notifications_label'], font=("Helvatica", 20))
        self.notifications_label.grid(row=1, column=0, padx=20, pady=5, sticky='w')
        self.notifications_switch = customtkinter.CTkSwitch(self.inner_frame, text="Off/On")

        self.notifications_switch.select() if master.notifications_value else self.notifications_switch.deselect()

        self.notifications_switch.grid(row=1, column=1, sticky='w')
        
        # Language Settings
        self.language_label = customtkinter.CTkLabel(self.inner_frame, text=texts[master.language_value]['language_label'], font=("Helvetica", 20))
        self.language_label.grid(row=2, column=0, padx=20, pady=5, sticky='w')
        self.language_mode_menu = customtkinter.CTkOptionMenu(self.inner_frame, values=["English", "Ukrainian"])
        self.language_mode_menu.set(master.language_value)
        self.language_mode_menu.grid(row=2, column=1, sticky='w')

        # Appearance Mode
        self.appearance_mode_label = customtkinter.CTkLabel(self.inner_frame, text=texts[master.language_value]['appearance_mode_label'], font=("Helvatica", 20))
        self.appearance_mode_label .grid(row=3, column=0, padx=20, pady=5, sticky='w')
        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.inner_frame, values=["Dark", "Light"], command=self.change_appearance_mode_event)
        self.appearance_mode_menu.set(master.appearance_value)
        self.appearance_mode_menu.grid(row=3, column=1, sticky='w')
        
        # Save Settings Button
        self.save_setting_button = customtkinter.CTkButton(self, text=texts[master.language_value]['save_button'], font=("Helvatica", 16), command=self.save_settings)
        self.save_setting_button.grid(row=2, column=0, pady=20, padx=20, sticky='w')

        # Version Of Program
        self.version_label = customtkinter.CTkLabel(self, text=texts[master.language_value]['version_label'], font=("Helvatica", 20))
        self.version_label.grid(row=3, column=0, padx=20, pady=20, sticky='se')
        
    def change_appearance_mode_event(self, new_appearance_mode):
        """Змінює режим вигляду додатку."""
        customtkinter.set_appearance_mode(new_appearance_mode)
        
    def save_settings(self):
        """Зберігає налаштування у конфігураційний файл."""
        config = configparser.ConfigParser()
        config['Settings'] = {
            'API': self.api_input.get(),
            'Notifications': self.notifications_switch.get(),
            'Language': self.language_mode_menu.get(),
            'Appearance': self.appearance_mode_menu.get()
        }
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)

        messagebox.showinfo(texts[self.language_mode_menu.get()]["success_message_topic"], texts[self.language_mode_menu.get()]["success_message_description"])

    def on_focus_in(self, event):
        """Змінює колір рамки поля вводу API ключа при фокусуванні."""
        self.api_input.configure(border_color=('black', 'white'))

    def on_focus_out(self, event):
        """Змінює колір рамки поля вводу API ключа при втраті фокусу."""
        self.api_input.configure(border_color=("#AFA292", "#725B4E")) 
    
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("650x350")
        self.iconbitmap("images\\logo_app.ico")
        self.resizable(False, False)
        self.title("Auto Subtitles")

        self.api_token_validation = 0
        self.load_settings()

        threading.Thread(target=self.is_api_token_valid).start()

        if self.appearance_value == "Dark":
            customtkinter.set_appearance_mode("dark")
        else:
            customtkinter.set_appearance_mode("light")

        self.bind_all("<Button-1>", lambda event: event.widget.focus_set())
        self.bind_all("<Key>", self.on_key_release, "+")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.navigation_frame = NavigationFrame(self)
        self.home_frame = HomeFrame(self)
        self.history_frame = HistoryFrame(self)
        self.settings_frame = SettingsFrame(self)
        self.show_frame(self.home_frame)

    def show_frame(self, frame):
        """Показує заданий фрейм."""
        self.home_frame.grid_forget()
        self.history_frame.grid_forget()
        self.settings_frame.grid_forget()
        frame.grid(row=0, column=1, sticky='nsew')

    def load_settings(self):
        """Завантажує налаштування з файлу settings.ini."""
        self.config = configparser.ConfigParser()
        self.config.read('settings.ini')

        if 'Settings' in self.config:
            self.api_value = self.config['Settings'].get('API')
            self.notifications_value = self.config['Settings'].get('Notifications') == '1'
            self.language_value = self.config['Settings'].get('Language')
            self.appearance_value = self.config['Settings'].get('Appearance')
            if self.notifications_value not in [0, 1] or self.language_value not in ["Ukrainian", "English"] or self.appearance_value not in ["Dark", "Light"]:
                self.notifications_value = 0
                self.language_value = "English"
                self.appearance_value = "Dark"
        else:
            self.api_value = ""
            self.language_value = "English"
            self.notifications_value = 0
            self.appearance_value = "Dark"

    def on_key_release(self, event):
        """Обробляє події натискання клавіш."""
        ctrl = (event.state & 0x4) != 0
        if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
            event.widget.event_generate("<<Cut>>")

        if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
            event.widget.event_generate("<<Paste>>")

        if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
            event.widget.event_generate("<<Copy>>")

    def is_api_token_valid(self):
        """Перевіряє валідність API токену."""
        try:
            headers = {"Authorization": self.api_value}
            response = requests.get("https://api.assemblyai.com/v2/transcript", headers=headers)
            if response.status_code == 200:
                self.api_token_validation = 1
                return True
            else:
                return False
        except Exception:
            return False

app = App()
app.mainloop()