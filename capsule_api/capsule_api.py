import requests
import requests.auth
import dateutil.parser
from decimal import Decimal
import datetime
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

    @property
    def value(self):
        try:
            return Decimal(self['value'])
        except KeyError:
            return Decimal(0)

    @property
    def weighted_value(self):
        return self.value * self.probability / 100

    @property
    def tags(self):
        return list(x['name'] for x in self['tags_id'])

    @property
    def datatags(self):
        return OrderedDict((x['label'], dateutil.parser.parse(x['date']).date()) for x in sorted(self['raw_datatags'], key=lambda x: x['date']))

    @property
    def positive_outcome(self):
        return not self.open and self.probability == 100

    @property
    def negative_outcome(self):
        return not self.open and self.probability == 0

    def load_customfields_from_api(self, customfields):
        self['raw_customfields'] = [x for x in customfields if 'date' not in x]
        self['raw_datatags'] = [x for x in customfields if 'date' in x]

    def load_tags_from_api(self, tags):
        self['tags_id'] = [x for x in tags]

    def __getattr__(self, element):
        if element == 'customfields':
            raise AttributeError
        if element in self:
            return self[element]
        if element in self.customfields:
            return self.customfields[element]
        raise AttributeError


class CapsuleAPI(object):
    Opportunity = Opportunity

    def __init__(self, capsule_name, capsule_key):
        self.capsule_name = capsule_name
        self.capsule_key = capsule_key
        self.base_url = "https://%s.capsulecrm.com/api/" % capsule_name

    def request(self, method, path, params=None, **kwargs):
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
        return self.request('get', path, params=params, **kwargs)

    def put(self, path, data=None, params=None):
        if data:
            return self.request('put', path, params=params, **data)
        return self.request('put', path)

    def post(self, path, data=None, params=None):
        if data:
            return self.request('post', path, params=params, **data)
        return self.request('post', path)

    def delete(self, path, data=None, params=None):
        if data:
            return self.request('delete', path, params=params, **data)
        return self.request('delete', path)

    def opportunities(self, **kwargs):
        result = self.get('opportunity', **kwargs)['opportunities'].get('opportunity')
        if not result:
            return []
        if isinstance(result, dict):
            result = [result]
        return [self.Opportunity(x) for x in result]

    def full_opportunities(self, **kwargs):
        opportunities = self.opportunities(**kwargs)
        for opportunity in opportunities:
            self.inject_customfields(opportunity)
            self.inject_tags(opportunity)
        return opportunities

    def opportunity(self, opportunity_id):
        result = self.get('opportunity/' + str(opportunity_id))
        return self.Opportunity(result['opportunity'])

    def post_opportunity(self, party_id, name, milestone_id, **kwargs):
        kwargs['name'] = name
        kwargs['milestoneId'] = milestone_id
        track_id = kwargs.pop('trackId', None)
        params = None
        if track_id:
            params = {'trackId': track_id}
        return self.post('party/%d/opportunity' % int(party_id), kwargs, params=params)

    def put_opportunity(self, opportunity_id, **kwargs):
        return self.put('opportunity/%d' % int(opportunity_id), kwargs)

    def delete_opportunity(self, opportunity_id):
        return self.delete('opportunity/%d' % int(opportunity_id))

    def deleted_opportunities(self, since):
        return self.get('opportunity/deleted', since=since)

    def full_opportunity(self, opportunity_id):
        opportunity = self.opportunity(opportunity_id)
        self.inject_customfields(opportunity)
        self.inject_tags(opportunity)
        return opportunity

    def opportunity_contacts(self, opportunity_id):
        return self.get('opportunity/%d/party' % int(opportunity_id))

    def post_opportunity_contact(self, opportunity_id, party_id):
        return self.post('opportunity/%d/party/%d' % (int(opportunity_id), int(party_id)))

    def delete_opportunity_contact(self, opportunity_id, party_id):
        return self.delete('opportunity/%d/party/%d' % (int(opportunity_id), int(party_id)))

    def milestones(self):
        return self.get('opportunity/milestones')

    def customfields(self, opportunity_id, **kwargs):
        result = self.get('opportunity/' + opportunity_id + '/customfields', **kwargs)
        if not result['customFields'].get('customField'):
            return []
        customfields = result['customFields']['customField']
        if isinstance(customfields, dict):
            customfields = [customfields]
        return customfields

    def tags(self, opportunity_id, **kwargs):
        result = self.get('opportunity/' + opportunity_id + '/tag', **kwargs)
        return result['tags'].get('tag') or []

    def inject_customfields(self, opportunity):
        return opportunity.load_customfields_from_api(self.customfields(opportunity.id))

    def inject_tags(self, opportunity):
        return opportunity.load_tags_from_api(self.tags(opportunity.id))

    def put_datatag(self, opportunity, name, date=None):
        date = date or datetime.date.today()
        new_datatag = {'tag': name, 'label': 'Date', 'date': date.strftime('%Y-%m-%dT00:00:00Z')}
        result = {'customFields': {'customField': [new_datatag]}}
        self.put('opportunity/' + opportunity.id + '/customfields', result)
