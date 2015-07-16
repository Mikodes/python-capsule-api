class CustomFieldsFetcher(object):
    def __init__(self, capsule_api):
        self._capsule_api = capsule_api

    def get_list(self, area, area_id, **kwargs):
        result = self._capsule_api.request.get('%s/%d/customfields' % (area, int(area_id)), **kwargs)
        if not result['customFields'].get('customField'):
            return []
        customfields = result['customFields']['customField']
        if isinstance(customfields, dict):
            customfields = [customfields]
        return customfields
