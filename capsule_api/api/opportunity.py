import datetime


class Opportunity(object):
    def __init__(self, capsule_api, model=None):
        self.capsule_api = capsule_api
        self.request = capsule_api.request
        self.model = model or dict

    def list(self, **kwargs):
        result = self.request.get('opportunity', **kwargs)['opportunities'].get('opportunity')
        if not result:
            return []
        if isinstance(result, dict):
            result = [result]
        return [self.model(x) for x in result]

    def list_full(self, **kwargs):
        opportunities = self.list(**kwargs)
        for opportunity in opportunities:
            self.inject_customfields(opportunity)
            self.inject_tags(opportunity)
        return opportunities

    def get(self, opportunity_id):
        result = self.get('opportunity/%d' % int(opportunity_id))
        return self.model(result['opportunity'])

    def get_full(self, opportunity_id):
        opportunity = self.get(opportunity_id)
        self.inject_customfields(opportunity)
        self.inject_tags(opportunity)
        return opportunity

    def get_deleted(self, since):
        return self.request.get('opportunity/deleted', since=since)

    def get_contacts(self, opportunity_id):
        return self.request.get('opportunity/%d/party' % int(opportunity_id))

    def get_customfields(self, opportunity_id, **kwargs):
        return self.capsule_api.api.customfields.list('opportunity', opportunity_id, **kwargs)

    def get_tags(self, opportunity_id, **kwargs):
        return self.capsule_api.api.tags.list('opportunity', opportunity_id, **kwargs)

    def get_milestones(self):
        return self.request.get('opportunity/milestones')

    def post(self, party_id, name, milestone_id, **kwargs):
        kwargs['name'] = name
        kwargs['milestoneId'] = milestone_id
        track_id = kwargs.pop('trackId', None)
        params = None
        if track_id:
            params = {'trackId': track_id}
        return self.request.post('party/%d/opportunity' % int(party_id), kwargs, params=params)

    def post_contact(self, opportunity_id, party_id):
        return self.request.post('opportunity/%d/party/%d' % (int(opportunity_id), int(party_id)))

    def put(self, opportunity_id, **kwargs):
        return self.request.put('opportunity/%d' % int(opportunity_id), kwargs)

    def put_datatag(self, opportunity, name, date=None):
        # TODO: shift this to customfields api
        date = date or datetime.date.today()
        new_datatag = {'tag': name, 'label': 'Date', 'date': date.strftime('%Y-%m-%dT00:00:00Z')}
        result = {'customFields': {'customField': [new_datatag]}}
        self.put('opportunity/' + opportunity.id + '/customfields', result)

    def delete(self, opportunity_id):
        return self.request.delete('opportunity/%d' % int(opportunity_id))

    def delete_contact(self, opportunity_id, party_id):
        return self.delete('opportunity/%d/party/%d' % (int(opportunity_id), int(party_id)))

    def inject_customfields(self, opportunity):
        return opportunity.load_customfields_from_api(self.get_customfields(opportunity.id))

    def inject_tags(self, opportunity):
        return opportunity.load_tags_from_api(self.get_tags(opportunity.id))
