class Tags(object):
    def __init__(self, capsule_api):
        self.capsule_api = capsule_api
        self.request = capsule_api.request

    def list(self, area, area_id, **kwargs):
        result = self.request.get('%s/%d/tag' % (area, int(area_id)), **kwargs)
        return result['tags'].get('tag', [])
