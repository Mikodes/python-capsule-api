import requests
import requests.auth


class Request(object):
    def __init__(self, capsule_name, capsule_key):
        self.capsule_name = capsule_name
        self.capsule_key = capsule_key
        self.base_url = "https://%s.capsulecrm.com/api/" % capsule_name

    def __call__(self, method, path, params=None, **kwargs):
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json'
        }
        auth = requests.auth.HTTPBasicAuth(self.capsule_key, self.capsule_name)
        method = method.lower()
        if method == 'get':
            if params:
                kwargs.update(params)
            result = requests.get(self.base_url + path, headers=headers, params=kwargs, auth=auth)
            result.raise_for_status()
            return result.json()
        if method in ('put', 'post', 'delete'):
            result = getattr(requests, method)(self.base_url + path, headers=headers, json=kwargs, auth=auth, params=params)
            result.raise_for_status()
            return result
        else:
            raise ValueError

    def get(self, path, params=None, **kwargs):
        return self('get', path, params=params, **kwargs)

    def put(self, path, data=None, params=None):
        if data:
            return self('put', path, params=params, **data)
        return self('put', path)

    def post(self, path, data=None, params=None):
        if data:
            return self('post', path, params=params, **data)
        return self('post', path)

    def delete(self, path, data=None, params=None):
        if data:
            return self('delete', path, params=params, **data)
        return self('delete', path)
