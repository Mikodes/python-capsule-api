import requests
import requests.auth
from decimal import Decimal
import datetime
import json
from collections import OrderedDict


def capsule_datetime_to_utc_aware(datetime_string):
    return datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)


class CustomFieldsMixin(object):
    @property
    def customfields(self):
        def to_tuple(entry):
            if 'text' in entry:
                return (entry['label'], entry['text'])
            if 'boolean' in entry:
                return (entry['label'], entry['boolean'] == 'true')
            if 'number' in entry:
                return (entry['label'], entry['number'])
            raise ValueError

        try:
            custom_fields = self.get('raw_customfields') or self['customfields']  # FIXME attempts old format until all objects are converted to raw_
            return dict(to_tuple(x) for x in custom_fields)
        except KeyError:
            raise AttributeError('customfields')

    @property
    def datatags(self):
        try:
            return OrderedDict((x.get('tag') or x['label'], capsule_datetime_to_utc_aware(x['date']).date()) for x in sorted(self['raw_datatags'], key=lambda x: x['date']))
        except KeyError:
            raise AttributeError('datatags')

    @property
    def tags(self):
        return list(x['name'] for x in self['tags_id'])

    def load_customfields_from_api(self, customfields):
        self['raw_customfields'] = [x for x in customfields if 'date' not in x]
        self['raw_datatags'] = [x for x in customfields if 'date' in x]

    def load_tags_from_api(self, tags):
        self['tags_id'] = [x for x in tags]


class Opportunity(dict, CustomFieldsMixin):

    @property
    def createdOn(self):
        return capsule_datetime_to_utc_aware(self['createdOn'])

    @property
    def expectedCloseDate(self):
        try:
            return capsule_datetime_to_utc_aware(self['expectedCloseDate'])
        except KeyError:
            raise AttributeError

    @property
    def actualCloseDate(self):
        try:
            return capsule_datetime_to_utc_aware(self['actualCloseDate'])
        except KeyError:
            raise AttributeError

    @property
    def updatedOn(self):
        return capsule_datetime_to_utc_aware(self['updatedOn'])

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
    def value(self):
        try:
            return Decimal(self['value'])
        except KeyError:
            return Decimal(0)

    @property
    def weighted_value(self):
        return self.value * self.probability / 100

    @property
    def positive_outcome(self):
        return not self.open and self.probability == 100

    @property
    def negative_outcome(self):
        return not self.open and self.probability == 0


    def __getattr__(self, element):
        if element == 'customfields':
            raise AttributeError
        if element in self:
            return self[element]
        if element in self.customfields:
            return self.customfields[element]
        raise AttributeError


class Party(dict, CustomFieldsMixin):

    @property
    def id(self):
        return self['id']

    @property
    def is_organisation(self):
        return 'name' in self

    @property
    def is_person(self):
        return 'firstName' in self or 'lastName' in self

    @property
    def name(self):
        if not self.is_organisation:
            raise AttributeError('name')
        return self['name']

    @property
    def first_name(self):
        if not self.is_person:
            raise AttributeError('first_name')
        return self.get('firstName', '')

    @property
    def first_name(self):
        if not self.is_person:
            raise AttributeError('last_name')
        return self.get('lastName', '')

    @property
    def contacts(self):
        # capsule returns an empty string if no contact details are provided
        return self['contacts'] or {}

    @property
    def emails(self):
        emails = self.contacts.get('email')
        if not emails:
            raise AttributeError('emails')
        if isinstance(emails, dict):
            emails = [emails]
        return [e['emailAddress'] for e in emails]

    @property
    def phone_numbers(self):
        phone_numbers = self.contacts.get('phone')
        if not phone_numbers:
            raise AttributeError('phone_numbers')
        if isinstance(phone_numbers, dict):
            phone_numbers = [phone_numbers]
        return [p['emailAddress'] for p in phone_numbers]


