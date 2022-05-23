
class IUseNgrok:

    ngrok = None

    @classmethod
    def set_ngrok(cls, ngrok):
        cls.ngrok = ngrok