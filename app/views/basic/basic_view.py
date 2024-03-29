from lazy_import import lazy_module

from app.enums import Options

choose_audio_for_samples_view = lazy_module("app.views.choose_audio_for_generating_samples_view")
choose_gender_view = lazy_module("app.views.choose_gender_language_view")
main_menu_module = lazy_module("app.views.main_view")
after_train_view = lazy_module("app.views.after_train_view")
train_module = lazy_module("app.views.train_view")


class BasicView:
    BUTTON_WIDTH_2 = 17
    BUTTON_HEIGHT_2 = 1
    SMALL_FONT = ("Helvetica", 10)
    BUTTON_FONT = ("Helvetica", 14)
    MAX_FONT = ("Helvetica", 25)
    ALLOWED_EXTENSIONS = ('.mp3', '.mp4', '.wav')
    PAGING = 10
    BACKGROUND_COLOR = '#AEA6A6'

    def __init__(self, root, voice_model_service, voice_recordings_service, version_service):
        self.size_grid_y = root.winfo_height() / 36
        self.size_grid_x = (root.winfo_width()) / 64
        self.root = root
        self.version_service = version_service
        self.voice_model_service = voice_model_service
        self.voice_recordings_service = voice_recordings_service
        self.WIDTH = 64 * self.size_grid_x
        self.HEIGHT = 36 * self.size_grid_y
        self.PAD_Y = 2.667 * self.size_grid_y
        self.Y_FIRST_MODEL = 5 * self.size_grid_y
        self.Y_MENU = 26.666 * self.size_grid_y
        self.POPUP_WIDTH = 10 * self.size_grid_x
        self.POPUP_HEIGHT = 3.333 * self.size_grid_y
        self.BUTTON_WIDTH_1 = 12 * self.size_grid_x
        self.BUTTON_HEIGHT_1 = 2.5 * self.size_grid_y
        self.BUTTON_WIDTH_2 = self.size_grid_x * 6.5
        self.BUTTON_HEIGHT_2 = self.size_grid_y

    def switch_to_choose_gender_language_train_old(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        choose_gender_view.ChooseGenderLanguageView(self.root, self.voice_model_service, self.voice_recordings_service,
                                                    self.version_service, Options.train_old)

    def switch_to_choose_gender_language(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        choose_gender_view.ChooseGenderLanguageView(self.root, self.voice_model_service, self.voice_recordings_service,
                                                    self.version_service, self.option)

    def switch_to_choose_gender_language_train_new(self):
        for widget in self.root.winfo_children():
          widget.destroy()
        choose_gender_view.ChooseGenderLanguageView(self.root, self.voice_model_service, self.voice_recordings_service,
                                                 self.version_service, Options.train_new)

       #for widget in self.root.winfo_children():
       #    widget.destroy()       # for testing
       #after_train_view.AfterTrainView(self.root, self.voice_model_service, self.voice_recordings_service,
       #                                self.version_service, 'woman', 'polish',
                                        #'/home/dawid/sem6/ProjektGrupowy22-23/output/woman_polish', 'dataset_8', 0)
        # for widget in self.root.winfo_children():
        #   widget.destroy()
        # train_module.TrainView(self.root,self.voice_model_service, self.voice_recordings_service,
        #                               self.version_service, 'woman', 'polish', Options.train_new,
        #         0, 15, '/home/dawid/sem6/ProjektGrupowy22-23/output/checkpoint_672000.pth',)

    def switch_to_choose_gender_language_synthesize(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        choose_gender_view.ChooseGenderLanguageView(self.root, self.voice_model_service, self.voice_recordings_service,
                                                    self.version_service, Options.synthesize_speech)

    def switch_to_generate_samples(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        choose_audio_for_samples_view.ChooseAudioForGeneratingSamplesView(self.root, self.voice_model_service,
                                                                          self.voice_recordings_service,
                                                                          self.version_service)

    def switch_to_main_view(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        main_menu_module.MainView(self.root, self.voice_model_service, self.voice_recordings_service,
                                  self.version_service)

    def switch_to_choose_language(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        choose_gender_view.ChooseGenderLanguageView(self.root, self.voice_model_service, self.voice_recordings_service,
                                                    self.version_service, Options.generate_samples)
