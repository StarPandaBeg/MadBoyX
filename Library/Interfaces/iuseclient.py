
class IUseClient:

    client = None

    @classmethod
    def set_client(cls, client):
        cls.client = client