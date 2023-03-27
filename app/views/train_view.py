from app.views.basic.basic_view import BasicView


class TrainView(BasicView):

    def __init__(self, root, voice_model_service, voice_recordings_service, version_service, gender, language, option,
                 model_id=None):
        super(TrainView, self).__init__(root, voice_model_service, voice_recordings_service, version_service)
        self.gender = gender
        self.language = language
        self.model_id = model_id
        # call train method
        # popup that it is going
        # cancel
