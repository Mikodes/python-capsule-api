class CustomFields(object):
    def __init__(self, capsule_api):
        self.capsule_api = capsule_api
        self.request = capsule_api.request

    def list(self, area, area_id, **kwargs):
        result = self.request.get('%s/%d/customfields' % (area, int(area_id)), **kwargs)
        if not result['customFields'].get('customField'):
            return []
        customfields = result['customFields']['customField']
        if isinstance(customfields, dict):
            customfields = [customfields]
        return customfields
