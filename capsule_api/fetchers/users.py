class UserFetcher(object):
    def __init__(self, capsule_api):
        self._capsule_api = capsule_api

    def get_list(self):
        return self._capsule_api.request.get('users')
