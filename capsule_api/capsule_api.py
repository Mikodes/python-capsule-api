import requests
import dateutil.parser

class Opportunity(dict):
    @property
    def createdOn(self):
        return dateutil.parser.parse(self['createdOn'])

    @property
    def expectedCloseDate(self):
        return dateutil.parser.parse(self['expectedCloseDate'])

    @property
    def open(self):
        return 'actualCloseDate' not in self

class CapsuleAPI(object):
    def __init__(self, capsule_name, capsule_key):
        self.capsule_name = capsule_name
        self.capsule_key = capsule_key
        self.base_url = "https://%s.capsulecrm.com/api/" % capsule_name

    def request(self, method, path, **kwargs):
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json' 
        }
        auth = requests.auth.HTTPBasicAuth(self.capsule_key, self.capsule_name)
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
        result = self.get('opportunity' + get_options)
        result['opportunities']['opportunity'] = [Opportunity(x) for x in result['opportunities']['opportunity']]
        return result

if __name__ == '__main__':
    crm = CapsuleAPI("name", "key")
    print(crm.opportunities())
    

