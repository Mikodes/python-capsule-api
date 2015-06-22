import requests
import dateutil.parser
from decimal import Decimal

class Opportunity(dict):
    @property
    def createdOn(self):
        return dateutil.parser.parse(self['createdOn'])

    @property
    def expectedCloseDate(self):
        return dateutil.parser.parse(self['expectedCloseDate'])

    @property
    def actualCloseDate(self):
        return dateutil.parser.parse(self['actualCloseDate'])

    @property
    def open(self):
        return 'actualCloseDate' not in self

    @property
    def probability(self):
        return int(self['probability'])

    @property
    def milestoneId(self):
        return int(self['milestoneId'])

    def __getattr__(self, element):
        if element == 'customfields':
            raise AttributeError
        if element in self:
            return self[element]
        if element in self.customfields:
            return self.customfields[element]
        raise AttributeError

    @property
    def value(self):
        return Decimal(self['value'])

    @property
    def weighted_value(self):
        return self.value * self.probability / 100


    def load_customfields_from_api(self, customfields):
        self.customfields = dict([(x['label'], x['text']) for x in customfields if 'text' in x])


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

    def customfields(self, opportunity_id, **kwargs):
        get_options = ''
        if kwargs:
            get_options = '?' + "&".join([x + "=" + y for (x,y) in kwargs.items()])
        result = self.get('opportunity/' + opportunity_id + '/customfields' + get_options)
        return result['customFields']['customField']

    def inject_customfields(self, opportunity):
        return opportunity.load_customfields_from_api(self.customfields(opportunity.id))

if __name__ == '__main__':
    crm = CapsuleAPI("name", "key")
    print(crm.opportunities())
    

