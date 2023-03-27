import os
import playsound
import threading
import tkinter as tk
from tkinter import messagebox
import queue

from app.entities.voice_model import VoiceModel
from app.views.basic.basic_view import WIDTH, HEIGHT, POPUP_HEIGHT, POPUP_WIDTH, BUTTON_FONT, Y_FIRST_MODEL, PAD_Y, \
    BUTTON_WIDTH_2, BUTTON_HEIGHT_2, MAX_FONT, BUTTON_HEIGHT_1, BUTTON_WIDTH_1
from app.settings import WORKING_DIR
from app.speech_synthesizer import SpeachSynthesizer
from app.views.basic.basic_view import BasicView

X_MODELS = 100
POPUP_WIDTH = 500
POPUP_HEIGHT = 150


class AfterTrainView(BasicView):

    def __init__(self, root, voice_model_service, voice_recordings_service, version_service, gender, language):
        super(AfterTrainView, self).__init__(root, voice_model_service, voice_recordings_service, version_service)
        self.gender = gender
        self.language = language
        self.choosen_model = tk.IntVar()
        self.choosen_model.set("0")  # default value
        self.event = threading.Event()
        self.speech_synthesizer = None
        self.stop = False
        self.paths_to_generated_voice_models = self.find_paths_to_generated_voice_models()
        self.q = queue.Queue()
        self.thread = threading.Thread(target=self.worker, args=(self.q,))
        self.thread.start()
        self.paths_to_basic_audio = []
        self.config_file_path = os.path.join(WORKING_DIR, "voice_models/test/config.json")
        self.popup = None
        self.start_synthesize_basic_audio()
        self.input_field = tk.Entry(root, width=60, font=BUTTON_FONT)
        self.input_field.place(x=1000, y=2 * PAD_Y)
        self.display_widgets()
        self.audio_text = ''
        self.audio_model = ''
        self.audio_path = ''
        self.entry2 = None

    def start_synthesize_basic_audio(self):
        screen_pos = self.root.winfo_x()  # we need this to popup on the same screen which is app
        x = (WIDTH - POPUP_WIDTH) // 2 + screen_pos
        y = (HEIGHT - POPUP_HEIGHT) // 2
        self.popup = tk.Toplevel(self.root)
        self.popup.geometry(f"{POPUP_WIDTH}x{POPUP_HEIGHT}+{x}+{y}")
        self.popup.title("Trwa generowanie audio")
        self.popup.grab_set()
        label = tk.Label(self.popup, text="Trwa proces generowania audio dla wygenerowanych modeli.")
        label.pack(padx=10, pady=10)
        label = tk.Label(self.popup,
                         text="Jeżeli przerwiesz, rezultat uczenia zostanie utracony.")
        label.pack(padx=10, pady=10)
        cancel_button = tk.Button(self.popup, text="Anuluj", command=self.cancel_process)
        cancel_button.pack(padx=10, pady=10)
        self.q.put(self.synthesize_basic_audio_for_models)
        pass

    def cancel_process(self):
        confirm = messagebox.askyesno("Przerwanie syntezowania audio",
                                      "Po skończeniu syntezowania cały proces uczenia zostanie utracony. Czy jesteś pewien?")
        if confirm:
            self.popup.destroy()
            self.stop = True

    def cancel_synthesize(self):
        confirm = messagebox.askyesno("Przerwanie syntezowania audio",
                                      "Czy jesteś pewien, że chcesz przerwać syntezowanie audio?")
        if confirm:
            self.popup.destroy()
            self.stop = True
            self.speech_synthesizer.stop_event.set()

    def synthesize_basic_audio_for_models(self):
        '''Synthesize basic audio for each generated models and returns path to it'''
        text = "Hello. I am from Poland. Nice to meet you." if self.language == "english" else "Cześć. Jestem z Polskim. Miło Cię poznać."
        for voice_model_path in self.paths_to_generated_voice_models:
            if not self.stop:
                self.paths_to_basic_audio.append(self.generate_basic_audio(voice_model_path, text))
        self.popup.destroy()
        print(len(self.paths_to_basic_audio))
        if self.stop:
            self.root.after(0, self.switch_to_main_view)
        else:
            self.root.after(0, self.display_models())

    def generate_basic_audio(self, voice_model_path, text):
        speech_synthesizer = SpeachSynthesizer(model_path=voice_model_path, config_path=self.config_file_path)
        output_name = speech_synthesizer.generate_sample_name()
        speech_synthesizer.generate_audio(output_name, text)
        return output_name

    def synthesize_audio(self):
        voice_model_path = self.paths_to_generated_voice_models[self.choosen_model.get()]
        text = self.input_field.get()
        if not text:
            messagebox.showerror(title="Błąd", message="Nie wprowadzono tekstu do syntezy")
            return
        if text == self.audio_text and voice_model_path == self.audio_model:
            self.play_audio(self.audio_path)
            return
        self.speech_synthesizer = SpeachSynthesizer(model_path=voice_model_path, config_path=self.config_file_path)
        screen_pos = self.root.winfo_x()  # we need this to popup on the same screen where the app is open
        output_name = self.speech_synthesizer.generate_sample_name()
        x = (WIDTH - POPUP_WIDTH) // 2 + screen_pos
        y = (HEIGHT - POPUP_HEIGHT) // 2
        self.popup = tk.Toplevel(self.root)
        self.popup.grab_set()
        self.popup.geometry(f"{POPUP_WIDTH}x{POPUP_HEIGHT}+{x}+{y}")
        self.popup.title("Trwa generowanie audio")
        label = tk.Label(self.popup, text="Trwa proces generowania audio dla wybranego modelu.")
        label.pack(padx=10, pady=10)
        cancel_button = tk.Button(self.popup, text="Anuluj", command=self.cancel_synthesize)
        cancel_button.pack(padx=10, pady=10)
        self.q.put(lambda: self.speech_synthesizer.generate_audio(output_name, text, self.finish_synthesize), ())

    def finish_synthesize(self, audio_path):
        self.popup.destroy()
        if not self.stop:
            self.play_audio(audio_path)
            self.audio_path = audio_path
            self.audio_model = self.choosen_model.get()
            self.audio_text = self.input_field.get()
        self.stop = False

    def find_paths_to_generated_voice_models(self):
        path = os.path.join(WORKING_DIR, 'voice_models/test/generated')
        paths = []
        for f in os.listdir(path):
            paths.append(os.path.join(path, f))
        return paths

    def display_widgets(self):
        label = tk.Label(self.root, font=MAX_FONT, text="Wpisz tekst", bg='green')
        label.place(x=1050, y=PAD_Y)
        # on the bottom is menu to save mdoel, go to main menu(with popup to be sure) and continue training
        play_button = tk.Button(self.root, text="Odsłuchaj", command=self.synthesize_audio,
                                width=BUTTON_WIDTH_2, height=BUTTON_HEIGHT_2)
        play_button.place(x=1300, y=3 * PAD_Y)
        main_menu_button = tk.Button(self.root, text="Menu główne", command=self.switch_to_main_view,
                                     width=BUTTON_WIDTH_1, height=BUTTON_HEIGHT_1)
        save_button = tk.Button(self.root, text="Zapisz wybrany model", width=BUTTON_WIDTH_1, height=BUTTON_HEIGHT_1,
                                command=self.display_window_to_enter_name_for_model)
        continue_training_button = tk.Button(self.root, text="Generuj nową próbkę", width=BUTTON_WIDTH_1,
                                             height=BUTTON_HEIGHT_1, command=self.continue_training)

        main_menu_button.place(x=200, y=700)
        save_button.place(x=800, y=700)
        continue_training_button.place(x=1400, y=700)
        pass

    def display_window_to_enter_name_for_model(self):
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Wpisz nazwę")
        self.popup.grab_set()
        label = tk.Label(self.popup, text="Wpisz nazwę dla modelu:")
        label.pack()

        self.entry2 = tk.Entry(self.popup)
        self.entry2.pack()

        ok_button = tk.Button(self.popup, text="Zapisz", command=lambda: self.save_model(self.entry2.get()))
        ok_button.pack(side=tk.LEFT)

    def save_model(self, name):
        if name == '':
            messagebox.showerror("Uzupełnij nazwę modelu!")
            return
        # move model to place with generated models(config also)
        voice_model = VoiceModel(name, ..., ..., self.gender, self.language)
        self.voice_model_service.insert(voice_model)
        self.popup.destroy()
        messagebox.showinfo("Model głosu został zapisany.")

    def switch_to_main_view(self):
        confirm = messagebox.askyesno("Powrót do menu głównego",
                                      "Po powrocie do menu głównego wszystkie niezapisane modele zostaną usuniete. Czy jesteś pewien?")

        if confirm:
            self.event.set()
            self.thread.join()
            # destroy all models
            super().switch_to_main_view()

    def continue_training(self):
        confirm = messagebox.askyesno("Kontunuowanie treningu",
                                      "Po wznowieniu trenowania wszystkie pozostałe niezapisane modele zostaną usunięte. Czy jesteś pewien?")

        if confirm:
            path_to_model = self.choosen_model.get()  # maybe need to move somewhere
            self.event.set()
            self.thread.join()  # destroy models
            # call train_view

    def display_models(self):
        model_labels = []
        counter = 0
        for _ in self.paths_to_generated_voice_models:
            label = tk.Radiobutton(self.root, activebackground='green', highlightthickness=0, highlightcolor='green',
                                   text=f"model_{counter}", bg='green', font=BUTTON_FONT, variable=self.choosen_model,
                                   value=len(
                                       model_labels))  # value is index in self.paths_to_generated_voice_models list
            label.place(x=X_MODELS, y=Y_FIRST_MODEL + len(model_labels) * PAD_Y)
            model_labels.append(label)
            audio_path = self.paths_to_basic_audio[counter]
            button = tk.Button(self.root, text="Odsłuchaj", width=BUTTON_WIDTH_2, height=BUTTON_HEIGHT_2,
                               font=BUTTON_FONT, command=lambda: self.play_audio(audio_path))
            button.place(x=X_MODELS + 250, y=Y_FIRST_MODEL + (len(model_labels) - 1) * PAD_Y)
            counter += 1

    def play_audio(self, path_to_audio):
        if os.path.isfile(path_to_audio):
            playsound.playsound(path_to_audio)

    def worker(self, q):
        while True:
            if self.event.is_set():
                return
            try:
                func = q.get(block=True)
                if func is not None:
                    func()
                    q.task_done()
            except Exception as e:
                print(str(e))
