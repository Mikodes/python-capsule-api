import requests

CAPSULE_NAME = ''
BASE_URL = "https://%s.capsulecrm.com/api/" % CAPSULE_NAME
CAPSULE_KEY = ''


class CapsuleAPI(object):
    def __init__(self):
        self.base_url = BASE_URL 

    def request(self, method, path, **kwargs):
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json' 
        }
        auth = requests.auth.HTTPBasicAuth(CAPSULE_KEY, CAPSULE_NAME)
        if method.lower() == 'get':
            return requests.get(self.base_url + path , headers=headers, params=kwargs, auth=auth).json()
        else:
            raise ValueError

    def get(self, path, **kwargs):
        return self.request('get', path, **kwargs)

    def opportunities(self, **kwargs):
        get_options = ''
        if kwargs:
            get_options = '?' + "&".join([x + "=" + y for (x,y) in kwargs.items()])
        return self.get('opportunity' + get_options)

if __name__ == '__main__':
    crm = CapsuleAPI()
    print(crm.opportunities(status="open"))
    

