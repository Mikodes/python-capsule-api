class CustomFieldsFetcher(object):
    def __init__(self, capsule_api):
        self._capsule_api = capsule_api

    def get_list(self, area, area_id, **kwargs):
        result = self._capsule_api.request.get('%s/%d/customfields' % (area, int(area_id)), **kwargs)
        customfields = result['customFields'].get('customField')
        if not customfields:
            return []
        if isinstance(customfields, dict):
            customfields = [customfields]
        return customfields

    def get_definitions(self, area):
        result = self._capsule_api.request.get('%s/customfield/definitions' % area)
        customfields = result['customFieldDefinitions'].get('customFieldDefinition')
        if not customfields:
            return []
        if isinstance(customfields, dict):
            customfields = [customfields]
        return customfields

    def put(self, area, area_id, **kwargs):
        data = {'customFields': {}}
        data['customFields']['customField'] = 'customField' in kwargs and kwargs['customField'] or kwargs
        self._capsule_api.request.put('%s/%d/customfields' % (area, int(area_id)), data)