class CapsuleAPI(object):
    Opportunity = Opportunity
    Party = Party

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
        method = method.lower()
        if method == 'get':
            result = requests.get(self.base_url + path, headers=headers, params=kwargs, auth=auth)
            result.raise_for_status()
            return result.json()
        if method in ('put', 'post', 'delete'):
            result = getattr(requests, method)(self.base_url + path, headers=headers, data=json.dumps(kwargs), auth=auth)
            result.raise_for_status()
            return result
        else:
            raise ValueError

    def get(self, path, **kwargs):
        return self.request('get', path, **kwargs)

    def put(self, path, data):
        return self.request('put', path, **data)

    def post(self, path, data):
        return self.request('post', path, **data)

    def delete(self, path, data):
        return self.request('delete', path, **data)

    def get_opportunities_by_party(self, party):
        result = self.get('party/%d/opportunity' %int(party.id))['opportunities'].get('opportunity')
        if not result:
            return []
        if isinstance(result, dict):
            result = [result]
        return [self.Opportunity(x) for x in result]

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

    def delete_opportunity(self, opportunity_id):
        return self.delete('opportunity/' + str(opportunity_id), {})

    def opportunity(self, opportunity_id):
        result = self.get('opportunity/' + str(opportunity_id))
        return self.Opportunity(result['opportunity'])

    def full_opportunity(self, opportunity_id):
        opportunity = self.opportunity(opportunity_id)
        self.inject_customfields(opportunity)
        self.inject_tags(opportunity)
        return opportunity

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

    def post_organisation(self, name, **kwargs):
        kwargs['name'] = name
        data = {'organisation': kwargs}
        resp = self.post('organisation', data)
        return resp.headers['location'].split('/')[-1]

    def post_person(self, **kwargs):
        if 'firstName' not in kwargs and 'lastName' not in kwargs:
            raise ValueError('first_name or last_name must be provided')
        data = {'person': kwargs}
        resp = self.post('person', data)
        return resp.headers['location'].split('/')[-1]

    def post_opportunity(self, name, party_id, milestone_id, **kwargs):
        kwargs['name'] = name
        kwargs['milestoneId'] = milestone_id
        data = {'opportunity': kwargs}
        resp = self.post('party/%d/opportunity' % int(party_id), data)
        return resp.headers['location'].split('/')[-1]

    def put_opportunity(self, opportunity_id, **kwargs):
        data = {'opportunity': kwargs}
        self.put('opportunity/%d' % int(opportunity_id), data)

    def put_opportunity_customfields(self, opportunity_id, data):
        if isinstance(data, dict):
            data = [data]
        data = {'customFields': {'customField': data}}
        self.put('opportunity/%d/customfields' % int(opportunity_id), data)

    def post_opportunity_history(self, opportunity_id, **kwargs):
        data = {'historyItem': kwargs}
        resp = self.post('opportunity/%d/history' % int(opportunity_id), data)
        return resp.headers['location'].split('/')[-1]

    def milestones(self):
        resp = self.get('opportunity/milestones')
        milestones = resp['milestones'].get('milestone')
        if not milestones:
            return []
        if isinstance(milestones, dict):
            milestones = [milestones]
        return milestones

    def users(self):
        resp = self.get('users')
        users = resp['users'].get('user')
        if not users:
            return []
        if isinstance(users, dict):
            users = [users]
        return users

    def parties(self, **kwargs):
        result = self.get('party', **kwargs)['parties']
        people = result.get('person')
        if not people:
            people = []
        if isinstance(people, dict):
            people = [people]

        organisations = result.get('organisation')
        if not organisations:
            organisations = []
        if isinstance(organisations, dict):
            organisations = [organisations]
        return [self.Party(x) for x in people], [self.Party(x) for x in organisations]

    def party(self, party_id):
        result = self.get('party/%s' % str(party_id))
        return self.Party(result.get('person', result['organisation']))

    def people(self, party_id):
        result = self.get('party/%s/people' % str(party_id))['parties']
        people = result.get('person')
        if not people:
            people = []
        if isinstance(people, dict):
            people = [people]
        return [self.Party(x) for x in people]
