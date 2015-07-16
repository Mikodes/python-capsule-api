import requests
import requests.auth
import datetime

from .models import Opportunity


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
