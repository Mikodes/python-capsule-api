class UserFetcher(object):
    def __init__(self, capsule_api):
        self._capsule_api = capsule_api

    def get_list(self):
        resp = self._capsule_api.request.get('users')
        users = resp['users'].get('user')
        if not users:
            return []
        if isinstance(users, dict):
            users = [users]
        return users
