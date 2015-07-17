class PartyFetcher(object):
    def __init__(self, capsule_api):
        self._capsule_api = capsule_api

    def get(self, party_id):
        return self._capsule_api.request.get('party/%d' % int(party_id))

    def get_list(self, **kwargs):
        return self._capsule_api.request.get('party', **kwargs)

    def get_people(self, party_id):
        return self._capsule_api.request.get('party/%d/people' % int(party_id))

    def post_person(self, **kwargs):
        return self._capsule_api.request.post('person', data=kwargs)

    def post_organisation(self, **kwargs):
        return self._capsule_api.request.post('organisation', data=kwargs)

    def put_person(self, party_id, **kwargs):
        return self._capsule_api.request.put('person/%d' % int(party_id), data=kwargs)

    def put_organisation(self, party_id, **kwargs):
        return self._capsule_api.request.put('organisation/%d' % int(party_id), data=kwargs)

    def delete_contact(self, party_id, contact_id):
        return self._capsule_api.request.delete('party/%d/contact/%d', (int(party_id), int(contact_id)))

    def delete_party(self, party_id):
        return self._capsule_api.request.delete('party/%d' % int(party_id))
