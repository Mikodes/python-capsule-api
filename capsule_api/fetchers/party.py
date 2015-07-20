class PartyFetcher(object):
    def __init__(self, capsule_api):
        self._capsule_api = capsule_api

    def get(self, party_id):
        result = self._capsule_api.request.get('party/%d' % int(party_id))
        if 'person' in result:
            result = result['person']
            result['person'] = True
            result['organisation'] = False
        else:
            result = result['organisation']
            result['person'] = False
            result['organisation'] = True
        return result

    def get_list(self, **kwargs):
        return self._capsule_api.request.get('party', **kwargs)['parties']

    def get_people(self, party_id):
        return self._capsule_api.request.get('party/%d/people' % int(party_id))['parties']

    def post_person(self, **kwargs):
        data = {'person': kwargs}
        resp = self._capsule_api.request.post('person', data=data)
        return resp.headers.get('location', '').split('/')[-1]

    def post_organisation(self, **kwargs):
        data = {'organisation': kwargs}
        resp = self._capsule_api.request.post('organisation', data=data)
        return resp.headers.get('location', '').split('/')[-1]

    def put_person(self, party_id, **kwargs):
        data = {'person': kwargs}
        self._capsule_api.request.put('person/%d' % int(party_id), data=data)

    def put_organisation(self, party_id, **kwargs):
        data = {'organisation': kwargs}
        self._capsule_api.request.put('organisation/%d' % int(party_id), data=data)

    def delete_contact(self, party_id, contact_id):
        self._capsule_api.request.delete('party/%d/contact/%d', (int(party_id), int(contact_id)))

    def delete(self, party_id):
        self._capsule_api.request.delete('party/%d' % int(party_id))
