import requests
import dateutil.parser
from decimal import Decimal
import datetime
import json
from collections import OrderedDict

class Opportunity(dict):
    @property
    def createdOn(self):
        return dateutil.parser.parse(self['createdOn'])

    @property
    def expectedCloseDate(self):
        try:
            return dateutil.parser.parse(self['expectedCloseDate'])
        except KeyError:
            raise AttributeError

    @property
    def actualCloseDate(self):
        return dateutil.parser.parse(self['actualCloseDate'])

    @property
    def updatedOn(self):
        return dateutil.parser.parse(self['updatedOn'])

    @property
    def open(self):
        return 'actualCloseDate' not in self

    @property
    def probability(self):
        return int(self['probability'])

    @property
    def milestoneId(self):
        return int(self['milestoneId'])

    @property
    def customfields(self):
        try:
            custom_fields = self.get('raw_customfields') or self['customfields'] #FIXME attempts old format until all objects are converted to raw_
            return dict((x['label'], x['text']) for x in custom_fields if 'text' in x)
        except KeyError:
            raise AttributeError

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
        try:
            return Decimal(self['value'])
        except KeyError:
            return Decimal(0)

    @property
    def weighted_value(self):
        return self.value * self.probability / 100


    def load_customfields_from_api(self, customfields):
        self['raw_customfields'] = [x for x in customfields if 'date' not in x]
        self['raw_datatags'] = [x for x in customfields if 'date' in x]

    def load_tags_from_api(self, tags):
        self['tags_id'] = [x for x in tags]

    @property
    def tags(self):
        return list([x['name'] for x in self['tags_id']])

    @property
    def datatags(self):
        return OrderedDict([(x['label'], dateutil.parser.parse(x['date']).date()) for x in sorted(self['raw_datatags'], key=lambda x:x['date'])])

    @property
    def positive_outcome(self):
        return not self.open and self.probability == 100

    @property
    def negative_outcome(self):
        return not self.open and self.probability == 0


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
            result = requests.get(self.base_url + path , headers=headers, params=kwargs, auth=auth)
            result.raise_for_status()
            return result.json()
        if method.lower() == 'put':
            return requests.put(self.base_url + path , headers=headers, data=json.dumps(kwargs), auth=auth)
        else:
            raise ValueError

    def get(self, path, **kwargs):
        return self.request('get', path, **kwargs)

    def put(self, path, data):
        return self.request('put', path, **data)

    def opportunities(self, **kwargs):
        get_options = ''
        if kwargs:
            get_options = '?' + "&".join([x + "=" + y for (x,y) in kwargs.items()])
        result = self.get('opportunity' + get_options)['opportunities'].get('opportunity')
        if not result:
            return []
        if isinstance(result, dict):
            result = [result]
        return [Opportunity(x) for x in result]

    def full_opportunities(self, **kwargs):
        opportunities = self.opportunities(**kwargs)
        for opportunity in opportunities:
            self.inject_customfields(opportunity)
            self.inject_tags(opportunity)
        return opportunities

    def opportunity(self, opportunity_id):
        result = self.get('opportunity/' + str(opportunity_id))
        return Opportunity(result['opportunity'])

    def full_opportunity(self, opportunity_id):
        opportunity=self.opportunity(opportunity_id)
        self.inject_customfields(opportunity)
        self.inject_tags(opportunity)
        return opportunity

    def customfields(self, opportunity_id, **kwargs):
        get_options = ''
        if kwargs:
            get_options = '?' + "&".join([x + "=" + y for (x,y) in kwargs.items()])
        result = self.get('opportunity/' + opportunity_id + '/customfields' + get_options)
        if not result['customFields'].get('customField'):
            return []
        customfields = result['customFields']['customField']
        if isinstance(customfields, dict):
            customfields = [customfields]
        return customfields

    def tags(self, opportunity_id, **kwargs):
        get_options = ''
        if kwargs:
            get_options = '?' + "&".join([x + "=" + y for (x,y) in kwargs.items()])
        result = self.get('opportunity/' + opportunity_id + '/tag' + get_options)
        return result['tags'].get('tag') or []

    def inject_customfields(self, opportunity):
        return opportunity.load_customfields_from_api(self.customfields(opportunity.id))

    def inject_tags(self, opportunity):
        return opportunity.load_tags_from_api(self.tags(opportunity.id))

    def put_datatag(self, opportunity, name, date = None):
        date = date or datetime.date.today()
        new_datatag = {'tag':name, 'label':'Date', 'date':date.strftime('%Y-%m-%dT00:00:00Z')}
        result = {'customFields':{'customField':[new_datatag]}}
        response = self.put('opportunity/' + opportunity.id + '/customfields', result)


if __name__ == '__main__':
    crm = CapsuleAPI()
    print(crm.opportunities())
    

